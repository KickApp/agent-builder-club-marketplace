"""
mrr_quality.py: data rules shared by mrr_build.py scan and build.

  NameMerger          merges names that are identical after trimming, collapsing spaces,
                      and case-folding ("Acme" and "acme " are one customer).
  adjust_schedules    rule C9: a stopped schedule that recognizes the rest at once, and a
                      reversal month, both use the customer's run-rate instead.
  coverage_and_gate   share of revenue assigned to customers, and the data-quality gate
                      (test or QA names, low coverage, mostly unassigned revenue).

Standard library only. references/mrr-method.md documents every rule and default.
"""

import re
from collections import defaultdict
from decimal import Decimal

D0 = Decimal("0")
TEST_NAME_RE = re.compile(r"\b(test(ing|s)?\d*|qa|dummy)\b", re.IGNORECASE)
REVERSAL_RE = re.compile(r"revers|go[- ]?live|true[- ]?up|catch[- ]?up adjust", re.IGNORECASE)


PROCESSORS = ("stripe", "paypal", "square", "shopify", "braintree", "adyen", "gocardless")
PAYOUT_RE = re.compile(r"\b(%s)\b.*\b(deposit|payout|transfer)\b|\bpayout\b|deposit for period ending"
                       % "|".join(PROCESSORS), re.IGNORECASE)


def is_payout(customer, description):
    """A processor payout bundles many customers' payments; it is never one customer."""
    name = " ".join((customer or "").split()).casefold()
    is_processor = name in PROCESSORS or name in {p + " payments" for p in PROCESSORS}
    return is_processor or bool(PAYOUT_RE.search(description or ""))


def canonical_name(name):
    return " ".join((name or "").split()).casefold()


class NameMerger:
    """First spelling seen is the display name; later variants map onto it."""

    def __init__(self):
        self.display = {}
        self.variants = defaultdict(set)

    def name(self, raw):
        cleaned = " ".join((raw or "").split())
        if not cleaned:
            return ""
        key = cleaned.casefold()
        self.display.setdefault(key, cleaned)
        self.variants[key].add(raw)
        return self.display[key]

    def merged(self):
        return [{"name": self.display[k], "variants": sorted(v)}
                for k, v in sorted(self.variants.items()) if len(v) > 1]


def is_reversal_text(text):
    return bool(REVERSAL_RE.search(text or ""))


def adjust_schedules(grid, schedule_customers, reversal_months, multiple):
    """Rule C9. Mutates grid (customer -> month -> amount) and returns the adjustments.

    Stopped schedule: a schedule customer's last month with revenue is at least `multiple`
    times the month before, and the month before had revenue. That month uses the prior
    month's amount.
    Reversal: a negative month that a description marks as a reversal or go-live
    adjustment, or a schedule customer's negative month with revenue after it. That month
    uses the prior month's amount, or zero when there was none.
    Other negative months are refunds and stay for the negative-month rule.
    """
    out = []
    mult = Decimal(str(multiple))
    for cust in sorted(grid):
        g = grid[cust]
        months = sorted(m for m, v in g.items() if v != 0)
        if not months:
            continue
        is_sched = cust in schedule_customers
        last_pos = max((m for m in months if g[m] > 0), default=None)
        for m in months:
            v, prev = g[m], g.get(m - 1, D0)
            kind = None
            if is_sched and m == last_pos and prev > 0 and v >= mult * prev and v > prev:
                kind = "schedule_stopped"
                used = prev
            elif v < 0:
                later = any(g.get(k, D0) > 0 for k in months if k > m)
                if (cust, m) in reversal_months or (is_sched and later):
                    kind = "reversal"
                    used = prev if prev > 0 else D0
            if kind:
                g[m] = used
                out.append({"customer": cust, "month_index": m, "kind": kind,
                            "booked": v, "used": used, "effect": v - used})
    return out


def coverage_and_gate(assigned, unassigned, names, min_coverage_pct, entity_names):
    """Coverage of revenue by customer, and the data-quality gate."""
    total = assigned + unassigned
    share = None if total == 0 else float((assigned / total * 100).quantize(Decimal("0.1")))
    hits = sorted({n for n in list(names) + list(entity_names) if n and TEST_NAME_RE.search(n)})
    reasons = []
    if hits:
        reasons.append("names that look like test or QA data: %s" % ", ".join(hits[:5]))
    if share is not None and share < min_coverage_pct:
        reasons.append("only %.1f%% of revenue is assigned to a customer" % share)
    if total > 0 and unassigned > assigned:
        reasons.append("most revenue has no customer")
    coverage = {"assigned_total": assigned, "no_customer_total": unassigned,
                "assigned_pct": share, "min_coverage_pct": min_coverage_pct}
    gate = {"fires": bool(reasons), "reasons": reasons, "test_names": hits[:10]}
    return coverage, gate
