# Profit First method reference

Table of contents

- Attribution
- Required statements
- Real Revenue
- Target Allocation Percentages (TAP)
- The seven-step Instant Assessment
- Boundary and out-of-range rules
- Mapping ledger statements to the five categories

## Attribution

The Instant Assessment arithmetic, the Target Allocation Percentages, and the Real Revenue
idea are Mike Michalowicz's Profit First method, from the "Profit First Instant Assessment"
(c) 2008-2014. The percentages below are published data, not tuned constants.

The statement checklist and where each category's actuals live (P&L, comparative Balance
Sheet, Statement of Cash Flows) follow the Profit First Professionals "Profit Assessment
Worksheet" (c) 2022. This skill uses the factual method and numbers; it does not reproduce
either copyrighted document.

## Required statements

Prepare these for the same trailing-12-month window before mapping:

1. **Profit & Loss** on a cash basis (prefer the cash ledger when one exists).
2. **Balance Sheet**, comparative, with a dollar-change column for the same window (Equity
   draws, liability paydowns, and dedicated Profit/Tax savings accounts often show here).
3. **Statement of Cash Flows** (accrual basis is acceptable for this statement). Use it to
   confirm debt principal, credit card, and lease payments that do not fully appear on the
   P&L.

Also read the chart of accounts so account names in the mapping match the ledger.

## Real Revenue

Real Revenue is the 100% base that every target percentage is applied to.

Real Revenue = Top Line Revenue minus the cost of Materials and Subcontractors.

It is close to Gross Profit, with one difference: you do NOT subtract employee labor.
You subtract only materials and subcontractor costs.

- Typical service business: no meaningful materials or subs, so Real Revenue equals total
  income (Top Line Revenue). Material & Subs is 0.
- Retailer, manufacturer, or agency with heavy subcontracting or resold goods: total
  income is adjusted down to Real Revenue by subtracting those material and subcontractor
  costs, so the percentages measure the money the business actually gets to keep and run on.
- **25% rule:** if Materials & Subcontractors is less than 25% of Income, treat that amount
  as Operating Expenses instead (do not subtract it when computing Real Revenue). Confirm
  this choice with the user when it applies.

## Target Allocation Percentages (TAP)

Percentages are OF Real Revenue. In every row Profit + Owner's Pay + Tax + Operating
Expenses = 100%.

| Real Revenue range | Profit | Owner's Pay | Tax | Operating Expenses |
| --- | --- | --- | --- | --- |
| $0-$250K | 5% | 50% | 15% | 30% |
| $250K-$500K | 10% | 35% | 15% | 40% |
| $500K-$1M | 15% | 20% | 15% | 50% |
| $1M-$5M | 10% | 10% | 15% | 65% |
| $5M-$10M | 15% | 5% | 15% | 65% |
| $10M-$50M | 20% | 0% | 15% | 65% |

This table is embedded in `scripts/pf_assessment.py` as the authoritative copy. If the two
ever disagree, the script wins for computation and this file should be corrected to match.

(The TAP table labels the owner row "Owner's Pay"; the PFP worksheet often says "Owner's
Comp." Treat them as the same Instant Assessment row.)

## The seven-step Instant Assessment

1. Find the last-12-months Real Revenue (Top Line Revenue minus Material & Subs, subject to
   the 25% rule above).
2. Pick the TAP column by that Real Revenue bracket.
3. Fill the Actual column with the last-12-months actuals for each account.
4. Fill the PF% column from the chosen bracket.
5. PF$ = Real Revenue actual times each PF%.
6. The Delta = Actual minus PF$ per row (can be negative). (The PFP worksheet
   Figure 2 labels this column "The Bleed"; this skill uses "The Delta" to match
   book terminology.)
7. The Fix = "Increase" when the Delta is negative, "Decrease" when positive.

The result, per account: whether to Increase or Decrease, and by how much (the Delta).

The script does steps 1, 2, and 4 through 7 for you once you supply the six confirmed figures.
Steps 2 and 3 are where your judgment lives: the bracket is mechanical, but the actuals
depend on how the client's ledger accounts map to the five categories across P&L, Balance
Sheet, and Cash Flow.

## Boundary and out-of-range rules

- Each bracket's lower bound is inclusive and its upper bound exclusive. A Real Revenue
  that lands exactly on a boundary uses the HIGHER bracket. Examples: $250,000 uses
  $250K-$500K; $500,000 uses $500K-$1M; $1,000,000 uses $1M-$5M.
- Real Revenue at or above $50,000,000 uses the top bracket ($10M-$50M) and the script
  returns a note that above $50M the percentages are a professional judgment call.
- Real Revenue below $0 (materials and subs exceed income) is a data error: the script
  stops and asks you to recheck the Material & Subs figure.

## Mapping ledger statements to the five categories

Profit First categories do not map one-to-one to a GAAP P&L. Pull all three statements,
propose the full mapping, and get an explicit yes before computing.

### Income (Top Line Revenue)

Total revenue into the business. Found on the P&L.

### Materials and Subcontractors

Physical goods used to produce the product or service, plus outsourced expertise to produce
it. Usually in Cost of Sales / Cost of Goods Sold on the P&L. Apply the 25% rule under
Real Revenue before locking Material & Subs for the script.

### Profit

Money set aside for a rainy day, not net income.

- **Profit savings:** dedicated profit account balances under Assets on the Balance Sheet
  (period change / amounts set aside over the window).
- **Profit distributions:** distributions in the Equity section that are true profit takes,
  not lifestyle support.
- Lifestyle distributions belong in Owner's Comp, not Profit.
- Pre-Profit-First businesses often show near $0 here; do not plug net income.

### Owner's Comp (Owner's Pay)

Everything that supports the owner's lifestyle. Sum:

- Owner salary / W-2 wages (gross, including payroll taxes) from the P&L
- Owner draws and shareholder distributions from Equity on the Balance Sheet
- Personal transactions run through the business on the P&L
- Common add-backs when present: owner's health insurance, company retirement
  contributions for the owner, owner's vehicle (loan, insurance, fuel, repairs), owner's
  cell phone, and other personal expenses paid by the business

Owner's Comp is often buried in Operating Expenses on the P&L or only visible as Equity
draws. Ask where it sits when unclear.

### Tax

Amounts set aside or paid for the owner's personal income taxes and taxes due on business
profit.

- **Tax savings:** dedicated tax reserve under Assets on the Balance Sheet
- **Taxes paid:** tax expense lines on the P&L, and/or tax-related draws/distributions on
  the Balance Sheet

### Operating Expenses

Regular cash responsibilities of the business:

```
Operating Expenses =
  Total P&L Expenses
  + COGS / Cost of Sales not already counted in Materials & Subcontractors
  + Debt responsibility (loan, credit card, and lease principal paid in the window)
  - Amounts already counted in Owner's Comp, Tax, or Profit
  - Depreciation and Amortization (non-cash; always exclude)
```

**Debt responsibility:** use the comparative Balance Sheet dollar-change on liability
accounts plus the Statement of Cash Flows to see what was actually paid on loans, credit
cards, and leases over the trailing 12 months. Profit First treats those principal
payments as part of Operating Expenses for the assessment (not as a GAAP expense
classification).

**Don't double account:** any expense line already used for Owner's Comp, Tax, or Profit
must be subtracted from Operating Expenses. Double counting throws off every Delta row.

Because Owner's Comp versus Operating Expenses, Material & Subs versus leftover COGS, and
debt principal versus P&L interest alone are the mappings people get wrong, propose the
full mapping (with statement sources) and get explicit confirmation before running the
script.
