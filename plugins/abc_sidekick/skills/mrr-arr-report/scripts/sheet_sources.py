#!/usr/bin/env python3
"""
sheet_sources.py: read every tab of a spreadsheet the same way, for Sheets mode.

Input is a folder with one CSV per tab, named "<tab name>.csv", holding the cell
values as read through the Sheets connection (save each read to a file; read large
tabs in pages and append, never truncate).

Subcommands
  inventory  Classifies each tab (Kick report, user data, or skill-owned 'MRR ...'),
             records entity, report, basis, stated date range, actual first and last
             date, grain, and the Waterfall or Rollforward grouping. With --window-from
             and --window-to it runs the date coverage preflight: a ledger whose lines
             fall short of its header, or a chosen source that doesn't cover the window,
             is a problem. Exit 4 when the preflight finds a problem (the JSON is still
             written); --proceed reports the problems and exits 0.
  rows       Builds mrr_build.py input rows from the chosen tabs with one source per
             customer: Waterfall first (source=schedule, term_months=1, term_end from
             the Rollforward), then the user's table (billing), then ledger lines in
             the revenue accounts. Ledger lines for customers on a schedule or in the
             table are left out and counted, never added twice.

Examples
  python3 sheet_sources.py inventory --tabs-dir tabs --window-from 2026-01 --window-to 2026-09
  python3 sheet_sources.py rows --tabs-dir tabs --waterfall "Acme - Revenue Waterfall" \
      --ledger "Acme - General Ledger" --revenue-accounts "400000 - Revenue" --out rows.csv

Standard library only. Exit codes: 0 ok, 1 bad input, 4 preflight problem.
"""

import argparse
import calendar
import csv
import json
import os
import re
import sys
from datetime import date, datetime, timedelta

KICK_REPORTS = ["Profit & Loss", "Balance Sheet", "Trial Balance", "Cash Flow Statement",
                "General Ledger", "Expenses by Vendor", "Revenue Rollforward", "Revenue Waterfall"]
MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
MONTHS.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})
MONTH_LABEL_RE = re.compile(r"^([A-Za-z]{3,9}) (\d{4})$")
BALANCE_ROW_RE = re.compile(r"^(beginning balance|ending balance|total\b)", re.I)
DATE_TOKEN_RE = re.compile(r"([A-Za-z]{3,9})(?: (\d{1,2}),)?(?: (\d{4}))?")
ROLE_HINTS = [("customer", r"customer|client|tenant|counterparty|company|account name|email"),
              ("date", r"date|period|month|created|paid"),
              ("amount", r"amount|total|subtotal|price|revenue|mrr"),
              ("plan", r"plan|product|description|item|memo"),
              ("months", r"billing months|term|interval")]


def fail(msg, code=1):
    sys.stderr.write("sheet_sources: %s\n" % msg)
    sys.exit(code)


def read_tabs(folder):
    tabs = {}
    for fn in sorted(os.listdir(folder)):
        if fn.lower().endswith(".csv"):
            with open(os.path.join(folder, fn), newline="", encoding="utf-8-sig") as fh:
                tabs[fn[:-4]] = [row for row in csv.reader(fh)]
    if not tabs:
        fail("no .csv files in %s" % folder)
    return tabs


def cell(rows, r, c):
    return rows[r][c].strip() if r < len(rows) and c < len(rows[r]) else ""


def parse_date(text):
    text = (text or "").strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%b %d, %Y", "%B %d, %Y", "%d %b %Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_month_label(text):
    m = MONTH_LABEL_RE.match((text or "").strip())
    if m and m.group(1).lower() in MONTHS:
        return date(int(m.group(2)), MONTHS[m.group(1).lower()], 1)
    d = parse_date(text)
    return date(d.year, d.month, 1) if d else None


def parse_range_label(text):
    """Kick header date label to (from, to); None where open or unreadable."""
    tokens = [(MONTHS[m.lower()], int(d) if d else None, int(y) if y else None)
              for m, d, y in DATE_TOKEN_RE.findall(text or "") if m.lower() in MONTHS]
    if not tokens:
        return None, None
    (m1, d1, y1), (m2, d2, y2) = tokens[0], tokens[-1]
    y2 = y2 or y1
    y1 = y1 or y2
    if not (y1 and y2):
        return None, None
    start = date(y1, m1, d1 or 1)
    end = date(y2, m2, d2 or calendar.monthrange(y2, m2)[1])
    if text.lower().startswith("before"):
        return None, end
    if text.lower().startswith("after"):
        return start, None
    return start, end


def parse_amount(text):
    t = (text or "").replace(",", "").replace("$", "").strip()
    neg = t.startswith("(") and t.endswith(")")
    try:
        v = float(t.strip("()"))
    except ValueError:
        return None
    return -v if neg else v


