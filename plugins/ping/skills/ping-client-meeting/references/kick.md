# Kick binding: ping-client-meeting

Loaded at Procedure steps 3, 5, 6, and 8. Kick holds the books half. Every call is a read.
Load Kick's own guide first: `list_kick_skills`, then `load_kick_skill` with
`kick/financial-reports`. It owns the report params and their traps; this file carries
only the pull list and the thresholds.

## Tools used

| Tool | Operation or report | Purpose |
| --- | --- | --- |
| `list_kick_skills`, `load_kick_skill` | `kick/financial-reports` | Report params and pitfalls |
| `context_resolve` | `target: "entity"`, then `target: "ledger"` | The client's `entityId`, `workspaceId`, `ledgerId` |
| `accounting_query` | `ledgers_get` | Ledger basis and closed-through or lock date |
| `reports_query` | `profit_loss` with `cycle: "month"` | Monthly P&L for swings and trends |
| `reports_query` | `balance_sheet` | Cash, receivables, and the balance check |
| `reports_query` | `expenses_by_vendor` | Cloud and payroll vendors |

## Call shapes

- **Guide:** `list_kick_skills`, then `load_kick_skill` with
  `{"name": "kick/financial-reports"}`.
- **Resolve:** `context_resolve` with `{"target": "entity", "query": "<client name>"}`,
  then `{"target": "ledger", "entityId": <entityId>}`.
- **Ledger:** an entity can have a cash and an accrual ledger. The ledger resolve then
  lists both as `candidates` with `isAmbiguous: true`, and `ledgers_get` returns both
  rows (`id`, `entityId`, `basis`). Use the ledger whose `basis` is `accruals`; with
  only one ledger, use it. The Read note names the basis. Every report call carries the
  chosen `ledgerId`.

`accounting_query` takes its fields at the top level:
`{"operation": "ledgers_get", "entityId": <entityId>}`. `reports_query` names the
report in `report`, not `operation`, and puts every other field inside `params`:
`{"report": "profit_loss", "params": {"entityId": <entityId>, "ledgerId": "<ledgerId>",
"startDate": "YYYY-MM-DD", "endDate": "YYYY-MM-DD", "cycle": "month"}}`. `entityId` is a
number. Load the guide before the first report call, in recap mode too. A recap that
needs no figure makes no Kick call, the guide included.

- **Latest closed month (M):** the closed-through or lock date from the ledger. Kick's
  ledger reads return no such field today, so expect none. None returned: M is the last
  full calendar month before today, and the Read note says "Kick returned no
  closed-through date; <month> used as the latest month." A missing date is not a
  failed check: it does not go under Watch out for and does not label numbers
  unreviewed. Never write "books closed through" without a date from a read.
- **P&L:** `profit_loss`, `cycle: "month"`, from the first day of M minus 17 months to
  the last day of M. Eighteen columns cover three test months, their baselines, and the
  same months a year earlier.
- **Balance sheets:** `balance_sheet` with `endDate` the last day of M, and again with
  `endDate` the day before the P&L window starts. The report reads at `endDate`; set
  `startDate` to the first of the same month because it is required.
