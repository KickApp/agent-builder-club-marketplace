#!/usr/bin/env python3
"""Apply the firm brand to a built advisory report.

    python3 theme.py SKILL.md report.html [report2.html ...]

Reads the config block out of the brand skill file and injects two blocks into each HTML file:

    <style  id="brand-theme">   palette and radius overrides, as :root custom properties
    <script id="brand-icons">   post-render DOM pass adding icons to KPI tiles and the callout

Both are replaced rather than appended, so running this repeatedly is safe.

Nothing here touches the renderer, the payload, or any number. It overrides the base :root by
cascade order and enhances the DOM after the template has finished drawing.
"""

import argparse
import base64
import json
import re
import sys
from pathlib import Path

# The base template defines these. Anything absent from the config falls through to it.
COLOR_KEYS = [
    "bg", "card", "line", "line2", "ink", "ink2", "mut", "mut2",
    "tint", "tintline", "accent", "prior", "neg", "posbar", "negbar", "negbg", "cmut",
]
# Hex, or rgb/rgba. Kick's borders are slate at low alpha rather than a flat grey, so the
# palette has to be able to say that. Categorical hues stay hex: a translucent series color
# would change meaning depending on what sat behind it.
HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
COLOR_RE = re.compile(
    r"^(?:#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})"
    r"|rgba?\(\s*[\d.]+\s*,\s*[\d.]+\s*,\s*[\d.]+\s*(?:,\s*[\d.]+\s*)?\))$"
)
# A theme value lands inside a CSS declaration, so it must not be able to close one and open
# a rule of its own. Belt and braces on top of the shape check above.
CSS_SAFE_RE = re.compile(r"^[A-Za-z0-9 ,.()#%/_-]+$")
JSON_BLOCK_RE = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)

FONT_FILE = "inter-latin.woff2"

STYLE_RE = re.compile(r'<style id="brand-theme">.*?</style>\s*', re.DOTALL)
SCRIPT_RE = re.compile(r'<script id="brand-icons">.*?</script>\s*', re.DOTALL)

# Lucide geometry, 24x24, stroke only. Embedded because the report must open with no network.
ICONS = {
    "trend":  '<polyline points="3 16.5 9 10.5 13 14.5 21 6.5"/><polyline points="15 6.5 21 6.5 21 12.5"/>',
    "trenddown": '<polyline points="3 7.5 9 13.5 13 9.5 21 17.5"/><polyline points="15 17.5 21 17.5 21 11.5"/>',
    "dollar": '<circle cx="12" cy="12" r="9"/><path d="M12 7v10"/>'
              '<path d="M14.8 9.6a2.4 2.4 0 0 0-2.4-1.9h-1.2a2 2 0 0 0 0 4h2.2a2 2 0 0 1 0 4h-1.4a2.4 2.4 0 0 1-2.4-1.9"/>',
    "wallet": '<rect x="3" y="6" width="18" height="13" rx="3"/><path d="M3 10h18"/><circle cx="17" cy="14.5" r="1.1"/>',
    "flame":  '<path d="M12 3c1 4 5 5 5 9a5 5 0 0 1-10 0c0-2 1-3.2 2-4.2 0 2 1 3 2 3 1-2-1-5 1-7.8z"/>',
    "clock":  '<circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15.5 14"/>',
    "users":  '<path d="M15 19v-1.6a3.4 3.4 0 0 0-3.4-3.4H6.4A3.4 3.4 0 0 0 3 17.4V19"/>'
              '<circle cx="9" cy="8" r="3.2"/><path d="M21 19v-1.6a3.4 3.4 0 0 0-2.6-3.3"/><path d="M15.6 5a3.2 3.2 0 0 1 0 6.1"/>',
    "pie":    '<path d="M21 15.5A9 9 0 1 1 8.5 3"/><path d="M21 11.5A8.5 8.5 0 0 0 12.5 3V11.5z"/>',
    "gauge":  '<path d="M4 18a9 9 0 1 1 16 0"/><path d="M12 18l4.2-5"/><circle cx="12" cy="18" r="1.3"/>',
    "receipt": '<path d="M5 3v18l2.5-1.6L10 21l2.5-1.6L15 21l2.5-1.6L20 21V3z"/><path d="M9 8h6M9 12h6"/>',
    "spark":  '<circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3'
              'M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1"/>',
    "box":    '<path d="M20.5 8.2v7.6a1.6 1.6 0 0 1-.85 1.4l-6.8 3.6a1.7 1.7 0 0 1-1.7 0l-6.8-3.6'
              'a1.6 1.6 0 0 1-.85-1.4V8.2a1.6 1.6 0 0 1 .85-1.4l6.8-3.6a1.7 1.7 0 0 1 1.7 0l6.8 3.6'
              'a1.6 1.6 0 0 1 .85 1.4z"/><polyline points="3.6 7.6 12 12 20.4 7.6"/><path d="M12 12v8.8"/>',
    "pin":    '<path d="M19 10.3c0 5-7 10.4-7 10.4s-7-5.4-7-10.4a7 7 0 0 1 14 0z"/>'
              '<circle cx="12" cy="10.1" r="2.6"/>',
    "bank":   '<path d="M12 3 3 7.8h18z"/><path d="M3 10.2h18"/>'
              '<path d="M6 10.2v7M10 10.2v7M14 10.2v7M18 10.2v7"/><path d="M3.8 20.4h16.4"/>',
    "dot":    '<circle cx="12" cy="12" r="7.5"/>',
}

