#!/usr/bin/env python3
"""
mrr_build.py: recurring revenue arithmetic for the mrr-arr-report skill.

Subcommands
  scan   Reads raw revenue rows (one row per payment, or per customer and month) and
         reports payment cadence per customer, the repeat-customer share of each income
         account, likely duplicate customer names, and revenue with no customer. Its
         reads billing words in descriptions, groups similar unclear customers into a
         few questions, and feeds the skill's first look.
  build  Reads the revenue rows that follow the user's choices and computes MRR, ARR,
         movements, the bridge check, retention, concentration, plans, classes, cohorts,
         renewals, a plain-words row per customer, and the sized exclusions. Writes
         mrr_report.json, customer_detail.csv, movements.csv, and trend.csv.

Input CSV columns (header row required, names are case-insensitive)
  scan:  customer, amount, and month or date; optional account, currency, cadence,
         description (or memo: bank description, invoice line, or schedule policy name)
  build: customer, month, amount; optional term_months, cadence, source, plan, class,
         currency, term_end, report_as
  references/mrr-method.md documents every column and rule.

Examples
  python3 mrr_build.py scan --input revenue_rows.csv --out scan.json
  python3 mrr_build.py build --input grid_rows.csv --end-month 2026-09 \
      --as-of 2026-10-08 --spread yes --min-history 2 --churn-after-months 1 --out-dir out

Standard library only (plus mrr_quality.py next to this file). Every threshold is a flag
with a documented default.
Exit codes: 0 success, 1 bad input or arguments, 2 bridge check failed (nothing written),
3 no row has a customer (mrr_report.json holds only the sizing, summary is null).
"""

import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from mrr_quality import (NameMerger, adjust_schedules, coverage_and_gate, is_payout,
                         is_reversal_text)

D0 = Decimal("0")
CENT = Decimal("0.01")
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
SOURCE_LABELS = {
    "schedule": "Recognized revenue",
    "ledger": "Booked revenue",
    "cash": "Cash collected",
    "invoice": "Invoices",
    "billing": "Billing system records",
}
ALLOWED_CADENCE = {"schedule", "detected", "described", "confirmed", "unconfirmed", "one_time"}
# Labels that make a customer recurring without the minimum-history test: the term
# comes from a schedule, the books state it (described), the user answered (confirmed),
# or the user skipped an unclear customer, counted in the month booked (unconfirmed).
QUALIFYING_CADENCE = {"schedule", "described", "confirmed", "unconfirmed"}
CADENCE_PRIORITY = ["schedule", "confirmed", "described", "detected", "unconfirmed"]
BILLING_WORDS = [
    (r"one[- ]?time|set ?up fee|implementation|onboarding fee", "one_time"),
    (r"semi[- ]?annual|half[- ]?year|6[- ]?month", 6),
    (r"annual|yearly|per year|/ ?yr\b|12[- ]?month", 12),
    (r"quarterly|per quarter|\bqtr\b|3[- ]?month", 3),
    (r"monthly|per month|/ ?mo\b", 1),
]
TERM_WORDS = {1: "monthly", 3: "quarterly", 6: "every 6 months", 12: "annual"}
BILLING_LABELS = {1: "Monthly", 3: "Quarterly", 6: "Every 6 months", 12: "Annual"}
STATUS_LABELS = {"new": "New", "expansion": "Upgraded", "contraction": "Downgraded",
                 "churn": "Churned", "reactivation": "Came back"}
KINDS = ["new", "expansion", "reactivation", "contraction", "churn"]
# Account names that suggest subscription revenue (default recurring accounts).
SUBSCRIPTION_HINTS = ("subscription", "recurring", "saas", "membership", "license",
                      "licence", "maintenance", "hosting", "retainer", "support plan")
LEGAL_SUFFIXES = {"inc", "llc", "ltd", "limited", "corp", "corporation", "co", "company",
                  "plc", "gmbh", "pty", "llp", "lp", "sa", "bv"}


class InputError(Exception):
    pass


class BridgeError(Exception):
    pass


class NoCustomerError(Exception):
    pass


def fail(msg, code=1):
    sys.stderr.write("mrr_build: %s\n" % msg)
    sys.exit(code)


# ---------- parsing helpers ----------

def month_index(text, where):
    t = (text or "").strip()
    m = re.match(r"^(\d{4})-(\d{1,2})(?:-(\d{1,2}))?", t)
    if not m:
        raise InputError("%s: '%s' is not a YYYY-MM or YYYY-MM-DD value" % (where, t))
    year, mon = int(m.group(1)), int(m.group(2))
    if not 1 <= mon <= 12:
        raise InputError("%s: month %d is out of range" % (where, mon))
    return year * 12 + mon - 1


def parse_date(text, where):
    t = (text or "").strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", t)
    if not m:
        raise InputError("%s: '%s' is not a YYYY-MM-DD date" % (where, t))
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        raise InputError("%s: '%s' is not a real date" % (where, t))


