# Kick binding: client-meeting

Loaded at Procedure step 2 when the books are on Kick; its calls serve steps 3, 5, 6, and 7.
Every call is a read: entity and ledger lookup, two P&L windows, a balance sheet, large
transactions, transaction counts, entity metadata, and open tasks. Every tool and parameter
here comes from the Kick connector pack.

## Published guides

Discover with `list_kick_skills` (query "financial reports", `includeHeader: true`), then
`load_kick_skill` the match. Guide names are not guessable; use the ones the list returns.
Load each guide before its first domain call. Each guide owns its full call shapes; where a
guide and this file differ, follow the guide.

| Guide | Serves |
| --- | --- |
| `kick/entity-lookup` | Step 3: numeric `entityId` plus `workspaceId`; step 7: entity metadata |
| `kick/chart-of-accounts-and-ledger-lookup` | Step 3: `ledgerId` and the accounting basis |
| `kick/financial-reports` | Steps 5 and 6: P&L, balance sheet, top transactions |
| `kick/period-end-close-review` | Step 6: material report swings, unmatched transfers, large items |
| `kick/find-and-query-transactions` | Steps 6 and 7: transaction search, `statistics` filters |
| `kick/tasks-and-comments-lookup` | Step 7: open tasks for the entity |

## Tools used

| Tool | Operation / report | Purpose |
| --- | --- | --- |
| `list_kick_skills` / `load_kick_skill` | none | Discover and load the guides above |
| `context_browse` | `workspaces` | List workspaces with nested entities when the client name is ambiguous |
| `context_resolve` | `entity` | Client name to numeric `entityId` and its `workspaceId` (selected with `target`) |
| `context_resolve` | `ledger` | `ledgerId` for the entity (selected with `target`) |
| `accounting_query` | `ledgers_get` | `ledgerId` and basis |
| `reports_query` | `profit_loss` | Revenue, gross profit, net income per window |
| `reports_query` | `balance_sheet` | Cash, clearing and in-transit, credit card balances |
| `reports_query` | `top_transactions` | Large one-off transactions |
| `transactions_query` | `find` | Transactions in the window, duplicate candidates |
| `transactions_query` | `similar` | Check a suspected duplicate import |
| `transactions_query` | `statistics` | Unreviewed and counterparty counts |
| `entities_query` | `get_metadata` | Readiness flags |
| `tasks_query` | `list` | Open tasks |

## Call shapes

- `context_resolve` `{ "target": "entity", "query": "<client name>" }`. `context_resolve`
  selects with `target` (values `workspace`, `entity`, `ledger`), not `operation`.
  `entityId` is a positive integer; `workspaceId` is a UUID. Never ask the user for either.
- `context_browse` `{ "operation": "workspaces", "limit": 25 }` when the name matches more
  than one entity: list the candidates and ask (step 3).
- `accounting_query` `{ "operation": "ledgers_get", "entityId": 123 }`, or `context_resolve`
  `{ "target": "ledger", "entityId": 123 }`. Takes the numeric `entityId`, not `workspaceId`.
  More than one ledger: list them with their basis and ask.
- `reports_query` `{ "report": "profit_loss", "params": { "entityId": 123, "ledgerId": "<ledger uuid>", "startDate": "YYYY-MM-DD", "endDate": "YYYY-MM-DD" } }`,
  two calls, one per window (current and prior). The report goes in `report`, never
  `operation`; inputs go inside `params`. Ledger-scoped: `ledgerId` required. Dates are
  `startDate` / `endDate`, never `since` / `until`. Leave `cycle` off for window totals;
  never one call per month.
- `reports_query` `balance_sheet` with the same `params`, `endDate` on the current
  window's end date. `ledgerId` required.
- `reports_query` `{ "report": "top_transactions", "params": { "entityIds": [123], "startDate": "YYYY-MM-DD", "endDate": "YYYY-MM-DD", "categoryIdentifier": "<from guide>" } }`.
  Takes `entityIds` (an array) and no `ledgerId`. Kick's extended notes show
  `categoryIdentifier: "income"` and list no other value: take the value for expense
  one-offs from `kick/financial-reports`; never guess it.
