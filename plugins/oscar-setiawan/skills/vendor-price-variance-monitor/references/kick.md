# Kick binding: vendor-price-variance-monitor

Loaded at Procedure steps 1, 3, and 5 when Kick is connected. It reads the entity, vendor
records, connected accounts, and each vendor's charges and period totals. Every tool and
parameter here comes from the Kick connector pack; the two filter keys marked unconfirmed
under Call shapes carry a named fallback.

## Published guides

Discover with `list_kick_skills` (query "vendor counterparty spend transactions"), then
`load_kick_skill` the match. Guide names are not guessable; use the ones the list returns.
They own counterparty resolution, account lookup, and transaction filter syntax; this file
carries only what they do not. When a loaded guide differs from this file, the guide wins.

| Guide | Serves |
| --- | --- |
| `kick/counterparty-lookup` | Step 3: one clean vendor record per name |
| `kick/financial-accounts-lookup` | Step 3: every card and bank account the charges post through |
| `kick/find-and-query-transactions` | Step 5: charge filters, period totals, paging |

## Tools used

| Tool | Operation / report | Purpose |
| --- | --- | --- |
| `list_kick_skills` / `load_kick_skill` | `query` / `name` | Find and load the guides above |
| `context_resolve` | `target: "entity"`, `target: "workspace"` | Resolve `entityId` and `workspaceId` by name |
| `context_browse` | `workspaces` | List workspaces with nested entity summaries; finds the workspace that holds the entity |
| `counterparties_query` | `search`, `list` | One `counterpartyId` per named vendor (`search`), or every vendor in scope (`list`) |
| `financial_accounts_query` | `list` | Every connected card and bank account; `financialAccountId` per account |
| `transactions_query` | `find`, `statistics` | `find` to inspect charges; `statistics` for the period total |

## Call shapes

- `context_resolve { "target": "entity", "query": "Acme Rocket Co" }` and
  `context_resolve { "target": "workspace", "query": "Acme Rocket Co" }`. Trap: `query` is
  required for both targets. `entityId` is a positive integer; `workspaceId` is a UUID
  string. Resolve the entity for scope, then pass the workspace to every call below.
- `context_browse { "operation": "workspaces", "limit": 25 }`. Trap: the only operation is
  `workspaces`; there is no `workspace`. Use it when the workspace name does not resolve, to
  find the workspace whose entity summaries hold the resolved entity.
- `counterparties_query { "operation": "search", "workspaceId": "<workspaceId>", "search": "Vercel" }`,
  or `{ "operation": "list", "workspaceId": "<workspaceId>" }` for every vendor in scope.
  Trap: the operations are `list` and `search` only; there is no `find`. It takes
  `workspaceId`, never `entityId`. `counterpartyId` is a UUID string.
- `financial_accounts_query { "operation": "list", "workspaceId": "<workspaceId>", "search": "Ramp" }`.
  `search` is optional; omit it to list every connected account. Trap: `workspaceId`, not
  `entityId`. `financialAccountId` is a positive integer.
- `transactions_query` `find`, one per vendor per window:

  ```json
  {
    "operation": "find",
    "workspaceId": "<workspaceId>",
    "since": "2026-07-01",
    "until": "2026-07-31",
    "filters": { "counterpartyIds": ["<counterpartyId>"], "financialAccountIds": [9012] }
  }
  ```

  Trap: `since` and `until` sit beside `filters`, never inside it. `find` returns 25 rows by
  default, 100 at most; follow `nextCursor` until it is `null` when inspecting every charge.
- `transactions_query` `statistics`: the same input with `"operation": "statistics"`.
  Trap: the public reference does not name the response fields. Read the total as the
  response returns it; never add `find` rows to get it. Neither reference lists a period
  grouping for transaction statistics, so a trend check makes one `statistics` call per
  month.

Unconfirmed filter keys. The public reference shows only `filters.search`;
`counterpartyIds` and `financialAccountIds` are not in the public reference.

- `filters.counterpartyIds`: if Kick rejects it, follow the error and the loaded
  `kick/find-and-query-transactions` guide, then use `filters.search` with the vendor's
  resolved name and say in the method note that the total is name-matched.
