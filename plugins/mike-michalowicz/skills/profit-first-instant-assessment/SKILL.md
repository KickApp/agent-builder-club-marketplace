---
name: profit-first-instant-assessment
description: "Runs Mike Michalowicz's Profit First Instant Assessment against a client's books. Pulls trailing-12-month actuals from the P&L, a comparative Balance Sheet, and the Statement of Cash Flows, derives Real Revenue, selects the Target Allocation Percentage (TAP) bracket, and produces the assessment table (Actual, PF%, PF$, The Delta, The Fix) showing how far Profit, Owner's Pay, Tax, and Operating Expenses sit from target and whether to increase or decrease each. Read-only; the arithmetic is a documented hand procedure. Use when someone asks to run a Profit First Instant Assessment, check Profit First allocations or TAPs, or see how a client is tracking to their Profit First targets."
---

# Profit First Instant Assessment

**Important:** this skill assists with a Profit First Instant Assessment and does not provide
financial advice. It is read-only: it produces an assessment table for a qualified professional
to review. Nothing in the books changes, and no money is moved.

**Goal:** turn a client's trailing-12-month books (P&L, comparative Balance Sheet, and Cash
Flow) into the Profit First Instant Assessment table, so an advisor can see the gap between
actual spending and Mike Michalowicz's target allocation percentages, account by account.

## When to use

- "Run a Profit First Instant Assessment for Copperbeam Design for the last 12 months."
- "Check how this client is tracking to their Profit First targets."
- "What are the TAPs for a firm doing about $420K, and where are they bleeding?"
- Named use cases: a Profit First Professional onboarding a client and needing the baseline
  assessment; a quarterly advisory check-in that reports movement toward the target percentages.
- **Not this skill:** setting up recurring allocations or bank transfers (a write-and-automation
  workflow).

## Data you need

Everything here is read-only. You need:

- **The books and trailing-12 window:** which client, and the same 12-month window on a stated
  basis (prefer cash basis for P&L and Balance Sheet).
- **Three statements:** Profit & Loss; comparative Balance Sheet with a dollar-change column;
  Statement of Cash Flows (accrual on cash flow is acceptable).
- **Chart of accounts context** so you can propose the ledger-to-Profit-First mapping.
- **Six confirmed actuals** after the user approves the mapping: Top Line Revenue, Material &
  Subs, actual Profit, Owner's Pay, Tax, and Operating Expenses.

## Workflow

Copy this checklist into your reply and tick it as you go:

```
Profit First Instant Assessment:
- [ ] 1. Confirm client, period, and cash basis; pull trailing-12 P&L, comparative BS, Cash Flow
- [ ] 2. Propose the ledger-to-Profit-First mapping and CONFIRM it
- [ ] 3. Derive Real Revenue and run the assessment arithmetic by hand
- [ ] 4. Present the assessment table and the method note
```

### 1. Orient and pull the statements

Confirm which set of books and the trailing-12 date range. Prefer cash basis for the P&L and
Balance Sheet; if only accrual is available, say so and ask before proceeding. Pull:

1. One profit-and-loss report covering those twelve months (a single-period total).
2. A comparative Balance Sheet for the same window with a dollar-change column (or beginning
   and ending Balance Sheets so you can compute Equity and liability changes).
3. The Statement of Cash Flows for the same window (to confirm debt principal, credit card,
   and lease payments).
4. The chart of accounts so mapping uses real account names.

### 2. Propose the Profit First mapping and confirm it

Profit First's five categories do not line up one-to-one with GAAP statements, so this step
is a judgment call the user has to confirm before any number is computed.

Propose, in a short table with statement sources, which ledger lines feed each of:

- **Real Revenue** = Top Line Revenue minus Material & Subs (P&L). State which income lines
  are true revenue and which cost lines are materials and subcontractors. For a typical
  service business, Material & Subs is 0 and Real Revenue equals total income. You do **not**
  subtract employee labor. If Mats & Subs is under 25% of Income, propose treating it as
  Operating Expenses instead (do not subtract it from Real Revenue) and confirm that choice.
- **Profit** = profit savings (Balance Sheet Assets) plus true profit distributions (Balance
  Sheet Equity). Lifestyle distributions go to Owner's Comp, not Profit. Not the same as net
  income; often near $0 pre-Profit-First.
- **Owner's Pay (Owner's Comp)** = owner salary/wages and personal expenses on the P&L, plus
  draws/distributions in Equity on the Balance Sheet. Often buried in OpEx or only visible in
  Equity; ask where it sits. Common add-backs when present: owner's health insurance,
  retirement contributions, vehicle, cell phone, and other personal expenses paid by the
  business.
