#!/usr/bin/env python3
"""
build_dashboard.py: one-page HTML MRR dashboard from mrr_build.py output.

Reads the mrr_report.json that `mrr_build.py build` wrote, composes the dashboard
payload, and injects it into references/templates/dashboard.html. The page renders every
figure from that payload, so no figure on it is typed by hand. Sections without data
(plans or classes, cohorts, renewals, retention) are left out of the payload and the page
drops them. Every active customer is listed when there are 25 or fewer. Standard library only. The output opens offline: inline CSS, inline SVG, no
network calls.

Usage
  python3 build_dashboard.py --report out/mrr_report.json \
      --entity "Northwind Analytics Inc." --plan Advanced \
      --definitions "Recurring revenue: 4010 Subscription revenue. Annual payments spread over their term. Churn after 1 month without revenue." \
      [--gaps gaps.json] [--generated 2026-10-08] [--chart-months 6] [--out-dir .]

gaps.json is a list of objects, in the order the report lists its gaps:
  {"text": "deposits in September have no customer and are left out", "from": "excluded.no_customer_latest"}
  {"text": "annual invoices have no schedule", "amount": "6 · $28,800"}
"from" fills the amount from the report JSON. Keys: excluded.no_customer,
excluded.no_customer_latest, excluded.one_time, excluded.below_min_history,
excluded.other_currency, cadence.unconfirmed. A literal "amount" must be copied unchanged
from a data read (for example the count and total of revenue recognition candidates).

Exit codes: 0 success, 1 bad input.
"""

import argparse
import json
import os
import re
import sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

PLACEHOLDER = "__MRR_DASHBOARD_PAYLOAD__"
MONTH_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_LONG = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
SYMBOLS = {"USD": "$", "EUR": "\u20ac", "GBP": "\u00a3", "CAD": "CA$", "AUD": "A$",
           "NZD": "NZ$", "ILS": "\u20aa", "JPY": "\u00a5"}
CLASS_COLORS = ["#2f6bff", "#14b8a6", "#f59e0b", "#9db8ff", "#dc2626", "#64748b"]
SERIES = [("new", "New", "#2f6bff"), ("expansion", "Expansion", "#14b8a6"),
          ("reactivation", "Reactivation", "#9db8ff"),
          ("contraction", "Contraction", "#f59e0b"), ("churn", "Churn", "#dc2626")]
LEGAL_SUFFIXES = {"inc", "llc", "ltd", "limited", "corp", "corporation", "co", "company",
                  "plc", "gmbh", "pty", "llp", "lp"}


class InputError(Exception):
    pass


def fail(msg):
    sys.stderr.write("build_dashboard: %s\n" % msg)
    sys.exit(1)