- `filters.financialAccountIds`: if Kick rejects it, follow the error and the loaded guide,
  then use `filters.accountIds` (the key the `kick/financial-accounts-lookup` guide
  resolves) with the same account ids.

## From reads to skill inputs

| Skill input | Read from | Draft rule |
| --- | --- | --- |
| Entity and workspace | `context_resolve`, or `context_browse` | Confirm the entity by name before reading; ambiguous match, ask |
| Vendor record | `counterparties_query` `search` | One clean record per vendor; more than one plausible match, ask |
| Accounts checked | `financial_accounts_query` `list` | Every card and bank account that could carry the vendor; name each in Scope |
| Actual total | `transactions_query` `statistics` | The response total per vendor per window; with more than one account, pass every account in the one call so the total covers them |
| Contracted price | Never read | Always from the user or their own document; the books hold no contract field |

## Traps

- **workspaceId, not entityId.** `counterparties_query`, `financial_accounts_query`, and
  both `transactions_query` operations require `workspaceId` (UUID string). None takes
  `entityId` (positive integer).
- **Operation names.** `counterparties_query` has `list` and `search`; `context_browse` has
  `workspaces`. Any other name is rejected.
- **ID types.** `counterpartyId` is a UUID string. `financialAccountId` is a positive
  integer.
- **Filter keys.** Confirm `counterpartyIds` and `financialAccountIds` in the loaded
  `kick/find-and-query-transactions` guide before the first pull; fallbacks under Call
  shapes.
- **Totals.** `statistics` gives the total. Never add `find` rows to get it.
- **Token scope.** A workspace-scoped token injects its own workspace. User-scoped tokens
  and OAuth must pass `workspaceId`.

## Workflow mapping

| Procedure step | Calls |
| --- | --- |
| 1. Load guides | `list_kick_skills`, `load_kick_skill` |
| 2. Set the scope | none |
| 3. Resolve | `context_resolve` (entity, workspace), or `context_browse`; `counterparties_query` `search` per vendor or `list`; `financial_accounts_query` `list` |
| 4. Contracted price | none: user input |
| 5. Pull charges | `transactions_query` `find`, then `statistics`, per vendor per window |
| 6. Variance | none: actual total from `statistics` minus the user's price |
| 7. Deliver | none |

Worked run for the Example in SKILL.md (synthetic ids):

1. `list_kick_skills { "query": "vendor counterparty spend transactions" }`, then load
   `kick/counterparty-lookup`, `kick/financial-accounts-lookup`, and
   `kick/find-and-query-transactions`.
2. `context_resolve { "target": "entity", "query": "Acme Rocket Co" }` returns
   `entityId: 4821`. `context_browse { "operation": "workspaces" }` returns the workspace
   holding entity 4821, `workspaceId: "019f0a11-2b3c-7d4e-8f50-61728394a5b6"`.
3. `counterparties_query { "operation": "search", "workspaceId": "019f0a11-2b3c-7d4e-8f50-61728394a5b6", "search": "Vercel" }`,
   repeated for Notion and Slack: one clean `counterpartyId` each.
4. `financial_accounts_query { "operation": "list", "workspaceId": "019f0a11-2b3c-7d4e-8f50-61728394a5b6" }`
   returns the Ramp corporate card, `financialAccountId: 9012`.
5. Per vendor: `transactions_query` `find`, then `statistics`, with
   `"workspaceId": "019f0a11-2b3c-7d4e-8f50-61728394a5b6"`, `"since": "2026-07-01"`,
   `"until": "2026-07-31"`, and
   `"filters": { "counterpartyIds": ["<that vendor>"], "financialAccountIds": [9012] }`.
6. `statistics` totals: Vercel $29, Notion $96, Slack $156.

## Tool errors and schema drift

- **Tool errors and schema drift:** if a live call is rejected, trust the live error hint (and
  any loaded guide) over this skill's examples. Fix the call and retry once. For writes, a
  rejected call restarts the confirmation flow: re-preview, never resend a stale confirmation
  token. If the working shape contradicts this skill's text, add a method note to the
  deliverable so it can be reported and fixed centrally. Never edit this skill file mid-run.

This skill makes no writes.