def month_str(i):
    return "%04d-%02d" % (i // 12, i % 12 + 1)


def month_label(i):
    return "%s %04d" % (MONTH_NAMES[i % 12], i // 12)


def quarter_label(q):
    return "Q%d %04d" % (q % 4 + 1, q // 4)


def parse_amount(text, where):
    raw = (text or "").strip()
    t = raw.replace(",", "")
    for sym in ("$", "€", "£"):
        t = t.replace(sym, "")
    t = t.strip()
    neg = False
    if t.startswith("(") and t.endswith(")"):
        neg, t = True, t[1:-1].strip()
    if t == "":
        raise InputError("%s: amount is empty" % where)
    try:
        v = Decimal(t)
    except InvalidOperation:
        raise InputError("%s: amount '%s' is not a number" % (where, raw))
    if not v.is_finite():
        raise InputError("%s: amount '%s' is not a finite number" % (where, raw))
    return -v if neg else v


def parse_term(text, where):
    t = (text or "").strip()
    if t == "":
        return 1
    try:
        v = Decimal(t)
    except InvalidOperation:
        raise InputError("%s: term_months '%s' is not a number" % (where, t))
    if v != v.to_integral_value() or not 1 <= v <= 120:
        raise InputError("%s: term_months must be a whole number from 1 to 120" % where)
    return int(v)


def money(v):
    return float(Decimal(v).quantize(CENT, rounding=ROUND_HALF_UP))


def pct(num, den, places=1):
    den = Decimal(den)
    if den == 0:
        return None
    q = Decimal(1).scaleb(-places)
    return float((Decimal(num) * 100 / den).quantize(q, rounding=ROUND_HALF_UP))


def ratio(num, den, places=1):
    den = Decimal(den)
    if den == 0:
        return None
    q = Decimal(1).scaleb(-places)
    return float((Decimal(num) / den).quantize(q, rounding=ROUND_HALF_UP))


def median(values):
    s = sorted(values)
    n = len(s)
    if n == 0:
        return D0
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def spread(amount, n):
    """Split amount over n months in cents; the last month takes the rounding remainder."""
    if n <= 1:
        return [amount]
    base = (amount / n).quantize(CENT, rounding=ROUND_HALF_UP)
    return [base] * (n - 1) + [amount - base * (n - 1)]


def safe_cell(text):
    """Customer names are untrusted: stop spreadsheet formula injection in CSV output."""
    t = str(text)
    return "'" + t if t[:1] in ("=", "+", "-", "@", "\t", "\r") else t


def read_rows(path, required):
    if not os.path.isfile(path):
        raise InputError("input file not found: %s" % path)
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise InputError("%s is empty" % path)
        names = [(f or "").strip().lower() for f in reader.fieldnames]
        missing = [c for c in required if c not in names]
        if missing:
            raise InputError("%s is missing column(s): %s" % (path, ", ".join(missing)))
        rows = []
        for n, raw in enumerate(reader, start=2):
            row = {}
            for k, v in raw.items():
                if k is None:
                    continue
                row[k.strip().lower()] = v.strip() if isinstance(v, str) else ""
            if not any(row.values()):
                continue
            rows.append((n, row))
    return names, rows


def normalize_name(name):
    t = name.lower().replace("&", " and ")
    t = re.sub(r"[^\w ]+", " ", t)
    tokens = t.split()
    while tokens and tokens[-1] in LEGAL_SUFFIXES:
        tokens.pop()
    if tokens and tokens[0] == "the":
        tokens = tokens[1:]
    return " ".join(tokens)


def write_json(obj, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


# ---------- scan ----------

def classify_cadence(by_month, tol, min_payments, slack):
    pays = sorted((m, a) for m, a in by_month.items() if a > 0)
    total = sum((a for _, a in by_month.items()), D0)
    out = {"payments": len(pays), "total": money(total), "term_months": None,
           "looks_annual": False}
    if not pays:
        out.update(cadence="none", reason="no positive revenue in the window")
        return out
    out["first_month"], out["last_month"] = month_str(pays[0][0]), month_str(pays[-1][0])
    amounts = [a for _, a in pays]
    out["min_amount"], out["max_amount"] = money(min(amounts)), money(max(amounts))
    if len(pays) == 1:
        out.update(cadence="unclear", reason="one payment in the window", looks_annual=True)
        return out
    gaps = [pays[i + 1][0] - pays[i][0] for i in range(len(pays) - 1)]
    if all(g == 1 for g in gaps):
        kind, term = "monthly", 1
    elif all(g == 3 for g in gaps):
        kind, term = "quarterly", 3
    elif all(12 - slack <= g <= 12 + slack for g in gaps):
        kind, term = "annual", 12
    else:
        out.update(cadence="unclear", reason="irregular gaps between payments (%s months)"
                   % ", ".join(str(g) for g in gaps))
        return out
    if len(pays) < min_payments:
        out.update(cadence="unclear", reason="%d payments, fewer than %d"
                   % (len(pays), min_payments))
        return out
    med = median(amounts)
    tol_d = Decimal(str(tol))
    if any(abs(a - med) > tol_d * med for a in amounts):
        out.update(cadence="unclear", reason="amounts vary more than %s%%"
                   % format(tol_d * 100, "f").rstrip("0").rstrip("."))
        return out
    out.update(cadence=kind, term_months=term, reason="%d payments, %s" % (len(pays), kind))
    return out


def described_term(text):
    """Billing cycle stated in a description or memo: months, 'one_time', or None."""
    t = (text or "").lower()
    for pattern, term in BILLING_WORDS:
        if re.search(pattern, t):
            return term
    return None


def apply_descriptions(c, texts):
    """Let what the books say settle the billing cycle before anyone is asked."""
    terms = {described_term(t) for t in texts} - {None}
    samples = []
    for t in texts:
        if t and t not in samples:
            samples.append(t[:120])
        if len(samples) == 3:
            break
    c["description_samples"] = samples
    if len(terms) != 1:
        if len(terms) > 1:
            c["described"] = "conflicting"
        return
    term = terms.pop()
    c["described"] = "one-time" if term == "one_time" else TERM_WORDS.get(term, "%d months" % term)
    if c["cadence"] == "unclear":
        c.update(cadence="described", reason="description says %s" % c["described"],
                 term_months=None if term == "one_time" else term,
                 one_time=term == "one_time")
    elif c.get("term_months") and term != "one_time" and c["term_months"] != term:
        c.update(cadence="unclear", reason="payments look %s but the description says %s"
                 % (c["cadence"], c["described"]))


def cmd_scan(args):
    if not 0 < args.tolerance < 1:
        raise InputError("--tolerance must be between 0 and 1")
    if args.min_payments < 1 or args.annual_slack < 0 or args.max_questions < 0:
        raise InputError("--min-payments must be 1 or more; slack and max questions 0 or more")
    if not 0 <= args.mixed_low < args.mixed_high <= 100:
        raise InputError("--mixed-low must be below --mixed-high, both within 0 to 100")
    names, rows = read_rows(args.input, ["customer", "amount"])
    if "month" not in names and "date" not in names:
        raise InputError("%s needs a month or date column" % args.input)
    primary = args.currency.strip().upper()
    per_cust = defaultdict(lambda: defaultdict(Decimal))
    per_acct = defaultdict(lambda: defaultdict(lambda: defaultdict(Decimal)))
    no_cust = {"rows": 0, "total": D0}
    other = defaultdict(lambda: {"customers": set(), "total": D0})
    schedule_customers = set()
    texts = defaultdict(list)
    months_seen = []
    merger = NameMerger()
    payouts = {"rows": 0, "total": D0}
    for n, r in rows:
        where = "row %d" % n
        amt = parse_amount(r.get("amount"), where)
        m = month_index(r.get("month") or r.get("date"), where)
        months_seen.append(m)
        ccy = (r.get("currency") or primary).upper()
        cust = merger.name(r.get("customer"))
        if is_payout(cust, r.get("description") or r.get("memo")):
            payouts["rows"] += 1
            payouts["total"] += amt
            continue
        if not cust:
            no_cust["rows"] += 1
            no_cust["total"] += amt
            continue
        if ccy != primary:
            other[ccy]["customers"].add(cust)
            other[ccy]["total"] += amt
            continue
        if (r.get("cadence") or "").lower() == "schedule":
            schedule_customers.add(cust)
            continue
        per_cust[cust][m] += amt
        per_acct[r.get("account") or "(no account)"][cust][m] += amt
        text = r.get("description") or r.get("memo") or ""
        if text:
            texts[cust].append(text)

    customers = []
    for cust, by_month in per_cust.items():
        c = classify_cadence(by_month, args.tolerance, args.min_payments, args.annual_slack)
        c["customer"] = cust
        apply_descriptions(c, texts.get(cust, []))
        customers.append(c)
    customers.sort(key=lambda c: (-c["total"], c["customer"]))
    counts = defaultdict(int)
    for c in customers:
        counts[c["cadence"]] += 1
    counts["schedule"] = len(schedule_customers)
    unclear = [c for c in customers if c["cadence"] == "unclear"]
    grouped = defaultdict(list)
    for c in unclear:
        same_amount = c.get("min_amount") == c.get("max_amount")
        key = (c["reason"], c["payments"], c.get("min_amount") if same_amount else None)
        grouped[key].append(c)
    groups_ranked = sorted(grouped.values(),
                           key=lambda g: (-sum(c["total"] for c in g), g[0]["customer"]))
    questions = []
    for g in groups_ranked[:args.max_questions]:
        one = len(g) == 1
        if g[0]["looks_annual"]:
            q = ("Is this a yearly plan, and did it start on the payment date?" if one else
                 "Are these all yearly plans that started on their payment date?")
        else:
            q = ("How does this customer pay: monthly, quarterly, yearly, or one-time?" if one
                 else "How do these customers pay: monthly, quarterly, yearly, or one-time?")
        questions.append({"customers": [c["customer"] for c in g], "what_we_see": g[0]["reason"],
                          "amount_each": g[0].get("min_amount") if len(g) > 1 else None,
                          "window_total": money(sum((Decimal(str(c["total"])) for c in g), D0)),
                          "question": q})
    not_asked = [{"customer": c["customer"], "window_total": c["total"], "reason": c["reason"]}
                 for g in groups_ranked[args.max_questions:] for c in g]

    accounts = []
    for acct, custs in per_acct.items():
        total = D0
        repeat = D0
        for by_month in custs.values():
            t = sum(by_month.values(), D0)
            total += t
            if sum(1 for a in by_month.values() if a > 0) >= 2:
                repeat += t
        share = pct(repeat, total, 0)
        hint = any(h in acct.lower() for h in SUBSCRIPTION_HINTS)
        if share is None:
            kind = "empty"
        elif share >= args.mixed_high:
            kind = "recurring"
        elif share >= args.mixed_low:
            kind = "mixed"
        else:
            kind = "one_time"
        accounts.append({"account": acct, "window_total": money(total),
                         "customers": len(custs), "repeat_customer_share_pct": share,
                         "pattern": kind, "name_suggests_subscription": hint,
                         "default_include": bool(hint or kind == "recurring")})
    accounts.sort(key=lambda a: -a["window_total"])

    groups = defaultdict(list)
    for cust, by_month in per_cust.items():
        key = normalize_name(cust)
        if key:
            pos = sorted(m for m, a in by_month.items() if a > 0)
            groups[key].append({"customer": cust,
                                "first_month": month_str(pos[0]) if pos else None,
                                "last_month": month_str(pos[-1]) if pos else None,
                                "window_total": money(sum(by_month.values(), D0)),
                                "_range": (pos[0], pos[-1]) if pos else None})
    duplicates = []
    for key, members in groups.items():
        if len(members) < 2:
            continue
        ranges = [mm["_range"] for mm in members if mm["_range"]]
        overlap = any(a[0] <= b[1] and b[0] <= a[1]
                      for i, a in enumerate(ranges) for b in ranges[i + 1:])
        for mm in members:
            del mm["_range"]
        duplicates.append({"normalized": key, "members": members,
                           "months_overlap": overlap})

    out = {
        "window": {"first": month_str(min(months_seen)) if months_seen else None,
                   "last": month_str(max(months_seen)) if months_seen else None},
        "currency": primary,
        "settings": {"tolerance": args.tolerance, "min_payments": args.min_payments,
                     "annual_slack": args.annual_slack, "mixed_low": args.mixed_low,
                     "mixed_high": args.mixed_high, "max_questions": args.max_questions},
        "cadence_counts": dict(counts),
        "customers": customers,
        "questions": questions,
        "unclear_not_asked": not_asked,
        "accounts": accounts,
        "duplicates": duplicates,
        "merged_names": merger.merged(),
        "payouts": {"rows": payouts["rows"], "total": money(payouts["total"])},
        "no_customer": {"rows": no_cust["rows"], "total": money(no_cust["total"])},
        "other_currency": [{"currency": k, "customers": len(v["customers"]),
                            "window_total": money(v["total"])}
                           for k, v in sorted(other.items())],
    }
    if args.out:
        write_json(out, args.out)
        print("scan written to %s" % args.out)
    else:
        print(json.dumps(out, indent=2, ensure_ascii=False))


# ---------- build ----------

def first_revenue_month(rows, end, primary):
    """First month with positive recurring revenue for a named customer in the primary currency."""
    first = None
    for n, r in rows:
        if not (r.get("report_as") or r.get("customer")):
            continue
        if not r.get("report_as") and is_payout(r.get("customer"), r.get("description")):
            continue
        if (r.get("cadence") or "").lower() == "one_time":
            continue
        if (r.get("currency") or primary).upper() != primary:
            continue
        m = month_index(r.get("month"), "row %d" % n)
        if m <= end and parse_amount(r.get("amount"), "row %d" % n) > 0:
            first = m if first is None else min(first, m)
    return first


def write_no_customer_report(args, primary, end, no_cust, merger):
    """Every row lacks a customer: size the problem instead of building a report."""
    window_total = money(no_cust["window_total"])
    report = {
        "meta": {"end_month": month_str(end), "currency": primary,
                 "warnings": ["No row has a customer, so there is no MRR to report."]},
        "summary": None,
        "excluded": {"no_customer": {"rows": no_cust["rows"], "total": money(no_cust["total"]),
                                     "window_rows": no_cust["window_rows"],
                                     "window_total": window_total}},
        "coverage": {"assigned_total": 0.0, "no_customer_total": window_total,
                     "assigned_pct": 0.0 if no_cust["window_total"] else None},
        "data_quality": {"fires": True, "reasons": ["most revenue has no customer"],
                         "test_names": []},
        "merged_names": merger.merged(),
    }
    os.makedirs(args.out_dir, exist_ok=True)
    write_json(report, os.path.join(args.out_dir, "mrr_report.json"))
    raise NoCustomerError("no row has a customer (%d rows, %s %s); wrote the sizing to "
                          "mrr_report.json" % (no_cust["rows"], money(no_cust["total"]), primary))


def cmd_build(args):
    if args.months is not None and not 1 <= args.months <= 120:
        raise InputError("--months must be between 1 and 120")
    if args.accel_multiple <= 1 or not 0 < args.ask_share < 1 \
            or not 0 <= args.min_coverage <= 100:
        raise InputError("--accel-multiple must be above 1, --ask-share within 0 to 1, "
                         "--min-coverage within 0 to 100")
    if args.renewal_days < 0 or args.top_n < 1 or args.cohort_min_months < 1:
        raise InputError("--renewal-days must be 0 or more; --top-n and --cohort-min-months 1 or more")
    if not 0 < args.unclosed_share < 1 or args.unclosed_multiple < 1 or args.break_sd <= 0:
        raise InputError("--unclosed-share must be within 0 to 1, --unclosed-multiple 1 or more, --break-sd above 0")
    try:
        offsets = [int(x) for x in args.cohort_offsets.split(",") if x.strip()]
    except ValueError:
        raise InputError("--cohort-offsets must be comma-separated whole numbers")
    if not offsets or any(o < 1 for o in offsets):
        raise InputError("--cohort-offsets must list positive month offsets")

    _, rows = read_rows(args.input, ["customer", "month", "amount"])
    end = month_index(args.end_month, "--end-month")
    primary = args.currency.strip().upper()
    auto_window = args.months is None
    if auto_window:
        first_rev = first_revenue_month(rows, end, primary)
        win_start = end if first_rev is None else max(first_rev, end - 119)
    else:
        win_start = end - args.months + 1
    window = list(range(win_start, end + 1))
    merger = NameMerger()
    reversal_months = set()
    payouts = {"rows": 0, "total": D0}
    as_of = parse_date(args.as_of, "--as-of") if args.as_of else date.today()
    do_spread = args.spread == "yes"

    grid = defaultdict(lambda: defaultdict(Decimal))
    other_grid = defaultdict(lambda: defaultdict(Decimal))
    other_total = defaultdict(Decimal)
    term_active = defaultdict(set)
    info = {}
    no_cust = {"rows": 0, "total": D0, "window_rows": 0, "window_total": D0,
               "latest_rows": 0, "latest_total": D0}
    one_time = defaultdict(Decimal)
    rows_after_end = 0
    first_data = None

    for n, r in rows:
        where = "row %d" % n
        m = month_index(r.get("month"), where)
        amt = parse_amount(r.get("amount"), where)
        if m > end:
            rows_after_end += 1
            continue
        cadence = (r.get("cadence") or "").lower()
        if cadence and cadence not in ALLOWED_CADENCE:
            raise InputError("%s: cadence '%s' is not one of %s"
                             % (where, cadence, ", ".join(sorted(ALLOWED_CADENCE))))
        source = (r.get("source") or "").lower()
        if source and source not in SOURCE_LABELS:
            raise InputError("%s: source '%s' is not one of %s"
                             % (where, source, ", ".join(sorted(SOURCE_LABELS))))
        term = parse_term(r.get("term_months"), where)
        ccy = (r.get("currency") or primary).upper()
        cust = merger.name(r.get("report_as") or r.get("customer"))
        in_window = m >= win_start
        if not r.get("report_as") and is_payout(cust, r.get("description")):
            if in_window:
                payouts["rows"] += 1
                payouts["total"] += amt
            continue
        if cust and amt < 0 and is_reversal_text(r.get("description")):
            reversal_months.add((cust, m))
        if not cust:
            no_cust["rows"] += 1
            no_cust["total"] += amt
            if in_window:
                no_cust["window_rows"] += 1
                no_cust["window_total"] += amt
            if m == end:
                no_cust["latest_rows"] += 1
                no_cust["latest_total"] += amt
            continue
        if cadence == "one_time":
            if in_window and ccy == primary:
                one_time[cust] += amt
            continue
        parts = spread(amt, term if do_spread else 1)
        if ccy != primary:
            for k, p in enumerate(parts):
                other_grid[(ccy, cust)][m + k] += p
            if in_window:
                other_total[ccy] += amt
            continue
        for k, p in enumerate(parts):
            grid[cust][m + k] += p
        inf = info.setdefault(cust, {"cadences": set(), "sources": defaultdict(Decimal),
                                     "class": "", "class_month": -1, "plan": "",
                                     "plan_month": -1, "term_ends": [], "multi_term": False,
                                     "window_booked": D0, "last_month": -1, "last_term": 1})
        inf["cadences"].add(cadence or "unlabeled")
        inf["sources"][source or "unlabeled"] += abs(amt)
        if r.get("class") and m >= inf["class_month"]:
            inf["class"], inf["class_month"] = r["class"], m
        if r.get("plan") and m >= inf["plan_month"]:
            inf["plan"], inf["plan_month"] = r["plan"], m
        if amt > 0 and m >= inf["last_month"]:
            inf["last_month"], inf["last_term"] = m, term
        if term > 1:
            inf["multi_term"] = True
            term_active[cust].update(range(m, m + term))
        if r.get("term_end"):
            inf["term_ends"].append(parse_date(r["term_end"], where))
        if in_window:
            inf["window_booked"] += amt
        first_data = m if first_data is None else min(first_data, m)

    if first_data is None:
        if no_cust["rows"] and not one_time and not other_total:
            write_no_customer_report(args, primary, end, no_cust, merger)
        raise InputError("no customer revenue rows in %s on or before %s"
                         % (primary, month_str(end)))
    warnings = []
    if auto_window:
        warnings.append("The report starts in %s, the first month with revenue, so every "
                        "customer in that month counts as new." % month_label(win_start))
    elif first_data >= win_start:
        warnings.append("No revenue rows before %s, so opening MRR is 0 and every customer "
                        "in the first month counts as new." % month_label(win_start))
    first = min(first_data, win_start - 1)
    all_months = list(range(first, end + 1))

    adjustments = []
    if args.adjust == "yes":
        sched = {c for c, inf in info.items() if "schedule" in inf["sources"]}
        adjustments = adjust_schedules(grid, sched, reversal_months, args.accel_multiple)

    def customer_source(inf):
        if "schedule" in inf["sources"]:
            return "schedule"
        return max(sorted(inf["sources"].items()), key=lambda kv: kv[1])[0]

    def cadence_label(inf):
        if customer_source(inf) == "schedule":
            return "schedule"
        for k in CADENCE_PRIORITY:
            if k in inf["cadences"]:
                return k
        return "unlabeled"

    # Minimum-history rule.
    included, below_min, too_new = [], {}, []
    for cust, g in grid.items():
        inf = info[cust]
        if (inf["cadences"] & QUALIFYING_CADENCE) or inf["multi_term"] \
                or customer_source(inf) == "schedule":
            included.append(cust)
            continue
        best = run = 0
        for m in all_months:
            if g.get(m, D0) > 0:
                run += 1
                best = max(best, run)
            else:
                run = 0
        if best >= args.min_history:
            included.append(cust)
        elif run > 0 and g.get(end, D0) > 0:
            # Still running at the end month and too young to pass the rule yet.
            included.append(cust)
            too_new.append(cust)
        else:
            below_min[cust] = inf["window_booked"]

    # Monthly series, activity, churn grace.
    series = {}
    negatives = []
    in_grace = []
    for cust in included:
        g = grid[cust]
        mrr, act = {}, {}
        for m in all_months:
            v = g.get(m, D0)
            if v < 0:
                negatives.append({"customer": cust, "month": month_str(m), "amount": money(v)})
                v = D0
            mrr[m] = v
            act[m] = v > 0 or m in term_active[cust]
        seen = False
        i = 0
        while i < len(all_months):
            m = all_months[i]
            if act[m]:
                seen = True
                i += 1
                continue
            if not seen:
                i += 1
                continue
            j = i
            while j < len(all_months) and not act[all_months[j]]:
                j += 1
            if j - i < args.churn_after_months:
                prev = mrr[all_months[i - 1]]
                for k in range(i, j):
                    mrr[all_months[k]] = prev
                    act[all_months[k]] = True
                if j == len(all_months):
                    in_grace.append({"customer": cust, "mrr": money(prev),
                                     "months_without_revenue": j - i})
            i = j
        series[cust] = (mrr, act)
    first_active = {}
    for cust in list(included):
        mrr, act = series[cust]
        fa = next((m for m in all_months if act[m]), None)
        if fa is None:
            included.remove(cust)
            below_min[cust] = info[cust]["window_booked"]
            del series[cust]
        else:
            first_active[cust] = fa

    def total_mrr(m):
        return sum((series[c][0].get(m, D0) for c in included), D0)

    def active_count(m):
        return sum(1 for c in included if series[c][1].get(m, False))

    # Movements and the bridge check.
    movements = []
    latest_detail = {k: [] for k in KINDS}
    cust_move = {}
    for m in window:
        sums = {k: D0 for k in KINDS}
        counts = {k: 0 for k in KINDS}
        for c in included:
            mrr, act = series[c]
            a0, a1 = mrr.get(m - 1, D0), mrr[m]
            x0, x1 = act.get(m - 1, False), act[m]
            kind = None
            if x1 and not x0:
                kind = "new" if first_active[c] == m else "reactivation"
            elif x0 and not x1:
                kind = "churn"
            elif x0 and x1:
                if a1 > a0:
                    kind = "expansion"
                elif a1 < a0:
                    kind = "contraction"
            amount = a1 - a0
            if kind:
                sums[kind] += amount
                counts[kind] += 1
            if m == end:
                cust_move[c] = (kind, amount)
                if kind:
                    latest_detail[kind].append((c, amount))
        opening, closing = total_mrr(m - 1), total_mrr(m)
        computed = opening + sum(sums.values())
        if computed != closing:
            raise BridgeError("%s: opening %s + movements %s = %s, but closing MRR is %s"
                              % (month_label(m), opening, sum(sums.values()), computed, closing))
        lost = -(sums["churn"] + sums["contraction"])
        gained = sums["new"] + sums["expansion"] + sums["reactivation"]
        opening_customers = active_count(m - 1)
        movements.append({
            "month": month_str(m), "label": month_label(m),
            "opening": money(opening),
            "new": money(sums["new"]), "expansion": money(sums["expansion"]),
            "reactivation": money(sums["reactivation"]),
            "contraction": money(sums["contraction"]), "churn": money(sums["churn"]),
            "closing": money(closing), "net_new": money(closing - opening),
            "counts": counts, "opening_customers": opening_customers,
            "closing_customers": active_count(m), "ties": True,
            "logo_churn_pct": pct(counts["churn"], opening_customers),
            "gross_mrr_churn_pct": pct(lost, opening),
            "net_mrr_churn_pct": pct(lost - sums["expansion"], opening),
            "quick_ratio": ratio(gained, lost),
        })

    trend = []
    for m in window:
        mrr_m, cust_m = total_mrr(m), active_count(m)
        prev = total_mrr(m - 1)
        trend.append({"month": month_str(m), "label": month_label(m), "mrr": money(mrr_m),
                      "arr": money(mrr_m * 12), "customers": cust_m,
                      "arpa": money(mrr_m / cust_m) if cust_m else None,
                      "change_pct": pct(mrr_m - prev, prev)})
    trend_quarterly = [t for t, m in zip(trend, window) if m % 3 == 2]

    arr_bridge = []
    for m in window:
        if m % 3 != 0 or m + 2 > end:
            continue
        q_moves = [mv for mv in movements if month_index(mv["month"], "q") in (m, m + 1, m + 2)]
        opening = total_mrr(m - 1) * 12
        closing = total_mrr(m + 2) * 12
        entry = {"quarter": quarter_label(m // 3), "opening_arr": money(opening),
                 "closing_arr": money(closing), "change": money(closing - opening),
                 "change_pct": pct(closing - opening, opening)}
        for k in KINDS:
            entry[k] = money(sum((Decimal(str(mv[k])) for mv in q_moves), D0) * 12)
        arr_bridge.append(entry)

    # Summary and KPI comparisons.
    cur, prv = trend[-1], (trend[-2] if len(trend) > 1 else None)
    cur_mv, prv_mv = movements[-1], (movements[-2] if len(movements) > 1 else None)
    if prv is None:
        pm = end - 1
        p_mrr, p_cust = total_mrr(pm), active_count(pm)
        prv = {"month": month_str(pm), "label": month_label(pm), "mrr": money(p_mrr),
               "arr": money(p_mrr * 12), "customers": p_cust,
               "arpa": money(p_mrr / p_cust) if p_cust else None}

    def diff(a, b):
        return None if a is None or b is None else money(Decimal(str(a)) - Decimal(str(b)))

    summary = {
        "month": cur["month"], "label": cur["label"], "mrr": cur["mrr"], "arr": cur["arr"],
        "customers": cur["customers"], "arpa": cur["arpa"], "net_new": cur_mv["net_new"],
        "prior": {"month": prv["month"], "label": prv["label"], "mrr": prv["mrr"],
                  "arr": prv["arr"], "customers": prv["customers"], "arpa": prv["arpa"],
                  "net_new": prv_mv["net_new"] if prv_mv else None},
        "mrr_change_pct": pct(total_mrr(end) - total_mrr(end - 1), total_mrr(end - 1)),
        "arr_change": diff(cur["arr"], prv["arr"]),
        "customers_change": cur["customers"] - prv["customers"],
        "arpa_change": diff(cur["arpa"], prv["arpa"]),
        "net_new_change": diff(cur_mv["net_new"], prv_mv["net_new"] if prv_mv else None),
    }
    kpi_keys = ["logo_churn_pct", "gross_mrr_churn_pct", "net_mrr_churn_pct", "quick_ratio"]
    kpis = {"current": {k: cur_mv[k] for k in kpi_keys},
            "prior": {k: prv_mv[k] for k in kpi_keys} if prv_mv else None,
            "change": {k: diff(cur_mv[k], prv_mv[k]) if prv_mv else None for k in kpi_keys}}

    # Retention (12 months, cohort active 12 months before the end month).
    c12 = end - 12
    if c12 < first_data:
        retention = {"available": False,
                     "reason": "needs revenue for %s, 12 months before %s"
                               % (month_label(c12), month_label(end))}
    else:
        cohort = [c for c in included if series[c][0].get(c12, D0) > 0]
        start = sum((series[c][0][c12] for c in cohort), D0)
        if not cohort or start == 0:
            retention = {"available": False,
                         "reason": "no customers with MRR in %s" % month_label(c12)}
        else:
            finish = sum((series[c][0][end] for c in cohort), D0)
            kept = sum((min(series[c][0][end], series[c][0][c12]) for c in cohort), D0)
            retention = {"available": True, "cohort_month": month_label(c12),
                         "cohort_size": len(cohort), "start_mrr": money(start),
                         "end_mrr": money(finish), "nrr_pct": pct(finish, start, 0),
                         "grr_pct": pct(kept, start, 0),
                         "small_sample": len(cohort) < args.retention_min_customers}

    # Concentration and top customers.
    end_total = total_mrr(end)
    ranked = sorted((c for c in included if series[c][0][end] > 0),
                    key=lambda c: (-series[c][0][end], c))
    top = ranked[:args.top_n]
    concentration = {
        "active_customers": len(ranked),
        "top_customer": top[0] if top else None,
        "top_customer_share_pct": pct(series[top[0]][0][end], end_total) if top else None,
        "top_n": args.top_n,
        "top_n_share_pct": pct(sum((series[c][0][end] for c in top), D0), end_total),
    }
    top_customers = []
    for c in top:
        kind, amount = cust_move.get(c, (None, D0))
        top_customers.append({"customer": c, "mrr": money(series[c][0][end]),
                              "share_pct": pct(series[c][0][end], end_total),
                              "movement": kind or "none", "movement_amount": money(amount),
                              "cadence": cadence_label(info[c]),
                              "source": customer_source(info[c]),
                              "class": info[c]["class"] or None,
                              "plan": info[c]["plan"] or None})

    bridge_steps = []
    for k in KINDS:
        detail = sorted(latest_detail[k], key=lambda x: (-abs(x[1]), x[0]))
        bridge_steps.append({"kind": k, "amount": cur_mv[k], "customers": cur_mv["counts"][k],
                             "top": [{"customer": c, "amount": money(a)} for c, a in detail[:3]]})
    bridge_latest = {"month": cur_mv["month"], "label": cur_mv["label"],
                     "opening_label": month_label(end - 1), "opening": cur_mv["opening"],
                     "closing": cur_mv["closing"], "opening_customers": cur_mv["opening_customers"],
                     "closing_customers": cur_mv["closing_customers"], "steps": bridge_steps,
                     "ties": True}

    # Breakdowns by class and by plan (plan comes from descriptions, policies, or answers).
    def breakdown(field, missing_label):
        if not any(info[c][field] for c in included):
            return None
        agg = defaultdict(lambda: {"mrr": D0, "customers": 0, "net_new": D0})
        for c in included:
            name = info[c][field] or missing_label
            mrr, act = series[c]
            agg[name]["mrr"] += mrr[end]
            agg[name]["net_new"] += mrr[end] - mrr.get(end - 1, D0)
            if act[end]:
                agg[name]["customers"] += 1
        return [{field: k, "mrr": money(v["mrr"]), "share_pct": pct(v["mrr"], end_total),
                 "customers": v["customers"],
                 "arpa": money(v["mrr"] / v["customers"]) if v["customers"] else None,
                 "net_new": money(v["net_new"])}
                for k, v in sorted(agg.items(), key=lambda kv: -kv[1]["mrr"])]

    classes = breakdown("class", "Unclassified")
    plans = breakdown("plan", "No plan named")

    # Cohort retention by start quarter.
    cohorts = None
    small_cohorts = 0
    if end - first_data + 1 >= args.cohort_min_months:
        groups = defaultdict(list)
        for c in included:
            if first_active[c] > first_data:
                groups[first_active[c] // 3].append(c)
        rows_out = []
        for q in sorted(groups):
            members = groups[q]
            start = sum((series[c][0][first_active[c]] for c in members), D0)
            if start == 0:
                continue
            if len(members) < args.cohort_min_customers:
                small_cohorts += 1
                continue
            values = []
            for k in offsets:
                if max(first_active[c] for c in members) + k <= end:
                    later = sum((series[c][0][first_active[c] + k] for c in members), D0)
                    values.append(int(pct(later, start, 0)))
                else:
                    values.append(None)
            if any(v is not None for v in values):
                rows_out.append({"label": quarter_label(q), "customers": len(members),
                                 "start_mrr": money(start), "values": values})
        if rows_out:
            cohorts = {"offsets": offsets, "rows": rows_out}

    # Next renewal per active customer: schedule end date first, else the month the last
    # multi-month payment runs out. Monthly payers have no renewal date.
    def next_renewal(c):
        inf = info[c]
        if not series[c][1].get(end, False):
            return None
        if inf["term_ends"]:
            d = max(inf["term_ends"])
            return {"date": d.isoformat(), "basis": "schedule",
                    "month": "%s %d, %d" % (MONTH_NAMES[d.month - 1], d.day, d.year)}
        if inf["last_term"] > 1 and inf["last_month"] >= 0:
            due_m = inf["last_month"] + inf["last_term"]
            return {"date": "%s-01" % month_str(due_m), "month": month_label(due_m),
                    "basis": "billing"}
        return None

    renewal_of = {c: next_renewal(c) for c in included}
    renewals = None
    if any(renewal_of.values()):
        horizon = as_of + timedelta(days=args.renewal_days)
        due = []
        for c, r in renewal_of.items():
            if not r:
                continue
            d = parse_date(r["date"], "renewal")
            month_end = date(d.year + d.month // 12, d.month % 12 + 1, 1) - timedelta(days=1)
            if (d if r["basis"] == "schedule" else month_end) >= as_of and d <= horizon:
                due.append((d, c, r))
        due.sort()
        renewals = {"window_days": args.renewal_days, "as_of": as_of.isoformat(),
                    "count": len(due),
                    "mrr": money(sum((series[c][0][end] for _, c, _ in due), D0)),
                    "rows": [{"customer": c, "mrr": money(series[c][0][end]),
                              "ends": r["month"], "date": r["date"],
                              "basis": r["basis"]} for _, c, r in due]}

    # One row per customer in plain words, for the chat, the dashboard, and the CSV.
    def billing_label(c):
        inf = info[c]
        if customer_source(inf) == "schedule":
            return "Revenue schedule"
        if cadence_label(inf) == "unconfirmed":
            return "Not known, counted when paid"
        return BILLING_LABELS.get(inf["last_term"], "Every %d months" % inf["last_term"])

    def status_of(c):
        mrr, act = series[c]
        kind, amount = cust_move.get(c, (None, D0))
        if kind:
            return STATUS_LABELS[kind], amount
        if act[end]:
            return "Active", D0
        last = max((m for m in all_months if act[m]), default=None)
        return ("Churned in %s" % month_label(last + 1)) if last is not None else "Inactive", D0

    customer_rows = []
    for c in sorted(included, key=lambda c: (-series[c][0][end], c)):
        status, change = status_of(c)
        r = renewal_of.get(c)
        customer_rows.append({
            "customer": c, "plan": info[c]["plan"] or None, "class": info[c]["class"] or None,
            "billing": billing_label(c), "started": month_label(first_active[c]),
            "last_billed": month_label(info[c]["last_month"]) if info[c]["last_month"] >= 0 else None,
            "next_renewal": r["month"] if r else None,
            "mrr": money(series[c][0][end]), "share_pct": pct(series[c][0][end], end_total),
            "status": status, "change": money(change),
            "monthly": [money(series[c][0][m]) for m in window]})

    # Source share (R2) and cadence labels.
    src = defaultdict(lambda: {"mrr": D0, "customers": 0})
    cadence_counts = defaultdict(int)
    for c in ranked:
        s = customer_source(info[c])
        src[s]["mrr"] += series[c][0][end]
        src[s]["customers"] += 1
        cadence_counts[cadence_label(info[c])] += 1
    source_share = [{"source": k, "label": SOURCE_LABELS.get(k, "Unlabeled source"),
                     "customers": v["customers"], "mrr": money(v["mrr"]),
                     "share_pct": pct(v["mrr"], end_total, 0)}
                    for k, v in sorted(src.items(), key=lambda kv: -kv[1]["mrr"])]
    unconfirmed = sorted(({"customer": c, "window_total": money(info[c]["window_booked"])}
                          for c in included if cadence_label(info[c]) == "unconfirmed"),
                         key=lambda x: -x["window_total"])

    def top_list(d, n=10):
        items = sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))
        return [{"customer": k, "window_total": money(v)} for k, v in items[:n]]

    other_currency = []
    for ccy in sorted({k[0] for k in other_grid}):
        keys = [k for k in other_grid if k[0] == ccy]
        latest = sum((other_grid[k].get(end, D0) for k in keys), D0)
        other_currency.append({"currency": ccy, "customers": len({k[1] for k in keys}),
                               "latest_mrr": money(latest),
                               "window_total": money(other_total[ccy])})
    excluded = {
        "no_customer": {"rows": no_cust["rows"], "total": money(no_cust["total"]),
                        "window_rows": no_cust["window_rows"],
                        "window_total": money(no_cust["window_total"]),
                        "latest_rows": no_cust["latest_rows"],
                        "latest_total": money(no_cust["latest_total"]),
                        "latest_label": month_label(end)},
        "one_time": {"customers": len(one_time),
                     "window_total": money(sum(one_time.values(), D0)),
                     "top": top_list(one_time)},
        "below_min_history": {"customers": len(below_min),
                              "window_total": money(sum(below_min.values(), D0)),
                              "top": top_list(below_min)},
        "other_currency": other_currency,
        "negative_months": negatives,
        "payouts": {"rows": payouts["rows"], "window_total": money(payouts["total"])},
    }

    # Trend breaks (I6), only with 12 or more months.
    trend_breaks = None
    changes = [(t["label"], Decimal(str(t["change_pct"]))) for t in trend
               if t["change_pct"] is not None]
    if len(window) >= 12 and len(changes) >= 12:
        vals = [v for _, v in changes]
        mean = sum(vals, D0) / len(vals)
        sd = (sum(((v - mean) ** 2 for v in vals), D0) / len(vals)).sqrt()
        flagged = [{"month": lbl, "change_pct": float(v)} for lbl, v in changes
                   if sd > 0 and abs(v - mean) > Decimal(str(args.break_sd)) * sd]
        history = end - first_data + 1
        trend_breaks = {"mean_change_pct": float(mean.quantize(Decimal("0.1"))),
                        "sd_change_pct": float(sd.quantize(Decimal("0.1"))),
                        "threshold_sd": args.break_sd, "flagged": flagged,
                        "confidence": "low, one year of history" if history < 24
                        else "medium, two or more years of history"}

    # Booked versus collected (I5).
    booked_vs_collected = None
    if args.collected:
        _, crow = read_rows(args.collected, ["customer", "month", "amount"])
        coll = defaultdict(Decimal)
        unmatched = {"rows": 0, "total": D0}
        inc = set(included)
        for n, r in crow:
            where = "collected row %d" % n
            m = month_index(r.get("month"), where)
            amt = parse_amount(r.get("amount"), where)
            if m < win_start or m > end or (r.get("currency") or primary).upper() != primary:
                continue
            cust = (r.get("report_as") or r.get("customer") or "").strip()
            if cust in inc:
                coll[cust] += amt
            else:
                unmatched["rows"] += 1
                unmatched["total"] += amt
        booked = sum((info[c]["window_booked"] for c in included), D0)
        collected = sum(coll.values(), D0)
        gaps = sorted(((c, info[c]["window_booked"] - coll.get(c, D0)) for c in included),
                      key=lambda x: (-abs(x[1]), x[0]))
        booked_vs_collected = {"booked": money(booked), "collected": money(collected),
                               "gap": money(booked - collected),
                               "collected_from_other_payers": {"rows": unmatched["rows"],
                                                               "total": money(unmatched["total"])},
                               "top_gaps": [{"customer": c, "gap": money(g)}
                                            for c, g in gaps[:5] if g != 0]}

    # Months that look unclosed (G5).
    unclosed = None
    if args.money_in:
        _, mrows = read_rows(args.money_in, ["month", "total_in", "uncategorized_in"])
        shares = []
        for n, r in mrows:
            where = "money-in row %d" % n
            m = month_index(r.get("month"), where)
            if m < win_start or m > end:
                continue
            tot = parse_amount(r.get("total_in"), where)
            unc = parse_amount(r.get("uncategorized_in"), where)
            share = (unc / tot) if tot > 0 else D0
            shares.append((m, share, unc))
        med = median([s for _, s, _ in shares])
        limit = Decimal(str(args.unclosed_share))
        mult = Decimal(str(args.unclosed_multiple))
        unclosed = {"threshold_share_pct": float(limit * 100),
                    "median_share_pct": float((med * 100).quantize(Decimal("0.1"))),
                    "flagged": [{"month": month_label(m),
                                 "uncategorized_share_pct": float((s * 100).quantize(Decimal("0.1"))),
                                 "uncategorized_in": money(u)}
                                for m, s, u in sorted(shares)
                                if s >= limit and (med == 0 or s >= mult * med)]}

    end_partial = (as_of.year * 12 + as_of.month - 1) == end
    end_label = month_label(end)
    if end_partial:
        end_label = "%s (to %s %d)" % (month_label(end), MONTH_NAMES[as_of.month - 1], as_of.day)
        warnings.append("%s is not over yet. Its MRR covers payments up to %s; label it month "
                        "to date everywhere." % (month_label(end), as_of.isoformat()))
    if small_cohorts:
        warnings.append("%d start cohorts had fewer than %d customers and were left out."
                        % (small_cohorts, args.cohort_min_customers))

    effect_by_month = defaultdict(Decimal)
    for a in adjustments:
        effect_by_month[a["month_index"]] += a["effect"]
    worst = max((abs(e) / total_mrr(m) for m, e in effect_by_month.items()
                 if m in window and total_mrr(m) > 0), default=D0)
    schedule_adjustments = {
        "accel_multiple": args.accel_multiple,
        "ask_share_pct": float(Decimal(str(args.ask_share)) * 100),
        "largest_share_of_month_pct": float((worst * 100).quantize(Decimal("0.1"))),
        "needs_question": worst >= Decimal(str(args.ask_share)),
        "rows": [{"customer": a["customer"], "month": month_label(a["month_index"]),
                  "kind": a["kind"], "booked": money(a["booked"]), "used": money(a["used"]),
                  "effect": money(a["effect"])} for a in adjustments],
    }

    assigned = sum((inf["window_booked"] for inf in info.values()), D0) \
        + sum(one_time.values(), D0)
    names = list(info) + [inf["plan"] for inf in info.values()]
    coverage, data_quality = coverage_and_gate(
        assigned, no_cust["window_total"], names, args.min_coverage,
        [args.entity_name] if args.entity_name else [])
    coverage["assigned_total"] = money(coverage["assigned_total"])
    coverage["no_customer_total"] = money(coverage["no_customer_total"])
    coverage["source_mix"] = source_share
    if data_quality["fires"]:
        warnings.append("Data-quality gate: %s. Confirm this is the right data before "
                        "sharing figures." % "; ".join(data_quality["reasons"]))

    report = {
        "meta": {"end_month": month_str(end), "end_label": end_label, "end_partial": end_partial,
                 "window": [month_str(m) for m in window], "currency": primary,
                 "as_of": as_of.isoformat(), "history_from": month_str(first_data),
                 "choices": {"spread": args.spread, "min_history": args.min_history,
                             "churn_after_months": args.churn_after_months,
                             "months": len(window), "window_from": "first revenue month"
                             if auto_window else "--months",
                             "adjust_schedules": args.adjust,
                             "renewal_days": args.renewal_days,
                             "top_n": args.top_n, "cohort_offsets": offsets},
                 "rows_after_end_ignored": rows_after_end, "warnings": warnings,
                 "sign_convention": "contraction and churn are negative; opening + all movements = closing"},
        "summary": summary, "kpis": kpis, "trend": trend, "trend_quarterly": trend_quarterly,
        "movements": movements, "bridge_latest": bridge_latest,
        "arr_bridge_quarterly": arr_bridge, "retention": retention,
        "concentration": concentration, "top_customers": top_customers,
        "classes": classes, "plans": plans, "customers": customer_rows,
        "cohorts": cohorts, "renewals": renewals,
        "source_share": source_share, "cadence_counts": dict(cadence_counts),
        "unconfirmed": unconfirmed,
        "new_not_yet_confirmed": [{"customer": c, "mrr": money(series[c][0][end])}
                                  for c in sorted(too_new)],
        "in_grace": in_grace, "excluded": excluded, "trend_breaks": trend_breaks,
        "booked_vs_collected": booked_vs_collected, "unclosed_months": unclosed,
        "schedule_adjustments": schedule_adjustments, "coverage": coverage,
        "data_quality": data_quality, "merged_names": merger.merged(),
    }

    os.makedirs(args.out_dir, exist_ok=True)
    write_json(report, os.path.join(args.out_dir, "mrr_report.json"))
    write_customer_csv(os.path.join(args.out_dir, "customer_detail.csv"), customer_rows,
                       [end_label if m == end else month_label(m) for m in window],
                       [money(total_mrr(m)) for m in window], month_label(end - 1))
    with open(os.path.join(args.out_dir, "movements.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        cols = ["month", "opening", "new", "expansion", "reactivation", "contraction",
                "churn", "closing", "net_new", "ties"]
        w.writerow(cols)
        for mv in movements:
            w.writerow([mv[k] for k in cols])
    with open(os.path.join(args.out_dir, "trend.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        cols = ["month", "mrr", "arr", "customers", "arpa", "change_pct"]
        w.writerow(cols)
        for t in trend:
            w.writerow(["" if t[k] is None else t[k] for k in cols])
    print("bridge check: ties for all %d months" % len(window))
    print("wrote mrr_report.json, customer_detail.csv, movements.csv, trend.csv to %s" % args.out_dir)


def write_customer_csv(path, rows, month_labels, totals, prior_label):
    """The CSV a reader opens: plain headers, and no column that is blank in every row."""
    fixed = [("Customer", "customer"), ("Plan", "plan"), ("Class", "class"),
             ("Billing", "billing"), ("Started", "started"), ("Last billed", "last_billed"),
             ("Next renewal", "next_renewal")]
    fixed = [(h, k) for h, k in fixed if k == "customer" or any(r[k] for r in rows)]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([h for h, _ in fixed] + ["MRR %s" % lbl for lbl in month_labels]
                   + ["Status", "Change vs %s" % prior_label])
        for r in rows:
            w.writerow([safe_cell(r[k] or "") for _, k in fixed]
                       + ["%.2f" % v for v in r["monthly"]]
                       + [r["status"], "%.2f" % r["change"]])
        w.writerow(["Total"] + [""] * (len(fixed) - 1) + ["%.2f" % v for v in totals] + ["", ""])


def build_parser():
    p = argparse.ArgumentParser(description="MRR and ARR arithmetic for the mrr-arr-report skill.")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("scan", help="cadence, account mix, and duplicates from raw revenue rows")
    s.add_argument("--input", required=True, help="CSV: customer, amount, month or date")
    s.add_argument("--currency", default="USD", help="primary currency code (default USD)")
    s.add_argument("--tolerance", type=float, default=0.10,
                   help="largest amount variation from the median for a clear cadence "
                        "(default 0.10, the 10 percent rule)")
    s.add_argument("--min-payments", type=int, default=2,
                   help="payments at one interval before a cadence is clear (default 2)")
    s.add_argument("--annual-slack", type=int, default=1,
                   help="months either side of 12 that still count as annual (default 1)")
    s.add_argument("--mixed-low", type=float, default=20.0,
                   help="repeat-customer share (percent) where an account becomes mixed (default 20)")
    s.add_argument("--mixed-high", type=float, default=80.0,
                   help="repeat-customer share (percent) where an account counts as recurring (default 80)")
    s.add_argument("--max-questions", type=int, default=3,
                   help="question groups (similar unclear customers asked together), ranked by revenue (default 3)")
    s.add_argument("--out", help="write JSON here instead of stdout")

    b = sub.add_parser("build", help="MRR, ARR, movements, retention from revenue rows")
    b.add_argument("--input", required=True, help="CSV: customer, month, amount, optional columns")
    b.add_argument("--end-month", required=True, help="last full month to report, YYYY-MM")
    b.add_argument("--months", type=int,
                   help="months to report; without it the report starts at the first "
                        "month with revenue (at most 120 months)")
    b.add_argument("--adjust", choices=["yes", "no"], default="yes",
                   help="rule C9: run-rate for stopped schedules and reversal months (default yes)")
    b.add_argument("--accel-multiple", type=float, default=3.0,
                   help="a schedule's last month at this many times the prior month counts "
                        "as stopped (default 3.0)")
    b.add_argument("--ask-share", type=float, default=0.10,
                   help="adjustments above this share of a month's MRR need the user's "
                        "answer (default 0.10)")
    b.add_argument("--min-coverage", type=float, default=80.0,
                   help="percent of revenue that must have a customer before the data-quality "
                        "gate passes (default 80)")
    b.add_argument("--entity-name", help="entity or workspace name, checked for test or QA wording")
    b.add_argument("--currency", default="USD", help="primary currency code (default USD)")
    b.add_argument("--spread", choices=["yes", "no"], default="yes",
                   help="spread multi-month payments over term_months (default yes)")
    b.add_argument("--min-history", type=int, choices=[1, 2, 3], default=2,
                   help="consecutive months before an unlabeled customer counts as recurring (default 2)")
    b.add_argument("--churn-after-months", type=int, choices=[1, 2, 3], default=1,
                   help="months with no revenue before churn; 2 is the 2-month grace option (default 1)")
    b.add_argument("--as-of", help="date the data was read, YYYY-MM-DD (default today)")
    b.add_argument("--renewal-days", type=int, default=60,
                   help="days ahead to list schedules ending (default 60)")
    b.add_argument("--top-n", type=int, default=10, help="customers in the concentration figure (default 10)")
    b.add_argument("--cohort-offsets", default="3,6,9", help="months after start to measure cohorts (default 3,6,9)")
    b.add_argument("--cohort-min-months", type=int, default=9,
                   help="months of history before cohorts are produced (default 9, three quarters)")
    b.add_argument("--cohort-min-customers", type=int, default=5,
                   help="smallest start cohort shown; smaller ones are left out (default 5)")
    b.add_argument("--retention-min-customers", type=int, default=10,
                   help="below this many customers, NRR and GRR are flagged small_sample (default 10)")
    b.add_argument("--break-sd", type=float, default=2.0,
                   help="standard deviations from the mean change that flag a trend break (default 2.0)")
    b.add_argument("--collected", help="optional CSV of money received: customer, month, amount")
    b.add_argument("--money-in", help="optional CSV: month, total_in, uncategorized_in")
    b.add_argument("--unclosed-share", type=float, default=0.15,
                   help="uncategorized share of money in that can flag a month as unclosed (default 0.15)")
    b.add_argument("--unclosed-multiple", type=float, default=2.0,
                   help="times the window median share a month must also reach (default 2.0)")
    b.add_argument("--out-dir", default=".", help="where to write outputs (default current folder)")
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.cmd is None:
        parser.print_help()
        sys.exit(1)
    try:
        if args.cmd == "scan":
            cmd_scan(args)
        else:
            cmd_build(args)
    except InputError as e:
        fail(str(e), 1)
    except BridgeError as e:
        fail("bridge check failed, nothing written: %s" % e, 2)
    except NoCustomerError as e:
        fail(str(e), 3)
    except OSError as e:
        fail("file error: %s" % e, 1)


if __name__ == "__main__":
    main()
