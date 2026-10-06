---
name: coa-cleanup-and-reclass
description: "Reviews an entity's chart of accounts and a full year of transactions, proposes a cleaner revenue and expense structure with an old-to-new mapping, then applies approved CoA changes and bulk-reclasses transactions into the new structure with a change log. Each write phase is previewed separately before posting. Use when a customer says clean up our chart of accounts, propose cleaner revenue and expense categories, restructure the CoA and reclass the year, or remap every transaction into a new account structure with a change log. Not for moving transactions between two existing accounts only."
---

# CoA cleanup and reclass

Important: this skill assists with chart-of-accounts redesign and transaction remapping and
does not provide financial advice. It writes to the books only after the proposal is approved
and each write phase echoes its full payload and receives one explicit "yes".

Goal: a user-approved cleaner revenue/expense CoA for the entity, every in-scope transaction
remapped into that structure, and a change log of what moved, with CoA writes and transaction
reclass each confirmed in their own preview round. Nothing posts until the user approves the
proposal, then each write phase.

## When to use

* "Review our chart of accounts and 2025 activity, propose cleaner categories, and reclass
  everything into the new structure with a change log."
* "Collapse duplicate expense accounts and remap the year."
* "Rebuild a messy P&L CoA and move the transactions."
* Use cases: CoA redesign proposal, duplicate/merge cleanup with remap, year-long
  reclassification into a new structure with a change log.
* Not this skill: bulk move from one existing wrong account to one existing correct account
  with no CoA redesign; uncategorized-queue triage alone; importing a full external CoA file as
  the primary job without a redesign conversation.

## Data you need

* The books and period: which set of books, ledger basis, and the year or window to redesign.
* Current chart of accounts: account names, types, and structure (including groups if used).
* Year activity: P&L and account activity that justify keep / create / merge / disable
  choices, plus the transaction population for later remap.
* Write capability: CoA create/update/merge/disable and bulk transaction reclass, each with
  a preview path.

## Workflow

Copy this checklist into your response and check items off as you go:

* [ ] 1. Confirm books; pull CoA + year activity (reads only)
* [ ] 2. Draft proposal: new/kept/merged/disabled accounts + old→new mapping + change-log skeleton
* [ ] 3. Get explicit approval of the proposal (no writes yet)
* [ ] 4. Phase 2a: apply CoA writes, each with its own echo → yes → write
* [ ] 5. Phase 2b: one bulk reclass preview for remaps; confirm; optional rules if requested
* [ ] 6. Deliver change log + before/after figures from fresh reads

### Phase 1: Orient, read, propose (no writes)

1. Confirm the books and window. Confirm which set of books and the year or date window.
2. Note how coding works. Some books post to chart-of-accounts accounts directly; others use
   categories. Remaps must use the field the books accept.
3. Pull the current CoA and ledger basis.
4. Pull year activity that informs the redesign: P&L for the year, and targeted account
   activity for noisy or duplicate accounts. Quote report figures; do not invent materiality
   math for books totals. Gather transaction ids for later remap when needed.
5. Draft one proposal the user can approve or edit:
   * Keep accounts that are clean and used.
   * Create clearer revenue/expense accounts (names, type/subtype, parent group).
   * Merge true duplicates into a survivor.
   * Disable accounts that should stop receiving activity (not hard-delete).
   * Old → new mapping for every in-scope source account that still has year activity.
   * Change-log skeleton: account actions + expected transaction remap counts from reads.
6. Ask for approval of the proposal before any write. One message, one ask. Revise if they
   push back. Do not preview a write until the structure is agreed.

### Phase 2a: CoA writes (own confirmation round per write/batch)

1. Apply approved CoA changes in a sensible order: create new accounts/groups first, then
   updates, then merges, then disables of emptied sources.
2. Each write is its own echo-payload → show summary → explicit yes → write. You may batch
   homogeneous rows (for example one bulk disable) when the tools support it; still state the
   count and get one yes for that preview. Never chain preview straight into confirm.
3. Never hard-delete accounts as the cleanup path. Prefer merge (balances and transactions
   move to the target) or disable. If the user insists on delete, explain the safer pattern and
   only proceed with an operation the live tools allow after a clear yes.
4. On lock-date errors: stop and ask. On a rejected write: re-echo; apply without re-asking only
   when the fresh preview matches the approved change.

### Phase 2b: Transaction reclass (separate confirmation round)

1. Resolve destination accounts (or categories) for every mapping line. Rebuild transaction
   lists from post-CoA reads: merges already move activity to the survivor, so only pull
   remaining source activity.
2. For each old→new mapping line still holding activity, gather the transaction ids over the
   year window. Report totals inform the proposal and change-log baselines only; the bulk
   payload uses the actual transaction identifiers.
3. One bulk reclass preview for the approved remap set (or user-agreed date chunks if huge).
   State the count. Use COA overrides when the books post directly to accounts; use categories
   when that is what the books accept.
4. After yes: write the identical payload. Echo what posted.
5. Optional: if the user wants ongoing automation, offer coding-rule creates or updates as a
   separate echo → yes → write, with "apply to existing" set explicitly. Never silently
   create rules.

