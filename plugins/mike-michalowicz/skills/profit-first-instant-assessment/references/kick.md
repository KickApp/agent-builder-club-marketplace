# Kick binding: profit-first-instant-assessment

Loaded at Procedure step 1 when the client's books are on Kick; its calls serve steps 1 and
2. Every call is a read: entity and ledger lookup, the trailing-12-month P&L, comparative
Balance Sheet, Statement of Cash Flows, and chart of accounts. Every tool and parameter here
comes from the Kick connector pack.

## Published guides

Discover with `list_kick_skills` (query "financial reports"), then `load_kick_skill` the
match. Guide names are not guessable; use the ones the list returns. Load
`kick/financial-reports` before any report call.

| Guide | Serves |
| --- | --- |
| `kick/financial-reports` | Steps 1 and 2: `entityId` and `ledgerId` resolution, date ranges, the P&L, Balance Sheet, and Cash Flow pulls |
| `kick/chart-of-accounts-and-ledger-lookup` | Steps 1 and 2: `ledgerId` and accounting basis; chart of accounts |
| `kick/find-and-query-transactions` | Step 2: the optional drill-down into one account |

## Tools used

| Tool | Operation / report | Purpose |
| --- | --- | --- |
| `list_kick_skills` / `load_kick_skill` | none | Load `kick/financial-reports` |
| `context_resolve` | `entity` | Client name to numeric `entityId` (selected with `target`) |
| `context_browse` | `workspaces` | Ambiguous name: list workspaces with nested entities, then ask |
| `accounting_query` | `ledgers_list` | `ledgerId` and accounting basis for the entity |
| `reports_query` | `profit_loss` | Trailing-12 P&L: income, Mats & Subs, expense lines |
| `reports_query` | `balance_sheet` | Comparative Balance Sheet: Equity draws, liability paydowns, Profit and Tax savings |
| `reports_query` | `cash_flow_statement` | Debt principal, credit card, and lease payments over the window |
| `accounting_query` | `accounts_get_workspace` | Chart of accounts, so the mapping uses real account names |
| `financial_accounts_query` | `list` | Optional: which connected accounts belong to the entity |
| `transactions_query` | `find`, `statistics` | Optional: drill into one account's actuals |

## Call shapes

- `context_resolve` `{ "target": "entity", "query": "<client name>" }`. `context_resolve`
  selects with `target` (values `workspace`, `entity`, `ledger`), not `operation`.
  `entityId` is a positive integer, not a UUID; `workspaceId` is a UUID. Never ask the user
  for either.
- `context_browse` `{ "operation": "workspaces", "limit": 25 }` when the name is ambiguous:
  show the entities and ask. Workspace-scoped tokens inject `workspaceId`; user-scoped
  tokens and OAuth pass it where a call requires it.
- `accounting_query` `{ "operation": "ledgers_list", "entityIds": [123] }`. `entityIds` is
  an array, even for one entity. Pick the cash ledger when one exists. Single-ledger
  alternatives: `accounting_query` `{ "operation": "ledgers_get", "entityId": 123 }`, or
  `context_resolve` `{ "target": "ledger", "entityId": 123 }`. When the response does not
  show the basis, load `kick/chart-of-accounts-and-ledger-lookup`.
- `reports_query` `profit_loss`, shaped as below. The report goes in `report`, never
  `operation`; inputs go inside `params`. Ledger-scoped: `entityId`, `ledgerId`,
  `startDate`, `endDate` (`YYYY-MM-DD`) are required. Never `since` / `until` here. Leave
  `cycle` off for single-period totals; never one call per month.

  ```json
  {
    "report": "profit_loss",
    "params": {
      "entityId": 123,
      "ledgerId": "<ledger uuid>",
      "startDate": "2025-10-01",
      "endDate": "2026-09-30"
    }
  }
  ```

- `reports_query` `balance_sheet` and `cash_flow_statement` take the same `params` and the
  same window; `ledgerId` is required on both. Accrual basis is acceptable on
  `cash_flow_statement`.
