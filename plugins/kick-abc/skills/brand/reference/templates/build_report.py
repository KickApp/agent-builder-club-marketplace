#!/usr/bin/env python3
"""Build an advisory HTML report from a JSON payload.

    python3 build_report.py data.json out.html

Writes the payload into report.html and validates it on the way through, so a
malformed number or an unknown section type fails here rather than rendering a
blank page in front of a client. Exits non-zero with the reason on any problem.

Optional flags:
    --template PATH   use a different template (default: report.html alongside this file)
    --strict          treat warnings as errors
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SECTION_TYPES = {
    "kpi", "yoy", "trend", "hbars", "donut", "share", "pnl", "budgets", "findings", "table", "text",
    "matrix", "waterfall", "bridge", "stack",
}
FORMATS = {"currency", "currency-short", "percent", "number", "x", "text"}
# A string that is *entirely* a formatted figure: "$410,220", "(1,240)", "26.2%", "1.5x".
# Prose that happens to open with a dollar amount is fine and must not trip this.
MONEY_RE = re.compile(r"^\s*[-(]?\$?\s*[\d,]+(?:\.\d+)?\s*[%x)]?\s*$")
# Fields that are prose or a deliberate text label, never a number.
PROSE_PATHS = {"callout.value", "callout.body", "callout.label"}

DATA_BLOCK = re.compile(
    r'(<script id="data" type="application/json">)(.*?)(</script>)',
    re.DOTALL,
)


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def check_evidence(where, ev, target):
    """An evidence drawer is capped detail under a number already on the page.

    The cap is decided at generation time, whichever is smaller, the top 20
    transactions or the set covering 90% of the number, because there is no lazy
    fetch once the file is sent. What is shown plus the declared remainder must
    re-sum to the number the drawer sits under, or the drawer contradicts its own
    cell, which is worse than no drawer at all.
    """
    if not isinstance(ev, dict) or not isinstance(ev.get("txns"), list):
        fail(f"{where}: evidence needs a txns[] list")
    txns = ev["txns"]
    if not txns:
        fail(f"{where}: evidence with no transactions, omit the key instead")
    if len(txns) > 20:
        fail(f"{where}: evidence carries {len(txns)} transactions, cap is 20. Keep "
             "whichever is smaller, the top 20 or the set covering 90% of the number, "
             "and put the rest in more/moreValue.")
    for ti, tx in enumerate(txns):
        if not isinstance(tx, dict) or not tx.get("date") or not tx.get("name"):
            fail(f"{where}.txns[{ti}]: every transaction needs date and name "
                 "(memo is optional)")
        try:
            float(tx.get("amount"))
        except (TypeError, ValueError):
            fail(f"{where}.txns[{ti}] ({tx.get('name')}): amount must be a raw number, "
                 f"got {tx.get('amount')!r}")
    more = ev.get("more")
    if more is not None:
        if not isinstance(more, int) or more < 1:
            fail(f"{where}: evidence 'more' must be a positive count, got {more!r}")
        if ev.get("moreValue") is None:
            fail(f"{where}: evidence declares {more} more transactions but no moreValue. "
                 "The drawer prints what the remainder adds up to, so it is required.")
    shown = sum(float(t.get("amount") or 0) for t in txns)
    covered = shown + float(ev.get("moreValue") or 0)
    if target is not None and abs(covered - float(target)) > 1.0:
        fail(f"{where}: evidence sums to {covered:,.2f} (shown plus remainder) but the "
             f"number it sits under is {float(target):,.2f}. The drawer must re-sum to "
             "its own cell. Fix the data.")


def numeric_fields(obj, path="", out=None):
    """Collect (path, value) for every key that should hold a raw number."""
    if out is None:
        out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            if (k == "value" and isinstance(v, str) and p not in PROSE_PATHS
                    and MONEY_RE.match(v)):
                out.append((p, v))
            elif k == "values" and isinstance(v, list):
                for i, x in enumerate(v):
                    if isinstance(x, str):
                        out.append((f"{p}[{i}]", x))
            else:
                numeric_fields(v, p, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            numeric_fields(v, f"{path}[{i}]", out)
    return out


def validate(data):
    """Return a list of warnings; raise SystemExit on anything fatal."""
    warn = []

    if not isinstance(data, dict):
        fail("payload must be a JSON object")

    meta = data.get("meta")
    if not isinstance(meta, dict) or not meta.get("title"):
        fail("meta.title is required")
    for key in ("entity", "period", "closedThrough"):
        if not meta.get(key):
            warn.append(f"meta.{key} is missing, the header will be incomplete")

    strip = data.get("strip")
    if strip is not None:
        for sec in ([strip] if isinstance(strip, dict) else strip):
            if not isinstance(sec, dict) or sec.get("type") not in SECTION_TYPES:
                fail(f"strip: unknown section type {(sec or {}).get('type')!r}")
            if sec.get("type") not in ("kpi", "yoy"):
                warn.append("strip holds a section taller than a kpi row or a half-width yoy "
                            "chart. The strip repeats on every tab, so anything taller than that "
                            "makes each tab start further down the page.")

    views = data.get("views")
    if views is None:
        sections = data.get("sections")
        if not sections:
            fail("payload needs either views[] or sections[]")
        views = [{"name": "", "sections": sections}]
    if not isinstance(views, list) or not views:
        fail("views must be a non-empty array")

    total_sections = 0
    for vi, v in enumerate(views):
        secs = v.get("sections") or []
        if not secs:
            warn.append(f"views[{vi}] ({v.get('name') or 'unnamed'}) has no sections")
        for si, s in enumerate(secs):
            where = f"views[{vi}].sections[{si}]"
            t = s.get("type")
            if t not in SECTION_TYPES:
                fail(f"{where}: unknown section type {t!r}. Known: {', '.join(sorted(SECTION_TYPES))}")
            f = s.get("fmt")
            if f is not None and f not in FORMATS:
                fail(f"{where}: unknown fmt {f!r}. Known: {', '.join(sorted(FORMATS))}")
            if t in ("yoy", "trend"):
                labels = s.get("labels") or []
                if not labels:
                    fail(f"{where}: {t} needs labels[]")
                if s.get("series"):
                    for k, ss in enumerate(s["series"]):
                        vals = ss.get("values")
                        if vals is None:
                            fail(f"{where}: series[{k}] needs values")
                        if len(vals) != len(labels):
                            fail(f"{where}: series[{k}] ({ss.get('name')}) has {len(vals)} points "
                                 f"but there are {len(labels)} labels")
                else:
                    if t == "trend":
                        fail(f"{where}: trend needs series[]")
                    for side in ("current", "prior"):
                        vals = (s.get(side) or {}).get("values")
                        if vals is None:
                            fail(f"{where}: yoy needs {side}.values")
                        if len(vals) != len(labels):
                            fail(f"{where}: {side}.values has {len(vals)} points "
                                 f"but there are {len(labels)} labels")
            if t == "stack":
                cols = s.get("columns") or []
                series = s.get("series") or []
                if not cols:
                    fail(f"{where}: stack needs columns[]")
                if not series:
                    fail(f"{where}: stack needs series[]")
                if len(series) > 6:
                    warn.append(f"{where}: stack has {len(series)} series. Past about six bands a "
                                "column is a stack of slivers, and the small ones are the ones "
                                "nobody can see. Group the tail into 'Other (n lines)'.")
                for si, ss in enumerate(series):
                    if not ss.get("label"):
                        fail(f"{where}.series[{si}]: every stack series needs a label")
                    vals = ss.get("values")
                    if vals is None:
                        fail(f"{where}.series[{si}] ({ss.get('label')}): needs values[]")
                    elif len(vals) != len(cols):
                        fail(f"{where}.series[{si}] ({ss.get('label')}): has {len(vals)} values "
                             f"but there are {len(cols)} columns")
                    # A band that changes sign across the row stacks up in one column and down in
                    # the next, so the same colour means income here and spend there.
                    elif any(v is not None and float(v) > 0 for v in vals) and \
                         any(v is not None and float(v) < 0 for v in vals):
                        warn.append(f"{where}.series[{si}] ({ss.get('label')}): has both positive and "
                                    "negative values, so the band crosses the zero line. Split it into "
                                    "an inflow series and an outflow series.")

            if t == "matrix":
                cols = s.get("columns") or []
                rows = s.get("rows") or []
                if not cols:
                    fail(f"{where}: matrix needs columns[]")
                if not rows:
                    fail(f"{where}: matrix needs rows[]")
                members = [r for r in rows if not r.get("group") and not r.get("subtotal")]
                if len(members) > 14:
                    warn.append(f"{where}: matrix has {len(members)} data rows. Collapse the tail into "
                                "an 'Other (n members)' row, see reference/DIMENSIONS.md.")
                # Grouped rows without subtotals, or subtotals without groups, is half a
                # statement: the reader gets blocks with no block figures, or the reverse.
                has_g = any(r.get("group") for r in rows)
                has_s = any(r.get("subtotal") for r in rows)
                if has_g != has_s:
                    warn.append(f"{where}: matrix has "
                                f"{'group headers but no subtotal rows' if has_g else 'subtotal rows but no group headers'}. "
                                "A grouped statement needs both.")
                is_dollar = (s.get("fmt") or "currency") in ("currency", "currency-short")
                for ri, r in enumerate(rows):
                    # A group header is a divider, not a row of data: no label, no values.
                    if r.get("group"):
                        if r.get("values"):
                            fail(f"{where}.rows[{ri}]: a group header carries no values")
                        continue
                    if not r.get("label"):
                        fail(f"{where}.rows[{ri}]: every matrix row needs a label")
                    vals = r.get("values")
                    if vals is None:
                        fail(f"{where}.rows[{ri}] ({r.get('label')}): needs values[]")
                    if len(vals) != len(cols):
                        fail(f"{where}.rows[{ri}] ({r.get('label')}): has {len(vals)} values "
                             f"but there are {len(cols)} columns")
                    # Dollar cells must arrive whole. Cells with cents round per-cell at
                    # display time, and per-cell rounding is how a grid ends up a dollar off
                    # its own total, the one defect a reviewer who cross-foots one column
                    # will find. Round every cell first, then compute totals from the
                    # rounded cells, never the other way around.
                    if is_dollar:
                        for v in vals:
                            if v is not None and float(v) != int(float(v)):
                                fail(f"{where}.rows[{ri}] ({r.get('label')}): cell {v} has "
                                     "cents. Round every cell in the payload, then build "
                                     "totals from the rounded cells, so the displayed grid "
                                     "cross-foots to the dollar.")
                                break
                    # Evidence rides per cell, parallel to values, and each drawer must
                    # re-sum to the cell it opens under.
                    if r.get("evidence") is not None:
                        evs = r["evidence"]
                        if not isinstance(evs, list) or len(evs) > len(cols):
                            fail(f"{where}.rows[{ri}] ({r.get('label')}): evidence must be "
                                 "a list parallel to values[], null where a cell has none")
                        for ci, ev in enumerate(evs):
                            if ev is None:
                                continue
                            cell = vals[ci] if ci < len(vals) else None
                            if cell is None or float(cell) == 0:
                                fail(f"{where}.rows[{ri}] ({r.get('label')}): evidence on "
                                     f"column {ci} but the cell there is empty")
                            check_evidence(f"{where}.rows[{ri}].evidence[{ci}]", ev, cell)
                    # A supplied row total must agree with its own cells, or the grid lies.
                    if r.get("total") is not None:
                        cell_sum = sum(float(v) for v in vals if v is not None)
                        if abs(cell_sum - float(r["total"])) > 0.51:
                            fail(f"{where}.rows[{ri}] ({r.get('label')}): cells total "
                                 f"{cell_sum:,.0f} but total is {float(r['total']):,.0f}. "
                                 "A dimensional cut must re-sum exactly. Fix the data.")
            if t == "table":
                cols = s.get("columns") or []
                if not cols:
                    fail(f"{where}: table needs columns[]")
                # A column header is text a reader reads, never a value the page has to
                # stringify. An object here renders as the literal text "[object Object]",
                # this is not a style nit, it is a header that never shipped as a header.
                for ci, c in enumerate(cols):
                    if isinstance(c, (dict, list)):
                        fail(f"{where}.columns[{ci}]: a column header must be a plain string, "
                             f"got {type(c).__name__}. Write the header text directly, "
                             '\'"columns": ["Account", "FY 2025", ...]\', not a list of objects.')
                # Sorting indexes cells by column position, so a ragged row would be sorted
                # on a cell that isn't there. Only enforced where sorting is switched on.
                if s.get("sort") is True:
                    for ri, r in enumerate(s.get("rows") or []):
                        cells = r if isinstance(r, list) else (r.get("cells") or [])
                        if len(cells) != len(cols):
                            fail(f"{where}.rows[{ri}]: a sortable table needs every row to have "
                                 f"{len(cols)} cells to match its columns; this one has "
                                 f"{len(cells)}. Pad the row with null rather than dropping cells.")
                # A bare number in a cell skips the renderer's fmt entirely and prints the raw
                # float, every digit of it, unrounded, exactly like a spreadsheet cell nobody
                # formatted. Every numeric cell has to be `{"v": <number>, "fmt": <format>}` so
                # the page rounds and formats it; a plain string is fine, that is a label.
                for ri, r in enumerate(s.get("rows") or []):
                    cells = r if isinstance(r, list) else (r.get("cells") or [])
                    for ci, x in enumerate(cells):
                        if isinstance(x, bool) or x is None:
                            continue
                        if isinstance(x, (int, float)):
                            fail(f"{where}.rows[{ri}].cells[{ci}]: a bare number ({x!r}) in a "
                                 "table cell skips formatting and ships every decimal place raw. "
                                 'Wrap it: \'{"v": ' + repr(x) + ', "fmt": "currency"}\' (or '
                                 '"percent", "number"), never a bare number or string of one.')
                        if isinstance(x, str) and MONEY_RE.match(x):
                            fail(f"{where}.rows[{ri}].cells[{ci}]: {x!r} is a number formatted by "
                                 "hand, not by the page. Pass the raw number in a {\"v\", \"fmt\"} "
                                 "object instead, so it sorts and rounds correctly.")
            if t in ("waterfall", "bridge"):
                items = s.get("items") or []
                if len(items) < 3:
                    fail(f"{where}: a bridge needs at least an opening anchor, a bar, and a "
                         f"closing anchor; got {len(items)}")
                anchors = [i for i, it in enumerate(items) if it.get("total")]
                if len(anchors) < 2 or anchors[0] != 0 or anchors[-1] != len(items) - 1:
                    fail(f"{where}: a bridge needs total:true on the first and last item. "
                         "Those are the anchors the floating bars run between.")
                # The bars have to walk from one anchor to the other. A bridge that does not
                # close is silently wrong in a way no reader can catch, so it fails the build.
                running = float(items[0].get("value") or 0)
                for it in items[1:]:
                    v = float(it.get("value") or 0)
                    if it.get("total"):
                        if abs(running - v) > 0.51:
                            fail(f"{where}: the bars walk to {running:,.0f} but the "
                                 f"{it.get('label')!r} anchor is {v:,.0f}, a gap of "
                                 f"{abs(running - v):,.0f}. A bridge must close. Fix the data.")
                        running = v
                    else:
                        running += v
                # Evidence lives on the floating bars. An anchor is a statement figure,
                # not a movement, so there is no set of transactions "behind" it.
                for ii, it in enumerate(items):
                    if it.get("evidence") is None:
                        continue
                    if it.get("total"):
                        fail(f"{where}.items[{ii}] ({it.get('label')}): evidence on an "
                             "anchor. Anchors are levels, not movements, put the "
                             "transactions on the bars between them.")
                    check_evidence(f"{where}.items[{ii}].evidence", it["evidence"],
                                   it.get("value"))
            if t == "budgets":
                for bi, b in enumerate(s.get("items") or []):
                    lines = b.get("lines") or []
                    line_sum = sum(float(x.get("value") or 0) for x in lines)
                    spend = b.get("budget", b.get("total"))
                    if spend is not None and lines:
                        if abs(line_sum - float(spend)) > 0.51:
                            fail(f"{where}.items[{bi}] ({b.get('name')}): itemised lines total "
                                 f"{line_sum:,.0f} but the spend budget is {float(spend):,.0f}. "
                                 "Every budget must tie to the cent. Fix the data, do not round.")
                    if b.get("total") is not None and b.get("budget") is not None:
                        prot = (b.get("protected") or {}).get("value") or 0
                        if abs(float(b["budget"]) + float(prot) - float(b["total"])) > 0.51:
                            fail(f"{where}.items[{bi}] ({b.get('name')}): spend budget plus "
                                 "protected margin does not equal the total budget.")
            total_sections += 1

    if total_sections == 0:
        fail("no renderable sections in the payload")

    bad = numeric_fields(data)
    if bad:
        lines = "\n  ".join(f"{p} = {v!r}" for p, v in bad[:8])
        fail("pre-formatted currency strings found where raw numbers belong.\n  "
             + lines + "\n  Pass 410220, not \"$410,220\": the renderer formats.")

    # headline and callout are deliberately not warned about when absent: most skills now put
    # the story in the ranked findings at the bottom, and nothing narrative sits above the
    # KPI tiles. See reference/ARTIFACTS.md.
    if not (data.get("footnote") or data.get("footnotes")):
        warn.append("no footnote, sourcing and the review gate are unstated")

    return warn


def check_js(html):
    """node --check the renderer so a syntax error can never ship a blank page."""
    node = shutil.which("node")
    if not node:
        return "node not found, renderer syntax not verified"
    scripts = re.findall(r"<script>(.*?)</script>", html, re.DOTALL)
    for i, src in enumerate(scripts):
        p = Path(f"/tmp/_advisory_check_{i}.js")
        p.write_text(src)
        r = subprocess.run([node, "--check", str(p)], capture_output=True, text=True)
        p.unlink(missing_ok=True)
        if r.returncode != 0:
            fail(f"renderer script {i} failed node --check:\n{r.stderr.strip()}")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("out")
    ap.add_argument("--template", default=str(Path(__file__).with_name("report.html")))
    ap.add_argument("--strict", action="store_true")
    # --brand is gone on purpose. Building and branding are two passes, in that order, and
    # collapsing them cost more than it saved: the copy audit lives in the brand pass, so a
    # single banned word failed the build and threw away a report that was structurally fine.
    # Now the artifact always lands, then theme.py brands it and tells you what to fix.
    ap.add_argument("--brand", metavar="SKILL.md", help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.brand:
        fail("--brand was removed. Build first, then brand the finished file:\n"
             f"  python3 build_report.py {a.data} {a.out}\n"
             f"  python3 theme.py {a.brand} {a.out}")

    try:
        raw = Path(a.data).read_text()
    except OSError as e:
        fail(f"cannot read {a.data}: {e}")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        fail(f"{a.data} is not valid JSON: line {e.lineno} column {e.colno}: {e.msg}")

    warnings = validate(data)

    try:
        tpl = Path(a.template).read_text()
    except OSError as e:
        fail(f"cannot read template {a.template}: {e}")
    if not DATA_BLOCK.search(tpl):
        fail("template is missing its <script id=\"data\"> block")

    payload = json.dumps(data, indent=2, ensure_ascii=False)
    if "</script" in payload:
        fail("payload contains '</script' which would break out of the data block")

    html = DATA_BLOCK.sub(lambda m: m.group(1) + "\n" + payload + "\n" + m.group(3), tpl, count=1)
    check_js(html)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)

    if warnings:
        if a.strict:
            for w in warnings:
                print(f"error: {w}", file=sys.stderr)
            sys.exit(1)
        for w in warnings:
            print(f"warning: {w}", file=sys.stderr)

    kb = len(html.encode()) / 1024
    print(f"wrote {out} ({kb:.0f} KB, self-contained)")
    print(f"next: python3 {Path(__file__).with_name('theme.py').name} "
          f"<brand SKILL.md> {out}   # unbranded until you do")


if __name__ == "__main__":
    main()
