---
name: intake
description: "Close readiness check that opens a close: proves what the provided data can prove and produces a readiness report with the missing-items request list inside it. Use when starting a close for a period, when the user asks whether books are ready to close, or when validating a trial balance and GL export against statements."
---

# Intake

## Purpose

Take whatever the user has provided, prove what it can prove, and produce a close readiness
report on the spot: what is present, what is missing, and what each gap blocks. The report is
the artifact; the request list lives inside it. Never require a perfect data package first.

1. Inventory and classify the inputs
2. Validate the TB, tie the GL, check period completeness
3. Build the coverage map against the client profile
4. Write the readiness report with the request list, and file it

## Procedure

- [ ] 1. Read the client profile first when one exists (`clients/<client>/profile.md`,
      `profile.md` at the root in a single-client workspace, or in project knowledge): it
      names the accounts, schedules, and statements this client's close expects.
- [ ] 2. Inventory what was provided: each file's type, system of origin, and period coverage,
      On Kick: guides and pull mapping in `reference/kick.md`. Other connectors: discover at runtime, never guess names.
      identified from its contents, never its filename or the user's description. Inputs, any
      subset: trial balance (required for a full close; a GL export substitutes per Caveats),
      prior-period TB, GL detail, bank and card statements, subledgers or schedules.
- [ ] 3. Validate the TB: debits equal credits; the period label matches the period being
      closed. With a prior TB, confirm prior close balances roll into this period's openings;
      flag any account that moved outside the period.
- [ ] 4. Tie the GL to the TB: per account, opening balance plus period activity equals the
      closing TB balance. List every account that does not tie. Before diagnosing any cause,
      run the constant-difference test on the failures (difference per account per period):
      constant from the first period means the records disagree about openings; appearing
      partway means activity or cutoff. A test that cannot distinguish supports no conclusion.
- [ ] 5. Check period completeness: GL activity spans the full period and nothing is dated
      after period end without explanation. A quiet boundary stretch is indistinguishable from
      a truncated export on its own; corroborate against the bank statement's first and last
      items when one exists, and say which check you used.
- [ ] 6. Build the coverage map: per balance sheet account, the evidence supporting it this
      period (statement, subledger, schedule, or nothing yet). Check it against the profile's
      business reality: every recorded fact (contracts spanning periods, inventory, loans,
      leases, related parties, foreign currency) has matching evidence or a request-list line
      naming what is missing and what it blocks.
- [ ] 7. Write the readiness report (format in Example) with the missing-items request list
      inside it as a client-ready message, per [reference/request-list-format.md](reference/request-list-format.md).
- [ ] 8. File it. In a close (a close folder exists or the user wants one): report to
      `workpapers/`, exactly one copy of each input into the folder's `inputs/`, the close's
      canonical data set. On divergence from originals elsewhere, stop and confirm which is
      current; a corrected file replaces the original, never a forked second copy. Note each
      input's row count and one control total (TB: total debits; GL: sum of debits;
      statement: ending balance) so a later phase can cheaply confirm its data. Append the
      outcome to the close log when kept. Standalone: deliver, offer to start a close folder.

## Guardrails

- A missing input downgrades the report; it never stops it.

  | Missing input | Fallback |
  | --- | --- |
  | Trial balance | Derive a working TB from the GL export and label every figure derived, not stated |
  | Prior-period TB | Skip roll-forward and flux checks; note that comparatives are unavailable |
  | Prior TB with balance sheet accounts only (post-closing) | Roll-forward and balance sheet flux proceed; P&L comparatives unavailable, disclosed |
  | GL detail | Validate the TB alone; reconciliation and cleanup will be blocked and say so |
  | Statements | Mark cash and card accounts unverifiable this period; the reconcile phase carries the exception |
  | Subledgers and schedules | Mark those balances unsupported; adjustments will need them for roll-forwards |

- **Ask vs proceed.** Fact: the data can settle it; derive it, never ask. Precedent: prior
  periods settle it; follow and note it. Judgment: below materiality take the conservative
  path, proceed, and disclose; above materiality, hard to reverse, or in a profile-flagged
  risk area, queue a question. Raise queued questions once, at the end, inside the report.
  Unattended, take every proceed-and-disclose default and finish with disclosed exceptions.
- **Write a question down the moment it is queued** (close log or exceptions register). A
  question held only in working memory will be silently answered.
- **Track the running total of proceed-and-disclose judgments.** When the aggregate crosses
  materiality, convert open ones to questions and say the aggregate out loud. Twenty
  immaterial guesses are one material guess.
- Figures come from the provided data. An unsupported number is a gap on the request list,
  never an estimate. **A recorded profile fact with no evidence is a gap, never an ignore.**
- State the verdict plainly: "ready with exceptions" names the exceptions, never rounds up.
- Voice, for every document this skill writes: a careful accountant's prose, not an
  assistant's. Short declarative sentences, sentence-case headings, real figures. Banned
  tells: em dashes, filler words, "not just X, but Y", AI boilerplate, decorative emoji,
  bolded keyword openers. If no accountant would say it aloud to a client, rewrite it.

## Example

```markdown
### Intake: <client>, <period>
**Verdict:** <ready / ready with exceptions / blocked>
**Provided:** <files received and what each covered>
**Proven:** <TB balanced, GL tie-out result, roll-forward result>
**Gaps:** <each missing item and what it blocks>
**Request list:** <client-ready message, per reference/request-list-format.md>
**Next step:** <one action>
```

## Completion

Done when:

- [ ] Every provided file is classified and either used or explicitly set aside with a reason
- [ ] The TB balances, or the imbalance is quantified and flagged
- [ ] Every TB account either ties to the GL or is on the exceptions list with the difference
- [ ] Every BS account is mapped: supported, or on the request list with what its absence blocks
- [ ] The verdict is stated (ready / ready with exceptions / blocked) with blocking items named

Cleanup: report filed in `workpapers/` with input row counts and control totals; one copy of
each input in the close folder's `inputs/`; outcome appended to the close log when kept; queued
questions written into the report. Standalone: report delivered, close folder offered.