# Matched against the lowercased KPI label, first hit wins, so order is meaningful.
# "net income" has to beat "income", and "cash on hand" has to beat "burn".
ICON_RULES = [
    # An up arrow beside "Least profitable" and a loss is the kind of detail that makes a
    # reader stop trusting the page, so the explicitly adverse labels are caught before the
    # profit rule can hand them the rising line. Deliberately narrow: "lowest cash" is a cash
    # tile and still wants the wallet.
    (["least profitable", "worst", "below cost", "net loss", "loss-making"], "trenddown"),
    # Anything measured in days or months of coverage. "days sales outstanding" has to be
    # caught here, or the "sales" in it falls through to the revenue rule.
    # "days " catches every duration measure in one go, and it has to outrank the rules
    # below it: "days to pay vendors" is a timing metric that happens to mention vendors,
    # not a vendor metric.
    (["runway", "months of", "days ", "aging", "dso", "dpo", "dio",
      "tied up", "shortfall"],                                         "clock"),
    (["burn", "spend", "expense", "cost", "opex", "payroll"],          "flame"),
    (["cash", "liquidity", "reserve", "working capital"],              "wallet"),
    # Anything owed to a lender, before the ratio rule, so "debt service coverage" reads as
    # debt rather than as one more gauge in a table that already has two.
    (["debt", "loan", "borrow", "leverage", "covenant", "interest"],   "bank"),
    (["margin", "ratio", "current ratio", "coverage"],                 "gauge"),
    (["customer", "client", "headcount", "employee", "member"],        "users"),
    (["mix", "share", "concentration"],                                "pie"),
    (["invoice", "receivable", "payable", "ar ", "ap ",
      "vendor", "supplier"],                                           "receipt"),
    (["income", "profit", "ebitda", "growth", "yoy"],                  "trend"),
    (["revenue", "sales", "bookings", "arr", "mrr"],                   "dollar"),
    # Dimension identifiers, last, so a financial word in the label always wins. "Branch
    # profit" is a profit tile that happens to be per branch, not a branch tile.
    (["product", "item", "sku", "seller"],                             "box"),
    (["branch", "location", "site", "store", "region", "office"],      "pin"),
]


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def load_brand(path, preset=None):
    """Pull the config out of the skill file. First fenced json block unless a preset is named."""
    try:
        text = Path(path).read_text()
    except OSError as e:
        fail(f"cannot read {path}: {e}")

    blocks = JSON_BLOCK_RE.findall(text)
    if not blocks:
        fail(f"{path} has no fenced json config block")

    chosen = blocks[0]
    if preset:
        marks = [m.start() for m in re.finditer(r"```json", text)]
        found = None
        for i, start in enumerate(marks):
            head = text[max(0, start - 200):start]
            if re.search(rf"preset:\s*{re.escape(preset)}\b", head, re.I):
                found = blocks[i]
                break
        if found is None:
            names = re.findall(r"^preset:\s*([A-Za-z0-9_-]+)", text, re.M) or ["(none defined)"]
            fail(f"no preset named {preset!r}. Available: {', '.join(names)}")
        chosen = found

    try:
        brand = json.loads(chosen)
    except json.JSONDecodeError as e:
        fail(f"config block in {path} is not valid JSON: line {e.lineno} column {e.colno}: {e.msg}")

    pal = brand.get("palette") or {}
    for k, v in pal.items():
        if k == "cats":
            if not isinstance(v, list) or not v:
                fail("palette.cats must be a non-empty array of hex colors")
            for c in v:
                if not HEX_RE.match(str(c)):
                    fail(f"palette.cats contains {c!r}, which is not a hex color")
        elif not COLOR_RE.match(str(v).strip()):
            fail(f"palette.{k} is {v!r}, which is not a color like #3793da "
                 "or rgba(83,100,126,0.13)")

    unknown = set(pal) - set(COLOR_KEYS) - {"cats"}
    if unknown:
        print(f"warning: palette keys the template does not use: {', '.join(sorted(unknown))}",
              file=sys.stderr)

    shadow = brand.get("shadow")
    if shadow and not CSS_SAFE_RE.match(str(shadow)):
        fail(f"shadow is {shadow!r}, which has characters a CSS value cannot carry")

    stack = ((brand.get("type") or {}).get("stack") or "").replace('"', "")
    if stack and not CSS_SAFE_RE.match(stack):
        fail("type.stack has characters a CSS font-family cannot carry")

    return brand