- Comparative Balance Sheet: the public reference lists only the required `params`. Kick's
  extended notes add optional `comparison` / `comparisonDiff`, or `comparisons` /
  `comparisonDiffs` (max 2, P&L and Balance Sheet only), for the dollar change. Their enum
  values are not documented: take them from `kick/financial-reports` or from a live error's
  accepted values; never invent an enum. If the flag is rejected or no call yields a
  dollar-change column, run two `balance_sheet` calls, one ending at the window start and
  one at the window end, and difference the Equity and liability lines.
- `accounting_query` `{ "operation": "accounts_get_workspace", "workspaceId": "<workspace uuid>" }`.
  Takes `workspaceId`, not `entityId`. Rows span the workspace's entities; keep the client
  entity's rows.
- Optional: `financial_accounts_query` `{ "operation": "list", "workspaceId": "<workspace uuid>" }`.
- Optional: `transactions_query` `find` or `statistics` with `workspaceId`. Date ranges use
  top-level `since` / `until`, not `filters`. Account filters come from
  `kick/find-and-query-transactions`.

## From reads to skill inputs

Category rules, the 25% rule, and the Operating Expenses formula stay in
[profit-first-method.md](profit-first-method.md). This table says which read each figure
comes from.

| Skill input | Read from | Draft rule |
| --- | --- | --- |
| Top Line Revenue | `profit_loss` income lines | True revenue lines only, named in the mapping |
| Material & Subs | `profit_loss` cost of sales lines | 0 for a service business; 25% rule before locking |
| Profit | `balance_sheet` profit savings (Assets) and true profit distributions (Equity) | Never net income |
| Owner's Pay | `profit_loss` owner salary and personal lines; `balance_sheet` Equity draws | Ask where it sits when unclear |
| Tax | `profit_loss` tax lines; `balance_sheet` tax reserve and tax draws | |
| Operating Expenses | `profit_loss` expenses; `balance_sheet` liability dollar change; `cash_flow_statement` debt, card, and lease payments | Exclude D&A and lines already counted above |
| Account names | `accounts_get_workspace` | The client entity's rows only |

## Traps

- `entityId` (integer) and `workspaceId` (UUID) are not interchangeable. Reports take
  `entityId`; `accounts_get_workspace`, `financial_accounts_query`, and
  `transactions_query` take `workspaceId`; `ledgers_list` takes `entityIds`.
- Reports take `startDate` / `endDate`; transaction queries take `since` / `until`.
- All three reports require `ledgerId`. Use the same window on all three.
- A read that still fails after the single retry: stop and tell the user what failed.

## Workflow mapping

| Procedure step | Calls |
| --- | --- |
| 1. Orient | `list_kick_skills`, `load_kick_skill`; `context_resolve` `entity` (or `context_browse` `workspaces`); `accounting_query` `ledgers_list` |
| 2. Read | `reports_query` `profit_loss`, `balance_sheet`, `cash_flow_statement`; `accounting_query` `accounts_get_workspace`; optional `financial_accounts_query` `list`, `transactions_query` `find` or `statistics` |
| 3. Map | No calls. Account names come from the step 2 reads |
| 4. Compute | No calls. The script runs locally |
| 5. Present | No calls. The method note reports any drift |

## Tool errors and schema drift

- **Tool errors and schema drift:** if a live call is rejected, trust the live error hint (and
  any loaded guide) over this skill's examples. Fix the call and retry once. For writes, a
  rejected call restarts the confirmation flow: re-preview, never resend a stale confirmation
  token. If the working shape contradicts this skill's text, add a method note to the
  deliverable so it can be reported and fixed centrally. Never edit this skill file mid-run.

This skill makes no writes and has no `confirmationToken` flow. Example method note: "one
step worked differently than this skill describes: `reports_query` wanted `since` / `until`
rather than `startDate` / `endDate`."
