# Kick binding: revenue-finder

Loaded at Procedure step 7 when the client's books are on Kick. The books corroborate or
contradict what the client said, and supply at most three questions to ask. Every call
is a read. Every tool and parameter here comes from the Kick connector pack.

## Published guides

Discover with `list_kick_skills` and no `query`, which lists every guide, then
`load_kick_skill` each of the three below. A `query` is a ranked fuzzy search that can
drop guides you need: on local Kick (2026-11-09), "financial reports" returned neither
of the two lookup guides. Guide names are not guessable; use the ones the list returns.

| Guide | Serves |
| --- | --- |
| `kick/entity-lookup` | Find the client's entity by name among the workspaces the user can see |
| `kick/chart-of-accounts-and-ledger-lookup` | `ledgerId` and the accounting basis |
| `kick/financial-reports` | Owns the report parameters and pitfalls; follow it for every `reports_query` call |

A guide that fails to load: retry once, then continue without it. A guide that names
tools or shapes the live list lacks: use the call shapes below and the live schema. Note
either in the method note.

## Tools used

| Tool | Operation / report | Purpose |
| --- | --- | --- |
| `list_kick_skills` / `load_kick_skill` | (none) | Load the three guides before any report call |
| `context_resolve` | `entity` | Numeric `entityId` for the client |
| `accounting_query` | `ledgers_get` | `ledgerId` and the basis (cash or accrual) |
| `reports_query` | `profit_loss` | Revenue, payroll, contractor, and margin lines by month |
| `reports_query` | `balance_sheet` | Cash, receivables, payables, sales tax payable, loans at window end |
| `reports_query` | `expenses_by_vendor` | Payroll providers, software, and outside advisors the client already pays |
| `reports_query` | `account_transactions` | Only when total equity and net income differ: the equity entries behind the gap |

## Call shapes

- **Entity:** `context_resolve { target: "entity", query: "<client name>" }` returns the
  numeric `entityId`. More than one match: list them and ask. Confirm the entity name
  matches the client before any report.
- **Ledger:** `accounting_query { operation: "ledgers_get", entityId }` returns the
  `ledgerId` and the basis. `operation` and `entityId` sit at the top level, never under
  `params`. No `ledgerId` in the response: `accounting_query { operation:
  "ledgers_list", entityIds: [entityId] }`. State the basis in coverage.
  An entity can return two ledgers, one with basis `"cash"` and one with basis
  `"accruals"` (observed on local Kick, 2026-11-09). Use the `"accruals"` ledger for
  every report: the receivables and payables checks need it. Only a cash ledger: use
  it and apply the cash-basis trap below. Run every report on the same ledger.
- **Window:** reports run on full months. Use the 12 full months ending at the last month
  end inside the skill's window, as `startDate` / `endDate` in `YYYY-MM-DD`, and name
  that period on every ledger line.
- **P&L:** one call, `reports_query { report: "profit_loss", params: { entityId, ledgerId,
  startDate, endDate, cycle: "month" } }`. Monthly columns come back in one response;
  never loop one call per month.
- **Balance sheet:** `reports_query { report: "balance_sheet", params: { entityId,
  ledgerId, startDate, endDate } }`, read at the window end, and at the window start
  for a change. For the start, run the month before the window (for a November to
  October window, `startDate` the first of October and `endDate` the last of October).
  Empty rows there mean no earlier history: compare from the first month in the window
  and say so on the ledger line.
- **A report that errors:** read the error's hint and retry once, changed or unchanged.
  A second failure means that report is unread; do not try other parameter shapes.
- **Vendors:** `reports_query { report: "expenses_by_vendor", params: { entityId,
  ledgerId, startDate, endDate } }`, same window.

## Reading the responses

The connector docs do not describe report bodies. These shapes were observed on local
Kick (2026-11-09); trust a live response that differs and note it in the method note.

- **P&L:** `data.data.periods` lists the months, then a last period with `isTotal: true`.
  `data.data.sections` holds `income`, `cogs`, `expenses`, `otherIncome`,
  `otherExpenses`, and `netIncome`. Each account row has `category` (the label) and a
  `data` array of `{ label, value }`, one per period. A section's own `data` array is
  its total. Window net income is the Total entry of `sections.netIncome.data`.
- **Balance sheet:** `data.data.rows` nests groups (`label`, `rows`, `totals`) down to
  account rows (`label`, `key` holding the account code, `values`). The Equity group
  lists each equity account plus a computed row labeled Net Income; the group's
  `totals` is total equity. Rows with no activity are hidden
  (`presentation.rowVisibility` `with_activity`). A missing row means a zero balance
  with no activity, never proof the account does not exist: write "no sales tax
  payable balance", not "no sales tax payable account".
- **Vendors:** `data.rows`, each with `vendorName` and `total`. Expense lines with no
  vendor come back as one row named "No vendor"; it is not a vendor.