def font_face():
    """Embed Kick's typeface as a data URL.

    Kick is set in Inter, the report has to open with no network, and Inter is not installed on
    most machines. Linking Google Fonts would break the offline rule, and leaving Inter first in
    a fallback stack only works for the handful of readers who happen to have it. So the font
    travels inside the file: a Latin subset of the variable face, about 25 KB, covering 100-900
    in one payload. Returns "" if the file is missing, which degrades to the fallback stack
    rather than stopping a build over a typeface.
    """
    path = Path(__file__).resolve().parent / FONT_FILE
    try:
        blob = path.read_bytes()
    except OSError:
        print(f"warning: {FONT_FILE} not found beside theme.py, falling back to the system stack",
              file=sys.stderr)
        return ""
    if blob[:4] != b"wOF2":
        print(f"warning: {FONT_FILE} is not a woff2 file, falling back to the system stack",
              file=sys.stderr)
        return ""
    b64 = base64.b64encode(blob).decode("ascii")
    return (
        "/* Inter, SIL Open Font License 1.1. See inter-LICENSE.txt. */"
        "@font-face{font-family:Inter;font-style:normal;font-weight:100 900;font-display:swap;"
        f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
    )


def css_block(brand):
    pal = brand.get("palette") or {}
    firm = brand.get("firm") or {}
    typ = brand.get("type") or {}
    radius = brand.get("radius", 12)
    shadow = brand.get("shadow")

    rows = [f"--{k}:{pal[k]};" for k in COLOR_KEYS if k in pal]
    for i, c in enumerate(pal.get("cats") or [], start=1):
        rows.append(f"--c{i}:{c};")

    css = ['<style id="brand-theme">']

    if typ.get("embed", True):
        face = font_face()
        if face:
            css.append(face)
    css.append(":root{" + "".join(rows) + "}")

    # Type. Kick's scale, not a generic one: Inter, -0.005em base tracking, and 600 on the two
    # things a reader looks at first, the report title and the headline numbers. Everything
    # else stays 400 and 500, so the page still has three weights in it and no more.
    if typ.get("stack"):
        css.append(f"body{{font-family:{typ['stack']};letter-spacing:-.005em}}")
    css.append(
        ".ttl{font-weight:600;letter-spacing:-.018em}"
        ".k-v{font-weight:600;letter-spacing:-.025em}"
        ".co-v{font-weight:500}"
    )

    if radius != 12:
        css.append(f".card,.kpi,.callout{{border-radius:{radius}px}}")

    # One soft lift under cards, the same one the product uses. It is the difference between a
    # page that looks composed and one that looks like a table dump. Never in print, where a
    # shadow costs toner and buys nothing.
    if shadow:
        css.append(f".card,.kpi{{box-shadow:{shadow}}}")
        css.append(f"@media print{{.card,.kpi{{box-shadow:none}}}}")

    if firm.get("markColor"):
        css.append(f".mark{{background:{firm['markColor']}}}")
    css.append(
        ".k-l{display:flex;align-items:center;gap:6px}"
        ".bi{width:14px;height:14px;flex:none}"
        # Measure-list rows. inline-block rather than flex, because a flex td loses its
        # baseline and the label stops lining up with the figures beside it.
        ".mlist tbody td:first-child .bi{display:inline-block;vertical-align:-2px;"
        "margin-right:8px;color:var(--mut2)}"
        ".mlist tbody td:first-child{white-space:nowrap}"
        ".callout{display:flex;gap:10px;align-items:flex-start}"
        ".callout>.bi{width:16px;height:16px;margin-top:2px}"
        ".co-wrap{min-width:0}"
        # Containment. The template pins the card note with flex:none, so a long note holds its
        # full width, squeezes the title into a narrow column, and runs past the card edge.
        ".ch{align-items:baseline;flex-wrap:wrap}"
        ".ct{flex:1 1 auto;min-width:0;overflow-wrap:anywhere}"
        ".cn{flex:0 1 auto;min-width:0;max-width:52ch;text-align:right;"
        "white-space:normal;overflow-wrap:anywhere}"
        # A flex child will not shrink below its content unless min-width is cleared.
        ".hd,.b-hd,.f-t,.pl-r,.b-l,.b-ur,.lgd>*{min-width:0}"
        ".ttl,.ent,.b-nm,.b-sub,.f-t>*,.k-l,.k-s,.k-v,.co-v,.co-b{overflow-wrap:anywhere}"
        ".lgd{max-width:100%}"
    )
    css.append("</style>")
    return "\n".join(css) + "\n"


