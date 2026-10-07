#!/usr/bin/env python3
"""
pf_assessment.py - deterministic Profit First Instant Assessment calculator.

The model must NOT do this arithmetic itself (house rule: "figures from reads never
model arithmetic"). It pulls the six actual figures from Kick tool responses, confirms
the ledger-to-Profit-First category mapping with the user, then feeds the confirmed
numbers to this script. The script owns every calculation and prints both a readable
table and a machine-readable JSON block.

Method and target percentages: Mike Michalowicz, "Profit First Instant Assessment"
(c) 2008-2014. The Target Allocation Percentages (TAPs) below are documented published
data from that assessment, not tuned constants.

Inputs (six figures, all trailing-12-month actuals in the ledger's currency):
  top_line_revenue          Total income before subtracting materials/subcontractors.
  materials_and_subs        Cost of materials and subcontractors to subtract. 0 for a
                            typical service business (then Real Revenue == Top Line).
  actual_profit             Actual amount held/distributed as profit.
  actual_owners_pay         Actual owner's compensation (draws/salary to owners).
  actual_tax               Actual amount set aside for tax.
  actual_operating_expenses Actual operating expenses (everything else).

Outputs: Real Revenue, the selected TAP bracket, and per allocation account the PF%,
PF$ (target dollars), the Delta (Actual - PF$), and the Fix (Increase / Decrease).

  Real Revenue      = top_line_revenue - materials_and_subs
  PF$  (per row)    = Real Revenue * PF%
  Delta (per row)   = Actual - PF$        (negative = under target, positive = over)
  Fix  (per row)    = "Increase" if Delta < 0, "Decrease" if Delta > 0, "On target" if 0

No network. Standard library only. No external packages.

Usage:
  python3 pf_assessment.py --top-line-revenue 420000 --materials-and-subs 0 \\
      --actual-profit 8000 --actual-owners-pay 150000 --actual-tax 12000 \\
      --actual-operating-expenses 250000

  echo '{"top_line_revenue":420000,"materials_and_subs":0,"actual_profit":8000,
         "actual_owners_pay":150000,"actual_tax":12000,
         "actual_operating_expenses":250000}' | python3 pf_assessment.py --json
"""

from __future__ import annotations

import argparse
import json
import sys

# Target Allocation Percentages by Real Revenue bracket.
# Source: Mike Michalowicz, "Profit First Instant Assessment" (Figure 1), (c) 2008-2014.
# Each bracket: (lower_bound_inclusive, upper_bound_exclusive, {account: fraction}).
# Profit + Owner's Pay + Tax + Operating Expenses = 100% of Real Revenue in every row.
# Boundary rule: the lower bound is inclusive, the upper bound exclusive, so a Real
# Revenue that lands exactly on a boundary (250000 / 500000 / 1000000 / 5000000 /
# 10000000) uses the HIGHER bracket. The top bracket's upper bound is treated as open:
# any Real Revenue at or above 10000000 uses it (see select_bracket).
TAP_TABLE = [
    ("$0-$250K",     0,        250_000,    {"profit": 0.05, "owners_pay": 0.50, "tax": 0.15, "operating_expenses": 0.30}),
    ("$250K-$500K",  250_000,  500_000,    {"profit": 0.10, "owners_pay": 0.35, "tax": 0.15, "operating_expenses": 0.40}),
    ("$500K-$1M",    500_000,  1_000_000,  {"profit": 0.15, "owners_pay": 0.20, "tax": 0.15, "operating_expenses": 0.50}),
    ("$1M-$5M",      1_000_000, 5_000_000, {"profit": 0.10, "owners_pay": 0.10, "tax": 0.15, "operating_expenses": 0.65}),
    ("$5M-$10M",     5_000_000, 10_000_000, {"profit": 0.15, "owners_pay": 0.05, "tax": 0.15, "operating_expenses": 0.65}),
    ("$10M-$50M",    10_000_000, 50_000_000, {"profit": 0.20, "owners_pay": 0.00, "tax": 0.15, "operating_expenses": 0.65}),
]

# Display order and labels for the four allocation accounts.
ACCOUNTS = [
    ("profit", "Profit"),
    ("owners_pay", "Owner's Pay"),
    ("tax", "Tax"),
    ("operating_expenses", "Operating Expenses"),
]


def select_bracket(real_revenue: float):
    """Return (label, tap_fractions, note) for a Real Revenue figure.

    Real Revenue < 0 raises ValueError (materials/subs exceed income - a data error).
    Real Revenue at or above the top bracket's ceiling (50000000) uses the top bracket
    and returns a note stating so, rather than failing.
    """
    if real_revenue < 0:
        raise ValueError(
            "Real Revenue is negative (materials & subs exceed top line revenue). "
            "Recheck the Material & Subs figure before running the assessment."
        )
    for label, lo, hi, taps in TAP_TABLE:
        if lo <= real_revenue < hi:
            return label, taps, None
    # At or above the top ceiling: the assessment table stops at $50M, so use the top row.
    top_label, _, top_hi, top_taps = TAP_TABLE[-1][0], TAP_TABLE[-1][1], TAP_TABLE[-1][2], TAP_TABLE[-1][3]
    note = (
        f"Real Revenue {real_revenue:,.2f} is at or above the published table ceiling "
        f"({top_hi:,.0f}); using the top bracket {top_label}. Above $50M, target "
        "percentages are a professional judgment call - review with the client."
    )
    return top_label, top_taps, note


