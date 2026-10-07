# Kick binding: coa-cleanup-and-reclass

Loaded at Procedure step 1 when Kick is connected, and used through step 10. It reads the
entity's chart of accounts, ledger, P&L, and transactions, then writes account groups,
accounts, and one bulk transaction reclass. Every tool and parameter here comes from the Kick
connector pack. Where the public reference stops at `payload` or `filters`, the inner keys
come from the loaded guide at run time; the hints below are marked unconfirmed where they are
not in Kick's public tool reference.

## Published guides

Discover with `list_kick_skills` (query "coa bulk migration transaction review",
`includeHeader: true`), then `load_kick_skill` the match by its exact `name`. Guide names are
not guessable; use the ones the list returns.

| Guide | Serves |
| --- | --- |
| `kick/coa-bulk-build-and-migration` | Step 1 load. Steps 4 and 6: account and group payloads for create, update, disable; dedupe before create; groups before children. The merge disables |
| `kick/transaction-review-and-categorization` | Step 1 load. Step 8: the bulk update payload for the reclass |
| `kick/gl-first-workspaces` | Load as soon as step 2 reads `glFirstEnabled: true`, before any step 3 read. Steps 7 and 8: the `accountOverrides` shape; never `categoryId` |
| `kick/entity-lookup` | Step 2: entity name to numeric `entityId` and its `workspaceId` |
| `kick/chart-of-accounts-and-ledger-lookup` | Steps 2, 3, 7: account IDs and codes, `ledgerId` and basis |
| `kick/financial-reports` | Steps 3 and 10, merge re-reads: report params, account scoping for `account_transactions` |
| `kick/find-and-query-transactions` | Steps 4 and 7, merge re-reads: `find` and `statistics` filter keys, paging |
| `kick/transaction-rules` | Step 9: rule payload, dry run, `applyToExistingTransactions` |
| `kick/activity-undo` | Rollback (Caveats): batch revert fields |

## Tools used

| Tool | Operation / report | Purpose |
| --- | --- | --- |
| `list_kick_skills`, `load_kick_skill` | (none) | Find and load the guides above |
| `context_resolve` | `target`: `entity`, `workspace`, `ledger` | Numeric `entityId`, `workspaceId` UUID, `ledgerId` |
| `context_browse` | `workspaces` | `glFirstEnabled` on the workspace; nested entity summaries |
| `accounting_query` | `ledgers_get`, `accounts_list`, `accounts_get_workspace` | Ledger and basis; current CoA with account UUIDs and codes |
| `reports_query` | `chart_of_accounts`, `profit_loss`, `account_transactions` | Structure, window activity, account detail, before and after figures |
| `transactions_query` | `find`, `statistics` | Reclass IDs; expected and moved counts |
| `categories_query` | `search` | Category IDs, category-first workspaces only |
| `opening_balances_query` | `get` | Opening balance left on a merge source before its disable |
| `accounting_act` | `create`, `update`, `bulk_update`, `bulk_disable`, `bulk_enable` | Phase 2a account writes and the disables that complete a merge; `bulk_enable` only to undo a wrong disable |
| `account_groups_act` | `create`, `update` | Group structure the proposal needs |
| `transactions_act` | `bulk_update` | Phase 2b reclass, merge lines included |
| `rules_query` | `groups_list`, `matching_transactions` | Resolve `ruleId`; dry-run a rule before creating it |
| `rules_act` | `create`, `update` | Optional ongoing rules, only on request |
| `activity_query` | `list`, `details_get` | Find and inspect a posted batch to roll back |
| `activity_undo` | (none) | Revert a posted batch |

Never used: `accounting_act` `bulk_delete` (hard delete); `account_groups_act` `delete`;
`categories_act` (blocked in GL-first, and creating categories is outside this job); any
transaction delete (this skill deletes nothing).

## Call shapes

Orientation (step 2).

- `context_resolve` `{ "target": "entity", "query": "Summit Coaching" }`. Trap: `entityId` is
  a positive integer, `workspaceId` is a UUID; never pass one where the other belongs. If the
  response lacks the `workspaceId`, use `context_resolve` `{ "target": "workspace", "query":
  "<name>" }` or the nested entity summaries from `context_browse`. Confirm the entity by name
  with the user before reading.
- `context_browse` `{ "operation": "workspaces", "limit": 25 }`. Trap: `workspaces` is its only
  operation. Read `glFirstEnabled` from the matching workspace row.
- `accounting_query` `{ "operation": "ledgers_get", "entityId": 287 }`, or `context_resolve`
  `{ "target": "ledger", "entityId": 287 }`. Trap: takes the numeric `entityId`; the result
  gives `ledgerId` and basis.