def script_block(brand):
    if not brand.get("icons", True):
        return ""
    firm = brand.get("firm") or {}
    cfg = {
        "icons": ICONS,
        "rules": [[kws, name] for kws, name in ICON_RULES],
        "mark": firm.get("mark") or None,
    }
    return (
        '<script id="brand-icons">\n'
        "(function(){\n"
        "  var B = " + json.dumps(cfg, ensure_ascii=False) + ";\n"
        "  function svg(name, cls){\n"
        "    var p = B.icons[name] || B.icons.dot;\n"
        "    return '<svg class=\"bi ' + (cls||'') + '\" viewBox=\"0 0 24 24\" fill=\"none\" '\n"
        "         + 'stroke=\"currentColor\" stroke-width=\"1.7\" stroke-linecap=\"round\" '\n"
        "         + 'stroke-linejoin=\"round\" aria-hidden=\"true\">' + p + '</svg>';\n"
        "  }\n"
        "  function pick(label){\n"
        "    var l = ' ' + String(label||'').toLowerCase() + ' ';\n"
        "    for (var i=0;i<B.rules.length;i++){\n"
        "      var kws = B.rules[i][0];\n"
        "      for (var j=0;j<kws.length;j++){ if (l.indexOf(kws[j]) !== -1) return B.rules[i][1]; }\n"
        "    }\n"
        "    return 'dot';\n"
        "  }\n"
        "  // Chart labels are SVG text, which CSS cannot truncate. Measure against the plot and\n"
        "  // clip anything hanging outside it, keeping the full string on hover.\n"
        "  function clampLabels(){\n"
        "    var svgs = document.querySelectorAll('svg');\n"
        "    for (var i=0;i<svgs.length;i++){\n"
        "      var box = svgs[i].getBoundingClientRect();\n"
        "      if (!box.width) continue;               // hidden view, measure it on tab switch\n"
        "      var texts = svgs[i].querySelectorAll('text');\n"
        "      for (var j=0;j<texts.length;j++){\n"
        "        var t = texts[j];\n"
        "        var full = t.getAttribute('data-full') || t.textContent;\n"
        "        if (!full) continue;\n"
        "        t.setAttribute('data-full', full);\n"
        "        t.textContent = full;\n"
        "        var r = t.getBoundingClientRect();\n"
        "        if (!r.width) continue;\n"
        "        if (r.left >= box.left - 0.5 && r.right <= box.right + 0.5) continue;\n"
        "        var s = full, guard = 0;\n"
        "        while (s.length > 3 && guard++ < 300){\n"
        "          s = s.slice(0, -1);\n"
        "          t.textContent = s.replace(/[\\s(,\\-]+$/, '') + '\\u2026';\n"
        "          r = t.getBoundingClientRect();\n"
        "          if (r.left >= box.left - 0.5 && r.right <= box.right + 0.5) break;\n"
        "        }\n"
        "        // Hand the full string to the report's own tooltip. An SVG <title> would\n"
        "        // raise the browser's native one on top of it after its own delay.\n"
        "        var host = t.closest ? t.closest('[data-tip]') : null;\n"
        "        if (!host) t.setAttribute('data-tip', full);\n"
        "      }\n"
        "    }\n"
        "  }\n"
        "  function run(){\n"
        "    // KPI tiles: one glyph per metric, every tile treated the same. A tile singled\n"
        "    // out in accent read as an active selection, which it never was.\n"
        "    var tiles = document.querySelectorAll('.kpi');\n"
        "    for (var i=0;i<tiles.length;i++){\n"
        "      var t = tiles[i], lab = t.querySelector('.k-l');\n"
        "      if (!lab || lab.querySelector('.bi')) continue;\n"
        "      lab.insertAdjacentHTML('afterbegin', svg(pick(lab.textContent)));\n"
        "      var g = lab.querySelector('.bi');\n"
        "      g.style.color = getComputedStyle(document.documentElement).getPropertyValue('--mut');\n"
        "    }\n"
        "    // Measure lists: one glyph per row, in the first cell, so a reader scanning for\n"
        "    // 'days to collect' finds it by shape. Injected inside the existing cell rather\n"
        "    // than as a new column, so the row still has as many cells as the table has\n"
        "    // headers and sorting keeps working.\n"
        "    var mrows = document.querySelectorAll('table.mlist tbody tr');\n"
        "    for (var m=0;m<mrows.length;m++){\n"
        "      var c0 = mrows[m].cells[0];\n"
        "      if (!c0 || c0.querySelector('.bi')) continue;\n"
        "      if (mrows[m].className.indexOf('tot') !== -1) continue;   // totals are arithmetic\n"
        "      var lab = (c0.textContent || '').trim();\n"
        "      if (!lab) continue;\n"
        "      c0.insertAdjacentHTML('afterbegin', svg(pick(lab)));\n"
        "    }\n"
        "    // Callout: the aha marker.\n"
        "    var cos = document.querySelectorAll('.callout');\n"
        "    for (var k=0;k<cos.length;k++){\n"
        "      var c = cos[k];\n"
        "      if (c.querySelector(':scope > .bi')) continue;\n"
        "      var wrap = document.createElement('div');\n"
        "      wrap.className = 'co-wrap';\n"
        "      while (c.firstChild) wrap.appendChild(c.firstChild);\n"
        "      c.appendChild(wrap);\n"
        "      c.insertAdjacentHTML('afterbegin', svg(c.classList.contains('neg') ? 'flame' : 'spark'));\n"
        "      c.querySelector(':scope > .bi').style.color =\n"
        "        getComputedStyle(document.documentElement)\n"
        "          .getPropertyValue(c.classList.contains('neg') ? '--neg' : '--accent');\n"
        "    }\n"
        "    // Firm override of the header mark. Absent, the client entity initials stand.\n"
        "    if (B.mark){\n"
        "      var m = document.querySelector('.mark');\n"
        "      if (m) m.textContent = B.mark;\n"
        "    }\n"
        "    clampLabels();\n"
        "  }\n"
        "  if (document.readyState === 'loading') {\n"
        "    document.addEventListener('DOMContentLoaded', run);\n"
        "  } else { run(); }\n"
        "  // Hidden tabs have no geometry, so re-measure when one is revealed or printed.\n"
        "  document.addEventListener('click', function(e){\n"
        "    if (e.target && e.target.classList && e.target.classList.contains('tab'))\n"
        "      setTimeout(clampLabels, 0);\n"
        "  }, true);\n"
        "  window.addEventListener('beforeprint', clampLabels);\n"
        "  window.addEventListener('resize', function(){ setTimeout(clampLabels, 120); });\n"
        "})();\n"
        "</script>\n"
    )


