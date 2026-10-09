# Google Sheets mode: live MRR report and dashboard

Sheets mode is a different place to read from, not a different method. The skill scans
every tab it can see in the user's spreadsheet (Kick reports pulled by the Kick add-on,
exports the user pasted in from Stripe, QuickBooks, or a bank, their own MRR or customer
tables), then runs the same scan, defaults, questions, build, report shapes, gaps, and
dashboard as every other path. It adds tabs named `MRR …` that hold formulas reading the
source tabs, so the report recalculates whenever a source tab changes. "Live" means as
current as the source tabs: for Kick tabs, the last add-on refresh; for a pasted export,
the last paste.

Anyone with a spreadsheet can use it. Offer it in plain words: "I can also set this up in
your Google Sheet so it updates whenever the data there does." The customer CSV stays the
snapshot option for people who don't want tabs added.

The chat report is still built from `scripts/mrr_build.py`. The sheet must show the same
numbers for the same rows, and the chat checks that after writing it (step 6).

## 1. Inventory every tab

Before asking the user to pull anything, open the spreadsheet through the chat's Google
Sheets connection and read it whole:

1. List all tabs: name, id, hidden or not, row and column counts.
2. Read the top of each tab (header block plus about 40 rows). Save each read to a file
   named `<tab name>.csv` in one folder. Large tabs: read in pages and append; never
   truncate. If a read was cut, say what was cut.
3. Run the classifier:

   ```
   python3 scripts/sheet_sources.py inventory --tabs-dir tabs \
       --window-from 2026-01 --window-to 2026-09 --out inventory.json
   ```

   It labels each tab:
   - **Kick report**: header block in column B (row 2 entity, row 3 report title, row 4
     date label), tab name `<Entity> - <Report>`, basis in the footer row. It records
     the entity, basis, the header's stated range, the first and last dated line, the
     grain, and for Waterfall and Rollforward tabs the grouping (By schedule or By
     customer) and whether the periods are months.
   - **User data**: a table with a header row. It suggests the customer, date, amount,
     plan, and term columns from the header text.
   - **Skill-owned**: tabs whose names start with `MRR `. Never a source.
4. Read `preflight`. It fails (exit 4) when a General Ledger's lines stop more than
   `--gap-days` (default 31) short of its header's dates, when a Waterfall is grouped by
   start month or uses quarterly periods, or when no tab covers the requested window.
   Stop and ask for exactly one re-pull: report, basis, entity, and dates. If the user
   says to proceed, re-run with `--proceed` and state the real window in "How I counted"
   and in the sheet's data checks.
5. Several entities across tabs: ask which one, once. Never mix entities in one total.
6. Say what was found in the first look, in plain words: "I found 5 Kick reports and one
   tab of yours; I'll use the Waterfall for customers on schedules and the ledger for
   the rest." Repeat it in "How I counted" and in the sheet's data checks.

Ask the user to pull or re-pull a report only when the preflight says no tab covers the
window. Then send one message:

> In this Google Sheet, open Extensions → Add-ons → Kick, sign in, and pull
> **<report>** for **<entity>** on the **<basis>** ledger, dates **<from> to <to>**,
> with auto-refresh on. Then tell me.

For a General Ledger pull: one entity, all accounts or only revenue accounts, dates from
12 months before the first reporting month to today. For a Waterfall: monthly periods,
grouped by schedule or by customer, never by start month. The spreadsheet locale must be
United States (File → Settings) so the add-on's dates parse.

## 2. Choose one source per customer

Rule R2 from `references/kick.md`, applied to tabs:

| Customer has | Use |
|---|---|
| Rows in a Revenue Waterfall | Recognized amount per month (`source = schedule`, `term_months = 1`, `term_end` from the Rollforward when present) |
| Billing records (the user's invoice or Stripe tab) | The billing record (`source = billing`) |
| Only ledger revenue lines | General Ledger lines in the revenue accounts (`source = ledger`) |
| Only bank deposits | Deposits (`source = cash`) |

- Never two sources for one customer's same revenue. An accrual ledger holds the
  recognition journal entries that the Waterfall already shows.
- The Rollforward is not a revenue source. It supplies term ends for renewals and a
  cross-check (recognized in period against the Waterfall).
- Processor payouts (`Stripe Deposit for period ending …`) are not customers. Left out
  and sized, as in `references/other-sources.md`.
- "No counterparty" rows in a Waterfall are revenue with no customer: excluded and sized.

Build the rows for the script from the chosen tabs:

```
python3 scripts/sheet_sources.py rows --tabs-dir tabs --out rows.csv \
    --waterfall "<Entity> - Revenue Waterfall" --rollforward "<Entity> - Revenue Rollforward" \
    --grouping "By schedule" \
    --table "Stripe invoices" --customer-col Customer --date-col Date --amount-col Amount \
    --ledger "<Entity> - General Ledger" --revenue-accounts "400000 - Revenue"
```

It prints how many ledger and table rows were left out to avoid double counting. Feed
`rows.csv` to `scripts/mrr_build.py scan` and `build` as in the main procedure.

## 3. Build the sheet plan

Write `sheets_config.json` from the inventory and the user's answers. The full shape is
in the header of `scripts/build_sheets.py`:

- `entity`, `firstMonth` (`YYYY-MM-01`), `includeCurrentMonth`, `currency`, `basis`.
- `sources`: `ledger` (tab, revenue account labels exactly as the tab shows them, the
  header's stated dates), `waterfall` and `rollforward` (tab, grouping), `userTable`
  (tab, headers, chosen columns). Every source is optional; at least one is required.
- `tabsFound`: every tab from the inventory with its kind and whether it is used, so the
  `MRR sources` tab can list them.
- `rules`: one per plan seen in the descriptions, most specific first (`plus quarterly`
  → Plus, 3 months). Generic monthly, quarterly, annual, and setup rules are appended
  unless `skipDefaultRules` is true.
- `overrides`: exclusions, `reportAs` to combine names, and plan or months for customers
  whose descriptions say nothing.
- `accelMultiple` (3), `gapDays` (31), `minCoverage` (0.8): the C9 and data-quality
  thresholds, same defaults as the script.

```
python3 scripts/build_sheets.py --config sheets_config.json --out-dir <dir> --emit-payloads
```

The formula lint (`scripts/sheets_lint.py`) runs first and fails the build on a name
collision or a formula that reads a source tab by name instead of through `MRR sources`.
Outputs: `<slug>-mrr-sheet-plan.json`, `<slug>-mrr-sheets-installer.gs`, and
`payloads/` (see step 4). Then simulate the rules on the scanned rows: every recurring
revenue line must match a rule or an override.

## 4. Write the plan into the spreadsheet

Write only `MRR …` tabs. Never write to, format, rename, move, hide, protect, or add a
formula, note, filter, frozen row, column width, named range, or validation to a Kick tab
or a user data tab. New tabs go after the user's tabs; the plan's `displayOrder` orders
only the MRR tabs among themselves.

Before the first write, say once what will happen: the tab names, how many write calls,
and that the existing tabs are untouched. Then send the files in `payloads/` verbatim, in
the order `manifest.json` lists:

| File | Sends | API call |
|---|---|---|
| `01-tabs.json` | `addSheet` for each missing tab with `columnCount`, `tabColor`, `frozenRows`; for existing MRR tabs, clear values, merges, charts, protections, and conditional formats; delete `retiredTabs` (`MRR lines`) | `spreadsheets.batchUpdate` |
| `02-values-NN.json` | Every `writes` range, chunked to `--chunk-bytes` (60000) | `values.batchUpdate`, `valueInputOption: USER_ENTERED` |
| `03-format-NN.json` | Formats, merges, dropdowns, conditional rules, widths, hidden columns, charts, warning-only protection, tab order | `spreadsheets.batchUpdate` |

`createOnly` tabs (`MRR settings`) are skipped when they exist, so the user's edits
survive a rebuild. Pass the existing sheet ids with `--sheet-ids` on a rebuild so the
payloads target them.

If the connection can write values but not run `batchUpdate`, send the values and say
that formats, charts, and protection were skipped; offer the installer (step 5) to
finish. Never send formulas as raw text.

If a write is refused: stop. Report exactly what exists now (tab names and ids from the
manifest's `created_tabs`), and offer three choices: retry, run the installer, or remove
the tabs this run created. Do not retry on your own. If the build fails or the user
cancels, offer to delete only the tabs this run created.

## 5. Fallback: paste-once installer

When the chat can't write, send `<slug>-mrr-sheets-installer.gs`: open Extensions → Apps
Script in the same spreadsheet, delete the starter code, paste the file, save, run
`installMrrReport`, and approve the prompt. It applies the same plan, including formats,
charts, and protection, and adds an "MRR report" menu with Rebuild and Remove. On an
error it reports which tabs it created. Then ask the user to paste `MRR report`!A3:G8
back into the chat for step 6.

## 6. Check the sheet against the report

Wait for the sheet to calculate, then read back:

1. Every cell of every `MRR` tab. Any `#REF!`, `#NAME?`, `#VALUE!`, `#N/A`, `#DIV/0!`,
   or `#ERROR!` means the build is not done.
2. `MRR report`!A3: the status banner must read "All checks passed". Anything else
   names the failing check.
3. `MRR rows`: export the rows whose check says OK and run `scripts/mrr_build.py build`
   on them with the same settings. Compare every month, not only the latest: MRR, ARR,
   customers, each movement, churn, within 0.01. Known differences the comparison must
   not hide: the sheet applies C9 per customer and policy while the script applies it
   per customer; the sheet relies on rules and terms rather than the minimum-history
   rule; the sheet's churn grace is one month only.
4. The design: the four charts exist on `MRR dashboard` where the plan anchors them, no
   cell shows `###`, tabs sit in `displayOrder` after the user's tabs.

Report the result in one line. If anything differs, find the lines that fell out (the
check column on `MRR rows` and the data checks panel) and fix the config, then rebuild.
Don't call it done with a difference unexplained.

Then tell the user what was built, what it updates from, and that the yellow cells on
`MRR settings` and `MRR sources` are theirs to edit.

## Tabs

In `displayOrder`. Colors: dashboard and report blue, settings and sources amber,
calculation tabs grey. Everything except settings and sources carries warning-only
protection.

| Tab | Holds | Edited by the user |
|---|---|---|
| `MRR dashboard` | Title, as-of month, source line, status banner, 8 KPI tiles, MRR sparkline, 4 charts (MRR by month, movements, MRR by plan, top customers), last 12 months | No |
| `MRR report` | Status banner, headline, KPIs, latest-month bridge with its strict tie, concentration, MRR by plan, renewals in 60 days, data checks, monthly table | No |
| `MRR settings` | First month, current-month toggle, plan rules, customer overrides, accounts found | Yes, yellow cells |
| `MRR sources` | One row per source (General Ledger, Revenue Waterfall, Revenue Rollforward, your table): tab picked from a dropdown of tabs found, grouping, stated and actual dates, rows read, status; C9 multiple, gap days, minimum coverage; the user table's column picks; the data-quality line; other tabs found | Yes, yellow cells |
| `MRR rows` | The single input for everything downstream: customer, month, amount, term months, cadence, source, plan, term end, check, built by unioning the adapters | No |
| `MRR inputs` | The adapters: ledger lines (A:N), Waterfall intersections with C9 (T:AG), Rollforward term ends (AI:AL), the user table (AN:BA); accounts found and the ledger tie-out | No |
| `MRR grid` | Customer by month MRR, starting at the first revenue month | No |
| `MRR movements` | New, expansion, contraction, churn, reactivation, or active per customer and month | No |
| `MRR customers` | Plan, billing, payments, first and last, term end, renewal, latest MRR, status, share | No |

Chart helper ranges live on the calculation tabs, never on a source tab.

Design: whole dollars on tiles, cents in detail tables, one decimal on percentages,
`mmm yyyy` dates, negatives red with a minus sign, zeros as a dash; text left, numbers
right; frozen headers; column widths set so nothing shows `###`; merges only for tiles;
column charts for MRR by month, stacked columns for movements, a donut for plan mix only
with two or more plans, bars for the top 10 customers; one palette from
`dashboard.html`; titles on every chart. No firm or Kick branding.

## How the numbers are built

- Every formula reads a source tab through `INDIRECT` of the tab name typed on
  `MRR sources`, and finds columns by header text. A refresh that clears and rewrites a
  source tab, adds rows, or shifts a column doesn't break anything.
- Ledger adapter: a revenue line is a ledger line in one of the revenue accounts. The
  customer is the counterparty or the override's "Report as". Plan and billing months
  come from the first rule whose pattern matches the description; overrides beat rules.
  A payment covers its billing months starting with the month it was booked, at amount
  divided by months. Payout descriptions are marked and left out.
- Waterfall adapter: finds the month columns by header, picks the customer and policy
  intersection rows (skipping subtotal and total rows), treats "No counterparty" as a
  blank customer, and applies C9: a last positive month at `accelMultiple` times the
  prior month, or a negative month followed by positive months, uses the prior month's
  amount and is counted in the data checks.
- Rollforward adapter: the `Schedule end date` per customer feeds renewals.
- User table adapter: the columns picked on `MRR sources`; rules run on the plan column.
- `MRR rows` unions the three blocks, canonicalizes names case-insensitively (so
  `UNIQUE` and `SUMIFS` agree), and marks ledger or table rows for a customer already
  counted from the Waterfall as "Counted from Waterfall", never twice.
- The grid clamps negative months at zero; the strict tie on the report fails closed on
  any error value. Movements, retention, and ARR follow `references/mrr-method.md`.

## Rules

- SH1. Never edit, rename, move, hide, protect, format, or add anything to a Kick tab or
  a user data tab. Only `MRR …` tabs are written.
- SH2. The MRR tabs hold formulas only. The only typed values are the yellow cells on
  `MRR settings` and `MRR sources`, and the lists of tabs and headers the build writes
  for the dropdowns.
- SH3. One entity per setup. For a second entity, a second spreadsheet.
- SH4. The skill writes nothing to Kick. In the spreadsheet it writes only MRR tabs, and
  only after the user sent the link.
- SH5. Write only what `build_sheets.py` produced, verbatim from the payload files.
  Never type a figure or hand-edit a formula; change the config and rebuild.
- SH6. The chat report is the reference. Step 6 runs before the sheet is called done.
- SH7. "Live" is allowed in this mode only, meaning as current as the source tabs. The
  HTML dashboard stays a snapshot.
- SH8. Inventory first. Ask for a pull only when no tab covers the window, and name the
  report, basis, entity, and dates.
- SH9. One source per customer. Ledger lines for a Waterfall or table customer are
  counted in the data checks, never in MRR.
- SH10. The lint passes before any write. No single-letter LET or LAMBDA names; no
  direct reads of a tab the skill doesn't own.
- SH11. Fail closed. An error anywhere in an MRR tab, a tie that doesn't hold, or a
  failing preflight is reported as unfinished, never worked around.
- SH12. Every tab this run created is tracked by id, and only those are offered for
  removal.

## Limits

- Churn grace in the sheet is one month. A late renewal shows as churn, then
  reactivation. The chat report can use the two-month option; say so if they differ.
- Classes aren't used. MRR by plan comes from rules and Waterfall policy names.
- Account labels can't contain commas.
- A renamed counterparty starts as a new customer unless an override maps the old name.
- Large ledgers (tens of thousands of lines) recalculate slowly. Pull only revenue
  accounts when a sheet gets slow, and say so.
- Connections differ by chat and change over time. Some only read; some write values
  but not formats or charts. Step 4 says what to do in each case.
- The Revenue Waterfall and Revenue Rollforward reports exist in the add-on only on
  workspaces with revenue recognition (Advanced plan). Elsewhere the ledger and user
  tables are the sources.

## Maintaining the plan

`references/templates/sheets_plan.json` is the single source for every tab, formula,
format, chart, color, protection, and order. `build_sheets.py` fills its placeholders,
`sheets_lint.py` checks every formula, `sheets_payloads.py` turns it into API request
bodies, and `references/templates/sheets_applier.gs` replays it as Apps Script. Formulas
use plain references to `'MRR settings'` and `'MRR sources'` cells, not named ranges,
so any tool that writes cells can apply them. Tests: `python3 -m unittest discover tests`
from the skill folder.
