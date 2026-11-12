#!/usr/bin/env python3
"""Revenue finder report engine. Feed it a payload, never edit this file.

Usage:    python3 <skill folder>/references/templates/build_report.py <report>.json [<report>.pdf]
          Run from the user's working folder. Without a PDF name, the PDF takes
          the payload's name, for example harbor-fabrication-revenue-finder.pdf.
          Writing inside the skill folder is refused.
Requires: pip install reportlab

The payload carries what survived the four cuts. The engine checks the skill's
hard rules (at most five findings, no score-one rows, every finding quoted and
sourced, no quote serving two services, no price on a generic catalog, the
unread-meeting count present), ranks by score and then value, and draws the
page. A payload that breaks a rule prints the reason and writes no file.

This PDF never passes through theme.py. The Kick brand tokens live here. Red
is reserved for what could not be read. Inter sits beside this script. A
Helvetica fallback is off-brand and must not be handed over.

Payload:
  client          str, the client's name
  firm            str, optional, the firm's name for the page header
  window          {start, end}, YYYY-MM-DD
  catalog         {kind: "firm"|"generic", source: str, services: int}
  candidates      int, how many candidates entered the cuts
  coverage        {sources: [{name, read, unread, note}], unread_meetings: int,
                   ledger: str or null, ledger_ties: bool (default true)}
                  ledger_ties false locks every ledger line to "none" and allows
                  no ledger signals
  opportunities   [{service, annual_value (number or null), score (2 or 3), quote,
                    speaker, source_kind, source, date, link, why,
                    ledger: {state: "corroborated"|"contradicted"|"none", detail},
                    next_step, support}]
                  source_kind is transcript, email, chat, portal, or note. A note
                  never scores 3. link is optional. support is optional, at most
                  two [{text, speaker, source_kind, source, date}] backing lines
  inference       [{service, reason}], score-one rows, printed as the runner's own
  raised_before   [{service, kind, detail, date}], kind is declined, pitched,
                  promised, promised_not_in_scope, or in_scope
  referrals       [{need, quote, speaker, date, source}]
  ledger_signals  [{signal, figure, source, question}], from the books, never ranked
  could_not_see   [str]
  method_notes    [str], never drawn on the page; printed as method_note= lines
                  for the chat handoff
"""

import json
import os
import re
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageTemplate,
                                Paragraph, Table, TableStyle)

INK = colors.HexColor("#0f1826")
INK2 = colors.HexColor("#515d71")
MUT = colors.HexColor("#949ba7")
LINE = colors.HexColor("#e9ecf0")
HEAD = colors.HexColor("#eef0f3")
BASE = colors.HexColor("#f6f8fa")
MISS = colors.HexColor("#9f4237")
QUOTE_BAR = colors.HexColor("#a8deff")
SCORE_FILLS = {3: "#bfe6d4", 2: "#dfe7ef"}
ACCENT = {3: colors.HexColor("#2e9e6e"), 2: colors.HexColor("#8aa1b8")}
GREEN_TXT = "#1d6b4a"
SLATE_TXT = "#3f5670"
BLUE_TXT = "#1b5f8f"
SLATE_BG = colors.HexColor("#f1f4f8")
SLATE_LINE = colors.HexColor("#8aa1b8")
LEDGER_PILL = {"corroborated": ("#d6f0e3", GREEN_TXT, "Books agree"),
               "contradicted": ("#f6dcd8", "#9f4237", "Books disagree"),
               "none": ("#eef0f3", "#515d71", "No ledger signal")}

FONT = "Helvetica"
FONTB = "Helvetica-Bold"

