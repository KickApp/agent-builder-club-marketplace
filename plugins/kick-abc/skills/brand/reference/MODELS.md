# Building the cash forecast workbook

Read this before `/cashflow`. It is the craft that makes a workbook a **model** the client keeps
using, instead of a table they look at once.

A model earns its keep the second time it is opened. That means someone other than you has to be
able to change an assumption, watch the whole workbook move, and trust the answer. Everything
below exists to make that true.

## Architecture: two tabs, one direction of flow

```
Forecast     →  the drivers the client owns in columns B to E, and the grid they feed.
Assumptions  →  every driver, where it came from, and the cells that control it.
```

Data flows one way: column B feeds the grid, and nothing feeds back. A number that appears in two
places has already started drifting. The second copy is a formula pointing at the first, or it
does not exist.

**Two tabs is a constraint, not a starting point.** Every extra tab is something the reader has to
be told about. If a workbook needs a "How to use" tab, the workbook is too complicated; fix the
workbook rather than documenting it.

## Formulas, never computed values

`ws["D10"] = "=SUM(D4:D9)"`, not the Python sum. A workbook of hardcoded numbers is a screenshot
with extra steps, and it goes stale the moment anyone edits an input.

Every driver lives in exactly one cell and every use of it is a reference: `=$B$17`, never
`=38400`. Absolute-reference the driver cells so the formula survives a copy across the grid.

### The timing is a driver too

An amount in a live cell is only half a model. The other half is *when*, and that is the half
that gets hardcoded, because it is easy to miss: the builder knows payroll is biweekly, works
out in Python which columns that hits, and writes `=$B$17` into those and a literal `0` into the
rest. The file passes every check. It ties out, it has no stale values, and the amounts are
genuinely live. It is still not a model, because nothing in the workbook knows *why* week three
got paid, so nothing can reconsider it.

So each line carries four editable cells, not one:

| Cell | Holds |
| --- | --- |
| `B` | the amount |
| `C` | how often: every week, every 2 weeks, monthly, one time |
| `D` | the date it starts, or the anchor a cadence counts from |
| `E` | the date it stops. Blank runs to the end of the horizon |

and every grid cell is one formula that reads all four against **the week's own date in the
header row**, which is itself a formula off a single start-date cell. Move that one cell and the
calendar moves, and every schedule re-anchors to it.

This is also what replaces a scenario switch. "What if collections slip 15%" is a smaller number,
"what if that receivable lands two weeks late" is a different date, and "what if we stop the
owner draw in March" is an end date. A switch adds a second way to do the same thing, and a
second thing to explain.

Cadence is a dropdown, because the grid formulas match on the exact strings and free text would
silently zero a row.

## Derive the schedule from dates, never hardcode columns

A model built for "week 3" is wrong the next time it is opened. Hold **dates** in config and
compute which column each event lands in:

```python
weeks = [anchor + timedelta(days=7*i) for i in range(n_weeks)]
def week_of(dt):                      # which column does this date fall in
    for i, w in enumerate(weeks):
        if w <= dt <= w + timedelta(days=6): return i
```

Then place each recurring item by its real cadence, not by counting columns:

- **Biweekly payroll**: walk back from any real payday to before the horizon, then step 14 days.
- **Monthly items**: the week containing the 1st, the 10th, or whichever day it actually lands.
- **Quarterly or one-off**: an explicit list of dates in config.
- **Weekly run-rate items**: every column.

The payoff: rerun it in six weeks and the model re-anchors itself correctly with no edits.

## Cash mechanics that answer the real question

A weekly grid is only useful if it tells the owner when cash gets tight and how much covers it.
Four rows do that, and there is no fifth:

```
Starting cash   first week = the input; after that = prior week's ending cash
Total money in  = sum of the inflow rows
Total money out = sum of the outflow rows
Net change      = total in − total out
Ending cash     = starting + net change
```

**Ending cash is allowed to go negative.** Do not add a funding row that tops it back up to the
floor. A funded grid hides the actual low point, and then needs three or four different funding
figures to describe the hole it just concealed. One unfunded line answers all of it:

```
=MIN(<ending cash over the horizon>)                    the worst it gets
=MAX(0, floor − MIN(<ending cash over the horizon>))    what it takes to hold the floor
```

The first is what happens with no help. The second is the ask. A business actively drawing on a
credit line in round wire increments needs more than this. Build it only when they ask.

## Make it readable without instructions

- **Amber fill plus blue font = a number you may change.** Charcoal on white = a formula, leave it
  alone. This is standard finance convention and accountants read it without being told. Use a
  soft amber rather than pure yellow, so the workbook and the HTML report look related.
- **Number format** `$#,##0;($#,##0);"-"`: negatives in parentheses, zeros as a dash. Dates
  `mmm d`.
- **Sentence case everywhere.** `Money in`, not `MONEY IN`. All-caps headers read as shouting and
  do not match the HTML artifacts.
- **Freeze panes** below the header and right of the label column, so labels stay put when
  scrolling a long horizon.