- Quote account and vendor labels exactly as the report returns them (Cash on Hand,
  Owner Capital, Salaries and Wages). Never rename or retype them.

## From reports to ledger checks

This is the pull list no guide carries. Each row says what corroborates a quoted need.

| Service the client asked about | Read | Corroborates when | Contradicts when |
| --- | --- | --- | --- |
| Payroll | P&L wage and payroll tax lines; vendors for a payroll provider | Wages appear or grow in the window, or contractor spend rises | An outside firm already runs payroll for them (a full-service provider or another accountant). Payroll software the client runs themselves is not the service and contradicts nothing |
| Bookkeeping or cleanup | P&L uncategorized or suspense lines; balance sheet clearing accounts | Uncategorized or clearing balances are material | None at the window end |
| Cash flow forecasting | Balance sheet bank cash at window end; P&L net income for the 3 months ending there | Those 3 months average a net loss, and bank cash is under six times that average loss. Show the cash and the three losses, no runway figure | Those 3 months average net income, not a loss |
| AP and AR | Balance sheet receivables and payables; P&L revenue | Receivables exceed one month of average revenue | Receivables near zero |
| Multi-state and sales tax | Balance sheet sales tax payable; P&L revenue by line | Sales tax payable carries a balance, or revenue lines show new channels | No sales tax lines and no product revenue |
| CFO or advisory | P&L revenue trend; balance sheet construction in progress, new fixed assets, new loans | Revenue moved more than 10% in the window, or a new location, buildout, or loan appears on the balance sheet | (no contradiction; mark no ledger signal) |
| Tax planning | P&L net income | Net income for the window is positive and material to the owner | A loss for the window |

A row not listed here gets "no ledger signal". Never stretch a table row to fit. For
cash flow forecasting, an average loss with bank cash at six times that loss or more is
neither: "no ledger signal".

The cash flow forecasting test matches ping-client-meeting's. Its other checks use other
windows, so the two skills can read the same books differently; never cite the other
skill's verdict.

Ledger signals with no quote (Procedure step 7): use the same reads and the same
thresholds. At most three, each with its figure, report, and period, phrased as a
question for the relationship owner.

## Tie check

Before any ledger line: expense totals should be positive, assets should equal
liabilities plus equity on both balance sheets, and the P&L net income for the window
should equal the change in total equity from the window-start balance sheet to the
window-end one.

- **Compare total equity, not Retained Earnings.** At a year end Kick closes the
  year's earnings into whichever equity account carries its retained-earnings role.
  That account may be labeled Owner Capital or Owner's Equity, and an account labeled
  Retained Earnings can stay flat. On local Kick (2026-11-09), a November to October
  window showed Retained Earnings unchanged and Owner Capital up by the prior year's
  earnings. Net Income on the balance sheet is this fiscal year to date only. So
  Retained Earnings plus Net Income alone misses whenever the window crosses a year end.
  A flat Retained Earnings is not a bookkeeping problem, and an equity account rising
  by the closed earnings is not an owner contribution.
- **Gap left in total equity.** If total equity moved by more or less than the P&L
  net income, the gap can only be owner contributions or distributions. When equity
  rows labeled for them (Contributions, Distributions, Draws) moved by the gap, the
  books tie; name those rows on the tie line. Otherwise read `reports_query { report:
  "account_transactions", params: { entityId, ledgerId, startDate, endDate,
  accountCodes: [<code of each equity account that moved>] } }` once for the window. The code is
  the row's `key`. Entries that put cash in or take it out explain the gap; anything
  left is a miss.

Any miss means the books did not tie; follow the skill's caveat for untied books. A
negative bank balance is not a miss; list it as a ledger signal.

## Traps

- `since` / `until` on a report call, or a workspace UUID as `entityId`. Read the
  error's named field and fix that field.
- Rebuilding the P&L from transactions instead of `reports_query`.
- Cash basis: revenue lands when collected. Receivables may be missing; say so before
  calling a receivables check contradicted.
- The firm's own entity is not the client's. Read only the client's entity.

## Workflow mapping

| Procedure step | Calls |
| --- | --- |
| 2. Discover | `list_kick_skills`, then `load_kick_skill` for the three guides |
| 3. Coverage | `context_resolve` (entity); `accounting_query` `ledgers_get` (or `ledgers_list`) for the `ledgerId` and basis |
| 7. Corroborate | `reports_query` `profit_loss` (monthly), `balance_sheet` (window end and start), `expenses_by_vendor`; `account_transactions` only for an equity gap |
| Every other step | No Kick calls |

## Tool errors and schema drift

**Tool errors and schema drift:** if a live call is rejected, trust the live error hint (and
any loaded guide) over this skill's examples. Fix the call and retry once. For writes, a
rejected call restarts the confirmation flow: re-preview, never resend a stale confirmation
token. If the working shape contradicts this skill's text, add a method note to the
deliverable so it can be reported and fixed centrally. Never edit this skill file mid-run.

This skill makes no writes.
