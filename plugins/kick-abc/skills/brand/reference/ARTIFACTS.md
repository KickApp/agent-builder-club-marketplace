# The deliverable

Every skill ends in a **file the client can open**, not a chat message. A chat message is what the
reader loses when they close the tab; the file is what gets forwarded to a spouse, a banker, or a
board. The analysis is the cheap part. Any model computes a current ratio. The artifact is what
nobody else hands them.

Two formats. Build the HTML always. Build the workbook whenever the deliverable contains a
projection, an annual plan, or a grid the reader will want to change.

## The HTML report

Never hand-write HTML and never restyle the template. Freehand markup is why AI reports look
different, and worse, every run. Write a **JSON payload**, build, then brand:

```
python3 reference/templates/build_report.py data.json out.html
python3 reference/templates/theme.py \
        reference/brand-config.md out.html
```

**Two passes, always in that order, never fused.** The first writes a complete but plain report.
The second applies the firm palette, embeds the typeface, adds the icons, and audits the copy. A
file handed over after only the first step is unbranded and looks it. There is deliberately no flag
that does both: the copy audit lives in the second pass, so fusing them meant one banned word threw
away a finished report and left nothing to inspect.

`build_report.py` validates the payload and refuses to write a broken file. It catches unknown
section types, `yoy` series that do not match the label count, a `matrix` row whose stated total
disagrees with its own cells, pre-formatted currency strings where raw numbers belong, and any syntax
error in the renderer. If it exits non-zero, fix the data. Do not edit the template to make the error
go away.

Pass **raw numbers**: `410220`, not `"$410,220"`. `0.262`, not `"26.2%"`. The renderer formats
everything, keeps currency exact to the dollar, and abbreviates only on chart axes.

### Payload shape

```
meta      entity, title, mark, period, source, closedThrough      always
headline  one or two sentences: the whole story                   see below (most skills omit it)
callout   the one thing to look at first                          see below (most skills omit it)
strip     a section rendered once above every tab                 rarely (repeats on every tab)
views     [{ name, sections }]: tabs. One view? Omit the name.    always
footnote  one line: sourcing, read-only, review gate              always
```