- **Tax** = tax savings (Balance Sheet Assets) plus taxes paid (P&L Expenses and/or Equity
  draws).
- **Operating Expenses** = P&L expenses + COGS not already in Mats & Subs + debt
  responsibility (loan/credit card/lease principal from comparative Balance Sheet $ change
  and Cash Flow) − amounts already counted in Owner's Comp, Tax, or Profit − Depreciation
  and Amortization.

Owner's Pay versus Operating Expenses, Material & Subs versus leftover COGS, and debt
principal versus interest-only P&L lines are the mappings people get wrong. Show the full
mapping and wait for an explicit yes before computing. If the user corrects a line, redo the
mapping table and confirm again.

### 3. Derive Real Revenue and compute the assessment (hand procedure)

Do not invent actuals. Use only the six confirmed figures from the ledger mapping. Then compute
exactly as follows (this is the method the bundled calculator enforced):

1. **Real Revenue** = Top Line Revenue - Material & Subs, rounded to cents (after applying the
   25% Mats & Subs rule if the user confirmed it).
2. If Real Revenue is negative, stop: materials and subs exceed income; recheck Material & Subs.
3. **Select the TAP bracket** using the table below. Each bracket's lower bound is inclusive and
   its upper bound exclusive, so a Real Revenue that lands exactly on a boundary uses the
   **higher** bracket. At or above $50,000,000, use the top bracket and note that above $50M the
   percentages are a professional judgment call.

| Real Revenue range | Profit | Owner's Pay | Tax | Operating Expenses |
| --- | --- | --- | --- | --- |
| $0-$250K | 5% | 50% | 15% | 30% |
| $250K-$500K | 10% | 35% | 15% | 40% |
| $500K-$1M | 15% | 20% | 15% | 50% |
| $1M-$5M | 10% | 10% | 15% | 65% |
| $5M-$10M | 15% | 5% | 15% | 65% |
| $10M-$50M | 20% | 0% | 15% | 65% |

(Percentages of Real Revenue. In every row Profit + Owner's Pay + Tax + Operating Expenses =
100%. Source: Mike Michalowicz, Profit First Instant Assessment (c) 2008-2014. Category
locations follow the Profit First Professionals Profit Assessment Worksheet (c) 2022.)

4. For each of Profit, Owner's Pay, Tax, Operating Expenses:
   - **PF$** = Real Revenue × PF%, rounded to cents.
   - **The Delta** = Actual - PF$ (negative = under target, positive = over).
   - **The Fix** = "Increase" if Delta < 0, "Decrease" if Delta > 0, "On target" if 0.

Show every intermediate figure next to its source so the arithmetic is auditable. Do not skip
to a finished table without showing Real Revenue and the chosen bracket.

### 4. Present the assessment

Show the table. State that every actual came from the ledger reads and that the targets came
from the Profit First percentages via the procedure above. Name the bracket. Surface any
out-of-range note. Add the method note if any live call behaved differently from this skill.

## Working with your data

This skill reads from whatever accounting system is connected. If you have documented bindings
for that system, use them. Otherwise:

### Unknown connector

1. List the available tools and read their schemas and descriptions.
2. Map them to the data needs above (trailing-12 P&L, comparative Balance Sheet, Cash Flow,
   and chart of accounts). Anything with no plausible tool is marked UNSUPPORTED.
3. STOP and show the user the mapping, and get confirmation, before any read beyond discovery.
   This skill performs no writes.
4. Never guess tool names. If the system exposes guide or skill discovery tools, load the
   relevant financial-reports guide first.

## Guardrails

- **Read-only.** This skill never writes, never moves money, and never schedules a transfer.
- **Figures come only from system responses.** Never invent or estimate a statement figure.
  Assessment arithmetic follows the documented procedure above and shows its work; it does
  not invent inputs.
- **Confirm the mapping before computing.** Do not pick a mapping silently across P&L,
  Balance Sheet, and Cash Flow.
- **Ambiguity stops and asks.** Ambiguous client name, unclear which Equity line is Owner's
  Comp, unclear debt principal, or a cost line that might be Material & Subs: surface the
  options and ask.
- **Tool errors and drift:** if a live call is rejected, trust the live error hint (and any
  loaded guide) over this skill's examples. Fix the call and retry once. If a read still fails
  after that single retry, stop and tell the user what failed. Never edit this skill file
  mid-run. Report any discrepancy in the deliverable's method note.

## Worked example