def fmt_money(v, sym, signed=False):
    if v is None:
        return "n/a"
    d = Decimal(str(v)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    body = sym + "{:,}".format(abs(int(d)))
    if d < 0:
        return "-" + body
    return ("+" + body) if signed and d > 0 else body


def fmt_pct(v, signed=False):
    if v is None:
        return "n/a"
    text = ("%s" % v).rstrip("0").rstrip(".") if "." in str(v) else str(v)
    if signed and v > 0:
        text = "+" + text
    return text + "%"


def short_month(ym, with_year):
    y, m = int(ym[:4]), int(ym[5:7])
    return MONTH_SHORT[m - 1] + (" %02d" % (y % 100) if with_year else "")


def long_period(ym):
    return "%s %s" % (MONTH_LONG[int(ym[5:7]) - 1], ym[:4])


def slugify(entity):
    tokens = re.sub(r"[^a-z0-9]+", " ", entity.lower()).split()
    while tokens and tokens[-1] in LEGAL_SUFFIXES:
        tokens.pop()
    slug = "-".join(tokens)[:60].strip("-")
    return slug or "entity"


def require(obj, key, where):
    if key not in obj:
        raise InputError("%s is missing '%s'; was it written by mrr_build.py build?" % (where, key))
    return obj[key]


def gap_amount(report, key, sym):
    ex = report.get("excluded", {})
    if key == "excluded.no_customer":
        e = ex["no_customer"]
        return "%d · %s" % (e["window_rows"], fmt_money(e["window_total"], sym))
    if key == "excluded.no_customer_latest":
        e = ex["no_customer"]
        return "%d · %s" % (e["latest_rows"], fmt_money(e["latest_total"], sym))
    if key in ("excluded.one_time", "excluded.below_min_history"):
        e = ex[key.split(".")[1]]
        return "%d · %s" % (e["customers"], fmt_money(e["window_total"], sym))
    if key == "excluded.other_currency":
        parts = ["%d · %s/mo" % (e["customers"],
                                 fmt_money(e["latest_mrr"], SYMBOLS.get(e["currency"], e["currency"] + " ")))
                 for e in ex.get("other_currency", [])]
        return "; ".join(parts) if parts else "0"
    if key == "cadence.unconfirmed":
        rows = report.get("unconfirmed", [])
        total = sum((Decimal(str(r["window_total"])) for r in rows), Decimal("0"))
        return "%d · %s" % (len(rows), fmt_money(total, sym))
    raise InputError("unknown gap key '%s'" % key)


def load_gaps(path, report, sym):
    if not path:
        return []
    if not os.path.isfile(path):
        raise InputError("gaps file not found: %s" % path)
    with open(path, encoding="utf-8") as fh:
        try:
            items = json.load(fh)
        except ValueError as e:
            raise InputError("gaps file is not valid JSON: %s" % e)
    if not isinstance(items, list):
        raise InputError("gaps file must hold a JSON list")
    out = []
    for i, g in enumerate(items, start=1):
        if not isinstance(g, dict) or not isinstance(g.get("text"), str) or not g["text"].strip():
            raise InputError("gap %d needs a non-empty text" % i)
        if "from" in g:
            amount = gap_amount(report, g["from"], sym)
        elif isinstance(g.get("amount"), str):
            amount = g["amount"]
        else:
            raise InputError("gap %d needs either 'from' or a string 'amount'" % i)
        out.append({"text": g["text"].strip()[:300], "amount": amount[:60]})
    return out


def compose(report, args):
    meta = require(report, "meta", "report")
    summary = require(report, "summary", "report")
    kpis = require(report, "kpis", "report")
    trend = require(report, "trend", "report")
    movements = require(report, "movements", "report")
    currency = meta.get("currency", "USD")
    sym = SYMBOLS.get(currency, currency + " ")
    prior = summary["prior"]
    plab = MONTH_SHORT[int(prior["month"][5:7]) - 1]

    def tone(v, good_when_up=True):
        if v is None or v == 0:
            return "mut"
        return "pos" if (v > 0) == good_when_up else "neg"

    shares = report.get("source_share", [])
    parts = []
    for i, s in enumerate(shares):
        label = s["label"] if i == 0 else s["label"][0].lower() + s["label"][1:]
        tail = "%s%% of MRR" % s["share_pct"] if i == 0 else "%s%%" % s["share_pct"]
        parts.append("%s for %d customers (%s)" % (label, s["customers"], tail))
    source = "Plan: %s. " % args.plan if args.plan else ""
    if parts:
        source += ", ".join(parts) + ". "
    if args.definitions.strip():
        source += args.definitions.strip().rstrip(".") + ". "
    source += "Management metric, not GAAP revenue."

    hero = [
        {"label": "MRR", "value": summary["mrr"], "fmt": "money",
         "delta": "%s vs %s" % (fmt_pct(summary["mrr_change_pct"], True), plab),
         "tone": tone(summary["mrr_change_pct"])},
        {"label": "ARR", "value": summary["arr"], "fmt": "money",
         "delta": "%s vs %s" % (fmt_money(summary["arr_change"], sym, True), plab),
         "tone": tone(summary["arr_change"])},
        {"label": "Net new MRR", "value": summary["net_new"], "fmt": "money",
         "delta": "%s: %s" % (plab, fmt_money(prior["net_new"], sym)) if prior.get("net_new") is not None else "",
         "tone": tone(summary["net_new"])},
    ]
    ret = report.get("retention") or {}
    if ret.get("available"):
        hero.append({"label": "Net revenue retention", "value": fmt_pct(ret["nrr_pct"]), "fmt": "raw",
                     "delta": "12 months, %d customers%s" % (ret["cohort_size"],
                                                             ", small sample" if ret.get("small_sample") else ""),
                     "tone": "mut"})

    cur_k, prv_k = kpis["current"], kpis.get("prior") or {}
    strip = [
        {"label": "Customers", "value": str(summary["customers"]),
         "delta": "%+d vs %s" % (summary["customers_change"], plab),
         "tone": tone(summary["customers_change"])},
        {"label": "ARPA", "value": fmt_money(summary["arpa"], sym),
         "delta": "%s vs %s" % (fmt_money(summary["arpa_change"], sym, True), plab),
         "tone": tone(summary["arpa_change"])},
    ]
    if cur_k.get("logo_churn_pct") is not None:
        strip.append({"label": "Logo churn", "value": fmt_pct(cur_k["logo_churn_pct"]),
                      "delta": "%s: %s" % (plab, fmt_pct(prv_k.get("logo_churn_pct"))),
                      "tone": tone(kpis["change"].get("logo_churn_pct"), good_when_up=False)})
    if ret.get("available"):
        strip.append({"label": "Gross revenue retention", "value": fmt_pct(ret["grr_pct"]),
                      "delta": "12 months", "tone": "mut"})
    if cur_k.get("quick_ratio") is not None:
        strip.append({"label": "Quick ratio", "value": "%.1f" % cur_k["quick_ratio"],
                      "delta": "%s: %s" % (plab, "%.1f" % prv_k["quick_ratio"]
                                           if prv_k.get("quick_ratio") is not None else "n/a"),
                      "tone": tone(kpis["change"].get("quick_ratio"))})

    k = max(1, min(args.chart_months, len(trend)))
    t_rows = trend[-k:]
    with_year = len({t["month"][:4] for t in t_rows}) > 1 and k > 12
    trend_out = {"months": [short_month(t["month"], with_year) for t in t_rows],
                 "mrr": [t["mrr"] for t in t_rows]}

    b = report["bridge_latest"]
    steps = [{"label": b["opening_label"][:3], "value": b["opening"], "kind": "total"}]
    for st in b["steps"]:
        steps.append({"label": st["kind"].capitalize(), "value": st["amount"],
                      "kind": "up" if st["kind"] in ("new", "expansion", "reactivation") else "down"})
    steps.append({"label": short_month(b["month"], False), "value": b["closing"], "kind": "total"})
    bridge = {"title": "%s MRR bridge" % MONTH_LONG[int(b["month"][5:7]) - 1], "steps": steps}

    mv_rows = movements[-max(k - 1, 1):]
    movements_out = None
    if len(mv_rows) >= 2:
        movements_out = {"months": [short_month(m["month"], with_year) for m in mv_rows],
                         "series": [{"name": name, "color": color,
                                     "values": [m[key] for m in mv_rows]}
                                    for key, name, color in SERIES]}

    classes = None
    key = "plan" if report.get("plans") else "class"
    rc = [c for c in (report.get("plans") or report.get("classes") or []) if c["mrr"] > 0]
    if rc and not (len(rc) == 1 and rc[0][key] in ("Unclassified", "No plan named")):
        classes = [{"name": c[key], "mrr": c["mrr"], "customers": c["customers"],
                    "color": CLASS_COLORS[i % len(CLASS_COLORS)]} for i, c in enumerate(rc)]

    conc = report.get("concentration", {})
    active = [r for r in report.get("customers") or [] if r["mrr"] > 0]
    show_all = 0 < len(active) <= args.list_all_up_to

    def move_label(r):
        if r["change"] and r["status"] in ("Upgraded", "Downgraded"):
            return "%s %s" % (r["status"], fmt_money(r["change"], sym, True))
        return "No change" if r["status"] == "Active" else r["status"]

    customers = None
    rows = active if show_all else active[:5]
    if rows:
        note = ""
        if show_all:
            note = "All %d active customers." % len(active)
        elif conc.get("top_n_share_pct") is not None:
            note = "Top %d customers: %s of MRR." % (conc["top_n"], fmt_pct(round(conc["top_n_share_pct"])))
        if conc.get("top_customer_share_pct") and conc["top_customer_share_pct"] >= 25:
            note += " %s alone is %s of MRR." % (conc["top_customer"], fmt_pct(conc["top_customer_share_pct"]))
        customers = {"rows": [{"name": r["customer"] + (" (%s)" % r["plan"] if r.get("plan") and r["customer"].lower() not in r["plan"].lower() else ""),
                               "mrr": r["mrr"], "move": move_label(r)} for r in rows],
                     "total": summary["mrr"], "note": note.strip(),
                     "title": "Customers" if show_all else "Top customers",
                     "month": MONTH_LONG[int(summary["month"][5:7]) - 1]}

    cohorts = None
    rco = report.get("cohorts")
    if rco and rco.get("rows"):
        cohorts = {"cols": ["Month %d" % o for o in rco["offsets"]],
                   "rows": [{"name": r["label"], "customers": r["customers"], "start": r["start_mrr"],
                             "values": r["values"]} for r in rco["rows"]]}

    renewals = None
    rr = report.get("renewals")
    if rr and rr.get("rows"):
        renewals = {"rows": [{"name": r["customer"], "mrr": r["mrr"], "ends": r["ends"]} for r in rr["rows"]],
                    "note": "%d %s up for renewal in the next %d days: %s of MRR."
                            % (rr["count"], "customer is" if rr["count"] == 1 else "customers are",
                               rr["window_days"], fmt_money(rr["mrr"], sym))}

    period = long_period(meta["end_month"])
    if meta.get("end_partial"):
        period = "%s, month to date" % period
    return {
        "entity": args.entity, "period": period,
        "generated": args.generated, "data_source": args.source_name, "currency": currency, "symbol": sym,
        "source": source, "hero": hero, "strip": strip, "trend": trend_out,
        "bridge": bridge, "movements": movements_out, "classes": classes,
        "customers": customers, "cohorts": cohorts, "renewals": renewals,
        "gaps": load_gaps(args.gaps, report, sym),
        "data_quality": data_quality_banner(report, sym),
    }


def data_quality_banner(report, sym):
    dq = report.get("data_quality") or {}
    if not dq.get("fires"):
        return None
    cov = report.get("coverage") or {}
    parts = list(dq.get("reasons") or [])
    if cov.get("no_customer_total"):
        parts.append("%s of revenue in the window has no customer" % fmt_money(cov["no_customer_total"], sym))
    return {"title": "Test or incomplete data",
            "text": "; ".join(parts) + ". The figures below may not describe the business."}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    p = argparse.ArgumentParser(description="Build the one-page MRR dashboard from mrr_build.py output.")
    p.add_argument("--report", required=True, help="mrr_report.json from mrr_build.py build")
    p.add_argument("--entity", required=True, help="business or entity name, as the user calls it")
    p.add_argument("--plan", default="", help="Kick workspace plan, for the source line; leave out for other sources")
    p.add_argument("--source-name", default="Kick",
                   help="where the data came from, for the footer (default Kick; e.g. \"a Stripe export\")")
    p.add_argument("--definitions", default="",
                   help="the user's chosen definitions in words (accounts, spreading, churn rule)")
    p.add_argument("--gaps", help="JSON list of gaps (see the header of this file)")
    p.add_argument("--generated", default=date.today().isoformat(),
                   help="date the data was read, YYYY-MM-DD (default today)")
    p.add_argument("--list-all-up-to", type=int, default=25,
                   help="list every active customer when there are this many or fewer (default 25)")
    p.add_argument("--chart-months", type=int, default=6,
                   help="months shown in the trend chart (default 6, as in the template look)")
    p.add_argument("--template", default=os.path.join(here, "..", "references", "templates", "dashboard.html"))
    p.add_argument("--out-dir", default=".", help="where to write the HTML file")
    args = p.parse_args()
    try:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", args.generated):
            raise InputError("--generated must be YYYY-MM-DD")
        if not args.entity.strip():
            raise InputError("--entity is empty")
        with open(args.report, encoding="utf-8") as fh:
            try:
                report = json.load(fh)
            except ValueError as e:
                raise InputError("report is not valid JSON: %s" % e)
        with open(args.template, encoding="utf-8") as fh:
            template = fh.read()
        if template.count(PLACEHOLDER) != 1:
            raise InputError("template must contain %s exactly once" % PLACEHOLDER)
        payload = compose(report, args)
        # Escape so untrusted names can never close the script tag or open markup.
        blob = (json.dumps(payload, ensure_ascii=False)
                .replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
                .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))
        page = template.replace(PLACEHOLDER, blob)
        os.makedirs(args.out_dir, exist_ok=True)
        name = "%s-mrr-dashboard-%s.html" % (slugify(args.entity), report["meta"]["end_month"])
        path = os.path.join(args.out_dir, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(page)
    except InputError as e:
        fail(str(e))
    except (KeyError, TypeError, ValueError) as e:
        fail("report JSON has an unexpected shape (%s); rebuild it with mrr_build.py build" % e)
    except OSError as e:
        fail("file error: %s" % e)
    print(path)


if __name__ == "__main__":
    main()