**Nothing narrative sits above the KPI tiles.** A reader opens a financial artifact to the
numbers, and two paragraphs in front of them is a toll. Worse, a sentence billed as *the one
thing* directly above a ranked list of five things argues with its own page. Where the artifact
carries a findings section (flux does), the story lives there, at the bottom, each sentence
beside its number and its rank. The dashboard carries no prose at all: its insights travel in
the chat message that delivers the file. `headline` and `callout` still render for the one
artifact that has a genuine single answer (a cash forecast's shortfall date), and each skill
says whether to use them. When in doubt, leave both out.

Sections carry `type`, an optional `title` and `note`, and `span:"half"` to sit two-up. Consecutive
halves pair automatically.

```
kpi       tiles. items[]: label, value, fmt, sub, delta{value},
          spark[]: 8 to 12 numbers drawing a trend line inside the tile. It
          needs 3+ points and silently omits itself below that. A tile with a
          sparkline says "and here is the shape behind it"; a tile without one
          is a number with no context. Four tiles or fewer render as the hero
          row: larger figures, more padding. Set compact:true on any strip
          below the page's first so only the top row is the hero. A page
          with four hero rows has no focal point. There is no
          highlight/selected variant. A tinted tile reads as an active
          filter, which it is not.
waterfall bridge. items[]: label, value, total, tone, color, evidence. A bar
          with total:true is an anchor drawn from zero; the rest float from the
          running balance. The bars therefore have to sum from one anchor to
          the other, which makes the chart its own tie-out proof: a bridge
          that does not close is visibly missing a driver. Negative bars take
          pastel red unless tone:"plain". Use that on a favorable fall, such
          as spend coming down. evidence (bars only, never anchors) opens a
          click drawer: see Evidence drawers below. Aliased as `bridge`.
yoy       this year vs last, with a live cumulative/monthly toggle.
          labels[12], current{name,values}, prior{name,values}. Trailing nulls
          on current for months that have not closed. The line stops there.
hbars     horizontal bars, ranked. items[]: label, value. Goes diverging by itself
          when any value is negative: zero line, loss-makers left in pastel red.
donut     mix. items[]: label, value. Negative items are dropped (a share of a
          mix cannot be negative), so put profit in hbars, never here.
share     table with a color dot and a share-of-total bar. items[]: label, value
pnl       statement rows: label, value, indent, total, sub, tone
matrix    members down, periods across. columns[], rows[]{label,values[],total,tone,
          evidence[]}, rowHeader, totalHeader, totalLabel, share:false, tone
          (section-wide). values[] must match columns[]; use null for a genuine
          gap; a true zero renders blank. Dollar cells must be whole dollars and
          a supplied row total must equal its own cells. The build fails
          otherwise, because a grid that is a dollar off its own total is the
          first thing a reviewer who cross-foots a column will find. Round every
          cell first, then build totals from the rounded cells. evidence[] is
          parallel to values[], null where a cell has none: see Evidence
          drawers below.
findings  ranked list: title, value, body
table     generic: columns[], rows[], sort, measures, search. search:true adds a
          filter box above the table that narrows member rows by label as you
          type, for the reader who arrives with an account in mind, once a
          statement runs long. Totals and everything below them stay put.
text      prose
```

`fmt` is `currency | percent | number | x | text`. Colors are assigned from the palette by
position. Only set `color` when a segment must keep a color across reports. `color` takes a
palette token name (`negbar`, `cmut`, `accent`, `prior`, `posbar`) or a literal hex; prefer the
token, which resolves through whatever brand the theme pass applies, so a semantic color (the
over-90 aging bucket in pastel red, a catch-all row in grey) never drifts from the firm's
palette.

### Statement presentation

The conventions a finance reader checks first, the same ones the bulge-bracket training firms
(Training The Street among them) drill, applied wherever they translate to a read-only page:

- **Negative currency renders in parentheses, everywhere.** The template does this on its own:
  `($16,819)`, never `-$16,819`. The parentheses carry the sign, so color is free to carry
  sentiment.
- **Sign and sentiment are separate channels.** Pastel red marks a genuinely adverse figure, not
  a minus sign. A negative `table` or `matrix` cell colors itself pastel red by default, which is
  right for a loss and wrong for a fall in spend. Set `tone:"plain"` on the cell (tables) or the
  row (matrix) whose negative is good news, and `tone:"neg"` on an adverse positive such as a
  rise in days to collect.
- **Totals look like totals.** The built-in total rows render bold with a rule above. Use them
  (`total:true` on a table row, the matrix's own foot) rather than hand-building a "Total" row
  that arrives unstyled.
- **One number format per schedule.** Every cell in a column carries the same `fmt`, decimals
  align on tabular figures, and a true zero renders blank rather than as a column of `$0`.
- **Declare units once.** The card note carries the unit when it is not plain dollars
  ("$ thousands", "days") instead of repeating it in every cell.

### Several entities in one report

A group engagement is one report over several sets of books, and the reader's first question is
which one they are looking at. Declare them in `meta.entities` and the header grows a filter; with
one entity or none, nothing is rendered, so a single-company report never carries a control with
one option in it.

```json
"meta": { "entities": [ { "name": "Rella Solutions", "code": "R" }, { "name": "CHRY" } ] }
```

Then tag the sections that belong to one entity:

```json
{ "type": "matrix", "title": "Revenue by month", "entities": ["Rella Solutions"], "...": "..." }
```

**A section with no `entities` is always shown.** That is the consolidated view, and it is correct
that it survives every selection: a consolidated total is not a member of the set it consolidates,
so hiding it when one entity is deselected would be wrong.

The filter shows and hides whole sections. It does not re-add anything, because a report that
recomputed its own totals in the browser would be claiming a tie-out it cannot prove. If a reader
needs revenue for one entity, that is a section built for one entity.

### `stack`: what made up each period

Stacked columns across periods, money in above the zero line and money out below it. This is the
one chart that answers *what made up this month* and *how do the months compare* at the same time,
which is why it earns the top of a cash view where a plain total-by-month line would not.

```json
{ "type": "stack", "title": "Cash in and cash out by month", "fmt": "currency",
  "columns": ["Jan", "Feb", "Mar"],
  "series": [ { "label": "Income", "values": [5977, 3774, 2775] },
              { "label": "Payroll", "values": [-10789, 0, -204] } ] }
```

**A series never changes sign.** One band is an inflow or it is an outflow, for every period. A
series that goes positive in March and negative in April stacks upward in one column and downward
in the next, so the same colour means income on the left and spend on the right. Split it into two
series. The builder warns when it sees this.

**Seven bands is the ceiling and five is better.** Past that a column is a stack of slivers. Group
the tail into `Other`, which `colorOf` renders in grey.

Bands are separated by a 2px gap that shows the card through, taken off the band rather than added
to it, so the stack still measures its total. Hovering a band gives the series, the period, the
figure, and the column's net.

### `matrix` groups and subtotals

A grid of members by period is a list. A grid with group headers and subtotals is a statement, and
the difference is whether a reader can find *cash in* without adding rows up in their head.

```json
"rows": [ { "group": "Cash in" },
          { "label": "Income", "values": [5977, 3774] },
          { "label": "Total cash in", "values": [5977, 3774], "subtotal": true },
          { "group": "Cash out" },
          { "label": "Payroll", "values": [-10789, 0] },
          { "label": "Total cash out", "values": [-10789, 0], "subtotal": true } ]
```

A `group` row is a divider: no label, no values. A `subtotal` row is arithmetic on the rows above
it, so it gets a rule, no colour dot, and is excluded from the column totals and the colour wash.
Set `"footTotal": false` when the groups already carry their own totals and a grand total at the
bottom would be a third kind of total on one grid.

Use both together or neither. Group headers without subtotals give the reader blocks with no block
figures, which is the worse half.

`"measures": true` marks a table whose rows are **named measures** rather than data points:
current ratio, days to collect, debt cover, gross margin. The brand pass puts one glyph per row in
the first cell, so a reader hunting for a row finds it by shape instead of reading every label.
The glyph goes inside the existing cell, so the row still has one cell per column and sorting is
unaffected. Total rows are skipped, since a total is arithmetic rather than a measure.

Use it on a liquidity block, a ratio summary, a KPI-style list. Never on a grid of numbers: a P&L,
a variance detail table, a week-by-week forecast. At that density a glyph on every row stops being
an identifier and becomes texture, which is the whole reason icons are off by default.

**A measures table carries a change column.** Two periods side by side with no change column
leaves the reader doing subtraction, and the gap invariably gets filled with a sentence of prose
per row narrating the movement. That is how a scannable card turns into a wall of text.

`"sort": true` makes every column header of a `table` sort on click, and it is off by default on
purpose: a P&L, a liquidity block, and a week-by-week grid each carry an order that means something,
and sorting one by value destroys the reading. Switch it on for a ranked or long list where the
reader has a question the default order does not answer: variance detail, a vendor list, a
per-member table. Sorting reads the underlying number rather than the formatted string, so currency
and percent columns sort correctly. Numeric columns open descending, `total` rows stay pinned at the
bottom, blank and `n/m` cells sink in both directions instead of sorting as zero, and equal values
hold their payload order. Still sort the payload itself into the order you want read first; sorting
is for the reader's second question, not a substitute for ranking. Every row needs a cell for every
column when sorting is on (use `null` for a gap), and the build rejects the payload otherwise.

`span:"half"` leaves an `hbars` label column about 108px wide. Long member names (full product names,
"Riverside Business Park") need the full-width chart, and so does anything past about six rows. Two
stacked full-width bar charts read better than two cramped halves.

The template also carries a `budgets` renderer. **No skill in this plugin uses it and none should**:
budget-versus-actual is deliberately out of scope here and belongs to a separate skill. It is left in
place so that skill does not have to rebuild it.

**Two skills draw a bridge, and each draws a different one.** Keep them apart or the plugin repeats
itself:

| Skill | Bridge | Anchors |
| --- | --- | --- |
| `flux` | The period change, exhaustively, every material line | Prior figure → current |
| `cashflow` | The cash walk | Starting cash → ending cash |

The management report draws none: statements carry it as statements. The dashboard points at flux
when a reader wants a mover decomposed rather than drawing a third bridge of its own.

`strip` holds a section (in practice a `kpi`) that renders once above the tab bar and stays put as
the reader switches tabs. Headline numbers belong to the whole report, so repeating them inside each
tab is the same page shown twice. A tile value never wraps: an eight-figure number steps its type
down until it fits rather than breaking across two lines, so you can put a real total in a tile
without checking how wide it renders.

`matrix` is the dimensional workhorse: it answers "which member is growing" in one look, which no
ranked bar chart can do. Cell shading scales with magnitude as quiet emphasis, never as a
red-versus-green score, and it is deliberately capped low so no single big cell reads as selected.
Negatives take pastel red only where negative genuinely means adverse (a loss-making member),
and `tone:"plain"` on a row (or the whole section) keeps a variance grid in charcoal, where a
negative can as easily be spend coming down. Keep it to 14 rows or fewer and collapse the tail
into `Other (n members)`; the build warns past that. See `DIMENSIONS.md` for what belongs in one
and for the integrity rules that make it trustworthy.

Omit a section rather than filling it with a placeholder.

### The design system is the contract, not a suggestion

The look is the product. Do not introduce new colors, fonts, weights, or components.

- **Off-white page, white cards, soft 1px borders, 12px radius.** Airy, not dense.
- **Charcoal text (`#2f2f36`), never pure black.** Black is too harsh at this weight.
- **System sans at 14px, weights 400 and 500 only.** No heavy or display faces anywhere.
- **Pastel categorical palette** for segments. **Pastel red only for genuinely adverse things**:
  a loss, an overrun, a negative delta. An ordinary expense line is not adverse: costs render in
  parentheses in charcoal, the way a statement reads. Never red/green scoring, never an alarm red.
- **Lavender tint** marks the one thing that matters: the callout where a report carries one,
  the protected-margin row. Never on a KPI tile. A tinted tile beside plain ones reads as an
  active selection, and the reader goes looking for what filtered the page.
- **No logo banners, no "note" callout boxes, one-line confidential footer.**
- **No dead controls.** Every pill, tab, and toggle on the page does something. A period dropdown
  that cannot change the period is worse than no dropdown.

### The aha sentence is not optional: its position at the top is

Every report still needs the one sentence a non-finance owner reads once and remembers, carrying a
dollar figure or a date: *"Your third-largest location has lost money for six months running,
$31,400 in total."* Not *"location performance presents an opportunity."* If you cannot write that
sentence from what you pulled, you have not finished the analysis. Go back to the numbers rather
than shipping a vague one.

Where it lives depends on the artifact: first item of the ranked findings where the page carries
them (flux), first line of the chat message where it doesn't (the dashboard). It is never a
callout floating above the KPI tiles. A sentence there is a claim the reader has to hold on
faith until they scroll. Use the `callout` block only in the one artifact whose whole answer is a
single figure, such as a cash forecast's shortfall date.

### Hover

Every chart carries a tooltip on hover, built by the template rather than declared in the payload,
so nothing is needed to switch it on. It exists because a chart has to round: an axis reads `$1400k`,
a bar gutter truncates a long name, and a mix chart shows an angle rather than a percentage. The
tooltip is where the exact figure and the full name live, which is what lets the chart stay clean
without losing the number underneath it.

What each one says: a ranked bar gives the label, the exact value, and its share of the total, where
the values all point the same way. A share row and a donut slice give the value and the percentage. A
bridge bar gives the change and the running total it carries the reader to. A matrix cell names its
row and column. A line chart has a hit band per period, so the whole column is hoverable rather than
the two-pixel stroke, and hovering shows every series at that period against a vertical guide.

Two consequences worth knowing. Hovering a ranked bar anywhere on its row works, including over a
truncated label, which is the cheapest fix for a name too long for the gutter. And a tooltip is not
a place to put something the reader needs: it never appears in print, on a touch screen, or for
anyone navigating by keyboard. Anything that must be read belongs on the page.

### Evidence drawers

A finding that reads "Salaries and wages, up $19,455, per payroll activity" asks the reader to
trust the sentence or open the ledger separately. Evidence closes that gap: attach it to a bridge
bar or a matrix cell and a click opens a drawer beneath it with the transactions behind that
number: date, name, memo, amount. The cell announces it with a dotted underline and its tooltip
says the drawer exists.

```
evidence  { txns: [{date, name, amount, memo}], more, moreValue }
```

The rules, each enforced by the build:

- **Embedded at generation time.** The transactions ride in the payload, so the file still opens
  with no network and still prints. An open drawer is just a table. There is no lazy fetch, which
  is why the cap is decided before anything is written.
- **Capped.** Whichever is smaller: the top 20 transactions by absolute amount, or the set that
  covers 90% of the number. The remainder is declared, never dropped: `more` carries the count
  and `moreValue` what it adds up to, and the drawer prints "N more in the ledger" with the figure.
- **Re-sums or it fails.** Shown transactions plus `moreValue` must equal the number the drawer
  sits under, to the dollar. A drawer that contradicts its own cell is worse than no drawer.
- **Scoped to lines that earned a finding.** Evidence on every cell bloats the file for detail
  nobody asked about. Attach it to the material, flagged lines and their dimensional cuts.
- **Never on a bridge anchor.** An anchor is a level, not a movement. There is no transaction
  set "behind" it.
- **The drawer must match the cut it sits under.** Evidence on the "Schultz Report" column holds
  only that member's transactions. A drawer showing a different slice than its own cell is a
  correctness bug, not a style one.

Transaction `name` is the party on the ledger line: a vendor on spend, a customer on revenue.

### Cross-highlighting

Hover a matrix row, a bridge bar, or a table row and every other exhibit showing the same label
lights up. The template keys them by normalized label automatically, no payload field involved.
It only fires when a label appears more than once on the page, so single-exhibit reports never
show it. This is what connects the three views of the same account in a flux report without the
reader scanning by eye. Keep labels consistent across sections to keep it working: "Salaries and
wages" on the bridge and "Salaries & wages" in the table never link.

### Shipping it

Name the file `{entity}-{skill}-{period}.html`. Tell the user the path, that it opens in any browser
with no internet, and that Cmd/Ctrl-P prints a clean PDF. Charts are inline SVG so they stay sharp
in print; multi-view reports print every tab, one per page.

`reference/templates/sample-data.json` is a complete worked payload: the one-page dashboard,
covering `kpi` at hero and compact sizes, `yoy`, `stack`, `table`, `donut`, and `hbars`. Read it
before writing your first one. `trend`, `waterfall`, and `findings` follow the same schema
(section shapes below); `text` is a title and a paragraph and needs no example.

## The Excel or Google Sheets workbook

Ship a workbook, not a report, when the reader's next move is to change an assumption and watch the
answer move: a projection, a driver model, a weekly cash grid, an annual plan the client maintains. A
static table cannot do that.

**`MODELS.md` is the full craft guide, and it is required reading before building one.** It covers
the two-tab architecture, date-derived schedules, cash mechanics, input conventions, verification,
refresh discipline, and the Google Sheets path. The short version:

- **Formulas, never computed values.** `sheet["B10"] = "=SUM(B2:B9)"`, not the Python sum. A
  workbook of hardcoded numbers is a screenshot with extra steps.
- **One direction of flow.** Inputs and an Actuals spine feed everything; nothing feeds back. This
  is what makes a monthly refresh safe.
- **Yellow fill plus blue font means an input you may change**; black on white means a formula.
  Standard finance convention, and accountants read it without being told.
- **Verify before delivering** with `templates/verify_model.py`. It catches error values *and*
  unevaluated formulas, which are usually a circular reference and show as 0 in Excel. Run it on
  every scenario.

Two verified builders to adapt rather than starting from a blank workbook:

| Template | What it builds |
| --- | --- |
| `templates/build_cash_model.py` | Weekly cash forecast. Two tabs, Forecast and Assumptions. Date-derived grid, every driver an editable cell in column B, no scenario switch and no funding row. Ending cash is allowed to go negative, because the dip is the finding. |

## What ships in chat

The chat message is a pointer to the artifact, not a copy of it. Give the one-sentence story, the
top finding, the file paths, and anything you need the user to confirm or supply. Never paste the
full report into chat. A reader who has it twice reads it zero times.