SOURCE_KINDS = ("transcript", "email", "chat", "portal", "note")
LEDGER_STATES = ("corroborated", "contradicted", "none")
STRENGTH = {3: "Named the need", 2: "Described the situation"}
RAISED_KINDS = {"declined": "Declined", "pitched": "Pitched, left open", "promised": "Promised",
                "promised_not_in_scope": "Promised, not in scope", "in_scope": "In scope"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def register_inter():
    global FONT, FONTB
    here = os.path.dirname(os.path.abspath(__file__))
    regular = os.path.join(here, "inter-latin-400.ttf")
    bold = os.path.join(here, "inter-latin-640.ttf")
    if not (os.path.isfile(regular) and os.path.isfile(bold)):
        print("warning: inter-latin-400.ttf / inter-latin-640.ttf not found beside "
              "this script, falling back to Helvetica. A fallback build is off-brand "
              "and must not be handed over.")
        return
    pdfmetrics.registerFont(TTFont("Inter", regular))
    pdfmetrics.registerFont(TTFont("Inter-Semibold", bold))
    FONT, FONTB = "Inter", "Inter-Semibold"


def money(n):
    n = int(round(float(n)))
    return f"-${abs(n):,}" if n < 0 else f"${n:,}"


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


ISO_IN_TEXT = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def human(d):
    """2025-12-12 -> Dec 12th, 2025. Text that is not a date passes through."""
    def one(m):
        y, mo, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if not (1 <= mo <= 12 and 1 <= day <= 31):
            return m.group(0)
        suffix = "th" if 11 <= day % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return f"{MONTHS[mo - 1]} {day}{suffix}, {y}"
    return ISO_IN_TEXT.sub(one, str(d or ""))


def found(n):
    return f"{n} {'opportunity' if n == 1 else 'opportunities'} found"


def reviewed(n):
    return f"{n} {'possibility' if n == 1 else 'possibilities'} reviewed"


def _txt(s):
    """Escape the runner's own prose, with its dates made human. Never for quotes."""
    return _esc(human(s))


def need(row, key, what):
    v = row.get(key)
    if v is None or (isinstance(v, str) and not v.strip()):
        fail(f"{what} needs {key}")
    return v.strip() if isinstance(v, str) else v


def norm_quote(q):
    return re.sub(r"[^a-z0-9 ]", "", " ".join(q.lower().split()))


CAPS = {"quote": 40, "why": 15, "next_step": 15, "ledger": 20, "support": 20, "note": 10,
        "signal": 6, "figure": 10, "question": 15, "raised": 15, "referral": 25,
        "reason": 15, "could_not_see": 15, "method_note": 20}


def short(text, cap, what):
    n = len(str(text).split())
    if n > CAPS[cap]:
        fail(f"{what} is {n} words; the limit is {CAPS[cap]}. Cut it, keep the fact")


def derive(data):
    client = need(data, "client", "the payload")
    window = data.get("window") or {}
    start, end = window.get("start"), window.get("end")
    if not (start and end and DATE_RE.match(start) and DATE_RE.match(end)):
        fail("window needs start and end as YYYY-MM-DD")
    if start > end:
        fail("window start is after its end")

    catalog = data.get("catalog") or {}
    kind = catalog.get("kind")
    if kind not in ("firm", "generic"):
        fail('catalog.kind must be "firm" or "generic"')
    generic = kind == "generic"

    cov = data.get("coverage") or {}
    if not isinstance(cov.get("unread_meetings"), int) or cov["unread_meetings"] < 0:
        fail("coverage.unread_meetings must be a whole number, 0 when every meeting was read")
    sources = cov.get("sources") or []
    if not sources:
        fail("coverage.sources needs at least one row")
    for s in sources:
        need(s, "name", "a coverage row")
        for k in ("read", "unread"):
            if not isinstance(s.get(k, 0), int) or s.get(k, 0) < 0:
                fail(f"coverage row {s['name']}: {k} must be a whole number")
    ledger = (cov.get("ledger") or "").strip() or None
    ties = cov.get("ledger_ties", True)
    if not isinstance(ties, bool):
        fail("coverage.ledger_ties must be true or false")
    if EMAIL_RE.search(json.dumps(data)):
        fail("the payload holds an email address; name people by name and role")

    opps = data.get("opportunities") or []
    if len(opps) > 5:
        fail(f"{len(opps)} findings survived; more than five means the cuts were too soft. "
             "Raise the bar and rerun the cuts")
    seen = {}
    for o in opps:
        what = f"finding {o.get('service') or '?'}"
        need(o, "service", what)
        for k in ("quote", "speaker", "source", "date", "why", "next_step"):
            need(o, k, what)
        if not DATE_RE.match(o["date"]):
            fail(f"{what}: date must be YYYY-MM-DD")
        score = o.get("score")
        if score == 1:
            fail(f"{what}: a score of one does not ship; move it to inference or cut it")
        if score not in (2, 3):
            fail(f"{what}: score must be 2 or 3")
        sk = o.get("source_kind")
        if sk not in SOURCE_KINDS:
            fail(f"{what}: source_kind must be one of {', '.join(SOURCE_KINDS)}")
        if sk == "note" and score == 3:
            fail(f"{what}: a note is a colleague's summary and never scores three")
        val = o.get("annual_value")
        if val is not None:
            if generic:
                fail(f"{what}: a generic catalog carries no prices; set annual_value to null")
            try:
                if float(val) <= 0:
                    fail(f"{what}: annual_value must be positive or null")
            except (TypeError, ValueError):
                fail(f"{what}: annual_value must be a number or null")
        lg = o.get("ledger") or {}
        if lg.get("state") not in LEDGER_STATES:
            fail(f"{what}: ledger.state must be one of {', '.join(LEDGER_STATES)}")
        if lg["state"] != "none" and not ledger:
            fail(f"{what}: ledger says {lg['state']} but coverage.ledger names no connected ledger")
        if lg["state"] != "none" and not (lg.get("detail") or "").strip():
            fail(f"{what}: a {lg['state']} ledger line needs its detail and source")
        if lg["state"] != "none" and not ties:
            fail(f"{what}: the books did not tie, so the ledger line must be none")
        support = o.get("support") or []
        if len(support) > 2:
            fail(f"{what}: at most two support lines")
        for sp in support:
            for k in ("text", "speaker", "source", "date"):
                need(sp, k, f"{what} support line")
            if sp.get("source_kind") not in SOURCE_KINDS:
                fail(f"{what}: support source_kind must be one of {', '.join(SOURCE_KINDS)}")
            short(sp["text"], "support", f"{what} support line")
        short(o["quote"], "quote", f"{what} quote")
        short(o["why"], "why", f"{what} why")
        short(o["next_step"], "next_step", f"{what} next step")
        short(lg.get("detail") or "", "ledger", f"{what} ledger detail")
        key = norm_quote(o["quote"])
        if key in seen:
            fail(f"one quote serves {seen[key]} and {o['service']}; a moment cited for "
                 "several services is evidence for none")
        seen[key] = o["service"]

    def rank(o):
        v = o.get("annual_value")
        return (-o["score"], 0 if v is not None else 1, -(float(v) if v is not None else 0))
    opps = sorted(opps, key=rank)

    for r in data.get("ledger_signals") or []:
        for k in ("signal", "figure", "source", "question"):
            need(r, k, "a ledger signal")
        for k in ("signal", "figure", "question"):
            short(r[k], k, f"ledger signal {k}")
    if (data.get("ledger_signals") or []) and not ledger:
        fail("ledger_signals need a connected ledger named in coverage.ledger")
    if (data.get("ledger_signals") or []) and not ties:
        fail("the books did not tie, so no ledger signals are listed")
    if len(data.get("ledger_signals") or []) > 3:
        fail("at most three ledger signals")
    for r in data.get("referrals") or []:
        for k in ("need", "quote", "speaker", "date", "source"):
            need(r, k, "a referral")
        short(r["quote"], "referral", f"referral {r['need']} quote")
    for r in data.get("raised_before") or []:
        for k in ("service", "detail"):
            need(r, k, "a raised-before row")
        short(r["detail"], "raised", f"raised-before row {r['service']}")
        if r.get("kind") not in RAISED_KINDS:
            fail(f"raised-before row {r['service']}: kind must be one of {', '.join(RAISED_KINDS)}")
    for r in data.get("inference") or []:
        for k in ("service", "reason"):
            need(r, k, "an inference row")
        short(r["reason"], "reason", f"inference row {r['service']}")
    for s in sources:
        short(s.get("note") or "", "note", f"coverage note for {s['name']}")
    if len(data.get("could_not_see") or []) > 3:
        fail("at most three could-not-see lines; coverage already shows unread sources")
    for i in data.get("could_not_see") or []:
        short(i, "could_not_see", "a could-not-see line")
    notes = data.get("method_notes") or []
    if len(notes) > 5:
        fail("at most five method notes; keep the ones that change a fix to the binding")
    for i in notes:
        short(i, "method_note", "a method note")

    candidates = data.get("candidates")
    if not isinstance(candidates, int) or candidates < len(opps):
        fail("candidates must be a whole number at least the count of findings")

    return {
        "client": client, "firm": (data.get("firm") or "").strip(),
        "start": start, "end": end, "generic": generic,
        "catalog_source": (catalog.get("source") or "").strip(),
        "catalog_count": catalog.get("services"),
        "candidates": candidates, "sources": sources,
        "unread_meetings": cov["unread_meetings"], "ledger": ledger, "ties": ties,
        "opps": opps,
        "inference": data.get("inference") or [],
        "raised_before": data.get("raised_before") or [],
        "referrals": data.get("referrals") or [],
        "ledger_signals": data.get("ledger_signals") or [],
        "could_not_see": data.get("could_not_see") or [],
        "method_notes": data.get("method_notes") or [],
    }


def styles():
    return {
        "h1": ParagraphStyle("h1", fontName=FONTB, fontSize=21, leading=25, textColor=INK),
        "sub": ParagraphStyle("sub", fontName=FONT, fontSize=9, leading=13, textColor=INK2, spaceBefore=3),
        "h2": ParagraphStyle("h2", fontName=FONTB, fontSize=11.5, leading=14, textColor=INK,
                             spaceBefore=13, spaceAfter=3),
        "h3": ParagraphStyle("h3", fontName=FONTB, fontSize=9.6, leading=12.5, textColor=INK,
                             spaceBefore=9, spaceAfter=2),
        "lede": ParagraphStyle("lede", fontName=FONT, fontSize=7.8, leading=11, textColor=MUT, spaceAfter=5),
        "body": ParagraphStyle("body", fontName=FONT, fontSize=8.4, leading=12, textColor=INK,
                               spaceBefore=2, spaceAfter=2),
        "result": ParagraphStyle("result", fontName=FONTB, fontSize=9.4, leading=13, textColor=INK,
                                 spaceBefore=9, spaceAfter=2),
        "bad": ParagraphStyle("bad", fontName=FONTB, fontSize=8.4, leading=12, textColor=MISS,
                              spaceBefore=3, spaceAfter=2),
        "quote": ParagraphStyle("quote", fontName=FONT, fontSize=9.2, leading=12.6, textColor=INK),
        "tile_n": ParagraphStyle("tile_n", fontName=FONTB, fontSize=17, leading=20, textColor=INK),
        "tile_l": ParagraphStyle("tile_l", fontName=FONT, fontSize=7.6, leading=10, textColor=INK2),
        "card_t": ParagraphStyle("card_t", fontName=FONTB, fontSize=11, leading=14, textColor=INK),
        "card_v": ParagraphStyle("card_v", fontName=FONTB, fontSize=11, leading=14, textColor=INK, alignment=2),
        "pill": ParagraphStyle("pill", fontName=FONTB, fontSize=7.2, leading=10, textColor=INK),
        "line": ParagraphStyle("line", fontName=FONT, fontSize=8.4, leading=12, textColor=INK),
        "call": ParagraphStyle("call", fontName=FONT, fontSize=8.6, leading=12.4, textColor=INK),
        "attr": ParagraphStyle("attr", fontName=FONT, fontSize=7.2, leading=10, textColor=MUT, spaceBefore=2),
        "note": ParagraphStyle("note", fontName=FONT, fontSize=7, leading=10, textColor=MUT),
        "cell": ParagraphStyle("cell", fontName=FONT, fontSize=7.8, leading=10, textColor=INK),
    }


def table(data, widths, width, left_cols=1, left_tail=0):
    scale = width / sum(widths)
    t = Table(data, colWidths=[w * scale for w in widths], hAlign="LEFT", repeatRows=1)
    style = [
        ("FONTNAME", (0, 0), (-1, -1), FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 7.8),
        ("TEXTCOLOR", (0, 0), (-1, 0), INK2),
        ("BACKGROUND", (0, 0), (-1, 0), HEAD),
        ("TEXTCOLOR", (0, 1), (0, -1), INK),
        ("TEXTCOLOR", (1, 1), (-1, -1), INK),
        ("ALIGN", (left_cols, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 3.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    if left_tail:
        style.append(("ALIGN", (len(widths) - left_tail, 0), (-1, -1), "LEFT"))
    t.setStyle(TableStyle(style))
    return t


def quote_block(o, S, width):
    attr = f"{_esc(o['speaker'])}, {_esc(o['source'])}, {_esc(human(o['date']))}"
    if o.get("link"):
        attr += f" (<link href=\"{_esc(o['link'])}\" color=\"#515d71\">open</link>)"
    if o["source_kind"] == "note":
        attr += ". A colleague's note, not the client's words"
    inner = [[Paragraph(f"\u201c{_esc(o['quote'])}\u201d", S["quote"])],
             [Paragraph(attr, S["attr"])]]
    t = Table(inner, colWidths=[width - 10], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BASE),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, QUOTE_BAR),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 1),
    ]))
    return t