def depth_of(label):
    return (len(label) - len(label.lstrip(" "))) // 2


def find_period_row(rows):
    for r in range(min(40, len(rows))):
        if any(parse_month_label(v) for v in rows[r][2:]):
            return r
    return None


def schedule_pairs(rows, data_start, grouping):
    """(customer, plan, row index) for each policy-customer row of a Waterfall or Rollforward."""
    labels = []
    for r in range(data_start, len(rows)):
        lbl = rows[r][1] if len(rows[r]) > 1 else ""
        if not lbl.strip():
            break
        labels.append((r, lbl))
    out, parent, owner = [], "", None
    for i, (r, lbl) in enumerate(labels):
        d, name = depth_of(lbl), lbl.strip()
        nxt = depth_of(labels[i + 1][1]) if i + 1 < len(labels) else -1
        if d == 0:
            parent = name
        is_total = name == "Total" or name.startswith("Total ") or name in ("Current", "Non-current")
        if d == 1 and nxt > 1 and not is_total:
            cust, plan = (parent, name) if grouping == "By customer" else (name, parent)
            owner = {"customer": "" if cust in ("No counterparty", "No customer") else cust,
                     "raw_customer": cust, "plan": plan, "row": r, "children": []}
            out.append(owner)
        elif d >= 2 and owner is not None:
            owner["children"].append(r)
    return out


def detect_grouping(rows, data_start):
    for r in range(data_start, min(len(rows), data_start + 400)):
        lbl = rows[r][1] if len(rows[r]) > 1 else ""
        if lbl.strip() == "No counterparty":
            return "By customer" if depth_of(lbl) == 0 else "By schedule"
    return None


def classify(name, rows):
    info = {"tab": name, "rows": len(rows), "columns": max((len(r) for r in rows), default=0)}
    if name.startswith("MRR "):
        return {**info, "kind": "skill-owned"}
    title = cell(rows, 2, 1)
    report = next((r for r in KICK_REPORTS if title == r or name.endswith(" - " + r)), None)
    if report:
        stated = parse_range_label(cell(rows, 3, 1))
        footer = " ".join(" ".join(r) for r in rows[-6:]).lower()
        basis = "accrual" if "accrual" in footer else "cash" if "cash basis" in footer else None
        info.update({"kind": "Kick report", "report": report, "entity": cell(rows, 1, 1) or None,
                     "basis": basis, "stated_from": stated[0], "stated_to": stated[1]})
        if report == "General Ledger":
            hdr = next((r for r in range(min(40, len(rows))) if cell(rows, r, 1) == "Date"), None)
            dates = [d for r in rows[(hdr or 0) + 1:] for d in [parse_date(r[1] if len(r) > 1 else "")] if d]
            info.update({"grain": "line", "first_date": min(dates, default=None),
                         "last_date": max(dates, default=None), "has_customers": True})
        elif report in ("Revenue Waterfall", "Revenue Rollforward"):
            pr = find_period_row(rows)
            start = None if pr is None else pr + (2 if report == "Revenue Rollforward" else 1)
            months = sorted({m for m in (parse_month_label(v) for v in (rows[pr] if pr is not None else [])) if m})
            by_start_month = pr is not None and cell(rows, pr, 1) == "Start month"
            info.update({"grain": "start month" if by_start_month else "customer and month", "period_row": pr,
                         "first_date": months[0] if months else None,
                         "last_date": months[-1] if months else None,
                         "grouping": "Start month summary" if by_start_month
                         else detect_grouping(rows, start) if start is not None else None,
                         "monthly_periods": bool(months), "has_customers": not by_start_month})
        else:
            info["grain"] = "account totals"
        return info
    hdr_row, roles = None, {}
    for r in range(min(20, len(rows))):
        texts = [v.strip() for v in rows[r] if v.strip()]
        if len(texts) >= 3 and sum(1 for v in texts if parse_amount(v) is None) >= 3:
            hdr_row = r
            break
    if hdr_row is not None:
        for i, h in enumerate(rows[hdr_row]):
            for role, pat in ROLE_HINTS:
                if role not in roles and h.strip() and re.search(pat, h, re.IGNORECASE):
                    roles[role] = h.strip()
                    break
    dates = []
    if "date" in roles:
        col = rows[hdr_row].index(roles["date"])
        dates = [d for r in rows[hdr_row + 1:] for d in [parse_date(r[col] if col < len(r) else "")] if d]
    return {**info, "kind": "user data", "header_row": hdr_row, "headers": rows[hdr_row] if hdr_row is not None else [],
            "suggested_columns": roles, "has_customers": "customer" in roles,
            "first_date": min(dates, default=None), "last_date": max(dates, default=None),
            "grain": "line" if dates else "unknown"}