Chart of accounts (step 3, and the fresh destination read in step 7).

- `accounting_query` `{ "operation": "accounts_list", "entityId": 287 }`. Trap: per entity, by
  numeric `entityId`; account rows carry the `accountId` UUIDs every account write needs.
- `accounting_query` `{ "operation": "accounts_get_workspace", "workspaceId": "<workspaceId>" }`.
  Trap: takes the UUID. In GL-first workspaces this catalog gives the reclass destinations and
  the `filters.coaAccounts` values.
- `reports_query` `{ "report": "chart_of_accounts", "params": { "workspaceId": "<workspaceId>" } }`.
  Trap: the only report keyed by `workspaceId`; no dates. Take `groupId` values from the
  chart-of-accounts reads as the guide names them; if no read returns one, stop and ask.

Window activity (step 3, and the after read in step 10).

- `reports_query` with `profit_loss`:

```json
{
  "report": "profit_loss",
  "params": {
    "entityId": 287,
    "ledgerId": "<ledgerId>",
    "startDate": "2025-01-01",
    "endDate": "2025-12-31",
    "cycle": "month"
  }
}
```

  Trap: dates are `startDate` and `endDate` inside `params`, never `since` and `until`;
  `ledgerId` is required. One call with `cycle: "month"`, never one call per month.
- `reports_query` `{ "report": "account_transactions", "params": { "entityId": 287, "ledgerId":
  "<ledgerId>", "startDate": "2025-01-01", "endDate": "2025-12-31", "accountCodes": [6120] } }`.
  Trap: `entityId` and `ledgerId` are the confirmed required params. The dates and
  `accountCodes` are not in the public reference (unconfirmed). If either is rejected,
  follow the error and `kick/financial-reports`; if the account scope still fails, count that
  account with `transactions_query` `statistics` scoped to it and say the count covers
  transactions only, not manual journal lines.
- An empty read (no P&L lines, `find` `total` 0): before reporting it, check that `entityId`
  came from the entity resolve, `ledgerId` from that entity's ledger, and the dates sit in the
  right fields for that call. Then follow step 3's empty-read rule.

Counts and reclass IDs (steps 4 and 7, merge re-reads, step 10).

- `transactions_query` `find`:

```json
{
  "operation": "find",
  "workspaceId": "<workspaceId>",
  "since": "2025-01-01",
  "until": "2025-12-31",
  "filters": { "<entity and old-account keys from the guide>": "..." },
  "fields": ["id", "date", "amount"],
  "limit": 100
}
```

  Trap: dates are top-level `since` and `until`, never inside `filters`. Maximum `limit` is
  100; page with the returned `nextCursor` until it is `null`. Only `find` row `id` values go
  in a reclass payload, never report rows.
- `transactions_query` `{ "operation": "statistics", "workspaceId": "<workspaceId>", "since":
  "...", "until": "...", "filters": { ... } }`. Trap: same date and filter semantics as `find`.
  Filter keys: GL-first scopes by GL account with `filters.coaAccounts`;
  category-first scopes with `filters.categoryIds` (not in the public reference, unconfirmed). If a
  key is rejected, follow the error and `kick/find-and-query-transactions`. The entity scope
  key is not in the pack; take it from that guide.
- `categories_query` `{ "operation": "search", "workspaceId": "<workspaceId>", "search":
  "Coaching Revenue" }`. Trap: category-first only; in GL-first, `categoryId` is rejected. More
  than one plausible match goes to the user.

Account and group writes (step 6, and the merge disables). Payload keys come from
`kick/coa-bulk-build-and-migration`.

- `accounting_act` `{ "operation": "create", "workspaceId": "<workspaceId>", "payload": { ... } }`.
  Trap: takes the UUID, not `entityId`. Hint (not in the public reference, unconfirmed): `name`,
  `type`, `subtype`, `entityIds`, `parentGroupId`. Scope `entityIds` to the target entity only.
  If a key is rejected, follow the error and the guide.
- `accounting_act` `{ "operation": "update", "entityId": 287, "accountId": "<UUID from
  accounts_list>", "payload": { ... } }`. Trap: requires both the numeric `entityId` and the
  `accountId` UUID. One account per call: renames and single regroups.
- `accounting_act` `bulk_update`, `bulk_disable`, `bulk_enable`: `{ "operation": "bulk_disable",
  "payload": ... }`. Trap: `payload` is the only required field. Hint (not in the public reference,
  unconfirmed): a list of `accountId` and `entityId` pairs, with `bulk_update` adding the shared
  fields. If rejected, follow the error and the guide; for a regroup, fall back to one `update`
  per account.
