---
name: management-report
description: "Builds the monthly or quarterly client deliverable as a paginated PDF: profitability summary, twelve-month trends with variance strips, cash management, balance sheet snapshot, the three statements in full, optional ratio appendix. Use when someone asks for a management report, monthly financials, a financial package, or month-end reporting to distribute."
---

# Management report

## Purpose

The deliverable an accountant hands over at close. Statement
lines over time, as a PDF. The governing filter: if a number cannot be traced to a line
on the P&L, balance sheet, or cash flow statement, it does not belong here.

1. Cover, contents, about
2. Profitability summary and trends
3. Cash management and cash flow
4. Balance sheet snapshot
5. The three statements in full
6. Ratio appendix, when a balance sheet exists

## Procedure

- [ ] 1. Confirm books, period, basis. Inventory what the ledger holds.
- [ ] 2. Pull in one pass: P&L leaves by month (24 where they exist), balance sheets at
      period end, prior end, prior year end, and the period's movements.
      On Kick: exact tools and call shapes in `reference/kick.md`. Other connectors: discover at runtime, never guess names.
      A P&L alone is still a report, just shorter. Omit empty sections and say so. Never pad.
- [ ] 3. Write `payload.json`: entity, contiguous months, chart of accounts with polarity
      per line, monthly ledger, optional balance sheet block.
      Feed the leaves and the movements; derive every total. Subtotals sum from leaves, never hardcoded.
      Supply real retained earnings where the books carry them; a derived plug prints itself.
- [ ] 4. Run the engine: `python3 reference/templates/build_mgmt_report.py payload.json out.pdf`.
      Validation and tie-out proofs must pass or no file is emitted. A failed proof is a books finding to report, never a figure to plug.
- [ ] 5. Verify against Completion, hand over the PDF path with one sentence on the period.

## Guardrails

- **No dimensional content, ever.** Locations, products, customers, vendors, rankings all
  belong to the dashboard. Grep the data for them before handover.
- **The engine carries the brand.** This PDF never passes through `theme.py`. Never
  restyle, swap fonts, substitute colors, or draw outside the provided flowables.
- **Color encodes effect on result, not sign.** Costs below prior are favorable and
  charcoal; income below prior is adverse and red. Immaterial variances get no color.
- **Cash flow subtotals are not toned by sign.** Buying equipment is not adverse. Only
  negative operating cash flow and net movement earn the tone.
- **Suppress meaningless percentages.** Over 300%, near-zero base, negative base, or a
  zero crossing: print the absolute change instead. A swing into loss is never "113%
  lower". Margin changes are points, `(1.5 pts)`, never `(1.5%)`.
- **Sentences are mechanical restatements.** One per chart, fixed word order, no
  interpretation: "Jun 2026: income ($862.3k) was 29% lower ($353.3k) than June 2025
  ($1.2m)." The dashboard and flux own judgment.
- Negatives in parentheses. Sum then round. True zero is an em rule, never `$0`. No cell
  fills. No budget columns without real budget data.
- A statement group never splits across a page break.
- The Inter font files sit beside the script or the build warns and falls back; a
  fallback build is off-brand and never handed over.

## Example

The one-page profitability summary: four comparison charts (income, cost of goods sold,
total expense, net profit; current and YTD against prior year, horizontal bars to scale)
above a six-row table in statement order. Every statement carries the same spine:

| Current period | Prior period | Variance $ | Prior year | Variance $ |

Year-to-date P&L drops the sequential column: January-to-June against July-to-December is
not like for like.

## Completion

Done when:

- [ ] Every total cross-foots to the dollar; the balance sheet balances at every date
- [ ] Statements tie to each other: net profit opens the cash flow; closing cash equals
      bank accounts on the balance sheet
- [ ] Zero dimensional content, zero `-$` strings, zero `$0` cells
- [ ] One favorable negative on a cost line spot-checked charcoal, not red
- [ ] Printed and read at letter size: no clipped labels, no orphaned totals, no group
      split from its total, no font warning in the build log
- [ ] Put beside the dashboard: a reader could never confuse the two

Cleanup: hand over `{entity}-management-report-{period}.pdf` with one sentence on the
period and what was omitted for missing data. Never paste the statements into chat.