- **Vendors:** `expenses_by_vendor` for the 12 months ending with M.
- **Recap figure:** the one report that answers the question asked today, usually
  `profit_loss` with `cycle: "month"` for the months named. A general ask ("the
  October numbers") gets the report's own total lines for that month and the month
  before: total income, cost of goods sold when the report has that section, total
  expenses, and net income. Never add lines together to make a total.

## Reading the reports

Shapes observed on live Kick (2026-11-11); the connector docs do not describe report
bodies, so trust a live response that differs and note it. Read figures from these fields; never rebuild a total.

- **P&L:** `data.data.periods` lists the month columns, then a `Total` column
  (`isTotal: true`). `data.data.sections` is keyed `income`, `cogs`, `expenses`, `otherIncome`, `otherExpenses`, `grossProfit`,
  `netOperatingIncome`, `netIncome`. Each section's own `data` is its total by period:
  total income is `income`, cost of goods sold is `cogs`, total expenses is `expenses`
  (COGS not included), net income is `netIncome`. Account lines sit in the section's
  `rows`, named by `category`, with one `data` entry per period. Each entry carries
  its period `label` ("Jul 2026"): take a month's figure by that label, never by
  position, and skip the `Total` entry when reading months.
- **Balance sheet:** `data.data.rows`, nested, each with `label`, and `values` for an account or
  `totals` for a group. The top two groups are `Assets` and `Liabilities and Equity`;
  their `totals` are the two sides of the balance check. Bank cash is every account
  under the `Cash` group (for example "Cash on Hand"). Equity carries a computed
  `Net Income` row for the year to date. Rows with no activity are hidden, so a missing
  row means no balance, never proof the account does not exist: write "no sales tax
  payable balance", not "no sales tax payable account".
- **Expenses by vendor:** `data.rows` with `vendorName` and `total`, COGS included.
  Spend with no vendor is the "No vendor" row, never a vendor. There is no grand total
  row; `data.total` is the row count, not dollars. `data.hasMore` true means the list is cut
  off: the Read note says vendor spend is partial. The docs list no paging parameter for
  this report, so never guess one.

## Unusual swings

Test every P&L account line (not totals) in each of the three months ending with M.

- Baseline: the average of that account's three months before the test month.
- A swing: the change is at least 25% of the baseline (any change from a zero baseline
  counts) and at least the larger of $5,000 or 5% of M's total income. Use M's income
  for all three test months.
- Seasonal: the same account, in the same month a year earlier, also moved at least 25%
  from its own three-month baseline in the same direction. Note it in one line, do not raise it.
  When the year-earlier month predates the books' first activity, the check cannot run:
  raise the swing, and the Read note says the books start in <month>, so no seasonal
  check.
- Raise at most three swings, largest dollar change first. Show the month figure, the
  three baseline months' figures (never their average), and the months. A conversation
  that explains the swing is cited next to it.

## Opportunities from the ledger

A ledger-only opportunity needs its threshold met. A client's own words can raise the
same opportunity below its threshold (`SKILL.md` step 6): show the read figures and do
not claim the threshold. Either way the matching service must be out of scope in Ping's
agreements. When Ping returns no agreements, scope is unknown: write "worth asking
whether this is in scope", and say under Watch out for that agreements were not read.
With no agreement on file, a transcript or the client summary that says the firm
already provides the service puts it in scope: drop the opportunity.
Cash forecasting uses the same test as revenue-finder. The other thresholds are not
revenue-finder's corroboration checks: those use other windows and cost lines, so the two
can read the same books differently. Never cite one skill's
verdict in the other's deliverable. Each shows the figures it read, and a ledger-only item
stays a question to ask in both.
Frame each as worth exploring. Never claim eligibility, estimate a credit or saving, or
give a tax position.

| Opportunity | Threshold (interim defaults) | Figures to show |
| --- | --- | --- |
| R&D credit conversation | Cloud platform spend of at least $60,000 over 12 months, or at least $5,000 in each of the last 6 months | Each cloud vendor's 12-month total as the report states it |
| Payroll services | Wages at least $10,000 in M, and one of: a self-serve payroll tool in vendors, wages in the 3 months ending M at least 15% above the same 3 months a year earlier, or a conversation about running payroll in-house, new hires, or a new state | Wages in M and in the month three months before M, the tool and its 12-month cost. No percentage |
| Cash forecasting | The 3 months ending M average a net loss, and bank cash at M divided by that average loss is under 6 months | Bank cash at M and the three monthly net losses, side by side. No runway figure. Bank cash is every bank and cash line on the balance sheet at M; with several, show each line, and a total only if the report prints one |
| Collections | Receivables at M divided by (total income of the 3 months ending M / 90) is over 60 days | Receivables at M and total income for each of the 3 months. No day count |
| Sales tax | An income line for product or online sales, and no sales tax payable balance on the balance sheet | The income line and its months, labeled "from the books only" unless a client raised sales tax |

- Cloud platforms: Amazon Web Services (AWS), Google Cloud, Microsoft Azure, Oracle
  Cloud, DigitalOcean, or an account named for cloud hosting or infrastructure. A vendor
  named only "Amazon" in supplies or office expense is a marketplace purchase, not cloud.
- Self-serve payroll tools: Gusto, OnPay, QuickBooks Payroll, Square Payroll, Patriot.
  A PEO or full-service provider (ADP, Paychex, Justworks, TriNet) means payroll is
  handled; raise payroll only if a conversation complains about it.
- R&D wording: "Cloud spend of $X suggests they build software. Worth asking whether an
  R&D credit study fits. Eligibility depends on the work, not the spend."

## Balance check

Both balance sheets: the `Assets` total equals the `Liabilities and Equity` total. A
balance sheet dated before the books' first activity has no `Assets` total; it counts
as balanced at zero. A
miss, or a closed-through date that a read returned and that falls before M, goes under
Watch out for and labels its numbers unreviewed. The Read note says both balanced.

## Workflow mapping

| Procedure step | Calls |
| --- | --- |
| 3. Resolve | `context_resolve` entity, then ledger |
| 5. Books | `load_kick_skill` `kick/financial-reports`; `accounting_query` `ledgers_get`; `reports_query` `profit_loss`, `balance_sheet` twice, `expenses_by_vendor` |
| 6. Swings and opportunities | No new calls; the reads from step 5 |
| 8. Recap figure | `context_resolve`; one `reports_query` per question |

## Tool errors and schema drift

**Tool errors and schema drift:** if a live call is rejected, trust the live error hint
over this file. Fix the call and retry once. If the working shape contradicts this
file, add a method note to the deliverable so it can be reported and fixed centrally.
Never edit this skill file mid-run.

This skill makes no writes. No Kick tool that creates, updates, or deletes is called.