LEDGER_LABEL = {"corroborated": "Corroborated", "contradicted": "Contradicted", "none": "No ledger signal"}


def pill(text, bg, fg):
    return f'<font backColor="{bg}" color="{fg}">&nbsp;{_esc(text)}&nbsp;</font>'


def tiles(items, S, width):
    cells = [[Paragraph(f'<font color="{c}">{_esc(n)}</font>', S["tile_n"]), Paragraph(_esc(l), S["tile_l"])]
             for n, l, c in items]
    gap = 6
    w = (width - gap * (len(items) - 1)) / len(items)
    row, widths = [], []
    for i, c in enumerate(cells):
        inner = Table([[c[0]], [c[1]]], colWidths=[w - 16])
        inner.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                   ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
        row.append(inner)
        widths.append(w)
        if i < len(cells) - 1:
            row.append("")
            widths.append(gap)
    t = Table([row], colWidths=widths, hAlign="LEFT")
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 8),
             ("BOTTOMPADDING", (0, 0), (-1, -1), 8), ("LEFTPADDING", (0, 0), (-1, -1), 8),
             ("RIGHTPADDING", (0, 0), (-1, -1), 8)]
    for i, (_, _, c) in enumerate(items):
        col = i * 2
        style += [("BACKGROUND", (col, 0), (col, 0), BASE),
                  ("LINEABOVE", (col, 0), (col, 0), 2.4, colors.HexColor(c))]
    t.setStyle(TableStyle(style))
    return t