def apply(html, brand):
    html = STYLE_RE.sub("", html)
    html = SCRIPT_RE.sub("", html)

    style = css_block(brand)
    if "</head>" not in html:
        fail("template has no </head>, so the theme block has nowhere to go")
    html = html.replace("</head>", style + "</head>", 1)

    script = script_block(brand)
    if script:
        if "</body>" in html:
            html = html.replace("</body>", script + "</body>", 1)
        else:
            html += script
    return html


# singular, plural. "dash" does not pluralize by adding an s.
BANNED = {
    "\u2014": ("em dash", "em dashes"),
    "\u2013": ("en dash", "en dashes"),
    ";": ("semicolon", "semicolons"),
}
EMOJI_NAME = ("emoji", "emoji")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]")

# Words that are correct in a ledger schema and wrong in front of an owner. "Counterparty"
# is the field name in most accounting systems, which is exactly why it leaks into report
# copy. A reader has a vendor they pay and a customer who pays them, and no counterparties.
#
# The flag is whether the word fails the build. "Counterparty" and "payee" never appear in a
# real company name, so a hit is always prose and always wrong. "Supplier" does appear in
# company names, and failing the build on a vendor called Acme Supplier Co would be worse
# than the copy slip, so it reports and lets a human read it.
#
# The second group is over-specific dimension vocabulary. "Branch profitability" fits a bank
# and excludes a studio, a contractor, and a clinic, and the plugin ships one set of skills to
# all of them. The axis takes the general word; the members keep their own names, so a client
# with branches still reads their branch names down a Location column. See DIMENSIONS.md.
#
# All of these report rather than fail, because every one can legitimately appear in a member
# name a client chose. "Riverside Branch" as a row label is their data, not our copy, and
# refusing to build the report over it would be the worse error.
BANNED_WORDS = {
    "counterparty":   ("vendor, or customer", True),
    "counterparties": ("vendors, or customers", True),
    "payee":          ("vendor", True),
    "payor":          ("customer", True),
    "supplier":       ("vendor", False),
    "suppliers":      ("vendors", False),
    "branch":         ("location", False),
    "branches":       ("locations", False),
    "storefront":     ("location", False),
    "storefronts":    ("locations", False),
    "outlet":         ("location", False),
    "outlets":        ("locations", False),
    "sku":            ("product", False),
    "skus":           ("products", False),
}
BANNED_WORD_RE = re.compile(r"\b(" + "|".join(sorted(BANNED_WORDS, key=len, reverse=True)) + r")\b",
                            re.IGNORECASE)


