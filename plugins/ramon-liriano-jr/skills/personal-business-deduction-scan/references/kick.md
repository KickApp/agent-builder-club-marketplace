# Kick binding: personal-business-deduction-scan

Loaded at Procedure steps 1 and 3 to 6 when Kick is connected. It reads the workspace, the
personal entity and its accounts, and each account's money-out transactions. Every tool and
operation here is in Kick's public tool reference;
the parameters marked unconfirmed under Call shapes came from this skill's live runs and
carry a named fallback.

## Published guides

Discover with `list_kick_skills` (query "find transactions", `includeHeader: true`), then
`load_kick_skill` the match. Guide names are not guessable; use the ones the list returns.
Load the transaction guide at workflow start and follow its query syntax alongside this
binding. The loaded guide is the authority for filter syntax.

| Guide | Serves |
| --- | --- |
| `kick/find-and-query-transactions` | Steps 1, 5, 6: filter syntax, sizing, paging, precedent lookups |
| `kick/financial-accounts-lookup` | Step 4: a deeper read on connected account metadata, when needed |

## Tools used

| Tool | Operation / report | Purpose |
| --- | --- | --- |
| `list_kick_skills` / `load_kick_skill` | `query` / `name` | Load `kick/find-and-query-transactions` at workflow start |
| `context_browse` | `workspaces` | List workspace candidates; entity summaries show which entity is personal |
| `context_resolve` | `target: "workspace"`, `target: "entity"` | Resolve `workspaceId`, and `entityId` when the user named an entity |
| `financial_accounts_query` | `list` | Identify the personal entity's accounts; verify a named account with `search` |
| `transactions_query` | `statistics`, `find`, `similar`, `get` | Size each account, pull its outflows, find precedents |
| `counterparties_query` | `search`, `list` | Resolve vendor names when merchant strings are unclear |
| `categories_query` | `search` | Optional context on how similar business-account rows were categorized |

## Call shapes

- `context_browse { operation: "workspaces" }`. No workspace name given: list the
  candidates and ask. Trap: the only operation is `workspaces`. Its nested entity summaries
  carry `isPersonal`, the entity-level attribute that marks the personal entity.
- `context_resolve { target: "workspace", query: "<name>" }` and
  `context_resolve { target: "entity", query: "<name>" }`. Trap: `query` is required for
  both targets. `workspaceId` is a UUID; `entityId` is a positive integer.
- `financial_accounts_query { operation: "list", workspaceId, fields: ["id","name","institutionName","mask","type","entityId","entityName"] }`.
  Keep only rows whose `entityId` matches the personal entity. Trap: `isPersonal` is not a
  field on these rows; personal is an entity attribute.
- `financial_accounts_query { operation: "list", workspaceId, search: "<institution or name>" }`
  to verify a named account or institution before scanning. Trap: masks are not unique
  across entities; confirm the account with the user.
- `transactions_query { operation: "statistics", workspaceId, since, until, filters: { accountIds: [<id>], entityIds: [<entityId>], direction: "MONEY_OUT" } }`,
  one per personal account, to size it. Trap: `since` and `until` are top-level
  `YYYY-MM-DD`, never inside `filters`.
- `transactions_query { operation: "find", workspaceId, since, until, filters: { accountIds: [<id>], entityIds: [<entityId>], direction: "MONEY_OUT" }, fields: ["id","date","amount","bank_description","counterparty","category"], limit: 100 }`,
  one personal account per query. Page with `cursor` until `nextCursor` is `null`. Trap:
  there is no per-row account column in `fields`, so one `find` per account is what
  attributes rows to accounts. Maximum `limit` is 100.