def callout(html, S, width):
    t = Table([[Paragraph(html, S["call"])]], colWidths=[width], hAlign="LEFT")
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), SLATE_BG),
                           ("LINEBEFORE", (0, 0), (0, -1), 3, SLATE_LINE),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t


def card(i, o, S, width):
    v = o.get("annual_value")
    lg = o["ledger"]
    bg, fg, label = LEDGER_PILL[lg["state"]]
    sfg = GREEN_TXT if o["score"] == 3 else SLATE_TXT
    inner_w = width - 21
    head = Table([[Paragraph(f'<font color="{sfg}">{i}</font>&nbsp;&nbsp;{_esc(o["service"])}', S["card_t"]),
                   Paragraph(f"{money(v)} <font size=8 color=\"#515d71\">a year</font>" if v is not None
                             else '<font size=8 color="#515d71">Not priced</font>', S["card_v"])]],
                 colWidths=[inner_w * 0.7, inner_w * 0.3])
    head.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                              ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                              ("VALIGN", (0, 0), (-1, -1), "BOTTOM")]))
    pills = Paragraph(pill(STRENGTH[o["score"]], SCORE_FILLS[o["score"]], sfg) + "&nbsp;&nbsp;" +
                      pill(label, bg, fg), S["pill"])
    attr = f"{_esc(o['speaker'])}, {_esc(o['source'])}, {_esc(human(o['date']))}"
    if o.get("link"):
        attr += f" (<link href=\"{_esc(o['link'])}\" color=\"{BLUE_TXT}\">open</link>)"
    if o["source_kind"] == "note":
        attr += ". A colleague's note, not the client's words"
    rows = [[head], [pills],
            [Paragraph(f"\u201c{_esc(o['quote'])}\u201d", S["quote"])],
            [Paragraph(attr, S["attr"])]]
    for sp in o.get("support") or []:
        tag = "Note" if sp["source_kind"] == "note" else "Also said"
        rows.append([Paragraph(f"<b>{tag}:</b> \u201c{_esc(sp['text'])}\u201d {_esc(sp['speaker'])}, "
                               f"{_esc(human(sp['date']))}", S["attr"])])
    books = _txt(lg["detail"]) if lg.get("detail") else "Nothing in the books bears on this."
    rows += [[Paragraph(f'<font name="{FONTB}" color="{sfg}">Why</font>&nbsp;&nbsp;{_txt(o["why"])}', S["line"])],
             [Paragraph(f'<font name="{FONTB}" color="{fg}">Books</font>&nbsp;&nbsp;{books}', S["line"])],
             [Paragraph(f'<font name="{FONTB}" color="{BLUE_TXT}">Next</font>&nbsp;&nbsp;{_txt(o["next_step"])}', S["line"])]]
    t = Table(rows, colWidths=[width], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("LINEBEFORE", (0, 0), (0, -1), 3, ACCENT[o["score"]]),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 11), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ("TOPPADDING", (0, 0), (-1, 0), 7), ("BOTTOMPADDING", (0, 1), (-1, 1), 5),
        ("BACKGROUND", (0, 2), (-1, 3 + len(o.get("support") or [])), BASE),
        ("TOPPADDING", (0, 2), (-1, 2), 5),
        ("BOTTOMPADDING", (0, 3 + len(o.get("support") or [])), (-1, 3 + len(o.get("support") or [])), 5),
        ("TOPPADDING", (0, 4 + len(o.get("support") or [])), (-1, 4 + len(o.get("support") or [])), 5),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 7),
    ]))
    return t