def copy_audit(html, path):
    """Flag banned marks and ledger words in the payload strings. Never rewrite.

    Swapping an em dash for a period changes where a sentence ends, which is a writing
    decision. The brand pass says what is wrong and the skill that owns the copy fixes it
    at the source.

    Returns the number of hard failures, which are the ledger words that cannot appear in a
    company name and are therefore always prose. Punctuation only ever reports: it is a
    judgement call, and a report withheld over a dash helps nobody.
    """
    m = re.search(r'<script[^>]*id="data"[^>]*>(.*?)</script>', html, re.DOTALL)
    if not m:
        return 0
    try:
        payload = json.loads(m.group(1))
    except json.JSONDecodeError:
        return 0

    found = {}
    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, str):
            for ch, names in BANNED.items():
                if ch in node:
                    found.setdefault(names, []).append(node)
            if EMOJI_RE.search(node):
                found.setdefault(EMOJI_NAME, []).append(node)
            for hit in BANNED_WORD_RE.findall(node):
                w = hit.lower()
                found.setdefault((f'"{w}"', f'uses of "{w}"'), []).append(node)
    walk(payload)

    # A title is usually the first thing read in its card, so a trailing pronoun has nothing
    # behind it to refer to: "What moved it" makes the reader consult the chart to learn what
    # the chart is about. Only a title *ending* in one is flagged, which catches "What moved it"
    # and "Why it happened" while leaving "Products that lose money" alone, where the pronoun is
    # a relative one with its antecedent right there.
    # Split into two sets, because the same word is a pronoun in one position and a determiner
    # in another. "This quarter against last" is a fine title and "What moved this" is not, so
    # this/that/these/those are only flagged in the trailing slot. "It" and "them" have no
    # determiner sense and are flagged anywhere in a title.
    DANGLING = {"it", "them", "they", "this", "that", "these", "those", "us", "we"}
    ANYWHERE = {"it", "them", "they"}
    # Card headings and tab names only. A findings item also has a `title`, but it is a whole
    # sentence rather than a heading: "Value Copy Paper sells for less than it costs you" is
    # correct English with its antecedent three words away, and flagging it would train people
    # to ignore the warning.
    def titles(node):
        if isinstance(node, dict):
            for key in ("title", "name"):
                if isinstance(node.get(key), str):
                    yield node[key]
            for k, v in node.items():
                if k != "items":
                    yield from titles(v)
        elif isinstance(node, list):
            for v in node:
                yield from titles(v)
    for title in titles(payload):
        words = [w.lower() for w in re.findall(r"[A-Za-z']+", title)]
        if not words:
            continue
        if words[-1] in DANGLING or ANYWHERE & set(words):
            key = ('a title leaning on a pronoun', 'titles leaning on a pronoun')
            found.setdefault(key, []).append(title)

    hard = 0
    for (one, many), strings in sorted(found.items()):
        n = len(strings)
        bare = one.strip('"')
        rule = BANNED_WORDS.get(bare)
        tag = "error" if rule and rule[1] else "copy"
        print(f"{tag}: {n} {one if n == 1 else many} in {path}", file=sys.stderr)
        if rule:
            print(f"  say {rule[0]} instead", file=sys.stderr)
            if rule[1]:
                hard += n
        for sample in strings[:2]:
            snippet = sample if len(sample) <= 88 else sample[:85] + "..."
            print(f"  {snippet}", file=sys.stderr)
    return hard