def assess(top_line_revenue: float, materials_and_subs: float, actual_profit: float,
           actual_owners_pay: float, actual_tax: float,
           actual_operating_expenses: float) -> dict:
    real_revenue = round(top_line_revenue - materials_and_subs, 2)
    bracket_label, taps, note = select_bracket(real_revenue)

    actuals = {
        "profit": actual_profit,
        "owners_pay": actual_owners_pay,
        "tax": actual_tax,
        "operating_expenses": actual_operating_expenses,
    }

    rows = []
    for key, label in ACCOUNTS:
        pf_pct = taps[key]
        pf_dollars = round(real_revenue * pf_pct, 2)
        actual = round(float(actuals[key]), 2)
        delta = round(actual - pf_dollars, 2)
        if delta < 0:
            fix = "Increase"
        elif delta > 0:
            fix = "Decrease"
        else:
            fix = "On target"
        rows.append({
            "account": label,
            "actual": actual,
            "pf_percent": round(pf_pct * 100, 2),
            "pf_dollars": pf_dollars,
            "delta": delta,
            "fix": fix,
        })

    result = {
        "top_line_revenue": round(top_line_revenue, 2),
        "materials_and_subs": round(materials_and_subs, 2),
        "real_revenue": real_revenue,
        "bracket": bracket_label,
        "rows": rows,
    }
    if note:
        result["note"] = note
    return result


def money(x: float) -> str:
    return f"{x:,.2f}"


def render_table(result: dict) -> str:
    lines = []
    lines.append("Profit First Instant Assessment")
    lines.append("Method: Mike Michalowicz, Profit First Instant Assessment (c) 2008-2014.")
    lines.append("")
    lines.append(f"Top Line Revenue   : {money(result['top_line_revenue'])}")
    lines.append(f"Material & Subs    : {money(result['materials_and_subs'])}")
    lines.append(f"Real Revenue       : {money(result['real_revenue'])}")
    lines.append(f"TAP bracket        : {result['bracket']}")
    if "note" in result:
        lines.append(f"Note               : {result['note']}")
    lines.append("")
    header = f"{'Account':<20}{'Actual':>16}{'PF%':>8}{'PF$':>16}{'The Delta':>16}{'The Fix':>12}"
    lines.append(header)
    lines.append("-" * len(header))
    for r in result["rows"]:
        lines.append(
            f"{r['account']:<20}{money(r['actual']):>16}{str(r['pf_percent']) + '%':>8}"
            f"{money(r['pf_dollars']):>16}{money(r['delta']):>16}{r['fix']:>12}"
        )
    lines.append("")
    lines.append("The Delta = Actual - PF$ (negative means below target).")
    lines.append("The Fix   = Increase when the Delta is negative, Decrease when positive.")
    lines.append("Figures come from the ledger reads you fed in; this script only computes targets.")
    return "\n".join(lines)


def parse_args(argv):
    p = argparse.ArgumentParser(
        description="Compute a Profit First Instant Assessment from trailing-12-month "
                    "actuals. Feed figures pulled from Kick reads; the script owns the math.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Percentages: Mike Michalowicz, Profit First Instant Assessment (c) 2008-2014.",
    )
    p.add_argument("--json", action="store_true",
                   help="read the six figures as a JSON object on stdin instead of flags")
    p.add_argument("--top-line-revenue", type=float,
                   help="total income before subtracting materials & subcontractors")
    p.add_argument("--materials-and-subs", type=float, default=0.0,
                   help="cost of materials & subcontractors to subtract (0 for a typical "
                        "service business; then Real Revenue == Top Line)")
    p.add_argument("--actual-profit", type=float, help="actual profit held/distributed")
    p.add_argument("--actual-owners-pay", type=float, help="actual owner's compensation")
    p.add_argument("--actual-tax", type=float, help="actual amount set aside for tax")
    p.add_argument("--actual-operating-expenses", type=float,
                   help="actual operating expenses")
    p.add_argument("--pretty", action="store_true",
                   help="print only the readable table (omit the JSON block)")
    return p.parse_args(argv)


def main(argv) -> int:
    args = parse_args(argv)

    if args.json:
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"error: could not parse JSON on stdin: {e}", file=sys.stderr)
            return 2
        fields = ("top_line_revenue", "materials_and_subs", "actual_profit",
                  "actual_owners_pay", "actual_tax", "actual_operating_expenses")
        missing = [f for f in fields if f not in data]
        if missing:
            print(f"error: JSON is missing required field(s): {missing}", file=sys.stderr)
            return 2
        kwargs = {f: float(data[f]) for f in fields}
    else:
        required = {
            "top_line_revenue": args.top_line_revenue,
            "actual_profit": args.actual_profit,
            "actual_owners_pay": args.actual_owners_pay,
            "actual_tax": args.actual_tax,
            "actual_operating_expenses": args.actual_operating_expenses,
        }
        missing = [name for name, val in required.items() if val is None]
        if missing:
            print("error: missing required figure(s): "
                  + ", ".join("--" + m.replace("_", "-") for m in missing)
                  + "\n(or pass --json and pipe a JSON object on stdin; see --help)",
                  file=sys.stderr)
            return 2
        kwargs = {
            "top_line_revenue": args.top_line_revenue,
            "materials_and_subs": args.materials_and_subs,
            "actual_profit": args.actual_profit,
            "actual_owners_pay": args.actual_owners_pay,
            "actual_tax": args.actual_tax,
            "actual_operating_expenses": args.actual_operating_expenses,
        }

    try:
        result = assess(**kwargs)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    print(render_table(result))
    if not args.pretty:
        print()
        print("JSON:")
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