def story(r, S, width):
    st = [Paragraph(_esc(f"Revenue finder: {r['client']}"), S["h1"])]
    sub = f"{human(r['start'])} to {human(r['end'])}. "
    if r["generic"]:
        sub += "Generic catalog: these services were not supplied by the firm, and no prices are shown."
    else:
        n = f"{r['catalog_count']} services" if r["catalog_count"] else "the firm's services"
        sub += f"Matched against {n}" + (f" from {r['catalog_source']}." if r["catalog_source"] else ".")
    st.append(Paragraph(_esc(sub), S["sub"]))

    opps = r["opps"]
    if not opps:
        line = f"No opportunities found, from {reviewed(r['candidates'])}. That is a valid result."
    else:
        line = f"{found(len(opps))}, from {reviewed(r['candidates'])}."
        line += f" Top finding: {opps[0]['service']}, {STRENGTH[opps[0]['score']].lower()}."
        priced = [o for o in opps if o.get("annual_value") is not None]
        if priced:
            top = max(priced, key=lambda o: float(o["annual_value"]))
            line += f" Highest value: {top['service']}, about {money(top['annual_value'])} a year."
        else:
            line += " No prices supplied, so findings rank on quote strength alone."
    if r["generic"]:
        line += " Generic catalog."
    st.append(Paragraph(_esc(line), S["result"]))

    unbilled = [x for x in r["raised_before"] if x["kind"] == "promised_not_in_scope"]
    priced = [float(o["annual_value"]) for o in opps if o.get("annual_value") is not None]
    um = r["unread_meetings"]
    items = [(f"{len(opps)}", f"{'opportunity' if len(opps) == 1 else 'opportunities'} found, "
                               f"from {reviewed(r['candidates'])}", "#2e9e6e")]
    if priced:
        items.append((money(sum(priced)), "a year combined, at the firm's prices", "#1b5f8f"))
    if unbilled:
        items.append((f"{len(unbilled)}", "promise outside the agreements: " + ", ".join(x["service"] for x in unbilled)
                      if len(unbilled) == 1 else "promises outside the agreements", "#8aa1b8"))
    items.append((f"{um}", f"calendar meeting{'s' if um != 1 else ''} not read", "#949ba7"))
    st += [Paragraph("", S["sub"]), tiles(items, S, width)]
    for x in unbilled:
        when = f" on {_esc(human(x['date']))}" if x.get("date") else ""
        st += [Paragraph("", S["sub"]), callout(
            f'<font name="{FONTB}" color="{SLATE_TXT}">Possibly unbilled: {_esc(x["service"])}</font><br/>'
            f"Promised{when}; the agreements do not include it. {_txt(x['detail'])}", S, width)]
    if r["ledger"] and not r["ties"]:
        st.append(Paragraph("The books did not tie, so nothing below is checked against them.", S["bad"]))

    if opps:
        st.append(Paragraph("Opportunities", S["h2"]))
        for i, o in enumerate(opps, start=1):
            st.append(KeepTogether([card(i, o, S, width), Paragraph("", S["attr"])]))

    cov_rows = [["Source", "Read", "Could not read", "Note"]]
    for s_ in r["sources"]:
        cov_rows.append([_esc(s_["name"]), str(s_.get("read", 0)), str(s_.get("unread", 0)),
                         Paragraph(_txt(s_.get("note") or ""), S["cell"])])
    cov = [Paragraph("Coverage", S["h2"]),
           table(cov_rows, [1.6, 0.6, 0.9, 3.4], width, left_tail=1)]
    if um:
        cov.append(Paragraph(
            f"{um} calendar meeting{'s' if um != 1 else ''} not read. Anything said only there is missing.", S["body"]))
    else:
        cov.append(Paragraph("Every calendar meeting in this window was read.", S["body"]))
    cov.append(Paragraph(_esc(f"Ledger: {r['ledger'] or 'not connected'}."), S["body"]))
    st.append(KeepTogether(cov))

    if r["ledger_signals"]:
        rows = [["Signal", "Figure", "Source", "Question to ask"]]
        for s in r["ledger_signals"]:
            rows.append([Paragraph(_txt(s["signal"]), S["cell"]), Paragraph(_txt(s["figure"]), S["cell"]),
                         Paragraph(_txt(s["source"]), S["cell"]), Paragraph(_txt(s["question"]), S["cell"])])
        st.append(KeepTogether([
            Paragraph("From the books: questions to ask", S["h2"]),
            Paragraph("Not asked for by the client, so not opportunities.", S["lede"]),
            table(rows, [1.6, 1.2, 1.6, 2.1], width, left_cols=99)]))

    if r["inference"]:
        st += [Paragraph("My inference, not the client's words", S["h2"])]
        st += [Paragraph(f"<b>{_esc(x['service'])}:</b> {_txt(x['reason'])}", S["body"]) for x in r["inference"]]

    if any(x["kind"] != "promised_not_in_scope" for x in r["raised_before"]):
        order = list(RAISED_KINDS)
        rows = [["Service", "Status", "Date", "Detail"]]
        for x in sorted((x for x in r["raised_before"] if x["kind"] != "promised_not_in_scope"),
                        key=lambda x: order.index(x["kind"])):
            rows.append([Paragraph(_esc(x["service"]), S["cell"]), RAISED_KINDS[x["kind"]],
                         _esc(human(x.get("date"))), Paragraph(_txt(x["detail"]), S["cell"])])
        st += [Paragraph("Raised before", S["h2"]),
               table(rows, [1.4, 1.3, 0.9, 3.4], width, left_cols=99)]

    if r["referrals"]:
        rows = [["Need", "Quote", "Who and when"]]
        for x in r["referrals"]:
            rows.append([Paragraph(_esc(x["need"]), S["cell"]), Paragraph(f"\u201c{_esc(x['quote'])}\u201d", S["cell"]),
                         Paragraph(f"{_esc(x['speaker'])}, {_esc(human(x['date']))}", S["cell"])])
        st += [Paragraph("Referrals out: refer, do not pitch", S["h2"]),
               table(rows, [1.4, 3.4, 1.7], width, left_cols=99)]

    st.append(Paragraph("What I could not see", S["h2"]))
    items = list(r["could_not_see"])
    if not r["ledger"]:
        items.append("The client's books: no ledger was connected, so nothing is corroborated.")
    if not items:
        items = ["Nothing beyond the coverage table above."]
    st += [Paragraph(_txt(i), S["body"]) for i in items]
    return st


