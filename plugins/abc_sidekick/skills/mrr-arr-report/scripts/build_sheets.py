#!/usr/bin/env python3
"""Build the live Google Sheets MRR report for one entity.

Usage:
  python3 build_sheets.py --config sheets_config.json --out-dir <dir> [--emit-payloads]
      [--spreadsheet spreadsheet.json | --sheet-ids existing_ids.json] [--chunk-bytes 60000]

--spreadsheet is a spreadsheets.get response with
sheets(properties(sheetId,title,index),charts(chartId),protectedRanges(protectedRangeId),conditionalFormats).
It supplies the ids of existing MRR tabs and what on them to clear, so a rebuild replaces
charts, protections, and color rules instead of adding copies.

Writes, from references/templates/sheets_plan.json:
  <slug>-mrr-sheet-plan.json       the filled plan: every tab, formula, format, and chart
  <slug>-mrr-sheets-installer.gs   the same plan as a paste-once Apps Script
  payloads/                        with --emit-payloads: Sheets API request bodies to send
                                   verbatim, in order (see sheets_payloads.py)

The build fails before writing anything when the formula lint (sheets_lint.py) finds a
problem.

Config shape (every source is optional; at least one is required):
  {
    "entity": "Acme Inc",
    "firstMonth": "2026-01-01",
    "includeCurrentMonth": true,
    "currency": "USD",
    "basis": "cash" | "accrual",
    "sources": {
      "ledger": {"tab": "Acme Inc - General Ledger", "revenueAccounts": ["400000 - Revenue"],
                 "statedFrom": "2026-01-01", "statedTo": "2026-09-30"},
      "waterfall": {"tab": "Acme Inc - Revenue Waterfall", "grouping": "By schedule"},
      "rollforward": {"tab": "Acme Inc - Revenue Rollforward", "grouping": "By schedule"},
      "userTable": {"tab": "Stripe invoices", "headers": ["Customer", "Date", "Amount"],
                    "columns": {"customer": "Customer", "date": "Date", "amount": "Amount",
                                "plan": "", "months": ""}}
    },
    "tabsFound": [{"name": "Acme Inc - Balance Sheet", "kind": "Kick report",
                   "report": "Balance Sheet", "used": "No"}],
    "accelMultiple": 3, "gapDays": 31, "minCoverage": 0.8,
    "sourceRows": 1840,
    "rules": [{"pattern": "plus quarterly", "plan": "Plus", "months": 3, "recurring": true}],
    "overrides": [{"customer": "Northgate", "exclude": true}],
    "skipDefaultRules": false
  }
The older shape with top-level "glTab" and "revenueAccounts" still works.

"sourceRows" is the total row count of the source tabs used. "MRR inputs" and "MRR rows"
hold one row per source line, so they get max(1000, 2 x sourceRows + 100) rows.

Rules are case-insensitive RE2 regexes matched against the ledger description (or the
user table's plan column); the first match wins. Overrides match the customer exactly
and beat rules.
"""

import argparse
import copy
import json
import re
import sys
from pathlib import Path

from sheets_lint import lint_plan
from sheets_payloads import DEFAULT_ROWS, emit_payloads, existing_from_spreadsheet

TEMPLATES = Path(__file__).resolve().parent.parent / "references" / "templates"
PLAN_TEMPLATE = TEMPLATES / "sheets_plan.json"
APPLIER_TEMPLATE = TEMPLATES / "sheets_applier.gs"
PLAN_PLACEHOLDER = "__MRR_SHEET_PLAN__"
GROUPINGS = ("By schedule", "By customer")

DEFAULT_RULES = [
    {"pattern": r"\b(setup|set-up|implementation|onboarding)\b", "plan": "One-time", "months": 1, "recurring": False},
    {"pattern": r"\bmonthly\b", "plan": "Monthly", "months": 1, "recurring": True},
    {"pattern": r"\bquarterly\b", "plan": "Quarterly", "months": 3, "recurring": True},
    {"pattern": r"\b(annual|yearly)\b", "plan": "Annual", "months": 12, "recurring": True},
]


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def require_str(config, key):
    value = config.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(f"'{key}' must be a non-empty string")
    return value.strip()


def optional_str(config, key):
    value = config.get(key) or ""
    if not isinstance(value, str):
        fail(f"'{key}' must be a string")
    return value.strip()