### Phase 3: Change log deliverable

1. Deliver a change log with: CoA actions taken (create/merge/disable/update), old→new mapping,
   transaction counts moved (from preview/statistics responses), and a short before/after P&L
   or account snapshot from fresh reads. Label any assumed materiality threshold used only for
   proposal ranking, never as a posted figure.

## Working with your data

This skill reads and writes through whatever accounting system is connected. If you have
documented bindings for that system, use them. Otherwise:

### Unknown connector

1. List the available tools and read their schemas and descriptions.
2. Map them to the data needs above (CoA list, P&L and account activity, transaction population,
   CoA writes, and bulk reclass). Anything with no plausible tool is marked UNSUPPORTED.
3. STOP and show the user the mapping, and get confirmation, before any read or write beyond
   discovery.
4. Never guess tool names. If the system exposes guide or skill discovery tools, load the
   relevant CoA migration and transaction-review guides first.

## Guardrails

* Default-deny writes. Echo the full payload → one explicit "yes" → then write. No
  auto-confirm.
* Two-phase discipline. Proposal approval first; then CoA write previews; then reclass
  preview. Never combine CoA mutations and transaction remaps into one confirmation.
* One confirmation per write or batch. No auto-confirm.
* A rejected write restarts the confirmation flow.
* No hard deletes of accounts as the default cleanup. Prefer disable or merge.
* Stop on lock-date errors.
* Figures from reads/previews only. Change-log counts and before/after amounts come from
  system responses, never mental arithmetic for books totals.
* Ambiguity → ask. Competing merge targets or unclear revenue vs expense placement: options,
  not silent picks.
* Merges have blast radius. The preview must name source → target and that balances and
  transactions move before asking.
* Existing wrong→correct only? If the user already has both accounts and wants no redesign,
  defer to a bulk account reclassifier.
* Tool errors and drift: if a live call is rejected, trust the live error hint (and any
  loaded guide) over this skill's examples. Fix the call and retry once. A rejected write
  restarts the confirmation flow. If the working shape contradicts this skill's text, add a
  method note to the deliverable so it can be reported and fixed centrally. Never edit this
  skill file mid-run.

## Worked example

"Review the chart of accounts and every transaction posted in 2025 for Summit Coaching,
propose a cleaner set of revenue and expense categories, and reclassify each transaction into
the new structure with a change log. Preview before posting."

1. Confirm the books for Summit Coaching; accrual ledger; categories (not direct COA overrides).
2. Pull CoA and 2025 P&L → several near-duplicate expense accounts (Software, SaaS Tools,
   Subscriptions) and two vague revenue buckets. Quote the report lines that justify the
   proposal (illustrative).
3. Proposal shown: create "Software Subscriptions"; merge "SaaS Tools" and "Subscriptions" into
   it; rename vague revenue accounts; disable emptied duplicates after merge; mapping table for
   five source accounts → destinations; expected remap counts. User approves with one edit (keep
   "Software" as the survivor name).
4. Phase 2a: create/update/merge/disable each echoed and confirmed in turn (merge preview names
   source → target). No deletes.
5. Phase 2b: for each non-merged source still holding activity, gather remaining transaction
   ids; skip sources emptied by merge. Assemble 126 remaining ids → one bulk reclass preview
   stating 126 → user yes → write.
6. Change log delivered; fresh P&L read quoted for the cleaned expense section.

## Common pitfalls

* Writing CoA changes before the user approves the proposal structure.
* Combining account creates and transaction remaps under one confirmation.
* Hard-deleting accounts instead of merge/disable.
* Remapping with the wrong coding field for how the books store categories vs accounts.
* Hand-building monthly totals instead of quoting report responses.
* Silently creating coding rules for "next time" without a separate preview.
* Treating a simple two-account move as this skill; that belongs to a bulk account reclassifier.

## Related skills

* Bulk account reclassifier: wrong → correct existing accounts only; no CoA redesign.
* Uncategorized review: uncategorized queue, not a full CoA redesign.
* Activity undo / audit guides for the connected system when a remapped batch needs review.

## Feedback and improvement

This copy of the skill belongs to the person running it, and it should get better
with use.

* During a run: when the user corrects an assumption, an output, or a preference
  (tone, format, thresholds, account or entity choices), apply the correction
  immediately and keep it for the rest of the run. A correction never overrides the
  safety contract: previews, confirmations, and figures-from-reads always stand.
* Between runs: when a correction should stick, offer to save it. With the user's
  explicit approval, add a dated entry under `## Learned preferences` at the end of
  this file, creating that section if it is missing. Newer entries beat older ones.
  Never edit this skill file mid-run, and never change the Guardrails, Tools used, or
  safety wording: preferences and defaults only. A preference is declined, not saved,
  when honoring it on a future run would loosen any Guardrails line or the safety
  contract, even though it leaves their text untouched. If this file is not writable
  where the skill runs, give the user the entry text to save wherever they keep their
  instructions.
* Improving the original: if someone sent the user this skill, end the deliverable
  with one plain-English line describing what worked differently or which preference
  was saved (inside the deliverable's method notes, when this skill's output template
  has them), and ask them to forward it to whoever maintains the original copy.