- `transactions_query` `{ "operation": "find", "workspaceId": "<workspace uuid>", "since": "YYYY-MM-DD", "until": "YYYY-MM-DD" }`.
  Dates are top-level `since` / `until`, never inside `filters`. Then `transactions_query`
  `{ "operation": "similar", "transactionId": 12345 }` on each duplicate candidate's
  numeric `transactionId`.
- `transactions_query` `{ "operation": "statistics", "workspaceId": "<workspace uuid>", "since": "YYYY-MM-DD", "until": "YYYY-MM-DD", "filters": { } }`.
  Uses `find` filter semantics. The review-state filter (`reviewState: "UNREVIEWED"`) is
  not in the public reference, which also names no counterparty filter:
  take both filter names from `kick/find-and-query-transactions`. If a filter is rejected,
  follow the error and the loaded guide, then count from `find` rows instead.
- `entities_query` `{ "operation": "get_metadata", "workspaceId": "<workspace uuid>", "entityId": 123 }`.
  Needs both IDs. The public reference does not name the opening-balances-ready or
  reports-ready fields: read them from the response when present; otherwise write
  "Not exposed" in the health table.
- `tasks_query` `{ "operation": "list", "workspaceId": "<workspace uuid>" }`. The `status`
  and `entityIds` filters are not in the public reference. Narrow to open tasks for this
  entity as `kick/tasks-and-comments-lookup` describes; if a filter is rejected, filter the
  returned rows.

## From reads to skill inputs

| Skill input | Read from | Draft rule |
| --- | --- | --- |
| Revenue, gross profit, net income | Two `profit_loss` calls | Current and prior window; gross profit only when the P&L shows it |
| Cash | `balance_sheet` at the current window's end | Bank lines only; transfer-clearing and in-transit lines go on their own line, outside the cash read |
| Credit-card balance growth | `balance_sheet` | Note as a cash-flow driver when material |
| P&L line swings | Two `profit_loss` calls, line by line | Apply the floor and the 10% and $100 rule from step 6 |
| Large one-offs | `top_transactions` | Sorted by amount |
| Suspected duplicates | `find`, then `similar` | Flagged separately from one-offs |
| Unreviewed items, counterparty gaps | `statistics` | Count and review completion as returned |
| Readiness flags | `get_metadata` | "Not exposed" when the response lacks the field |
| Open tasks | `tasks_query` `list` | Open tasks for this entity only |

## Traps

- `entityId` (integer) and `workspaceId` (UUID) are not interchangeable. Resolve both
  through `context_resolve` or `context_browse` before the first report; never ask the
  user for either.
- Reports take `startDate` / `endDate`; transaction queries take top-level `since` /
  `until`.
- `profit_loss` and `balance_sheet` require `ledgerId`. `top_transactions` takes
  `entityIds` and no `ledgerId`.
- More than one entity or ledger matches the client name: list the candidates and ask
  (step 3).

## Workflow mapping

| Procedure step | Calls |
| --- | --- |
| 1. Set defaults | No calls |
| 2. Detect connector mode | No calls; this file loads here |
| 3. Orient to the books | `list_kick_skills`, `load_kick_skill`; `context_resolve` `entity` (or `context_browse` `workspaces`); `accounting_query` `ledgers_get` (or `context_resolve` `ledger`) |
| 4. Set the lookback window | No calls |
| 5. Financial highlights | `reports_query` `profit_loss` (twice), `balance_sheet` |
| 6. Anomalies | `profit_loss` lines from step 5; `reports_query` `top_transactions`; `transactions_query` `find`, `similar` |
| 7. Health and open items | `transactions_query` `statistics`; `entities_query` `get_metadata`; `tasks_query` `list` |
| 8. Talking points | No calls |
| 9. Deliver | No calls; any drift goes in the Method note |

## Tool errors and schema drift

- **Tool errors and schema drift:** if a live call is rejected, trust the live error hint (and
  any loaded guide) over this skill's examples. Fix the call and retry once. For writes, a
  rejected call restarts the confirmation flow: re-preview, never resend a stale confirmation
  token. If the working shape contradicts this skill's text, add a method note to the
  deliverable so it can be reported and fixed centrally. Never edit this skill file mid-run.

This skill makes no writes. For this skill the method note is the brief's Method note.