DISCLAIMER = ("Read only. Nothing was written anywhere and no client was contacted. "
              "A discussion prompt, not a proposal.")
PW, PH = letter
LM = RM = 0.75 * inch
CW = PW - LM - RM


class Doc(BaseDocTemplate):
    def __init__(self, path, r):
        BaseDocTemplate.__init__(
            self, path, pagesize=letter, leftMargin=LM, rightMargin=RM,
            topMargin=0.75 * inch, bottomMargin=0.6 * inch,
            title=f"Revenue finder, {r['client']}, {human(r['start'])} to {human(r['end'])}", author="Kick")
        self.r = r
        frame = Frame(LM, 0.6 * inch, CW, PH - 0.75 * inch - 0.6 * inch, id="n",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id="body", frames=[frame], onPage=self.body_page)])

    def body_page(self, c, d):
        r = self.r
        c.saveState()
        c.setFont(FONT, 7)
        c.setFillColor(MUT)
        c.drawRightString(PW - RM, PH - 0.48 * inch, "  |  ".join(
            p for p in ("Revenue finder", r["client"], r["firm"], f"{human(r['start'])} to {human(r['end'])}") if p))
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.line(LM, PH - 0.6 * inch, PW - RM, PH - 0.6 * inch)
        c.setFont(FONT, 5.6)
        c.drawString(LM, 0.38 * inch, DISCLAIMER)
        c.setFont(FONT, 7)
        c.drawRightString(PW - RM, 0.38 * inch, str(c.getPageNumber()))
        c.restoreState()