- `transactions_query { operation: "similar", transactionId }`, then
  `transactions_query { operation: "get", transactionId }`. Trap: `similar` returns ids only
  (per Kick's extended notes); read a precedent with `get`.
- `counterparties_query { operation: "search", workspaceId, search: "<merchant>" }`, or
  `list` with `workspaceId`. Trap: `search` requires both `workspaceId` and `search`.
- `categories_query { operation: "search", workspaceId, search: "<term>" }`. Trap: requires
  both `workspaceId` and `search`. In a GL-first workspace (`glFirstEnabled: true` on
  `context_browse`), categories are not the classification; skip this optional lookup and
  rely on `similar` plus `get` for precedent.

Unconfirmed parameters. The public reference lists no `filters` keys beyond `search`, no
`direction` values, no entity summary fields, and no account field names. These came from
this skill's live runs:

- `filters.accountIds`: if Kick rejects it, follow the error and the loaded guide, then use
  `filters.financialAccountIds` (the key Kick's extended notes list) with the same ids.
- `filters.entityIds`: if Kick rejects it, follow the error and the loaded guide, then drop
  it; the single-account filter already limits rows to an account step 4 tied to the
  personal entity. Say so in Method notes.
- `filters.direction: "MONEY_OUT"`: if Kick rejects it, follow the error and the loaded
  guide for the direction filter; if the guide names none, pull without it, keep only
  money-out rows, and say so in Method notes.
- `isPersonal` on entity summaries: if the live summaries carry none, list the entities and
  ask which one is personal.
- `fields` lists on `financial_accounts_query` and `transactions_query`: if a field name is
  rejected, drop it per the error hint, or omit `fields` and read the default row shape.

## From reads to skill inputs

| Skill input | Read from | Draft rule |
| --- | --- | --- |
| Personal entity | `context_browse` entity summaries (`isPersonal`) | No flag, or more than one: list the entities and ask |
| Personal accounts | `financial_accounts_query` `list` | Only rows whose `entityId` is the personal entity; confirm with the user and record the ids |
| Rows per account | `transactions_query` `statistics` | Over about 500 rows on one account: offer to scan by quarter |
| Flagged row detail | `transactions_query` `find` rows | Date, amount, description, and transaction id come from the row; the account comes from the query that pulled it |
| Precedent | `similar` plus `get`, `categories_query` `search` | Context only, never proof |

## Traps

- `financialAccountIds` was the wrong filter key in this skill's live runs; use
  `accountIds` first. Kick's extended notes list
  `financialAccountIds`, so it stays the fallback.
- Dates inside `filters` fail; `since` and `until` are top-level on `transactions_query`.
- Omitting `entityIds` on `find` makes the search workspace-wide and returns other
  entities' transactions.
- `financialAccount` is not projectable in `fields`. Query one account at a time instead.
- Masks are not unique across entities. Confirm the account with the user before scanning.
- Resolve every id via `context_resolve`, `financial_accounts_query`, and
  `transactions_query`. Never ask the user for UUIDs. `workspaceId` is a UUID; `entityId`,
  `transactionId`, and account ids are integers.
- Never conclude from an empty result until a known-positive control query (same filter
  key) succeeds.

## Workflow mapping

| Procedure step | Calls |
| --- | --- |
| 1. Load binding and guide | `list_kick_skills`, `load_kick_skill` |
| 2. Set scope | none |
| 3. Resolve workspace and entity | `context_browse`, `context_resolve` |
| 4. Identify personal accounts | `context_browse` (entity `isPersonal`), `financial_accounts_query` `list` (plus `search` to verify a named account) |
| 5. Size and pull | `transactions_query` `statistics`, then `find` per account, paged |
| 6. Screen | `counterparties_query` `search` or `list`; optional `transactions_query` `similar` plus `get`; optional `categories_query` `search` |
| 7. Estimate, 8. Deliver | none: figures come from the rows pulled in step 5 |

Worked run for [examples.md](examples.md). Ids are illustrative.

1. `load_kick_skill { name: "kick/find-and-query-transactions" }`
2. `context_resolve { target: "workspace", query: "Acme LLC" }` returns the `workspaceId`.
3. `context_browse` returns the entity with `isPersonal: true`;
   `financial_accounts_query { operation: "list", workspaceId, fields: [...] }` returns the
   accounts matching that `entityId`. The user confirms Amex ••1234 and Personal Checking
   ••5678.
4. Per account: `transactions_query { operation: "statistics", workspaceId, since: "2025-01-01", until: "2025-12-31", filters: { accountIds: [111], entityIds: [57], direction: "MONEY_OUT" } }`
   returns about 420 rows each.
5. Per account: `transactions_query { operation: "find", …, filters: { accountIds: [111], entityIds: [57], direction: "MONEY_OUT" }, limit: 100 }`,
   paged to the end.

## Tool errors and schema drift

- **Tool errors and schema drift:** if a live call is rejected, trust the live error hint (and
  any loaded guide) over this skill's examples. Fix the call and retry once. For writes, a
  rejected call restarts the confirmation flow: re-preview, never resend a stale confirmation
  token. If the working shape contradicts this skill's text, add a method note to the
  deliverable so it can be reported and fixed centrally. Never edit this skill file mid-run.

This skill makes no writes.
