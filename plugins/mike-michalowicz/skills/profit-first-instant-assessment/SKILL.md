---
name: profit-first-instant-assessment
description: Runs Mike Michalowicz's Profit First Instant Assessment against a client's Kick books. Pulls trailing-12-month actuals from the P&L, a comparative Balance Sheet, and the Statement of Cash Flows, derives Real Revenue, selects the Target Allocation Percentage (TAP) bracket, and produces the assessment table (Actual, PF%, PF$, The Delta, The Fix) showing how far Profit, Owner's Pay, Tax, and Operating Expenses sit from target and whether to increase or decrease each. Read-only; the arithmetic runs in a bundled script. Use when someone asks to run a Profit First Instant Assessment, check Profit First allocations or TAPs, or see how a client is tracking to their Profit First targets.
---

# Profit First Instant Assessment

## Purpose

Turn a client's trailing-12-month books into Mike Michalowicz's Profit First Instant
Assessment, so an advisor sees how far actual Profit, Owner's Pay, Tax, and Operating
Expenses sit from the target allocation percentages, and whether to increase or decrease
each (a Profit First Professional's onboarding baseline, or a quarterly check-in). The
skill is read-only: it never moves money, schedules transfers, or sets up recurring
allocations, and a request to do any of those is a write-and-automation task it does
not run.

1. Orient: the client entity and its cash-basis ledger.
2. Read: P&L, comparative Balance Sheet, Statement of Cash Flows, chart of accounts.
3. Map: ledger lines to the Profit First categories, confirmed by the user.
4. Compute: the bundled script on the six confirmed figures.
5. Present: the assessment table, the mapping, and the method note.

## Procedure

- [ ] 1. Orient: load the reporting guide, resolve the client entity, pick the ledger.
      On Kick, [references/kick.md](references/kick.md) gives the guide, every call, and the step mapping. Elsewhere, discover the tools at runtime and never guess names.
      Ambiguous client name: show the candidates and ask which entity. Never ask the user for an ID; never guess one.
      Prefer the cash ledger (the PFP worksheet prepares the P&L and Balance Sheet on a cash basis). Accrual only: say so and ask before proceeding.
- [ ] 2. Read the trailing-12-month statements, one window for every report.
      P&L; comparative Balance Sheet with a dollar-change column; Statement of Cash Flows (accrual basis is acceptable on this statement); chart of accounts, so the mapping uses real account names.
      No dollar-change column from one comparative pull: pull the Balance Sheet at the window start and at the window end, and use the difference for Equity and liability lines.
      Optional: connected accounts, to confirm which belong to the entity; a transaction drill-down when a mapping line needs a closer look.
      Empty or all-zero P&L: stop before the mapping. Name the entity and window read, and ask the user to confirm the client or pick a window with activity. Never run the assessment on zeros.
- [ ] 3. Propose the ledger-to-Profit-First mapping and wait for an explicit yes.
      A short table, every line with its statement source, feeding six figures: Top Line Revenue, Material & Subs, Profit, Owner's Pay, Tax, Operating Expenses.
      State which income lines are true revenue and which cost lines are materials and subcontractors.
      Category rules, the 25% Mats & Subs rule, and the Operating Expenses formula: [references/profit-first-method.md](references/profit-first-method.md).
      Mats & Subs under 25% of Income: propose treating it as Operating Expenses (not subtracted from Real Revenue) and confirm that choice.
      Owner's Pay location unclear: ask where it sits. User corrects a line: redo the mapping table and confirm again.
- [ ] 4. Run the script on the six confirmed figures.
      `python3 scripts/pf_assessment.py --top-line-revenue <total income> --materials-and-subs <0 for a service business> --actual-profit <n> --actual-owners-pay <n> --actual-tax <n> --actual-operating-expenses <n>`
      Or pipe the same six fields as JSON on stdin with `--json`. `--help` lists every argument.
      The script derives Real Revenue, selects the TAP bracket, and computes PF$, The Delta, and The Fix. A negative Real Revenue stops with an error: recheck Material & Subs.
- [ ] 5. Present the assessment in the six fields shown in the Example.
      Result, Scope, Details, Status, Exceptions, Next step. Name the bracket. Surface any script note.
      Add the method note when any live call behaved differently from the binding.

## Caveats

- **Read-only.** The tell: a request to move money, schedule a transfer, or set up allocations. This skill has no write step and no confirmation flow; say the request is out of scope and point to transfer scheduling or rules automation.
- **Figures come only from reads.** Never invent or estimate a statement figure. Every actual fed to the script is read from the books. The model does no assessment arithmetic; the script does, so a table figure the script did not print is wrong.
- **Mapping confirmed before computing.** The category mapping is a judgment call across three statements. Never pick a mapping silently; no explicit yes, no script run.
- **Ambiguity stops and asks.** Ambiguous client name, unclear which Equity line is Owner's Comp, unclear debt principal, a cost line that might be Material & Subs: surface the options and ask. Never guess IDs or accounts.
- **Profit is not net income.** The Profit actual is what was held or taken as profit (profit savings in Assets, true profit distributions in Equity), usually small before Profit First. Never plug net income in.
- **Owner's Pay hides.** Owner compensation often sits in Equity draws or is buried in Operating Expenses. Lifestyle distributions belong in Owner's Pay, not Profit. Split it out, or both rows are wrong.
- **Debt principal belongs in Operating Expenses.** Loan, credit card, and lease principal paid in the window counts. Use the comparative Balance Sheet dollar change and the Cash Flow; P&L interest expense alone is the tell of a miss.
- **Depreciation and Amortization are excluded.** Non-cash; always remove them from Operating Expenses.
- **No double counting.** Any line already used for Owner's Pay, Tax, or Profit comes out of Operating Expenses. Double counting throws off every Delta row.
- **Material & Subs on a product or agency business.** Real Revenue is Top Line minus materials and subcontractors, unless the 25% rule moves Mats & Subs into Operating Expenses. A typical service business has Material & Subs of 0.
- **Boundaries go up.** A Real Revenue exactly on a boundary uses the higher bracket ($500,000 uses $500K-$1M). At or above $50M the script uses the top bracket and returns a note. The script enforces both; never override it by hand.
- **In-run corrections stick for the run.** A user correction to format, an account, or an entity choice applies at once and for the rest of the run. It never overrides figures-from-reads or the mapping confirmation.

## Example

Request: "Run a Profit First Instant Assessment for Copperbeam Design for the last 12
months." After the reads, the user confirms the mapping and the run is:

```
python3 scripts/pf_assessment.py --top-line-revenue 420000 --materials-and-subs 0 \
  --actual-profit 8000 --actual-owners-pay 150000 --actual-tax 12000 \
  --actual-operating-expenses 250000
```

The response:

```markdown
**Result.** Real Revenue: 420,000.00   TAP bracket: $250K-$500K

Account               Actual       PF%          PF$      The Delta    The Fix
Profit               8,000.00    10.0%    42,000.00    -34,000.00    Increase
Owner's Pay        150,000.00    35.0%   147,000.00      3,000.00    Decrease
Tax                 12,000.00    15.0%    63,000.00    -51,000.00    Increase
Operating Expenses 250,000.00    40.0%   168,000.00     82,000.00    Decrease

Profit and Tax are well below target (negative Delta, so Increase). Owner's Pay is
slightly over and Operating Expenses are $82,000 over target (positive Delta, so
Decrease). The Delta is the dollar gap to close per account.

**Scope.** Copperbeam Design, trailing 12 months, cash basis. Read the P&L, the
comparative Balance Sheet, and the Statement of Cash Flows.

**Details.** Confirmed mapping: Top Line Revenue $420,000 and Material & Subs $0 (a
service business, so Real Revenue equals total income). Profit $8,000 (profit savings
and distributions). Owner's Pay $150,000 (salary plus Equity draws). Tax $12,000.
Operating Expenses $250,000 (including debt principal, excluding D&A and amounts
already counted above). Every actual came from the ledger reads; the targets came from
the Profit First percentages via the script.

**Status.** Read-only assessment. No changes were made to the books.

**Exceptions.** None. No script note, and every call ran as the binding describes.

**Next step.** Operating Expenses carry the largest Delta. Address it first. This is
advisory input for the accountant, not a filing or a transfer instruction.

Method: Mike Michalowicz's Profit First Instant Assessment, with category locations
guided by the Profit First Professionals Profit Assessment Worksheet.
```

## Completion

Done when:
- The mapping table, with statement sources, got an explicit yes before the script ran.
- Every actual fed to the script came from a read, and every PF%, PF$, Delta, and Fix came from the script.
- The response names the entity, the window, the basis, the statements read, and the TAP bracket.
- Exceptions lists any script note, every ambiguity the user resolved, and any method note.
- Next step names the largest Delta as advisory input, not a filing or transfer instruction.
- The method is credited to Mike Michalowicz's Profit First Instant Assessment and the PFP worksheet.
- Nothing was written to the books.

Cleanup: the table, the confirmed mapping, and the method note go to the user in the
response. Open mapping questions are listed under Exceptions. The script writes no files.