- `account_groups_act` `{ "operation": "create", "workspaceId": "<workspaceId>", "payload": { ... } }`.
  Hint (not in the public reference, unconfirmed): `name`, `class` (`Income` or `Expenses` for this
  skill), `initialChildAccountIds`. If rejected, follow the error and the guide.
- `account_groups_act` `{ "operation": "update", "workspaceId": "<workspaceId>", "groupId":
  "<group UUID>", "payload": { ... } }`. Trap: requires `groupId` from a read.

Reclass (step 8). One call for the approved set, or one per user-agreed date chunk.

```json
{
  "operation": "bulk_update",
  "workspaceId": "<workspaceId>",
  "payload": { "transactions": [ { "transactionId": 12345, "<destination>": "..." } ] }
}
```

- Trap: `transactionId` is a positive integer from `find`. GL-first sends `accountOverrides`
  only, shape from `kick/gl-first-workspaces`; `categoryId` is rejected there. Category-first
  sends the new `categoryId`. The `payload.transactions` list is a hint not in the public
  reference (unconfirmed); if rejected, follow the error and
  `kick/transaction-review-and-categorization`.

Rules (step 9, only on request).

- `rules_query` `{ "operation": "groups_list", "workspaceId": "<workspaceId>" }`. Trap: the
  source of `ruleId` and the rule `groupId`; never guess either.
- `rules_query` `{ "operation": "matching_transactions", "workspaceId": "<workspaceId>",
  "payload": { ... } }`. Dry run before `create`.
- `rules_act` `create` (`workspaceId`, `payload`) and `update` (`workspaceId`, `ruleId`,
  `payload`). Trap: set `applyToExistingTransactions` explicitly, per `kick/transaction-rules`.

Rollback (Caveats).

- `activity_query` `{ "operation": "list", "workspaceId": "<workspaceId>", "filters": {
  "resourceTypes": ["transaction"] } }`, then `details_get` (`workspaceId`, `date`,
  `sourceType`) to confirm the batch's scope.
- `activity_undo` requires `workspaceId`, `date`, `sourceType`, `resourceType`, `fields`, and
  `changeTypes`. Trap: copy each from the activity row exactly, per `kick/activity-undo`. Not
  every batch is revertible; a refusal goes to the user.
- A wrong disable is undone with `accounting_act` `bulk_enable`, same payload shape as the
  disable.

## Writes

Every write tool here is preview-first.

- Resolve every ID with a read first: `workspaceId` and `entityId` (step 2), `accountId`
  (`accounts_list`, fresh after Phase 2a), `groupId` (chart-of-accounts reads), `transactionId`
  (`find`), `categoryId` (`categories_query`), `ruleId` (`groups_list`). Never ask the user for
  an ID, never guess one.
- Call without `confirmationToken`. The response is a `preview` with a `summary` and a fresh
  token. Quote the summary unaltered.
- Ask once. Only the user's explicit yes to that preview, in their next message, authorizes
  the apply. A token is not consent; the original request is not approval.
- Apply with the identical input plus the returned `confirmationToken`. Never invent or reuse
  a token; each preview binds a new token to its exact input.
- One token per phase action. Never put account changes and transaction remaps under one
  `confirmationToken`.
- Bulk: one call per bulk operation (`bulk_disable`, `bulk_enable`, `bulk_update`), with the row
  count stated in the preview. When `create` takes one account per call, preview each, quote
  every summary in one message with the count, ask once, and apply each with its own token.
- Expired token (roughly 40 minutes): re-preview with the identical input. If the fresh preview
  matches what the user approved, apply without asking again. If anything differs, show the
  difference and re-ask. Never resend a stale token.
- A 409 or lock-date error: stop and ask the user. Never retry into a closed period.
- No hard deletes. Cleanup is merge (below) or `bulk_disable`.

## Merging accounts on Kick

### The limitation

Kick's hosted MCP has no merge write. The public reference states: "Account merge is not
available through hosted MCP." The `accounting_act` operations are `create`, `update`,
`bulk_update`, `bulk_disable`, `bulk_enable`, and `bulk_delete`; none merges, and no other
hosted tool merges accounts. Never promise the user a merge call, and never send
`bulk_delete` as a substitute.

### The workaround

On Kick, each approved merge (Procedure step 4, applied in step 6) runs as reclass, then
disable. The skill's meaning holds: the source's activity ends on the survivor and the source
stops receiving activity. The order of work changes:

1. Step 6: create the survivor if the proposal needs one. Do not disable the source yet.
2. Step 7: add one mapping line per merge, source to survivor, to the reclass set. Here the
   step's "merges already moved their activity" does not apply: on Kick the merged sources'
   rows are in the set. Label these lines "merge" so the preview reads as one.