def require_months(value, label):
    if not isinstance(value, int) or isinstance(value, bool) or value < 1 or value > 36:
        fail(f"{label} must be an integer from 1 to 36")
    return value


def optional_date(config, key):
    value = optional_str(config, key)
    if value and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        fail(f"'{key}' must be YYYY-MM-DD")
    return value


def validate_rule(rule, index):
    if not isinstance(rule, dict):
        fail(f"rules[{index}] must be an object")
    pattern = rule.get("pattern")
    if not isinstance(pattern, str) or not pattern:
        fail(f"rules[{index}].pattern must be a non-empty string")
    try:
        re.compile(pattern)
    except re.error as error:
        fail(f"rules[{index}].pattern is not a valid regex: {error}")
    if re.search(r"\(\?[=!<]", pattern):
        fail(f"rules[{index}].pattern uses lookarounds, which Google Sheets (RE2) doesn't support")
    return {
        "pattern": pattern,
        "plan": str(rule.get("plan") or "Unlabeled"),
        "months": require_months(rule.get("months", 1), f"rules[{index}].months"),
        "recurring": bool(rule.get("recurring", True)),
    }


def validate_override(override, index):
    if not isinstance(override, dict) or not isinstance(override.get("customer"), str):
        fail(f"overrides[{index}] must be an object with a 'customer' string")
    months = override.get("months")
    return {
        "customer": override["customer"],
        "plan": override.get("plan") or "",
        "months": "" if months is None else require_months(months, f"overrides[{index}].months"),
        "reportAs": override.get("reportAs") or "",
        "exclude": bool(override.get("exclude", False)),
    }


def accrual_rules(rules):
    return [
        {**rule, "pattern": rf"^Revenue recognition schedule:.*(?:{rule['pattern']})", "months": 1}
        for rule in rules
        if rule["recurring"]
    ]


def grouping(source, key):
    value = source.get("grouping", "By schedule")
    if value not in GROUPINGS:
        fail(f"sources.{key}.grouping must be one of {', '.join(GROUPINGS)}")
    return value


def build_sources(raw):
    sources = dict(raw.get("sources") or {})
    if "glTab" in raw and "ledger" not in sources:
        sources["ledger"] = {"tab": raw["glTab"], "revenueAccounts": raw.get("revenueAccounts")}
    ledger = sources.get("ledger") or {}
    waterfall = sources.get("waterfall") or {}
    rollforward = sources.get("rollforward") or {}
    table = sources.get("userTable") or {}
    if not any(s.get("tab") for s in (ledger, waterfall, table)):
        fail("name at least one revenue source tab: sources.ledger, sources.waterfall, or sources.userTable")
    accounts = ledger.get("revenueAccounts") or []
    if ledger.get("tab"):
        if not isinstance(accounts, list) or not accounts or not all(isinstance(a, str) and a for a in accounts):
            fail("sources.ledger.revenueAccounts must be a non-empty list of account labels")
        if any("," in account for account in accounts):
            fail("account labels can't contain commas; the settings tab stores them comma-separated")
    columns = table.get("columns") or {}
    if table.get("tab") and not all(columns.get(k) for k in ("customer", "date", "amount")):
        fail("sources.userTable.columns needs customer, date, and amount header names")
    return {
        "ledger": {"tab": optional_str(ledger, "tab"), "accounts": accounts,
                   "from": optional_date(ledger, "statedFrom"), "to": optional_date(ledger, "statedTo")},
        "waterfall": {"tab": optional_str(waterfall, "tab"), "grouping": grouping(waterfall, "waterfall")},
        "rollforward": {"tab": optional_str(rollforward, "tab"), "grouping": grouping(rollforward, "rollforward")},
        "userTable": {"tab": optional_str(table, "tab"), "headers": [str(h) for h in table.get("headers") or []],
                      "columns": {k: str(columns.get(k) or "") for k in ("customer", "date", "amount", "plan", "months")}},
    }


