---
name: coa-cleanup-and-reclass
description: "Reviews a Kick entity's chart of accounts and a full year of transactions, proposes a cleaner revenue and expense structure with an old-to-new mapping, then applies approved CoA changes and bulk-reclasses transactions into the new structure with a change log. Each write phase is previewed separately before posting. Use when a customer says 'clean up our chart of accounts', 'propose cleaner revenue and expense categories', 'restructure the CoA and reclass the year', or 'remap every transaction into a new account structure with a change log'. Not for moving txns between two existing accounts only; that is bulk-account-reclassifier."
---

# CoA cleanup and reclass

## Purpose

Propose a cleaner revenue and expense chart of accounts for one entity, move every in-scope
transaction in the window into it, and hand back a change log. Nothing posts until the user
approves the proposal, and each write phase gets its own preview and confirm.

1. Phase 1: read the chart of accounts and the window's activity, then propose.
2. Phase 2a: chart-of-accounts writes (groups, new accounts, renames, regroups, merges, and
   disables of emptied sources).
3. Phase 2b: one bulk reclass of the activity still on old accounts.
4. Phase 3: the change log, with before and after figures from fresh reads.

Not this skill: a move from one existing wrong account to one existing right account with no
redesign (bulk-account-reclassifier); uncategorized-queue triage alone
(kick-uncategorized-gl-review); importing a full external chart of accounts as the main job,
with no redesign conversation (the connector's own CoA migration guide).

On Kick, load [references/kick.md](references/kick.md) before step 1.

## Procedure

Copy this checklist into the response and check items off as you go.

- [ ] 1. Load the connector's CoA migration and transaction review guides.
      Also load the GL-first guide when the workspace classifies by GL account (GL-first).
- [ ] 2. Resolve the entity, its workspace, and its ledger and basis. Confirm the window.
      Reads only through step 5. Never ask the user for an ID.
- [ ] 3. Pull the current chart of accounts and the window's activity.
      Monthly P&L for the window, plus account detail for noisy or duplicate accounts. Quote
      the report lines that justify each change. Empty read: name the entity and window read,
      and ask the user to confirm the entity or widen the window. A new entity with no
      activity goes structure-only (CoA changes, no reclass) only on the user's yes.
- [ ] 4. Draft one proposal the user can approve or edit.
      - Keep: accounts that are clean and used.
      - Create: clearer revenue and expense accounts, with name, type, subtype, and parent group.
      - Rename or regroup: accounts whose name or placement is wrong, updated in place.
      - Merge: each true duplicate merges into one survivor, so its balances and transactions
        move there.
      - Disable: accounts that should stop receiving activity. Never hard-delete.
      - Old-to-new mapping for every in-scope source account with activity in the window.
      - Change-log skeleton: account actions plus the expected count per mapping line, from
        transaction statistics or report reads.
- [ ] 5. Get explicit approval of the proposal.
      One message, one ask. Revise on pushback. No write preview until the structure is agreed.
- [ ] 6. Phase 2a: apply the approved CoA writes.
      Order: groups first, then new accounts, then renames and regroups, then merges, then
      disables of emptied sources. For each write: preview the change, show the summary, wait
      for one explicit confirm, apply it once with the identical input. A homogeneous batch is
      one preview, one stated count, one yes. Where the connector has no merge write, the
      binding gives the equivalent path and where it falls in this sequence.
- [ ] 7. Phase 2b: build the reclass set from post-2a reads.
      Resolve the destination for every mapping line. Merges already moved their sources'
      activity, so pull only activity still on old accounts. For each line, page the
      transaction finder over the window, filtered to the entity and the old account. Finder
      transaction IDs are the only payload IDs. Each ID appears in one mapping line only.
- [ ] 8. Phase 2b: preview one bulk reclass, confirm, apply once.
      State the count. GL-first: set the GL account only, never a category. Category-first:
      set the new category, keeping category and GL aligned. Huge sets go in user-agreed date
      chunks, each its own preview and yes. Echo what posted.
- [ ] 9. Offer ongoing coding rules only if the user asks.
      A separate preview and confirm, with apply-to-existing transactions set explicitly.
- [ ] 10. Phase 3: deliver the change log in the Example format.
      Actions taken, the old-to-new mapping, counts moved from preview and statistics
      responses, and before and after P&L lines and net income from fresh reads.

## Caveats

- **Two-phase discipline.** Proposal approval first, then CoA write previews, then the reclass
  preview. Tell: one confirmation covering account changes and transaction remaps. Never
  combine them under one confirmation.
- **One preview, one ask per write or batch.** No auto-confirm. Never chain a preview straight
  into the apply. The original request is not approval.
- **No hard deletes of accounts.** Tell: a delete anywhere in the plan. Cleanup is merge or
  disable. If the user insists on deleting, explain the safer pattern and proceed only with an
  operation the loaded guide and live tools allow, after a clear yes. Never instruct
  irreversible deletion.
- **Merges have blast radius.** The merge preview names source and survivor, and what moves:
  balances and transactions. The disable preview names every account that stops receiving
  activity.
- **GL-first takes the GL account only.** Tell: a category on a GL-first reclass line; the
  connector rejects it. Speak to the user in their own word, "category".
- **Figures from reads and previews only.** Change-log counts and before and after amounts come
  from tool responses. Tell: hand-built monthly totals or mental arithmetic on books totals.
- **Materiality is for ranking.** A threshold used to order the proposal is labeled assumed and
  never appears as a posted figure.
- **Resolve every ID by query.** Never ask for an ID, never guess one. Tell: a workspace ID
  passed where the entity ID belongs.
- **Date fields differ by read.** Transaction reads and report reads take different date
  fields, and ledger-scoped reports need the ledger. The binding names each.
- **Reports are not payloads.** Report rows inform the proposal and baselines only. Tell: a
  reclass payload built from report rows.
- **Double remap.** Tell: one transaction ID in two mapping lines, a merged source's rows in
  the reclass set, or an ID list built before Phase 2a landed. Rebuild from post-2a reads;
  each ID appears once.
- **Ambiguity goes to the user.** Competing survivors, or unclear revenue versus expense
  placement, get options, not a silent pick.
- **No silent rules.** Never create a coding rule "for next time" without its own preview.
- **Simple moves belong elsewhere.** Tell: both accounts already exist and the proposal has no
  create, rename, or merge line. Defer to bulk-account-reclassifier.
- **Locked period stops the run.** A write rejected for a closed period stops; ask the user.
  Never retry into it. Expired approvals follow the binding.
- **Rollback.** A posted batch that proves wrong is reverted through the connector's undo
  path, with its own preview and confirm. A wrong disable is re-enabled the same way.
- **Net income ties.** Remaps between revenue and expense accounts leave net income for the
  window unchanged. Tell: the before and after reads differ. Name the mapping line that moved
  activity off the P&L.
- **In-run corrections.** A user correction to an assumption, format, threshold, or account
  choice applies at once and holds for the run. It never overrides previews, confirmations, or
  figures from reads.
- **Drift.** A rejected call follows the drift rule in the binding. Never edit this skill file
  mid-run.

## Example

Request: "Review the chart of accounts and every 2025 transaction for Summit Coaching, propose
cleaner revenue and expense categories, reclass everything into the new structure with a
change log. Preview before posting."

The workspace is category-first, on the accrual ledger. Phase 1 found three near-duplicate
software accounts and two vague revenue buckets. The proposal created three accounts, merged
SaaS Tools and Subscriptions into Software (the user kept "Software" as the survivor name),
disabled the two emptied duplicates, and mapped three source accounts for the reclass. Each
write below ran under its own preview and one yes.

```markdown
## Change log: Summit Coaching, 2025-01-01 to 2025-12-31

| # | Phase | Action | From | To | Count | Figure source | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2a | Create | | 4010 Coaching Revenue | | Create preview | Posted |
| 2 | 2a | Create | | 4020 Workshop Revenue | | Create preview | Posted |
| 3 | 2a | Create | | 6410 Professional Development | | Create preview | Posted |
| 4 | 2a | Merge | 6120 SaaS Tools | 6110 Software | 48 | Merge preview | Posted |
| 5 | 2a | Merge | 6130 Subscriptions | 6110 Software | 31 | Merge preview | Posted |
| 6 | 2a | Disable | 6120, 6130 | | 2 accounts | Disable preview | Posted |
| 7 | 2b | Reclass | 4000 Sales | 4010 Coaching Revenue | 29 | Bulk reclass preview | Posted |
| 8 | 2b | Reclass | 4900 Other Income | 4020 Workshop Revenue | 12 | Bulk reclass preview | Posted |
| 9 | 2b | Reclass | 6990 Misc Expense | 6410 Professional Development | 6 | Bulk reclass preview | Posted |

Reclass total: 47 transactions in one bulk preview. The merged sources' rows were not in it.

### Before and after (2025 P&L reads)

| Line | Before | After |
| --- | --- | --- |
| 4000 Sales | $58,000 | $0 |
| 4010 Coaching Revenue | | $58,000 |
| 4900 Other Income | $6,400 | $0 |
| 4020 Workshop Revenue | | $6,400 |
| 6110 Software | $4,200 | $8,640 |
| 6120 SaaS Tools | $2,880 | $0 |
| 6130 Subscriptions | $1,560 | $0 |
| 6990 Misc Expense | $1,150 | $250 |
| 6410 Professional Development | | $900 |
| Net income | $31,750 | $31,750 |

6990 Misc Expense keeps $250 of true miscellaneous spend and stays enabled.
```

This run's connector merged natively. On a connector with no merge write, such as Kick, rows
4 and 5 join the Phase 2b reclass instead (126 rows in that preview), row 6 follows it, and
each merge row's Action reads "Merge (reclass then disable on Kick)". The binding gives that
path; the before and after figures are the same.

## Completion

Done when:
- The user approved the proposal before any write preview.
- Each Phase 2a write and the Phase 2b reclass had its own preview and one explicit yes.
- No account was hard-deleted.
- Every merge preview named source and survivor, and each merged source was disabled only
  after its merge landed.
- Every mapping line shows a count from a preview or statistics response.
- Before and after P&L lines and net income come from fresh reads, and net income ties or the
  difference is named.
- The change log has the Example's columns.

Cleanup: the change log goes to the user in chat, or to the file they name. Residuals and
declined items sit in the log's Open lines with the user as owner. When a step worked
differently than the binding describes, the deliverable ends with the method note from the
binding.