def check_offline(html, path):
    """The report has to open on a plane. A remote reference is a defect, not a preference."""
    hits = re.findall(r'(?:src|href)\s*=\s*["\']https?://[^"\']+', html) + \
           re.findall(r"@import\s+url\(\s*['\"]?https?://[^)]+", html)
    if hits:
        print(f"warning: {path} references {len(hits)} remote resource(s). "
              "The report is meant to open with no network.", file=sys.stderr)
        for h in hits[:3]:
            print(f"  {h[:90]}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brand", help="path to the brand skill file")
    ap.add_argument("html", nargs="+", help="one or more built report files, edited in place")
    ap.add_argument("--preset", help="named preset block in the skill file")
    ap.add_argument("--no-copy-check", action="store_true",
                    help="skip the copy audit for banned punctuation")
    a = ap.parse_args()

    brand = load_brand(a.brand, a.preset)

    for f in a.html:
        p = Path(f)
        try:
            src = p.read_text()
        except OSError as e:
            fail(f"cannot read {f}: {e}")
        out = apply(src, brand)
        check_offline(out, f)
        if not a.no_copy_check and copy_audit(out, f):
            fail(f"copy: fix the wording in {f} and re-run, or pass --no-copy-check")
        p.write_text(out)
        accent = (brand.get("palette") or {}).get("accent", "template default")
        icons = "with icons" if brand.get("icons", True) else "no icons"
        print(f"themed {f} ({accent}, {icons})")


if __name__ == "__main__":
    main()