def build_config(raw, plan):
    first_month = require_str(raw, "firstMonth")
    if not re.fullmatch(r"\d{4}-\d{2}-01", first_month):
        fail("'firstMonth' must be the first day of a month, as YYYY-MM-01")
    basis = raw.get("basis", "cash")
    if basis not in ("cash", "accrual"):
        fail("'basis' must be 'cash' or 'accrual'")
    sources = build_sources(raw)

    rules = [validate_rule(rule, i) for i, rule in enumerate(raw.get("rules", []))]
    if not raw.get("skipDefaultRules"):
        rules += DEFAULT_RULES
    if basis == "accrual":
        rules = accrual_rules(rules) + rules
    limits = plan["settings"]
    if len(rules) > limits["ruleRows"]:
        fail(f"{len(rules)} plan rules; the settings tab holds {limits['ruleRows']}")
    overrides = [validate_override(o, i) for i, o in enumerate(raw.get("overrides", []))]
    if len(overrides) > limits["overrideRows"]:
        fail(f"{len(overrides)} overrides; the settings tab holds {limits['overrideRows']}")

    accel = raw.get("accelMultiple", 3)
    gap = raw.get("gapDays", 31)
    coverage = raw.get("minCoverage", 0.8)
    if not (isinstance(accel, (int, float)) and accel > 1):
        fail("'accelMultiple' must be a number above 1")
    if not (isinstance(gap, int) and gap >= 0):
        fail("'gapDays' must be a whole number, 0 or more")
    if not (isinstance(coverage, (int, float)) and 0 <= coverage <= 1):
        fail("'minCoverage' must be a share from 0 to 1")
    source_rows = raw.get("sourceRows", 0)
    if not (isinstance(source_rows, int) and source_rows >= 0):
        fail("'sourceRows' must be a whole number, 0 or more")
    tabs_found = raw.get("tabsFound") or []
    if not all(isinstance(t, dict) and isinstance(t.get("name"), str) for t in tabs_found):
        fail("'tabsFound' must be a list of objects with a 'name'")

    return {
        "entity": require_str(raw, "entity"),
        "firstMonth": first_month,
        "includeCurrentMonth": bool(raw.get("includeCurrentMonth", False)),
        "currency": raw.get("currency", "USD"),
        "basis": basis,
        "sources": sources,
        "tabsFound": tabs_found,
        "accelMultiple": accel, "gapDays": gap, "minCoverage": coverage,
        "sourceRows": source_rows,
        "rules": rules,
        "overrides": overrides,
    }


def as_text(value):
    """Keep sheet data from being read as a formula when written as USER_ENTERED."""
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@"):
        return "'" + value
    return value


def fill_tokens(node, tokens):
    if isinstance(node, str):
        for token, value in tokens.items():
            node = node.replace(token, value)
        return node
    if isinstance(node, list):
        return [fill_tokens(item, tokens) for item in node]
    if isinstance(node, dict):
        return {key: fill_tokens(value, tokens) for key, value in node.items()}
    return node


def tab_by_name(plan, name):
    return next(tab for tab in plan["tabs"] if tab["name"] == name)


def resolve_lists(plan, config):
    detected = sorted({t["name"] for t in config["tabsFound"]}
                      | {s["tab"] for s in config["sources"].values() if s.get("tab")})
    lists = {"tabs": detected, "userTableHeaders": config["sources"]["userTable"]["headers"]}
    for tab in plan["tabs"]:
        kept = []
        for v in tab.get("validations", []):
            if "listFrom" in v:
                values = lists.get(v.pop("listFrom"), [])
                if not values:
                    continue
                v["list"] = values
            kept.append(v)
        tab["validations"] = kept


