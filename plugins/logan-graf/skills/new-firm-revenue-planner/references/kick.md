# Kick binding: new-firm-revenue-planner

Loaded at Procedure steps 2 and 3 when Kick is connected. It finds the firm's own books
and drafts the plan's inputs from them. Every call is a read. Every tool and parameter
here comes from the Kick connector pack.

## When Kick has nothing to give

Skip this file and go to the skill's step 4 when:

- No Kick tools are available in the session.
- `context_browse` lists no workspace that is the firm's own. A firm owner often sees only
  client workspaces; those are not the firm's books.
- The firm's entity has fewer than three full months of revenue on the P&L.

Do not say which of these applied. Step 4 opens the projection conversation without announcing the miss.

## Published guides

Discover with `list_kick_skills` (query "financial reports"), then `load_kick_skill` the
match. Guide names are not guessable; use the ones the list returns.

| Guide | Serves |
| --- | --- |
| `kick/entity-lookup` | Step 2: find the firm's own entity among the workspaces the user can see |
| `kick/chart-of-accounts-and-ledger-lookup` | Step 2: `ledgerId` and the accounting basis |
| `kick/financial-reports` | Step 3: owns the report parameters and pitfalls; follow it for every `reports_query` call |

## Tools used

| Tool | Operation / report | Purpose |
| --- | --- | --- |
| `list_kick_skills` / `load_kick_skill` | (none) | Load `kick/financial-reports` before any report call |
| `context_browse` | `workspaces` | List workspaces and entities; spot the firm's own |
| `context_resolve` | `entity` | Numeric `entityId` and the `workspaceId` for the firm |
| `accounting_query` | `ledgers_get` | `ledgerId` and the basis (cash or accrual) |
| `reports_query` | `profit_loss` | Revenue by client by month, delivery and overhead lines, net income |
| `reports_query` | `expenses_by_vendor` | Which vendors are contractors and per-client software |
| `reports_query` | `owner_cash_flow` | Owner draws, for the current take-home pace |
| `reports_query` | `top_transactions` | Fallback for revenue by client when the P&L has no client breakdown |

## Call shapes

- **Workspaces:** `context_browse { operation: "workspaces" }` lists every workspace the
  user can access, with its entities. Pick the one named for the firm and confirm the name
  with the owner. Never read a client's entity as the firm's.
- **Entity:** `context_resolve { target: "entity", query: "<firm name>" }` returns the
  numeric `entityId` and the `workspaceId` (a UUID). Never ask the owner for either ID.
- **Ledger:** `accounting_query { operation: "ledgers_get", entityId }` returns the
  `ledgerId` and the basis. State the basis in the plan.
- **Window:** the last 12 full months ending at the latest month end, or from the first
  month with revenue if later. Report dates are `startDate` / `endDate` in `YYYY-MM-DD`.
- **P&L:** one call, `reports_query { report: "profit_loss", params: { entityId, ledgerId,
  startDate, endDate, cycle: "month", includeCounterpartyBreakdown: true } }`. Monthly
  columns come back in one response; never loop one call per month. The counterparty
  breakdown gives revenue per client. If the flag is rejected, follow the error and the
  loaded guide, then use the `top_transactions` fallback for revenue by client.
- **Vendors:** `reports_query { report: "expenses_by_vendor", params: { entityId,
  ledgerId, startDate, endDate } }`, same window.
- **Owner draws:** `reports_query { report: "owner_cash_flow", params: { entityIds:
  [entityId], startDate, endDate, cycle: "month" } }`. This report takes `entityIds` (an
  array) and rejects `ledgerId`.
- **Revenue fallback:** `reports_query { report: "top_transactions", params: { entityIds:
  [entityId], startDate, endDate, categoryIdentifier: "income" } }`. No `ledgerId`. Group
  the deposits by payer to draft each client's amount and cadence.

## From reports to plan inputs

This is the pull list no guide carries.

| Plan input | Read from | Draft rule |
| --- | --- | --- |
| Recurring clients and prices | P&L income by counterparty, by month | Paid in most months of the window: monthly recurring, at the latest full month's amount. One payment in the window: annual or one-time, owner decides. |
| Delivery cost % | P&L contractor, client-work wages, per-client software lines; `expenses_by_vendor` to tell which vendors those are | Window total of those lines / window revenue. A line that may also fund overhead goes to the owner to split. |
| Fixed overhead | The remaining operating expense lines | Window total, annualized when the window is under 12 months. |
| Current pace (context) | P&L net income; `owner_cash_flow` draws | Shown beside the goal. Never used as the goal. |
| Active client count | Clients with revenue in the latest full month | A floor for capacity, never the capacity. |

Every figure in the drafted table is a sum or a single value from these reads, tagged
"Books" with its period.

## Traps

- `since` / `until` on a report call, a workspace UUID as `entityId`, or `ledgerId` on
  `owner_cash_flow`. Read the error's named field and fix that field.
- Rebuilding the P&L from transactions instead of `reports_query`.
- Cash basis: revenue lands when collected. A client billed but unpaid is invisible; ask.
- Revenue under an unverified or empty counterparty: list the amount as "unassigned
  client revenue" and ask who it is. Never assign it to a client by guess.

## Workflow mapping

| Procedure step | Calls |
| --- | --- |
| 2. Look for data | `list_kick_skills`, then `load_kick_skill` for the three guides; `context_browse`; `context_resolve` (entity); `accounting_query` `ledgers_get` |
| 3. Draft inputs | `reports_query` `profit_loss` (monthly, by counterparty), `expenses_by_vendor`, `owner_cash_flow`; `top_transactions` only as the fallback |
| 4 onward | No Kick calls. The rest of the plan is the owner's answers and the skill's math. |

## Tool errors and schema drift

**Tool errors and schema drift:** if a live call is rejected, trust the live error hint (and
any loaded guide) over this skill's examples. Fix the call and retry once. For writes, a
rejected call restarts the confirmation flow: re-preview, never resend a stale confirmation
token. If the working shape contradicts this skill's text, add a method note to the
deliverable so it can be reported and fixed centrally. Never edit this skill file mid-run.

This skill makes no writes.