3. Step 8: the merge lines post in the same bulk reclass preview, with their counts stated.
4. After step 8 posts: re-read each merged source over the window, with `transactions_query`
   `statistics` filtered to the source and `reports_query` `account_transactions` for the
   account. Zero window activity left means the source is empty.
5. Then the disables that complete the merges: one `accounting_act` `bulk_disable` for the
   emptied sources, its own preview and confirm. This is the step 6 "disables of emptied
   sources" write, moved after the reclass on Kick.

### What a native merge would move that this does not

- Transactions outside the window. To move a source's full history, widen that merge line's
  `since` and `until` to the account's first and last activity, stated in the reclass preview,
  with the user's yes.
- Manual journal lines and opening balances on the source. The reclass cannot move them, and
  editing journals or opening balances is outside this skill.

Check for these before the disable: `account_transactions` for the source with `sourceTypes:
["manual_journal_entry"]` (field-reported, unconfirmed) for journal lines, and
`opening_balances_query` `{ "operation": "get", "entityId": 287, "accountId": "<source UUID>" }`
for an opening balance. When a source still holds any of these after the re-read, do not
disable it. List the residual in the change log as an Open line and ask the user: keep the
source enabled, or disable it with the residual in place.

### In the change log

Record each merge as Action "Merge (reclass then disable on Kick)", with the count from the
reclass preview, and the disable as its own row. Net income for the window is unchanged by a
merge between accounts of the same type; the before and after reads show it.

## Traps

- `entityId` vs `workspaceId`: account `update`, `ledgers_get`, `accounts_list`, and the
  ledger reports take the integer; `create`, group writes, `find`, `statistics`,
  `bulk_update`, and `chart_of_accounts` take the UUID.
- `since` and `until` on `find` and `statistics`; `startDate` and `endDate` inside `params` on
  reports. Mixing them is the common cause of a wrong or empty read.
- `ledgerId` is required on `profit_loss` and `account_transactions`, and comes from the same
  entity's ledger read.
- GL-first: `accountOverrides` with account UUIDs from `accounts_get_workspace`, filter with
  `filters.coaAccounts`. Any `categoryId`, or `categories_act`, is rejected.
- Category-first with no category for a new account: `categories_query` returns nothing.
  Stop and ask; this skill does not create categories.
- Stale IDs: an ID list or destination lookup built before Phase 2a posted is stale. Re-read
  after each Phase 2a write lands.
- Paging: a `find` that stops before `nextCursor` is `null` drops rows from the reclass, and the
  preview count will not match the step 4 count. Reconcile before asking for the yes.

## Workflow mapping

| Procedure step | Calls |
| --- | --- |
| 1 | `list_kick_skills`, `load_kick_skill` (CoA migration, transaction review) |
| 2 | `context_resolve` (`entity`, `workspace`, `ledger`), `context_browse` `workspaces` (`glFirstEnabled`), `accounting_query` `ledgers_get`; `load_kick_skill` GL-first guide when flagged |
| 3 | `accounting_query` `accounts_list` or `accounts_get_workspace`, `reports_query` `chart_of_accounts`, `profit_loss`, `account_transactions` |
| 4 | `transactions_query` `statistics` per mapping line |
| 5 | No calls |
| 6 | `account_groups_act` `create`, `update`; `accounting_act` `create`, `update`, `bulk_update`, and `bulk_disable` for accounts not being merged. Merges have no call here; see Merging accounts on Kick |
| 7 | `accounting_query` `accounts_list` or `accounts_get_workspace`, or `categories_query` `search`, for destinations; `transactions_query` `find`, including the merge lines |
| 8 | `transactions_act` `bulk_update` |
| After 8, merges only | `transactions_query` `statistics`, `reports_query` `account_transactions`, `opening_balances_query` `get`, `accounting_act` `bulk_disable` |
| 9 | `rules_query` `groups_list`, `matching_transactions`; `rules_act` `create`, `update` |
| 10 | `reports_query` `profit_loss`, `transactions_query` `statistics` |
| Rollback | `activity_query` `list`, `details_get`, `activity_undo`; `accounting_act` `bulk_enable` for a wrong disable |

## Tool errors and schema drift

- **Tool errors and schema drift:** if a live call is rejected, trust the live error hint (and
  any loaded guide) over this skill's examples. Fix the call and retry once. For writes, a
  rejected call restarts the confirmation flow: re-preview, never resend a stale confirmation
  token. If the working shape contradicts this skill's text, add a method note to the
  deliverable so it can be reported and fixed centrally. Never edit this skill file mid-run.

The method note reads: "Note: one step worked differently than this skill describes: <what
changed>. Please forward this note to whoever sent you the skill."