- **Conditional formatting for the exceptions only**: cash below the floor in pastel red, never
  an alarm red. Formatting that fires on every row signals nothing.
- **Turn gridlines off** (`ws.sheet_view.showGridLines = False`) and let the fills carry structure.
- **Hidden helper rows are fine** for lookups like "which week is the first one below the floor"
  (`=IF(ending<floor, week_number, 9999)` then `INDEX(…, MIN(…))`). Hide them; do not move the
  logic into Python, and do not make the client meet an array formula.
- **A totals column** at the right of every flow row, and it is `=SUM(...)`, not a value.

## The Assumptions tab

Every driver, its value as a formula pointing back at the Forecast tab, how often it lands, where
the number came from, and the cell address that controls it. This is where a reader decides
whether to trust the forecast, so the basis matters more than the number: from the books,
user-stated, a trailing average, or a judgement call.

Say plainly which lines are assumptions rather than booked activity. Forward revenue always is.

## Verify before delivering

openpyxl writes formula *strings*; it does not evaluate them. An unverified workbook can open full
of `#REF!`, or quietly showing 0 down a whole chain, and you would never know.

There are two different failures here and they need two different checks.

`verify_model.py` catches a workbook that is **broken**: errors and unresolved formulas.
`model_test.py` catches a workbook that is **inert**, which is the worse one because nothing
about the file looks wrong. It edits an input, recalculates, and asserts the numbers moved:
a new amount reaches every week it is paid, switching a cadence changes which weeks light up,
moving a one-off two weeks later moves it two columns, an end date stops a line, and shifting
the start date by one week flips a biweekly pattern. That last one is the test that matters,
because a grid keyed to column position passes every other check and fails that one.

Run both. A model nobody can change is a table.

Use `templates/verify_model.py` (`pip install formulas openpyxl`):

```
python3 templates/verify_model.py cash-forecast.xlsx \
  --report "Forecast!<lowest cash tile>" "Forecast!<shortfall tile>"
```

It checks two failures, and both matter:

1. **Error values**: `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, `#N/A`, `#NUM!`.
2. **Unevaluated formulas**: a cell holding a formula the engine refused to resolve. In practice
   this is a **circular reference**, and it is the dangerous one: the workbook opens looking fine
   while Excel shows 0 for the entire chain. A count above zero is a real defect, not a quirk of
   the checker.

Require zero on both. If the checker cannot run, say plainly that the formulas calculate on open,
rather than implying you checked.

Better still, recompute the cash walk independently in Python and compare it to the evaluated
workbook week by week. That is the only check that proves the formulas say what the config meant.

Two habits that avoid the common traps:

- **Prefer `INDEX` to `OFFSET`** for a lagged reference. `OFFSET` is volatile in Excel, harder to
  audit, and not checkable by the verifier.
- **Guard a boundary that reads a blank.** Wrap an actual-or-projection pick in `ISNUMBER`, so
  pointing at a week that has not closed yet falls back to the projection instead of reading blank
  as zero and collapsing everything downstream.

## Refresh discipline

- **Roll forward**: closed weeks refreshed from the books, the client's drivers untouched. Those
  are their judgements, not yours.
- **Rebuild**: a new dated file every run (`..._YYYY-MM-DD.xlsx`). Never overwrite the prior
  version; the old file is the record of what was believed when.
- **Report what moved**, not what the workbook contains. They want to know whether the low week or
  the shortfall changed since last time, and why.

## Google Sheets

Sheets is often the better answer when several people will touch the file, because commenting and
version history are built in and nobody emails a v7.

Build the `.xlsx` exactly as above and tell the user to import it: Google Drive → New → File
upload, then open and Save as Google Sheets. Everything here survives: formulas, number formats,
conditional formatting, freeze panes.

This survives because the builder deliberately stays inside a small function vocabulary that
behaves identically in both applications:

`IF` `AND` `OR` `NOT` `SUM` `MIN` `MAX` `ABS` `ROUND` `ROUNDUP` `ROUNDDOWN` `AVERAGE` `COUNTIF`
`SUMIF` `INDEX` `MATCH` `TEXT` `IFERROR` `ISNUMBER` `EOMONTH` `DATE` `YEAR` `MONTH`

Stay inside it. Anything openpyxl writes with an `_xlfn.` prefix is Excel-only and lands in Sheets
as `#NAME?`. Two lines of Python will tell you whether a build drifted:

```bash
python - <<'PY'
import openpyxl, re, collections
wb = openpyxl.load_workbook("cash-forecast.xlsx"); used = collections.Counter()
for ws in wb:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith("="):
                used.update(re.findall(r"([A-Z][A-Z0-9\.]*)\s*\(", c.value.upper()))
print(sorted(used))
PY
```

Charts are the weak point; openpyxl charts sometimes need rebuilding in Sheets. Prefer tiles whose
numbers stand on their own, so a lost chart costs nothing.

Say which format you built and why, and offer the other one rather than assuming.
