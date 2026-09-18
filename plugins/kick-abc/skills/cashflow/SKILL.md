---
name: cashflow
description: "Builds a weekly cash forecast as a working Excel or Google Sheets model: a date-derived weekly grid where payroll, rent, and loan payments land in the week they actually hit, every cell a formula off an editable driver, plus burn, the lowest cash week, and the cash needed to stay above a minimum balance. Ships with an optional HTML companion to forward. Also rolls an existing forecast forward. Read-only. Use when someone asks for a 13-week cash forecast, a cash flow forecast or model in Excel or Google Sheets, will we run out of cash, how much runway do we have, what is our burn rate, how much do we need to cover the gap, to flag low cash weeks, or to refresh a cash forecast."
---

# Cash flow forecast

## Purpose

Answers two questions: when does cash get tight, and how much covers it. The deliverable
is a working workbook whose grid responds when an input changes, plus an optional HTML
companion. The phases:

1. Scope: build or roll forward, horizon, opening cash, minimum balance
2. Pull cash, aging, and the spend run-rate; put every recurring item on a real date cadence
3. Build, verify, deliver

## Procedure

- [ ] 1. Confirm scope. Read `reference/HOUSE-RULES.md`, `reference/DATA.md`, and
      `reference/MODELS.md` first. Horizon is 13 weeks: state it, do not ask; 6 to 8 when
      cash is tight, through year-end for a funding conversation. Roll forward when a prior
      forecast is attached or named: same grid, closed weeks refreshed, assumptions
      preserved, ask before changing any the client set. Opening cash: the system balance
      from the transaction ledger, never a balance-sheet report, confirmed against the bank;
      a user override is labeled *user-stated*, system figure kept beside it. Minimum
      balance: call it that, never a *floor*; if unnamed, propose a round number near two to
      four weeks of outflows as a planning heuristic, confirm once. Never ask who funds a
      gap or in what increments.
- [ ] 2. Pull cash and bank balances, AR and AP aging, the recurring expense list, and the
      On Kick: guides and pull mapping in `reference/kick.md`. Other connectors: discover at runtime, never guess names.
      trailing 13 weeks of actual flows as the baseline. Without aging, build from the P&L:
      average weekly flows labeled a *straight-line assumption from the P&L*, noting that an
      aging report converts timing into real collection dates. Deliver; never refuse.
- [ ] 3. Put every recurring item on its real cadence, driven by dates, never by counting
      columns: payroll biweekly or semi-monthly from a real recent pay date (two runs in one
      week is the squeeze the grid exists to reveal); monthly items in the week their day
      lands; quarterly and one-off on their dates; a weekly run-rate only for genuinely
      smooth spend. Collections at the aging's historical days-to-collect, never invoice date.
- [ ] 4. Build by adapting `reference/templates/build_cash_model.py`: fill `CONFIG`, run it.
      Two tabs, Forecast and Assumptions. Construction rules in `MODELS.md` and the caveats.
- [ ] 5. Verify:

      ```
      python3 reference/templates/verify_model.py cash-forecast.xlsx \
        --report "Forecast!<lowest cash tile>" "Forecast!<shortfall tile>"
      python3 reference/templates/model_test.py
      ```

      The first (needs `pip install formulas openpyxl`) must report zero errors and zero
      unevaluated formulas (an unevaluated formula is a circular reference, showing 0 in
      Excel); the second edits inputs and asserts the grid responds, which a Python-decided
      schedule fails. If the checker cannot run, say the formulas were not verified.
- [ ] 6. Deliver `{entity}-cash-forecast-{YYYY-MM-DD}.xlsx`, leading with the week and the
      number. Then burn, read off the grid, operands shown: gross burn (average monthly
      outflows), net burn (outflows less inflows, what "burn rate" means unless they say
      gross), runway (cash over net burn, in months); a cash-flow positive business has no
      runway figure, say the cushion in months of outflows, never a negative or infinite
      number. Offer Google Sheets (same `.xlsx` to Drive, per `MODELS.md`) rather than
      assuming; it wins when more than one person edits.

## Guardrails

- **The schedule lives in the sheet, not in the builder** (full rules in `MODELS.md`): four
  editable cells per line (amount, frequency, anchor date, optional end date), every grid
  cell a formula against a header row hung off one start-date cell, so a roll-forward is a
  date edit. A multi-date line becomes one row per date; three dates on one row is three
  hardcoded numbers. Never work out the landing column in Python: that file ties out
  perfectly and does nothing when an input changes.
- **Nothing rescues the cash.** Ending cash goes below the minimum and below zero when the
  drivers say so, in pastel red. No funding row, scenario switch, or facility tracking except
  on explicit request: a funding row hides the dip, and the dip is the finding. Report one
  funding number, the shortfall to cover, the deepest point below the minimum. Never schedule
  or write a payment: when the forecast exposes a gap, name the right conversation
  (collections, financing, payment timing) and stop.
- **The minimum balance is the client's**: propose, confirm once, apply; never move it
  silently or re-flag against a different number without saying so. Forward revenue is an
  assumption, not books data: label it, surface it where they can change it.
- **A roll-forward is never a rebuild, and a rebuild is always a new dated file.** Move the
  window, preserve the assumptions that hold, never resize the grid silently; never
  overwrite the prior forecast, the old file is the record of what was believed when.
- **A first client-facing model goes to a senior reviewer**, and the workbook says so.
- **The HTML companion** (to forward, not edit): write the payload to `data.json`, then

  ```
  python3 reference/templates/build_report.py data.json {entity}-cash-forecast-{date}.html
  python3 reference/templates/theme.py \
          reference/brand-config.md {entity}-cash-forecast-{date}.html
  ```

  Two steps, always in that order: the first writes the report, the second applies the firm
  brand and runs the copy audit; never fuse them, never hand over after only step one.
  Sections: kpi (cash today, lowest cash, its week, cash to cover), waterfall *Where the cash
  goes*, trend of ending cash with the minimum as `threshold`, stack *Money in and money out
  by week* (five or six bands, tail in `Other`, a band never changes sign), the week-by-week
  table, findings *Assumptions* (source and controlling cell each), footnote. A snapshot
  with the data embedded: say so and stamp the as-of date.

## Example

> "You go below your $30,000 minimum in the week of September 7, and cash bottoms out at
> -$8,000 in the week of November 2. Staying above it across the whole thirteen weeks
> takes $38,000. Change the collections cell to test it."

## Completion

Done when:

- [ ] `verify_model.py`: zero errors, zero unevaluated formulas; `model_test.py` passes
- [ ] Week 1 ending cash equals opening plus net change; outflows match the pulled run-rate
- [ ] Minimum balance confirmed with the client, once; delivery led with the shortfall week
      and the one funding number, operands shown

Cleanup: hand over `{entity}-cash-forecast-{YYYY-MM-DD}.xlsx` (plus the HTML path if built);
prior forecasts stay untouched on disk; open assumption questions ride in the delivery message.
