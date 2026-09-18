---
name: close
description: "Runs a full accounting close for one client and one period, from readiness check to delivered close package, by sequencing the intake, prep, adjust, review, and deliver skills. Derives where the close stands from evidence, batches questions at phase boundaries, and stops the moment a phase is blocked. No entry is marked approved and no close called complete without explicit confirmation. Use when asked to close a period: /close with the client and period."
argument-hint: "<client> <period>"
disable-model-invocation: true
---

# Close

## Purpose

Run one client's close through five phases; six skills do the work, this skill sequences
them, derives where the close stands from the evidence, and stops when a phase blocks.

1. Intake: inputs present and validated
2. Prep: reconcile, then categorize
3. Adjust: JE register staged and gated
4. Review: ready verdict or routed blockers
5. Deliver: package tied to the adjusted TB

## Procedure

- [ ] 1. Parse `<client>` and `<period>` (month `2026-07`, quarter `2026-Q2`, or `FY2025`).
      Resolve the client: explicit argument; a root `profile.md` or a client named in project instructions (single-client workspace, no client name needed); a near-match under `clients/`. Ask only when none resolve or the period is missing. Profile location decides layout: root profile means `closes/<period>/`, a profile under `clients/<name>/` means `closes/<client>/<period>/`, even with one client.
- [ ] 2. Gather client context from every readable source before asking, trusted in order: profile (file, project instructions or knowledge, connected store), then memory and prior conversations (orientation only: form hypotheses, re-verify against data before relying on them). No profile anywhere: check `clients/` for a near-match and confirm before treating as new, then offer the choice and wait: run close-setup now, or proceed on the defaults below. Proceeding without asking is for unattended runs only, and the deliverable says so.
- [ ] 3. Derive close state from evidence everywhere it could live: this workspace, the named state home, project documents, connected stores. Play the derived state back before doing anything: phases done, what is open, whose work. Resume from the first phase whose evidence is incomplete. Never start a second close for a period when evidence of one exists.
- [ ] 4. Pick where the run writes: the close folder (`inputs/`, `workpapers/`, `package/`) in the state home the profile names, or this workspace. `inputs/` is the canonical data set: source files provided elsewhere get one copy here; if the two ever differ, stop and confirm which is current before any phase builds on either.
- [ ] 5. Run the phases in order, each via its skill. At each boundary: report the phase in one line, raise the batched questions, write the artifact where the team will find it, append the close log when kept, offer the one-line announcement when the profile names a channel, and stop for the user. Never roll into the next phase in the same turn.
- [ ] 6. Wrap the run (or a stop) with the run-level summary in Example.

| Phase | Skill | Done when | Evidence it is done |
| --- | --- | --- | --- |
| Intake | intake | Every required input present, or on the request list with impact stated | Inputs validated for the period; readiness report with gaps resolved or disclosed |
| Prep | prep (reconcile, then categorize) | Every account reconciled or excepted; cleanup list dispositioned | Rec proof per in-scope account that still foots; every uncategorized or unmatched-transfer item dispositioned or on the exceptions register |
| Adjust | adjust (entries under the je contract) | Every entry approved, declined, or blocked with its missing source named | JE register exists; every required entry posted, approved-pending, or disclosed |
| Review | review | Verdict: ready, or blockers routed to owning phases | Ready-verdict report postdating the latest change to books and workpapers |
| Deliver | deliver | Package filed; every figure ties to the adjusted TB | Package files exist and tie to the books as they stand |

Exceptions register, at `workpapers/exceptions-register.md`, one table every phase reads
and writes: `| # | Item | Amount | Raised by | Owned by | Status | Disclosure |`. Raised
by and Owned by are phases; status is open, resolved, or accepted (with who accepted).
Items are appended, never deleted, numbered in the order raised; a resolved item keeps its
row. A stage skill run standalone creates the same table next to its artifact.

## Guardrails

- State is derived from evidence, never from a file's say-so. "In the books" is strongest: a posted entry needs no other record. An artifact counts when it still agrees with current data; re-run the cheap check (does the proof still foot? is the register in the TB?) rather than trusting its conclusion. A close log speeds orientation but never outranks the evidence.
- Conflicting sources (two internally consistent records that disagree, no arbiter on hand): run the constant-difference test first (difference per account per period; constant dates to the opening, moving to period activity), argue each reading from behavior, name the document that would settle it, and put it on the request list. Proceed only when the arbiter arrives or the user picks a basis with the conflict disclosed as a blocking exception. Never average, never pick silently.
- A profile or note claiming a past close is a claim: verify against artifacts and books; when the workspace contradicts it, say so and ask. Inherited open questions re-raise at the next phase boundary; a question gating a later phase travels to that boundary.
- Approvals: posted to the books is approved and done. Register marks are honored only when corroborated by a close-log entry in this workspace or the named state home; otherwise they are proposals, re-confirmed before any entry enters an import CSV. Never infer an approval from a past conversation or memory.
- A blocked phase stops the close; a phase carrying blocked items is not blocked (adjust with every entry approved, declined, or blocked-with-source-named is complete; review routes its blockers). Route each exception to the owning phase; never skip forward to make the close look complete.
- Batching is for flow, never for gravity: an acceptance or approval above materiality is presented on its own with its consequence stated. When the aggregate of small proceed-and-disclose judgments crosses materiality, the batch converts to questions. Interrupt mid-phase only for the JE approval gate or a true blocker. Write each question down (close log or exceptions register) the moment it is queued.
- A later finding that invalidates an earlier phase sends the close back: fix and rerun from there.
- Unattended runs take every proceed-and-disclose default and finish with a disclosed-exceptions close; entries stay proposed, approval always needs a human.
- No durable workspace (plain chat): deliver each artifact inline and end the phase naming exactly what to save where. Unsaved work is undone work to the next session's derivation; say so.
- Defaults with no profile: accrual basis if the TB carries AR, AP, or accrued liabilities, otherwise cash, inference stated. Materiality: the greater of $500 or 1% of period expenses before adjustments (a stable base; adjustments must not move their own gate), confirmed at the first judgment call and recorded. No risk areas flagged; standard scrutiny everywhere.
- A derived figure enters a document only from an executed computation, never from arithmetic performed in prose. A gap is an exception, never an estimate.
- A correction propagates or it did not happen: when a figure changes, re-check every artifact that quoted it; anything appearing in more than one artifact is generated from its single source, never retyped.
- Never claim a phase ran if its skill's instructions were unavailable; stop and name what is missing. Reading the stage skill's SKILL.md from the installed plugin and following it counts as running it. Phase skills own their own gates; starting a close is not approval for anything a later phase wants to do.

## Example

```markdown
### Close: <client>, <period>

**Result:** <delivered / stopped at <phase>>
**Phases:** <derived state per phase>
**Exceptions:** <open items with owners, or none>
**Approvals:** <entries approved, by whom, evidenced where>
**Next step:** <one action>
```

## Completion

Done when:

- [ ] Every phase derives as done per the table, or the run reports where it stopped and why
- [ ] Every exception is open with an owner, resolved, or accepted with who accepted
- [ ] Every approval is evidenced in the books or corroborated by a close-log entry
- [ ] The run-level summary is delivered

Cleanup: artifacts sit in the close folder (`inputs/`, `workpapers/`, `package/`) in the
chosen state home; open questions live on the exceptions register or in `STATUS.md`, the
optional append-only close log (one line per decision, approval, question outcome, and
phase completion, with who and when; a resuming session with no log starts one, opening
with the derived state it resumed from). Nothing ends in working memory.