Request: "Run a Profit First Instant Assessment for Copperbeam Design for the last 12 months."

After confirming Copperbeam Design and reading the trailing-12 P&L, comparative Balance Sheet,
and Cash Flow, the confirmed mapping gives (illustrative): Top Line Revenue $420,000, Material
& Subs $0 (a service business), actual Profit $8,000, Owner's Pay $150,000 (salary plus Equity
draws), Tax $12,000, Operating Expenses $250,000 (including debt principal, excluding D&A).

Real Revenue = 420,000 - 0 = 420,000 -> TAP bracket $250K-$500K.

```markdown
Real Revenue: 420,000.00   TAP bracket: $250K-$500K

Account               Actual       PF%          PF$      The Delta    The Fix
Profit               8,000.00    10.0%    42,000.00    -34,000.00    Increase
Owner's Pay        150,000.00    35.0%   147,000.00      3,000.00    Decrease
Tax                 12,000.00    15.0%    63,000.00    -51,000.00    Increase
Operating Expenses 250,000.00    40.0%   168,000.00     82,000.00    Decrease
```

Reading: Profit and Tax are well below target (negative Delta, so Increase), while Owner's Pay
is slightly over and Operating Expenses are $82,000 over target (positive Delta, so Decrease).

## Common pitfalls

- Confusing Profit with net income. The Profit actual is what was held or taken as profit
  (often from Balance Sheet Assets/Equity), usually small before Profit First.
- Leaving Owner's Pay inside Operating Expenses or missing Equity draws. Owner compensation
  often sits in Equity or is buried in OpEx.
- Ignoring debt principal. Loan, credit card, and lease principal paid in the window belong
  in Operating Expenses for this assessment; use the comparative Balance Sheet and Cash Flow.
- Forgetting to exclude Depreciation and Amortization (non-cash).
- Double counting lines already used for Owner's Comp, Tax, or Profit.
- Forgetting Material & Subs on a product or agency business (or skipping the 25% rule when
  it applies).
- Boundary confusion. A Real Revenue exactly on a boundary uses the higher bracket ($500,000
  uses $500K-$1M). Do not override this by hand.
- Skipping the shown arithmetic and jumping to a finished table without Real Revenue and bracket.

## Human deliverable

- **Result:** the assessment table (Actual, PF%, PF$, The Delta, The Fix per account) and the
  selected TAP bracket.
- **Scope:** the client, the trailing-12-month window, the accounting basis (cash preferred),
  and that P&L, comparative Balance Sheet, and Cash Flow were read.
- **Details:** the confirmed ledger-to-Profit-First mapping (with statement sources), Real
  Revenue and how it was derived, and that targets came from the Profit First percentages via
  the procedure above.
- **Status:** read-only assessment. No changes were made to the books.
- **Exceptions:** any out-of-range note, ambiguous mappings the user resolved, and the
  schema-drift method note if a call behaved differently.
- **Next step:** the largest Delta to address first, offered as advisory input for the
  accountant, not a filing or a transfer instruction.

Credit the method: this is Mike Michalowicz's Profit First Instant Assessment, with category
locations guided by the Profit First Professionals Profit Assessment Worksheet.

## Related skills

- Cash sweep analysis: idle-cash-versus-buffer and foregone yield; different question from
  target allocation percentages.
- Cash flow forecast: forward runway and weekly cash position, not a Profit First target check.
- Financial reports: the underlying P&L, Balance Sheet, and Cash Flow this skill reads.

## Feedback and improvement

This copy of the skill belongs to the person running it, and it should get better
with use.

- **During a run:** when the user corrects an assumption, an output, or a preference
  (tone, format, thresholds, account or entity choices), apply the correction
  immediately and keep it for the rest of the run. A correction never overrides the
  safety contract: previews, confirmations, and figures-from-reads always stand.
- **Between runs:** when a correction should stick, offer to save it. With the user's
  explicit approval, add a dated entry under `## Learned preferences` at the end of
  this file, creating that section if it is missing. Newer entries beat older ones.
  Never edit this skill file mid-run, and never change the Guardrails, Tools used, or
  safety wording: preferences and defaults only. A preference is declined, not saved,
  when honoring it on a future run would loosen any Guardrails line or the safety
  contract, even though it leaves their text untouched. If this file is not writable
  where the skill runs, give the user the entry text to save wherever they keep their
  instructions.
- **Improving the original:** if someone sent the user this skill, end the deliverable
  with one plain-English line describing what worked differently or which preference
  was saved (inside the deliverable's method notes, when this skill's output template
  has them), and ask them to forward it to whoever maintains the original copy.
