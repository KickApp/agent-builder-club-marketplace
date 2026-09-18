---
name: adjust
description: "Turns schedules and exceptions into a period-end JE register: accruals with reversals, prepaid amortization, depreciation, deferred revenue recognition. Every entry waits on explicit approval; approved entries leave as an import-ready CSV for the user's own system, and nothing is posted anywhere. Use when booking or rolling forward adjusting entries for a period."
---

# Adjust

## Purpose

Turn schedules and exceptions into a JE register: every adjusting entry the period needs,
each with its workpaper, waiting on explicit approval. Approved entries leave as an
import-ready CSV; this skill posts nothing anywhere.

1. Collect schedules, register items, and standing accruals
2. Check reversals, roll schedules, run the completeness scan
3. Draft entries, gate on approval, emit the CSV

## Procedure

- [ ] 1. Collect the work: profile schedules to roll forward, adjustment-required items
      from the exceptions register (when running inside a close), standing accruals due.
      Other inputs: the client profile, GL detail and TB for control account tie-outs.
- [ ] 2. Check reversals before drafting anything new.
      On Kick: guides and pull mapping in `reference/kick.md`. Other connectors: discover at runtime, never guess names.
      Every prior auto-reverse accrual either has its reversal in this period's GL, was settled directly against the liability (documented on the schedule), or gets a reversal proposed here. Relieved neither way: first entry on the register. Relieved both ways: double-relief flag.
      The prior period's JE register carries the auto-reverse flags; read them when available, fall back to the GL pattern when not.
- [ ] 3. Roll each schedule forward per [reference/schedule-formats.md](reference/schedule-formats.md), including the optional loan roll with its interest recalc whenever a lender statement is on hand.
      Each schedule ties to its GL control account exactly: closing balance equals TB balance, rounding documented on the schedule, never absorbed silently.
- [ ] 4. Run the completeness scan against the period's activity, both directions.
      Tells: a payment to a prepaid-type vendor with no schedule row; an asset-sized purchase not on the register; a new billing whose service period extends past close (existing deferral contract, or invoice language like "annual" or "12 months") sitting fully in revenue.
      Check the exceptions register first: an item cleanup already dispositioned or already asked about is settled, not re-asked. Each fresh hit becomes a question or a schedule row, never silently left where it landed.
      Unrecorded liabilities check: read post-period evidence (early next-period GL or bank activity, bills dated after period end for period services, late statements) for expenses in neither AP nor accruals. In-period patterns count: a pay cadence whose last run predates period end means earned, unpaid wages; request the run summary. Each catch is a proposed accrual with the evidence cited. File the scan as its own workpaper listing what was searched and found, including a clean result. No post-period data: the scan covers bills and statements on hand, disclosed as such.
      When the profile records revenue earned on a different pattern than billed (contracts spanning periods, progress billings), the matching WIP or deferral schedule is a required input; missing blocks that area with the schedule on the request list, never quietly treated as billed-equals-earned.
- [ ] 5. Draft each entry under the je skill's contract: balanced, dated in the period,
      accounts from the client's chart, stable memo, cited source, and a workpaper
      showing source, calculation, and tie-out.
      Missing source data blocks that adjustment onto the register with what is missing, never estimated into existence, unless the profile authorizes a named estimation policy for exactly that item (apply the policy and label the figure estimated per policy).
- [ ] 6. Present the register for approval: entries above materiality individually, the
      rest as a reviewed batch. No entry is marked approved without the user's explicit
      confirmation; no confirmation means it stays proposed.
- [ ] 7. Emit the import CSV of approved entries only, per the je skill's CSV contract.
      File it with the register in `workpapers/`; append the outcome to the close log when one is kept.

Cash-basis client (per profile): steps 2 to 4 collapse to a reversal and carryover check;
accrual conversion is an explicit opt-in, never assumed.

## Guardrails

- **Out of scope, each with its manual path**: inventory and COGS (needs a count or costing method; workpaper, then import), FX remeasurement (rate policy), tax provision (preparer's call), equity compensation (grant ledger), intercompany (both entities' books), AR allowance and bad debt write-offs (review flags candidates; the reserve is the preparer's policy call), impairments (screens flag indicators; measurement is a valuation judgment), contract cost estimation and loss provisions (the WIP schedule takes estimated total cost as user input and flags loss contracts). Name these in the deliverable when the data suggests them; never attempt them.
- Out of scope converts when the user supplies the governing judgment mid-run. A stated policy or measurement (allowance percentage, estimated total cost, costing method) is theirs: record it, offer to save it to the profile, then run it like any authorized policy under the usual gate.
- **The estimate that closes the gap.** A schedule that will not tie gets a rounding entry to force it. The tell: an entry whose memo cannot name a source document or policy. The gap goes on the register instead.
- **The permanent accrual.** An accrual repeats every period but its reversal never posts, quietly doubling the liability. The tell: a liability balance that only ever grows. Reversals are checked before new accruals are drafted.
- A method gap blocks like a data gap. Any measurement with more than one accepted method (inventory costing, contract revenue recognition, depreciation convention, FX rates) runs under the profile's stated method or stops with a question; an assumed method is never the silent default.
- An approval mark of unknown provenance (a register found on a shared drive, no session trail) is a proposal: re-confirm before that entry enters the import CSV. Batch approval is fine; silent approval is not.
- Ask vs proceed: a fact the schedule and GL settle is derived, never asked. A precedent the client books the same way every period is followed and noted. A judgment below materiality takes the conservative treatment, proceeds, and discloses; above materiality, hard to reverse, or in a flagged risk area, it queues a question.
- Write a question down (close log or exceptions register) the moment it is queued; a question held in working memory gets silently answered. Track the running total of proceed-and-disclose judgments: when the aggregate crosses materiality, convert the open ones to questions and say the aggregate out loud. Twenty immaterial guesses are one material guess. Raise queued questions with the register presentation.
- Running unattended: every entry stays proposed with the register complete; approval never happens without a human.
- Degradation: a missing profile schedule is rebuilt from GL history only when the pattern is unambiguous, labeled rebuilt, otherwise blocked with a request. No fixed asset register: depreciation blocked; carry the prior period's entry only if the profile authorizes it as policy. No exceptions register: standalone run from provided schedules, saying cleanup items were not sourced. No prior-period GL: the reversal check is limited to what the user confirms, each unverified reversal disclosed.

## Example

```markdown
### JE register: <client>, <period>

| # | Entry | Dr | Cr | Amount | Source | Status |
| - | ----- | -- | -- | ------ | ------ | ------ |
| 1 | <description> | <account> | <account> | <amount> | <schedule/doc/policy> | <approved/proposed/blocked> |

**Schedules:** <each: closing balance, control account, tie-out result>
**Reversals:** <prior accruals reversed or flagged>
**Blocked:** <each with the missing source>
**Out of scope observed:** <named, with manual path, or omit>
**CSV:** <path, entry count, total Dr = total Cr>
```

## Completion

Done when:

- [ ] Every schedule ties to its control account exactly, rounding documented
- [ ] Every prior auto-reverse accrual is reversed, or its missing reversal is on the register
- [ ] Every register entry is approved, declined, or blocked with the missing source named
- [ ] The CSV holds approved entries only and foots: total debits equal total credits
- [ ] Out-of-scope adjustments the data suggests are named in the deliverable

Cleanup: file the register, scan workpaper, and CSV in `workpapers/`; append outcomes to
the close log when one is kept. Open questions land on the exceptions register or close
log, never in working memory. The entry contract and CSV format live with the je skill.
