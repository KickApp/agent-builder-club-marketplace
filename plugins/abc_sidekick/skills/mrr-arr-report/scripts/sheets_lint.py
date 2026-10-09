#!/usr/bin/env python3
"""Static checks for every formula in a Google Sheets plan (sheets_plan.json).

  1. Names: LET names and LAMBDA parameters in one formula must not differ only by
     case. Sheets names are case-insensitive, so `T` and `t` are the same name and the
     inner one silently replaces the outer one.
  2. Header-driven: a formula may name only skill-owned tabs ('MRR ...') directly.
     Source tabs are read through INDIRECT of a tab name typed on 'MRR sources', so a
     refresh that clears and rewrites a source tab never breaks a formula.
  3. Grid bounds: every write, format, merge, validation, conditional color, width,
     height, hidden column, and chart anchor fits inside its tab's rowCount and
     columnCount. The Sheets API rejects a whole batch for one range past the grid.

Usage:
  python3 sheets_lint.py [plan.json]     (default: references/templates/sheets_plan.json)
Exit 0 when clean, 1 with one line per problem.
"""

import json
import re
import sys
from pathlib import Path

from sheets_payloads import DEFAULT_ROWS, grid

DEFAULT_PLAN = Path(__file__).resolve().parent.parent / "references" / "templates" / "sheets_plan.json"
TOKEN_RE = re.compile(r'"(?:[^"]|"")*"|\'(?:[^\']|\'\')*\'!|[A-Za-z_][A-Za-z0-9_.]*|[(),]|\s+|.')
QUOTED_TAB_RE = re.compile(r"'((?:[^']|'')+)'!")


def bound_names(formula):
    """LET names and LAMBDA parameters, in order of appearance."""
    tokens = [t for t in TOKEN_RE.findall(formula) if not t.isspace()]
    names, stack = [], []
    for i, tok in enumerate(tokens):
        nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
        if tok == "(":
            prev = tokens[i - 1].upper() if i else ""
            stack.append({"fn": prev, "arg": 0, "start": True})
            continue
        if tok == ")":
            if stack:
                stack.pop()
            continue
        if tok == ",":
            if stack:
                stack[-1]["arg"] += 1
                stack[-1]["start"] = True
            continue
        if not stack or not re.match(r"[A-Za-z_]", tok) or nxt == "(":
            if stack:
                stack[-1]["start"] = False
            continue
        frame = stack[-1]
        is_arg_start = frame["start"] and nxt == ","
        if frame["fn"] == "LET" and frame["arg"] % 2 == 0 and is_arg_start:
            names.append(tok)
        elif frame["fn"] == "LAMBDA" and is_arg_start:
            names.append(tok)
        frame["start"] = False
    return names


def case_collisions(formula):
    seen = {}
    found = set()
    for name in bound_names(formula):
        key = name.casefold()
        if key in seen and seen[key] != name:
            found.add(tuple(sorted((seen[key], name))))
        seen.setdefault(key, name)
    return sorted(found)


def foreign_tabs(formula):
    code = re.sub(r'"(?:[^"]|"")*"', '""', formula)
    return sorted({m.replace("''", "'") for m in QUOTED_TAB_RE.findall(code)
                   if not m.startswith("MRR ")})


def tab_ranges(tab):
    """(kind, A1, rows written, columns written) for every range the plan sends to a tab."""
    for w in tab.get("writes", []):
        values = w.get("values", [])
        yield "write", w["range"], len(values), max((len(r) for r in values), default=0)
    for key, field in (("formats", "range"), ("validations", "range"), ("conditionalFormats", "range"),
                       ("columnWidths", "columns"), ("rowHeights", "rows")):
        for item in tab.get(key, []):
            yield key, item[field], 0, 0
    for a1 in tab.get("merges", []):
        yield "merges", a1, 0, 0
    if tab.get("hiddenColumns"):
        yield "hiddenColumns", tab["hiddenColumns"], 0, 0
    for chart in tab.get("charts", []):
        yield "chart anchor", chart["anchor"], 0, 0


def bounds_problems(tab):
    max_rows, max_cols = tab.get("rowCount", DEFAULT_ROWS), tab.get("columnCount", 26)
    problems = []
    for kind, a1, nrows, ncols in tab_ranges(tab):
        g = grid(0, a1)
        end_col = max(g.get("endColumnIndex", 0), g.get("startColumnIndex", 0) + ncols)
        end_row = max(g.get("endRowIndex", 0), g.get("startRowIndex", 0) + nrows)
        if end_col > max_cols or end_row > max_rows:
            problems.append("%s!%s (%s): outside the tab's %d rows x %d columns"
                            % (tab["name"], a1, kind, max_rows, max_cols))
    return problems


def lint_plan(plan):
    problems = []
    for tab in plan.get("tabs", []):
        problems += bounds_problems(tab)
        for write in tab.get("writes", []):
            for row in write.get("values", []):
                for cell in row:
                    if not (isinstance(cell, str) and cell.startswith("=")):
                        continue
                    where = "%s!%s" % (tab["name"], write["range"])
                    for a, b in case_collisions(cell):
                        problems.append("%s: names '%s' and '%s' differ only by case" % (where, a, b))
                    for name in foreign_tabs(cell):
                        problems.append("%s: reads tab '%s' directly; read source tabs through "
                                        "INDIRECT of a name on 'MRR sources'" % (where, name))
    return problems


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PLAN
    problems = lint_plan(json.loads(path.read_text()))
    for p in problems:
        print(p)
    if problems:
        sys.exit(1)
    print("lint: clean")


if __name__ == "__main__":
    main()