def main():
    if len(sys.argv) not in (2, 3):
        fail("usage: python3 build_report.py <report>.json [<report>.pdf]")
    register_inter()
    try:
        data = json.loads(open(sys.argv[1], encoding="utf-8").read())
    except (OSError, json.JSONDecodeError) as e:
        fail(f"cannot read payload: {e}")
    r = derive(data)
    out = sys.argv[2] if len(sys.argv) == 3 else os.path.splitext(sys.argv[1])[0] + ".pdf"
    here = os.path.dirname(os.path.abspath(__file__))
    skill_root = os.path.dirname(os.path.dirname(here))
    if os.path.realpath(os.path.abspath(out)).startswith(os.path.realpath(skill_root) + os.sep):
        fail("write the report to the user's working folder, not inside the skill folder")
    Doc(out, r).build(story(r, styles(), CW))
    print(f"wrote {os.path.abspath(out)}")
    print(f"result={found(len(r['opps'])) if r['opps'] else 'No opportunities found'}, "
          f"from {reviewed(r['candidates'])}")
    print(f"unread_meetings={r['unread_meetings']}")
    print(f"ledger={r['ledger'] or 'not connected'}")
    print(f"catalog={'generic' if r['generic'] else 'firm'}")
    print(f"books_tie={'yes' if r['ties'] else 'no'}")
    for note in r["method_notes"]:
        print(f"method_note={note}")
    for i, o in enumerate(r["opps"], start=1):
        v = o.get("annual_value")
        print(f"finding={i}|{o['service']}|score {o['score']}|{money(v) if v is not None else 'not priced'}"
              f"|ledger {o['ledger']['state']}")
    for x in r["raised_before"]:
        if x["kind"] == "promised_not_in_scope":
            print(f"promised_not_in_scope={x['service']}")


if __name__ == "__main__":
    main()
