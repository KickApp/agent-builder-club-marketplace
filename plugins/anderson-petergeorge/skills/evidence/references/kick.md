# Kick binding: evidence

Loaded at Procedure step 2 when Kick is connected, and used at steps 3, 4, 6, and 8. It
reads two kinds of books: each client's workspace (volume, review backlog, accounts, tasks,
the client's own revenue) and the firm's own workspace (fees the firm collected from each
client). Every tool and parameter here comes from the Kick connector pack.

## When Kick has nothing to give

Skip this file and write the Kick line "not connected" (footer: "Control query: none, Kick
not connected") when no Kick tools are in the session or the first call returns an auth
error. Skip only the firm-books fee read (step 6) when no workspace matches the firm's name:
client workspaces are not the firm's books, so the Fee line comes from the other sources.

## Published guides

Discover with `list_kick_skills` (one `query` per need below, `includeHeader: true`), then
`load_kick_skill` each match before its first domain call. Guide names are not guessable;
use the ones the list returns. A guide already loaded in the conversation is not loaded
again. Read each tool's live descriptor before its first call.

| Guide | Serves |
| --- | --- |
| `kick/entity-lookup` (query "entity lookup") | Workspaces, entities, metadata, address (steps 3, 4) |
| `kick/counterparty-lookup` (query "counterparty lookup") | The client as a payer in the firm's own workspace (step 6) |
| `kick/find-and-query-transactions` (query "find and query transactions") | Counts, totals, filter keys, the control query (steps 6, 8) |
| `kick/transaction-review-and-categorization` (query "transaction review") | The filter keys for awaiting review and missing a payee (step 8) |
| `kick/financial-accounts-lookup` (query "financial accounts") | Connected accounts and their entity (step 8) |
| `kick/tasks-and-comments-lookup` (query "tasks") | Open tasks (step 8) |
| `kick/chart-of-accounts-and-ledger-lookup` (query "ledger lookup") | `ledgerId` and basis before the P&L (step 8) |
| `kick/financial-reports` (query "financial reports") | The client's own P&L for a size band (step 8) |
| `kick/period-end-close-review` (query "close review") | Uncategorized or unmatched counts, only if this guide exposes them in one call (step 8) |

## Tools used

| Tool | Operation / report | Purpose |
| --- | --- | --- |
| `list_kick_skills` | (no operation; `query`, `includeHeader`) | Find the guides above |
| `load_kick_skill` | (no operation; `name`) | Load each guide the list returned |
| `context_browse` | `workspaces` (no required fields) | Every workspace and nested entity the firm can reach |
| `context_resolve` | target `workspace` (`query`) | Confirm the firm's own workspace by the firm's name |
| `entities_query` | `get_metadata` (`workspaceId`, `entityId`); `get_address` (`entityId`) | Industry, description, personal flag if shown, location |
| `counterparties_query` | `search` (`workspaceId`, `search`) | The client as a payer in the firm's own workspace |
| `transactions_query` | `statistics` (`workspaceId`) | Client volume and review counts; fees received from one payer in the firm's books |
| `transactions_query` | `find` (`workspaceId`) | The control query; checking which payers a fee search matched |
| `financial_accounts_query` | `list` (`workspaceId`) | Connected bank, card, and processor accounts |
| `tasks_query` | `list` (`workspaceId`) | Open work items |
| `accounting_query` | `ledgers_get` (`entityId`) | The `ledgerId` and basis for the client's P&L |
| `reports_query` | `profit_loss` (`params`: `entityId`, `ledgerId`, `startDate`, `endDate`) | The client's own revenue, for a size band only |

## Call shapes

Periods below use Sep 2025 to Aug 2026 as the example.

- `context_browse` `{ "operation": "workspaces", "limit": 100 }`. Trap: default page 25,
  maximum 100; page while `hasMore` is true, sending `nextCursor` in the cursor field the
  live descriptor names. Take every `workspaceId` (UUID string) and `entityId` (positive
  integer) from here; never ask the owner for either.
- `context_resolve` `{ "target": "workspace", "query": "<firm name>" }`. Trap: this tool
  takes `target`, not `operation`. More than one match, or none: the firm-books fee read is
  "Not available"; never pick one.
- `entities_query` `{ "operation": "get_metadata", "workspaceId": "<uuid>", "entityId": 123 }`
  and `{ "operation": "get_address", "entityId": 123 }`. Trap: `get_metadata` needs both
  IDs; `get_address` takes the entity alone. The docs name no "personal" field: set an
  entity aside only when this response or the `context_browse` summary marks it so.
- `transactions_query` `{ "operation": "statistics", "workspaceId": "<client uuid>", "since": "2025-09-01", "until": "2026-08-31" }`.
  Trap: dates are top-level `since` and `until`, never inside `filters` and never
  `startDate`/`endDate`. One call for the period, never one per month. Transactions a
  month is the returned total over the months in the period, with both operands kept.
- Awaiting review: the same statistics call with `"filters": { "reviewState": "UNREVIEWED" }`.
  Unconfirmed: `reviewState` and its values are not in the public reference. If rejected,
  take the key from the loaded review guide and retry once; if neither works, the share is
  "Not available" for the client.
- Missing a payee: no documented filter. Take the key from the loaded review guide or the
  live descriptor; none: "Not available", never estimated.
- Control query: `transactions_query` `{ "operation": "find", "workspaceId": "<client uuid>", "since": "2025-09-01", "until": "2026-08-31", "limit": 1 }`.
  Quote its `total` in the footer before any zero appears.
- `financial_accounts_query` `{ "operation": "list", "workspaceId": "<client uuid>" }`. Trap:
  in a shared workspace, count only accounts assigned to the client's entity. No entity
  assignment in the response: the count is workspace-wide and "Not available" for the
  client.
- `tasks_query` `{ "operation": "list", "workspaceId": "<client uuid>" }`. Unconfirmed: the
  `status` filter (`todo`, `in_progress`, `blocked`) and `entityIds` are not in the
  public reference. If rejected, list unfiltered, page through, and count the rows the
  response marks open.
- `accounting_query` `{ "operation": "ledgers_get", "entityId": 123 }`, then
  `reports_query` `{ "report": "profit_loss", "params": { "entityId": 123, "ledgerId": "<from ledgers_get>", "startDate": "2025-09-01", "endDate": "2026-08-31" } }`.
  Trap: `ledgerId` is required on this report, and dates are `startDate`/`endDate` inside
  `params`. One call for the whole period; no `cycle` is needed for a size band.
- Fee from the firm's books, step one: `counterparties_query` `{ "operation": "search", "workspaceId": "<firm uuid>", "search": "<client name or alias>" }`.
  Trap: the firm's `workspaceId`, never the client's. Two matching counterparties go on the
  unmatched list; never sum them silently.
- Fee from the firm's books, step two: `transactions_query` `{ "operation": "statistics", "workspaceId": "<firm uuid>", "since": "2025-09-01", "until": "2026-08-31", "filters": { "counterpartyIds": ["<uuid>"] } }`.
  Unconfirmed: `counterpartyIds` and filters on `statistics` are not in the public
  reference. Fallback: the same call with the public `"filters": { "search": "<counterparty name>" }`,
  checked first by a `find` with the same filter and `"fields": ["id", "date", "amount", "counterparty"]`.
  More than one payer in those rows, or a rejected call: the Kick fee is "Not available"
  and the Fee line stands on the other sources.
- No report splits revenue by customer. `reports_query` has nine reports and none is a
  per-counterparty P&L; never request one.

## From reads to skill inputs

| Skill input | Read from | Draft rule |
| --- | --- | --- |
| Client list | `context_browse` | Many workspaces with one entity each: each workspace is a client. One workspace with several entities: each non-personal entity is a client, and the list says so. The firm's own workspace is never a client. |
| Business line (industry, location) | `entities_query` metadata and address | Tag "Kick". A field the response lacks stays "unknown". |
| Fee (Kick, firm books) | The firm's own workspace, payer-scoped statistics | Third choice after an invoice export or practice tool and the owner's fee. Tag "Kick, firm books" with the period, and "collected", since it is money received. A net figure is labeled net. |
| Kick line counts | The client's workspace, period-scoped | Each count names the period. A read that cannot be scoped to the client's entity is "Not available" for the client. |
| Size band | The client's own P&L revenue | A band on the Business line only. Never placed on the Fee line or mixed with fees. |
| Control count | The `find` call | Quoted in the footer before any zero. |

## Traps

- Reading the wrong books. Fees come only from the firm's own workspace; client volume and
  size come only from that client's workspace. Confirm each workspace by name before the
  read, and never read a client's P&L revenue as the firm's fee.
- `workspaceId` is a UUID string and `entityId` a positive integer; `transactions_query`,
  `financial_accounts_query`, `tasks_query`, and `counterparties_query` take the workspace,
  `accounting_query` `ledgers_get` and `reports_query` take the entity.
- An entity inside a shared workspace has no documented transaction filter. Use the key
  the loaded guide gives; none: that figure is "Not available" for the client.
- A plan-capability or "is not enabled for this workspace" error is a fact about that
  workspace: one "Not available" line, no retry loop.
- Anything whose descriptor creates, updates, deletes, or reverts is out of scope.

## Workflow mapping

| Procedure step | Calls |
| --- | --- |
| 1. Classify the inputs | A response to the step 2 calls means Kick is present |
| 2. Load the connector guidance | `list_kick_skills`, then `load_kick_skill` per guide above |
| 3. Collect client names | `context_browse` workspaces, paged; `entities_query` `get_metadata` and `get_address` |
| 4. Match identities | `context_browse` and `get_metadata` for personal entities; `context_resolve` workspace for the firm's own |
| 6. Fees | Firm's workspace: `counterparties_query` `search`, then `transactions_query` `statistics` (fallback: `find` and `statistics` with `search`) |
| 7. Hours | No Kick call; Kick holds no time data |
| 8. Read Kick per client | `transactions_query` `statistics` (total, awaiting review, missing a payee) and `find` (control); `financial_accounts_query` `list`; `tasks_query` `list`; `accounting_query` `ledgers_get`, then `reports_query` `profit_loss` |
| 10. Books condition | No new call; the step 8 figures |
| 11. Footer | The step 8 control count |

## Tool errors and schema drift

- **Tool errors and schema drift:** if a live call is rejected, trust the live error hint (and any loaded guide) over this skill's examples. Fix the call and retry once. For writes, a rejected call restarts the confirmation flow: re-preview, never resend a stale confirmation token. If the working shape contradicts this skill's text, add a method note to the deliverable so it can be reported and fixed centrally. Never edit this skill file mid-run.

This skill makes no writes.