def build_plan(template, config):
    src = config["sources"]
    cols = src["userTable"]["columns"]
    tokens = {
        "{{ENTITY}}": config["entity"],
        "{{GL_TAB}}": src["ledger"]["tab"],
        "{{GL_FROM}}": src["ledger"]["from"],
        "{{GL_TO}}": src["ledger"]["to"],
        "{{WF_TAB}}": src["waterfall"]["tab"],
        "{{WF_GROUPING}}": src["waterfall"]["grouping"],
        "{{RF_TAB}}": src["rollforward"]["tab"],
        "{{RF_GROUPING}}": src["rollforward"]["grouping"],
        "{{UT_TAB}}": src["userTable"]["tab"],
        "{{UT_CUSTOMER}}": cols["customer"], "{{UT_DATE}}": cols["date"], "{{UT_AMOUNT}}": cols["amount"],
        "{{UT_PLAN}}": cols["plan"], "{{UT_MONTHS}}": cols["months"],
        "{{REVENUE_ACCOUNTS}}": ", ".join(src["ledger"]["accounts"]),
        "{{FIRST_MONTH}}": config["firstMonth"],
        "{{INCLUDE_CURRENT_MONTH}}": "Yes" if config["includeCurrentMonth"] else "No",
        "{{CURRENCY}}": config["currency"],
        "{{BASIS}}": config["basis"],
        "{{ACCEL_MULTIPLE}}": str(config["accelMultiple"]),
        "{{GAP_DAYS}}": str(config["gapDays"]),
        "{{MIN_COVERAGE}}": str(config["minCoverage"]),
    }
    plan = fill_tokens(copy.deepcopy(template), {k: as_text(v) for k, v in tokens.items()})
    resolve_lists(plan, config)
    for tab in plan["tabs"]:
        if tab.pop("rowsFollowSource", False):
            tab["rowCount"] = max(DEFAULT_ROWS, 2 * config["sourceRows"] + 100)
    settings = tab_by_name(plan, "MRR settings")
    if config["rules"]:
        settings["writes"].append({
            "range": plan["settings"]["rulesStart"],
            "values": [
                [as_text(r["pattern"]), as_text(r["plan"]), r["months"], "Yes" if r["recurring"] else "No"]
                for r in config["rules"]
            ],
        })
    if config["overrides"]:
        settings["writes"].append({
            "range": plan["settings"]["overridesStart"],
            "values": [
                [as_text(o["customer"]), as_text(o["plan"]), o["months"], as_text(o["reportAs"]), "Yes" if o["exclude"] else ""]
                for o in config["overrides"]
            ],
        })
    if config["tabsFound"]:
        tab_by_name(plan, "MRR sources")["writes"].append({
            "range": "A26",
            "values": [[as_text(t["name"]), t.get("kind", ""), t.get("report", ""), t.get("used", "")]
                       for t in config["tabsFound"]],
        })
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", json.dumps(plan))
    if leftover:
        fail(f"unfilled tokens in the plan: {sorted(set(leftover))}")
    return plan


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--emit-payloads", action="store_true",
                        help="also write Sheets API request bodies under <out-dir>/payloads")
    existing_src = parser.add_mutually_exclusive_group()
    existing_src.add_argument("--spreadsheet", help="spreadsheets.get response; existing MRR tabs are "
                                                    "reused and their charts, protections, and color rules replaced")
    existing_src.add_argument("--sheet-ids", help="JSON object of existing tab name to sheetId (or the full "
                                                  "entry); those tabs are reused instead of added")
    parser.add_argument("--chunk-bytes", type=int, default=60000,
                        help="largest payload file in bytes (default 60000)")
    args = parser.parse_args()

    template = json.loads(PLAN_TEMPLATE.read_text())
    config = build_config(json.loads(Path(args.config).read_text()), template)
    plan = build_plan(template, config)
    problems = lint_plan(plan)
    if problems:
        fail("formula lint failed, nothing written:\n  " + "\n  ".join(problems))

    applier = APPLIER_TEMPLATE.read_text()
    if applier.count(PLAN_PLACEHOLDER) != 1:
        fail(f"applier template must contain {PLAN_PLACEHOLDER} exactly once")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(config["entity"])
    plan_path = out_dir / f"{slug}-mrr-sheet-plan.json"
    installer_path = out_dir / f"{slug}-mrr-sheets-installer.gs"
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
    installer_path.write_text(applier.replace(PLAN_PLACEHOLDER, json.dumps(plan, indent=2, ensure_ascii=False)))

    summary = {
        "plan": str(plan_path),
        "installer": str(installer_path),
        "tabs": [tab["name"] for tab in plan["tabs"]],
        "writes": sum(len(tab.get("writes", [])) for tab in plan["tabs"]),
        "charts": sum(len(tab.get("charts", [])) for tab in plan["tabs"]),
        "rules": len(config["rules"]),
        "overrides": len(config["overrides"]),
        "sources": {k: v["tab"] for k, v in config["sources"].items() if v.get("tab")},
        "lint": "clean",
    }
    if args.emit_payloads:
        if args.spreadsheet:
            existing = existing_from_spreadsheet(json.loads(Path(args.spreadsheet).read_text()), plan)
        else:
            existing = json.loads(Path(args.sheet_ids).read_text()) if args.sheet_ids else {}
        summary["payloads"] = emit_payloads(plan, out_dir / "payloads", existing, args.chunk_bytes)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