def month_start(text):
    return date(int(text[:4]), int(text[5:7]), 1)


def cmd_inventory(args):
    tabs = read_tabs(args.tabs_dir)
    items = [classify(n, rows) for n, rows in tabs.items()]
    gap = timedelta(days=args.gap_days)
    problems = []
    for it in items:
        if it.get("report") == "General Ledger" and it.get("first_date"):
            if it.get("stated_from") and it["first_date"] - it["stated_from"] > gap:
                problems.append("%s: lines start %s but the header says %s" % (it["tab"], it["first_date"], it["stated_from"]))
            if it.get("stated_to") and it["stated_to"] - it["last_date"] > gap:
                problems.append("%s: lines end %s but the header says %s" % (it["tab"], it["last_date"], it["stated_to"]))
        if it.get("report") in ("Revenue Waterfall", "Revenue Rollforward") and not it.get("monthly_periods"):
            problems.append("%s: no monthly period columns; re-pull it with monthly periods" % it["tab"])
        if it.get("grouping") == "Start month summary":
            problems.append("%s: rows are start months, not customers; re-pull it grouped by schedule or customer"
                            % it["tab"])
    if args.window_from and args.window_to:
        w0, w1 = month_start(args.window_from), month_start(args.window_to)
        revenue = [it for it in items if it.get("report") in ("General Ledger", "Revenue Waterfall")
                   or (it["kind"] == "user data" and it.get("has_customers") and it.get("first_date"))]
        covering = [it for it in revenue if it.get("first_date") and it["first_date"] <= w0 + gap
                    and it["last_date"] and date(it["last_date"].year, it["last_date"].month, 1) >= w1]
        if not covering:
            problems.append("no tab covers %s to %s; pull or re-pull a report for those dates" % (w0, w1))
    entities = sorted({it["entity"] for it in items if it.get("entity")})
    out = {"tabs": items, "entities": entities, "several_entities": len(entities) > 1,
           "preflight": {"ok": not problems, "problems": problems, "gap_days": args.gap_days}}
    text = json.dumps(out, indent=2, default=str, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
    else:
        print(text)
    if problems and not args.proceed:
        fail("preflight: " + "; ".join(problems), 4)


def waterfall_rows(rows, grouping, term_ends):
    pr = find_period_row(rows)
    if pr is None:
        fail("no period header row in the Waterfall tab")
    cols = [(c, m) for c, v in enumerate(rows[pr]) if c >= 2 for m in [parse_month_label(v)] if m]
    out = []
    for p in schedule_pairs(rows, pr + 1, grouping):
        for c, m in cols:
            amt = parse_amount(cell(rows, p["row"], c))
            if amt:
                out.append({"customer": p["customer"], "month": m.strftime("%Y-%m"), "amount": "%.2f" % amt,
                            "term_months": 1, "cadence": "schedule", "source": "schedule", "plan": p["plan"],
                            "term_end": term_ends.get(p["customer"].casefold(), ""), "description": p["plan"]})
    return out


def rollforward_term_ends(rows, grouping):
    pr = find_period_row(rows)
    if pr is None:
        return {}
    try:
        end_col = rows[pr].index("Schedule end date")
    except ValueError:
        return {}
    ends = {}
    for p in schedule_pairs(rows, pr + 2, grouping):
        found = [d for r in [p["row"]] + p["children"] for d in [parse_date(cell(rows, r, end_col))] if d]
        if found and p["customer"]:
            key = p["customer"].casefold()
            ends[key] = max(found + ([ends[key]] if key in ends else []))
    return {k: v.isoformat() for k, v in ends.items()}


def ledger_rows(rows, accounts):
    hdr = next((r for r in range(min(40, len(rows))) if cell(rows, r, 1) == "Date"), None)
    if hdr is None:
        fail("no 'Date' header in the ledger tab")
    head = [v.strip() for v in rows[hdr]]
    ci = {k: head.index(k) for k in ("Description", "Counterparty", "Amount") if k in head}
    out, account = [], ""
    for r in rows[hdr + 1:]:
        b = r[1].strip() if len(r) > 1 else ""
        d = parse_date(b)
        amt = parse_amount(r[ci["Amount"]]) if "Amount" in ci and ci["Amount"] < len(r) else None
        if BALANCE_ROW_RE.match(b):
            continue
        if b and d is None and amt is None:
            account = b
            continue
        if d and amt is not None and account in accounts:
            out.append({"customer": r[ci["Counterparty"]].strip() if "Counterparty" in ci else "",
                        "month": d.strftime("%Y-%m"), "amount": "%.2f" % amt, "source": "ledger",
                        "description": r[ci["Description"]].strip() if "Description" in ci else "",
                        "account": account})
    return out


def table_rows(rows, cols):
    head_row = next((r for r in range(min(20, len(rows))) if cols["customer"] in [v.strip() for v in rows[r]]), None)
    if head_row is None:
        fail("header '%s' not found in the table tab" % cols["customer"])
    head = [v.strip() for v in rows[head_row]]
    idx = {k: head.index(v) for k, v in cols.items() if v and v in head}
    out = []
    for r in rows[head_row + 1:]:
        get = lambda k: r[idx[k]].strip() if k in idx and idx[k] < len(r) else ""
        d, amt = parse_date(get("date")), parse_amount(get("amount"))
        if d and amt is not None:
            row = {"customer": get("customer"), "month": d.strftime("%Y-%m"), "amount": "%.2f" % amt,
                   "source": "billing", "description": get("plan"), "plan": get("plan")}
            if get("months").isdigit():
                row["term_months"] = int(get("months"))
            out.append(row)
    return out


def cmd_rows(args):
    tabs = read_tabs(args.tabs_dir)

    def tab(name):
        if name not in tabs:
            fail("tab '%s' is not in %s" % (name, args.tabs_dir))
        return tabs[name]

    ends = rollforward_term_ends(tab(args.rollforward), args.grouping) if args.rollforward else {}
    chosen, skipped = [], {"ledger_rows_on_schedule": 0, "ledger_rows_in_table": 0, "table_rows_on_schedule": 0}
    if args.waterfall and cell(tab(args.waterfall), find_period_row(tab(args.waterfall)) or 0, 1) == "Start month":
        fail("the Waterfall rows are start months, not customers; re-pull it grouped by schedule or customer")
    sched = waterfall_rows(tab(args.waterfall), args.grouping, ends) if args.waterfall else []
    on_sched = {r["customer"].casefold() for r in sched if r["customer"]}
    chosen += sched
    if args.table:
        cols = {"customer": args.customer_col, "date": args.date_col, "amount": args.amount_col,
                "plan": args.plan_col or "", "months": args.months_col or ""}
        trows = table_rows(tab(args.table), cols)
        kept = [r for r in trows if r["customer"].casefold() not in on_sched or not r["customer"]]
        skipped["table_rows_on_schedule"] = len(trows) - len(kept)
        chosen += kept
    in_table = {r["customer"].casefold() for r in chosen if r["source"] == "billing" and r["customer"]}
    if args.ledger:
        accounts = {a.strip() for a in (args.revenue_accounts or "").split(",") if a.strip()}
        if not accounts:
            fail("--revenue-accounts is required with --ledger")
        for r in ledger_rows(tab(args.ledger), accounts):
            key = r["customer"].casefold()
            if key and key in on_sched:
                skipped["ledger_rows_on_schedule"] += 1
            elif key and key in in_table:
                skipped["ledger_rows_in_table"] += 1
            else:
                chosen.append(r)
    fields = ["customer", "month", "amount", "term_months", "cadence", "source", "plan", "term_end",
              "description", "account"]
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(chosen)
    print(json.dumps({"rows": len(chosen), "by_source": {s: sum(1 for r in chosen if r["source"] == s)
                                                         for s in sorted({r["source"] for r in chosen})},
                      "left_out_to_avoid_double_counting": skipped, "out": args.out}))


def build_parser():
    p = argparse.ArgumentParser(description="Sheets mode: inventory and rows from saved tab reads.")
    sub = p.add_subparsers(dest="cmd")
    i = sub.add_parser("inventory")
    i.add_argument("--tabs-dir", required=True)
    i.add_argument("--window-from", help="first month of the requested report, YYYY-MM")
    i.add_argument("--window-to", help="last month of the requested report, YYYY-MM")
    i.add_argument("--gap-days", type=int, default=31,
                   help="days a ledger may fall short of its header before it is stale (default 31)")
    i.add_argument("--proceed", action="store_true", help="report preflight problems but exit 0")
    i.add_argument("--out")
    r = sub.add_parser("rows")
    r.add_argument("--tabs-dir", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--waterfall")
    r.add_argument("--rollforward")
    r.add_argument("--grouping", choices=["By schedule", "By customer"], default="By schedule")
    r.add_argument("--ledger")
    r.add_argument("--revenue-accounts", help="comma-separated account labels as the ledger shows them")
    r.add_argument("--table")
    r.add_argument("--customer-col")
    r.add_argument("--date-col")
    r.add_argument("--amount-col")
    r.add_argument("--plan-col")
    r.add_argument("--months-col")
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.cmd == "inventory":
        cmd_inventory(args)
    elif args.cmd == "rows":
        if not (args.waterfall or args.ledger or args.table):
            fail("name at least one of --waterfall, --ledger, --table")
        if args.table and not (args.customer_col and args.date_col and args.amount_col):
            fail("--table needs --customer-col, --date-col, and --amount-col")
        cmd_rows(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
