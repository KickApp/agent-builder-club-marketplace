---
name: dashboard
description: "Builds a scannable performance dashboard as a client-ready HTML file, one page and one scroll: four hero KPI tiles, year-over-year trend charts, and, wherever the ledger carries them, profit by location or department, product margins with a revenue mix donut, top customers and vendors, and AR and AP aging. Ranks members by contribution, not revenue. All metrics, no prose; the ranked insights travel in the chat message. Runs on a bare P&L and gets richer with tagging. Read-only. Use when someone asks for a dashboard, a KPI snapshot, how the business is doing, which locations or products make money, top performers, spend by vendor, who owes us money, overdue invoices or bills, or revenue concentration. Not for why one line moved (flux), a week-by-week cash projection (cashflow), or the statements-first PDF deliverable (management-report)."
---

# Dashboard

## Purpose

Business segments at a point in time, same shape every cycle; the management report owns
statement lines over time, so every dimensional cut and ranked member list lives here only.
Fixed page order, most important first:

1. Hero KPI tiles
2. Revenue and net income against last year
3. Location (or department, or project) profitability
4. Product margins, closing on the revenue mix
5. Top customers and vendors
6. Money owed to you, money you owe: the AR and AP aging

## Procedure

- [ ] 1. Confirm books, period, basis. Read `reference/HOUSE-RULES.md`, `reference/DATA.md`,
      `reference/ARTIFACTS.md`, and `reference/DIMENSIONS.md` first.
- [ ] 2. Pull the P&L for the period and the comparisons: prior period, trailing three-period
      On Kick: guides and pull mapping in `reference/kick.md`. Other connectors: discover at runtime, never guess names.
      average, same period last year when twelve months exist. Label every column; no targets
      or plans, only what happened against what happened before.
- [ ] 3. Detect dimensions and measure coverage per `reference/DIMENSIONS.md`: never ask, read
      for it, then say what you found; its coverage bands decide whether a view ships. One
      section per owner question, three dimensional sections maximum.
- [ ] 4. Compute variance by category; contribution by member where costs are tagged. Dollar
      variance, percent against the absolute base, `n/m` on a zero base. Flag rows off by more
      than 10% and more than about 1% of period revenue as worth a flux; name the threshold
      and the largest contributing member in the finding, and stop there. Build the ladder,
      ranking, and loss-run counts per `DIMENSIONS.md`; rank by contribution, not revenue,
      and report where the two rankings disagree.
- [ ] 5. Tie out: members plus `Unassigned` re-sum to the reported P&L line; contribution plus
      unallocated overhead re-sums to operating income. Show the identity once in the
      footnote. A cut that does not tie does not ship.
- [ ] 6. Write the payload to `data.json`, then build in two steps, always in this order:

      ```
      python3 reference/templates/build_report.py data.json {entity}-dashboard-{period}.html
      python3 reference/templates/theme.py \
              reference/brand-config.md {entity}-dashboard-{period}.html
      ```

      Step one writes the report, step two applies the firm brand and runs the copy audit;
      never fuse them, and never hand over after only step one.

## Guardrails

- **One page, one scroll, no tabs, the fixed order.** Every exhibit answers a question no
  other answers, in a form that fits it (section vocabulary in `ARTIFACTS.md`); a page of
  eight bar charts reads as one chart repeated. Metrics only, no prose: no `headline`,
  `callout`, `text`, or findings sections; notes under 90 characters, defining a measure only.
- **Insights ride in the chat message**: three to five ranked items, each titled with a
  number or date, framed as questions for review, never prescriptions. A shortfall is not a
  closure recommendation; naming a driver is in scope, explaining why it moved is flux's job,
  said in plain language. With GL vendor detail, scan for found money (duplicate tools, a
  stepped-up recurring charge, an invoice paid twice), annualize each, call it a candidate
  to confirm.
- **The hero row is exactly four tiles: revenue, net income, cash on hand, monthly spend**
  (trailing three-month average, months of cash in its `sub`). Revenue and net income carry a
  `delta` against last year, a `spark` where twelve periods exist. Omit the cash tiles rather
  than guess a balance. The yoy pair beneath (revenue, net income, half width) ships together
  or not at all, only when twelve months of both years exist. At most one external figure, in
  a hero tile's `sub`, from the run's benchmark reference set with its label intact: never
  source, compute, or trim it; no set, no empty slot.
- **Title a section for the measure on its dimension**: *Location profitability*, *Product
  margins*, *Top customers and vendors*. Never a question word (*Who*), a bare dimension noun
  (*Locations*), analyst vocabulary (*concentration*), or one industry's word (*Branch*,
  *SKU*). The axis takes the general word; members keep their book spellings. Owner language
  throughout: contribution is *Profit*, cash conversion cycle is *Cash tied up*, liquidity is
  *Cash available*, cash floor is *Minimum balance*, unit economics is *Profit per unit*.
  Define the measure once in the note. A labeling rule, never a measurement rule: the ladder
  and re-sums are unchanged. A label and its value agree: months are months, multiples `x`.
- **Location profitability**: compact strip (member count, top share, best and worst by
  contribution; no hero metrics) plus one `stack`, *Profit by location, by month*,
  `Unassigned` a grey band like any other.
- **Product margins** only when products carry revenue; *Product revenue* when no cost. Strip
  includes the below-cost item count. `table` *Profit per unit by product*, sortable, total
  tying to gross profit; `donut` *Revenue mix*.
- **Top customers and vendors**: two full-width `hbars`, `Other (n)` last and always grey,
  vendor note stating if the base excludes payroll. No strip.
- **Aging buckets ship exactly as**: `Current`, `1-30 days late`, `31-60 days late`,
  `61-90 days late`, `Over 90 days late`, age order, never re-ranked. Color per bucket:
  `posbar` Current, `cmut` the late three, `negbar` over-90 only when it holds money; an
  empty over-90 bucket is grey, and that is good news. Both sides re-sum to their control
  accounts to the dollar or the section does not ship; one side alone ships full width.
- **Results by entity** only with more than one set of books, right after the yoy charts,
  noting nothing is eliminated; entity declarations per `ARTIFACTS.md`, one entity sets nothing.
- **The integrity rules in `DIMENSIONS.md` hold**: `Unassigned` is a row, never dropped; an
  untagged cost is never allocated (where only revenue is tagged, ship the revenue cut and say
  margin by member is unavailable); like for like, a member that opened or closed
  mid-comparison reported as its own set. No tagging means a shorter page, never an empty card.

## Example

```json
{ "type": "yoy", "title": "Revenue", "span": "half", "fmt": "currency",
  "labels": ["Jan", "Feb", "...", "Dec"],
  "current": { "name": "FY 2026", "values": [340000, 355000, "...", null] },
  "prior":   { "name": "FY 2025", "values": [298000, 310000, "...", 331000] } }
```

## Completion

Done when:

- [ ] Exactly four hero tiles; every strip below them is compact
- [ ] Every cut re-sums to its P&L line or control account to the dollar; identity in footnote
- [ ] Zero prose on the page; every note under 90 characters
- [ ] Both build steps ran in order; footnote carries basis, comparisons, sourcing, coverage,
      and the review gate

Cleanup: hand over the path to `{entity}-dashboard-{period}.html` with the ranked insights
in the chat message. Never paste the page contents into chat.
