---
name: review
description: "Reviewer pass over a prepared close: re-derives every check from the underlying data and records a binary ready or not ready verdict with blockers routed to their owning phase. Use when reviewing a close before delivery, running flux analysis on draft statements, or when a manager asks to check work a preparer finished."
---

# Review

## Purpose

Fresh eyes on a prepared close. Re-derive every check from the underlying data, never from a
workpaper's own summary line. The verdict is binary, ready or not ready, with blockers routed
to the phase that owns the fix. The manager's entry point: any close folder, whoever or
whatever prepared it.

1. TB roll and balance sheet substantiation
2. Entries check and flux
3. Exceptions register, verdict, review report

## Procedure

- [ ] 1. Locate the close folder (`closes/<client>/<period>/`, or `closes/<period>/` in a
      single-client workspace) with `inputs/`, `workpapers/`, the close log when kept, and
      the client profile for materiality and risk areas. No close folder: review what the
      user provides (a TB and draft statements at minimum), scope the verdict to it.
- [ ] 2. TB roll: prior TB plus GL activity plus approved adjustments equals the final
      On Kick: guides and pull mapping in `reference/kick.md`. Other connectors: discover at runtime, never guess names.
      adjusted TB, account by account. List every account that does not roll.
- [ ] 3. Substantiation: every material balance sheet account ties to a reconciliation proof,
      a schedule, or a named register exception; none of the three is a blocker.
      First-period equity: the equity roll (contributions traced to cash receipts plus
      income); later periods carry it via the roll-forward. Reality check: every
      profile-recorded fact (contracts, inventory, loans, leases, related parties, foreign
      currency) maps to evidence or a named exception; a fact the close never touched is a
      finding.
- [ ] 4. Entries check: every approved JE-register entry appears in the adjusted TB at the
      approved amount; no unapproved entry leaked in. Reversal flags set per the register.
- [ ] 5. Flux: compare the adjusted P&L and balance sheet to prior period. Each move above
      materiality gets its explanation from GL detail (what actually drove it), never from
      plausibility; profile risk areas get explained regardless of size. Deep driver
      decomposition belongs to advisory. Screens ride along: receivables aged past 90 days
      or stale against their own history, and fixed assets with impairment indicators
      (idle, damaged, discontinued line, fully depreciated but load-bearing), become memo
      disclosures, measurement routed to the preparer; the close never books either.
- [ ] 6. Exceptions register: every open item has an owner phase and a disclosure; nothing
      aged out silently. Items marked investigate are resolved or consciously accepted.
- [ ] 7. Verdict. **Ready**: all checks pass; open exceptions disclosed and below
      materiality, or explicitly accepted, recording who. **Not ready**: any check fails or
      an unaccepted material exception remains; list each blocker with its owning phase
      (readiness, reconcile, cleanup, adjustments) so the fix lands in the right place.
- [ ] 8. Record the verdict in the review report filed in `workpapers/` (and the close log
      when kept). The review report is what unlocks the deliver skill.

## Guardrails

- **One exception is unacceptable at any size**: books that do not balance or an unexplained
  difference inside the data itself. That always blocks.
- **Acceptance above materiality is informed consent, never a checkbox.** Present each such
  exception one at a time with its consequence in the deliverable's terms ("accepting this
  means the balance sheet shows $7,000 of receivables nobody has verified"); never batch
  material acceptances. An acceptance substantively the client's (an unsupported material
  balance, a judgment on their revenue) may be operator-accepted, memo-disclosed as pending client confirmation.
- **Reviewing the summary.** Confirming a workpaper by reading its own conclusion. The tell: a
  review pass with no recomputation. Every check re-derives from data.
- **The narrative flux.** An explanation equally true of any period ("revenue grew due to
  increased sales"). The tell: no transaction, customer, or vendor named. Cite the GL.
- **Verdict creep.** "Ready, mostly" or "ready pending items". The tell: qualifiers on the
  word ready. The verdict is binary; pending material items mean not ready.
- **Staleness is judged by content, never file dates** (timestamps lie when folders move).
  The report records the figures it reviewed: adjusted TB totals, entry count and total,
  exception count. When the books or workpapers no longer match, the review reruns.
- A missing input downgrades the review; the fallback is disclosed.

  | Missing input | Fallback |
  | --- | --- |
  | Prior TB | Flux limited to accounts with prior data; say comparatives were unavailable |
  | Prior TB with balance sheet accounts only (post-closing) | Balance sheet flux proceeds; P&L flux unavailable, disclosed. TB roll treats P&L accounts as opening at zero |
  | Prior TB carrying YTD P&L balances | TB roll rolls P&L accounts from prior YTD; state the assumption |
  | Workpapers for an account | That account fails substantiation; route to its owning phase |
  | Close log | Derive scope from the artifacts and books alone; note the review ran without a log |

- **Ask vs proceed.** Fact: the data settles whether a check passes; derive it, never ask.
  Judgment: a material disclosed exception is the user's call; below materiality, accept,
  disclose, move on. Queue judgment calls, written down as queued; raise once with the draft
  verdict. Unattended, a material unaccepted exception means not ready; never accept for the user.
- **Aggregation is a review check**: sum proceed-and-disclose judgments and disclosed
  exceptions; an aggregate above materiality is itself a material finding even when each piece was small.
- Independence: recompute; never accept a stage's self-report as evidence. The verdict cannot
  be negotiated past a failed check. Read-only: no proposed entries, no workpaper edits; it routes.
- Voice, for every document this skill writes: a careful accountant's prose. Banned tells: em
  dashes, filler words, "not just X, but Y", AI boilerplate, decorative emoji, bolded keyword
  openers. Rewrite anything no accountant would say aloud to a client.

## Example

```markdown
### Review: <client>, <period>
**Verdict:** <ready / not ready>
**TB roll:** <clean, or accounts listed>
**Substantiation:** <n of m material BS accounts tied; failures listed>
**Entries:** <register vs TB result>
**Flux:** <each material move: amount, driver from GL>
**Blockers:** <each with owning phase, or omit when ready>
**Accepted exceptions:** <each with who accepted it, or omit>
```

## Completion

Done when:

- [ ] TB rolls account by account, or every non-rolling account is a named blocker
- [ ] Every material BS account is substantiated or a named blocker
- [ ] Register and adjusted TB agree: all approved entries in, no unapproved entries in
- [ ] Every flux above materiality and every risk-area move has a GL-sourced explanation
- [ ] The verdict is recorded in the review report with blockers routed to owning phases

Cleanup: review report filed in `workpapers/` recording the figures reviewed (adjusted TB
totals, entry count and total, exception count); verdict in the close log when kept; material
acceptances recorded with who accepted, client-owned ones pending client confirmation.
