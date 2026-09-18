---
name: brand
description: Applies the firm's visual identity and copy standards to a finished deliverable. Themes HTML reports, applies input conventions and number formats to Excel and Google Sheets workbooks, and enforces copy standards on anything with words in it. Runs last, as a pass over completed artifacts. Use when the user asks to brand, restyle, re-skin, theme, or clean up a report or workbook, when they change their palette or firm details, or automatically as the final step of an advisory or close run. Never computes, recomputes, or changes a number.
---

# Brand

This file is the whole appearance layer. The config, the rules, and the script that applies them
all live here, so a firm has exactly one thing to edit and one thing to hand to someone else.

Skills compute. Brand decides how it looks. Those two jobs never mix, which is why a calculation
skill can be shared without shipping the sharer's colors with it, and why asking for a current
ratio should carry no aesthetic instruction at all.

**The rule that outranks everything below: never change a number.** Not a rounding, not a sign, not
a total. If a figure looks wrong, say so in chat and leave it alone. A brand pass that silently
edits data destroys the audit trail the close depends on.

## Config

The only part a firm changes. Everything after it is the house standard and does not vary.

```json
{
  "firm": {
    "name": "Kick",
    "mark": null,
    "markColor": "#3793da",
    "footer": "Prepared from the client ledger. Read only. Review before distribution."
  },
  "palette": {
    "bg":       "#fafbfc",
    "card":     "#ffffff",
    "line":     "rgba(83,100,126,0.13)",
    "line2":    "rgba(83,100,126,0.06)",
    "ink":      "#0f1826",
    "ink2":     "#515d71",
    "mut":      "#949ba7",
    "mut2":     "#b7bcc5",
    "tint":     "#f2faff",
    "tintline": "#cae6fc",
    "accent":   "#3793da",
    "prior":    "#94c9f1",
    "neg":      "#d4343c",
    "lossInk":  "#9f4237",
    "posbar":   "#a8deff",
    "negbar":   "#faa4ab",
    "negbg":    "#fff5f6",
    "cmut":     "#d9dde2",
    "cats": ["#a8deff", "#d9c1e3", "#c4f2b2", "#b5ecf2", "#f9e3ae", "#bcb9f4", "#b8efd0"]
  },
  "type": {
    "embed": true,
    "stack": "Inter, -apple-system, BlinkMacSystemFont, \"SF Pro Text\", \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif"
  },
  "radius": 12,
  "shadow": "0 15px 30px rgba(83,100,126,0.06)",
  "icons": true
}
```

Every value above is a Kick design token, not an approximation of one, compiled from the Kick
app's own design tokens, so a report and the product it came from are the same blue. If those
tokens move, this block moves with them.

| Config | Kick token | Why it is the one that matters |
| --- | --- | --- |
| `accent` `#3793da` | `$primary`, blue 500 | The product's primary. It carries the brand across every chart |
| `markColor` `#3793da` | `$primary` | The header square, the first branded thing a reader sees |
| `ink` `#0f1826` | gray 900 | Kick's near-black. Pure black is harsher than the product |
| `line` | alpha 200, slate at 13% | Kick borders are slate at low alpha, never a flat grey |
| `shadow` | the `shadow` mixin | One soft lift under cards. The product has it and a flat report does not read like it |
| `cats` | seven pastels, one lightness | Data is quiet so the shape carries. Saturation is reserved for the accent |

`mark` renders as a rounded square of one or two characters, the way an entity badge does in the
Kick app. Left null it shows the client entity's initials, which is what the header is about. Set
it to stamp the firm's own mark on every report instead. A firm with a real logo file still uses
initials, because the report opens with no network and an embedded raster logo prints badly.

`markColor` is that square's fill, so it is where a firm's one brand color lands even when the
rest of the palette is left alone.

`cats` is the categorical ramp, assigned by position. The first four entries are sampled from the
Kick product's own charts. Four rules hold it together and `brand_verify.js` enforces all four:
one lightness across the ramp, chroma under 0.42 rather than a saturation cap, nothing in the red
range `negbar` owns, and at least 25 degrees of hue between neighbours.

Read `reference/PALETTE.md` before changing any of it. Every rule there has a
failure behind it, and the ones that sound like taste are the load-bearing ones.

To carry a second look, add another fenced json block below, preceded by a line reading `preset:`
and the name. The first block wins unless a preset is named.

## The standard

An artifact should be indistinguishable from something a CFO's office produced on purpose, and
it should survive being screenshotted in front of strangers. A reader who sees a clipped label
or a default font concludes nobody checked the arithmetic either.

## Surfaces

Off-white page, white cards, one hairline border, 12px radius, one soft shadow. Airy rather than
dense. A financial report earns trust by looking unhurried, and packing rows to the edge reads as a
data dump.

- Page `bg`, cards `card`, borders `line` at 1px, which is slate at low alpha rather than a flat
  grey. Grey borders are the single most generic thing on a page.
- **One shadow, the config `shadow`, on cards and tiles.** It is Kick's own, a wide soft lift at 6%
  rather than a drop shadow, and it is most of the difference between a page that looks composed
  and a page that looks like a table dump. Never a second shadow, never a gradient, never a nested
  card. Print drops it, where it costs toner and buys nothing.
- 12px radius on cards and tiles. Full pill on segmented controls and toggles only.
- Charts are inline SVG. Never canvas, because canvas prints fuzzy or blank, and the reader's next
  move after opening the file is often Cmd-P.

### Hover and controls

Every chart shape is hoverable, and the tooltip is a light card rather than a dark chip: a black
tooltip on a pale page is the one element that looks borrowed from another product. Controls are
pills in `card` with a 1px `line` border, right-aligned above the content.

**A control with one option is not a control.** One entity, no entity filter.

See `reference/SURFACES.md` for the tooltip's four parts and the entity chips.

## Nothing escapes its container

Clipped text is the most visible defect a report can have. Cap the strings when writing the
payload. These are limits, not suggestions.

| Field | Limit | Past the limit |
| --- | --- | --- |
| Section `note` | about 90 characters, one line | move it to a `text` section under the chart |
| Section `title` | about 40 characters | shorten it, the note carries the detail |
| `hbars` and `matrix` member labels | about 28 characters | shorten in the payload, full name in the note |
| KPI `label` | about 22 characters | shorten it |
| KPI `sub` | about 34 characters | shorten it |

A note explaining coverage, methodology, or an exclusion runs two sentences, which does not belong
in a header slot beside a title. Put it in a `text` section. The header note is for a short
qualifier such as "top 2 = 85.9% of revenue", nothing more.

**A long member name is a signal, not just a layout problem.** A label reading "Unassigned
(Lackawanna services contract)" is telling you something real about the data. Shorten it to
"Unassigned" and explain what it is in the note or a finding, where there is room to say it
properly.

The theme pass adds defensive containment (headers wrap, overlong chart labels truncate with
the full string on hover), but that is a backstop, not permission: a truncated label is a worse
label, and a printed page never shows the hover.

**Annotations live inside the SVG, next to what they annotate.** Axis labels in the plot, bar
values on or beside their bars, a sparkline's range labeled at its endpoints. An annotation
rendered as prose above or below the chart separates the number from its mark and dies in print.

## Type

**Inter at 14px, embedded in the file.** Kick is set in Inter, and linking a web font would
break the offline rule, so the brand pass embeds a Latin subset (about 25 KB, base64, one
`@font-face`). The stack keeps a fallback behind it, so a stripped font block degrades to the
system face instead of to Times.

```
Inter, -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif
```

Set `"type": {"embed": false}` to drop the embedded face and take the fallback. The only reason to
is a hard file-size limit.

Base tracking `-0.005em`, Kick's own, which is what stops 14px Inter reading loose.

Three weights and no more. 400 body, 500 labels and section titles, 600 on the two things a reader
looks at first: the report title and the headline numbers in the KPI tiles. Numbers always carry
`font-variant-numeric: tabular-nums`, so columns of figures line up on the decimal instead of
jittering.

Sentence case everywhere. Not Title Case, not caps. "Revenue by show", not "Revenue By Show".

## What color means

Color carries meaning in a financial document or it should not be there. Every hue has one job,
and using it for anything else costs the reader the ability to trust any of them.

| Token | Means | Never used for |
| --- | --- | --- |
| `accent` | the brand, the primary series, the largest ranked member | a positive result |
| `tint` | the one thing to look at first: the callout, where a report carries one | general emphasis, or any KPI tile, since a tinted tile reads as an active selection |
| `neg` family | genuinely adverse: a loss, an overrun, a covenant breach | any negative number |
| `lossInk` | an adverse figure rendered as text, dark enough to read at 4.5:1 | fills, bars, tints |
| `posbar` | a favorable bar on a bridge, paired with `negbar` | emphasis, or a categorical series |
| `cats` | categorical members, assigned by position | ranking or scoring |
| `cmut` grey | unclassified, unassigned, other | a real member |

`posbar` and `negbar` are a matched pair and must stay one: same lightness on both sides, so
the palette never argues for a conclusion. The sign carries the meaning.

Rules that get broken constantly.

**No red versus green scoring.** Ever. It is the fastest way to look like a spreadsheet someone
conditional-formatted in a hurry, and color-blind readers lose the signal entirely. Adverse things
get pastel red. Good things get no color at all.

**A negative number is not automatically bad.** Costs render in parentheses in charcoal, the way a
statement reads. A fall in spend is a negative number and good news. Set the plain tone on any cell
whose negative is favorable, whether a `table` cell or a `matrix` row.

**Fills and text are different reds.** The `neg` family colors fills: bars, cell tints, chart
marks. An adverse figure rendered as text takes `lossInk`, which reads at 4.5:1 on every
background in the palette. A pastel used as text ink fails contrast, and the runner that meets
that conflict will invent its own red rather than ship an unreadable figure.

**Color lands on signed numerals, never on worded deltas.** `($13,500)` may carry the tone;
"Up $5,425" and "down 18%" render in body ink. The word already carries the direction, and a
colored word reads as alarm.

**This pass owns chart hues.** An incoming artifact carrying its own chart colors gets restyled
to this palette during the pass. The content layer never picks chart colors; two ramps in one
report is a defect, not a blend.

## Statement presentation

The formatting canon the bulge-bracket training firms teach (Training The Street is the one
accountants cite) exists because a finance reader judges the numbers by the formatting before
reading them. The workbook half, input provenance colors, lives under Workbooks. What carries to
a read-only page: negatives in parentheses, never a minus sign; sums bold with a rule above, from
the built-in total rows; grids that cross-foot to the dollar because cells were rounded before
totals were built; one number format per schedule; units declared once in the card note; a true
zero rendered blank, not a column of `$0`. The template and build enforce most of it; the full
list with payload mechanics is in `reference/ARTIFACTS.md` under Statement presentation.

## Icons

Icons are identifiers, not decoration. One glyph per row in a dense list so the eye can find the
row again. That is the behaviour worth having. The failure mode is a cheerful glyph beside "Net
income", which turns a financial statement into a pitch deck.

Inline SVG paths embedded in the file. Lucide geometry, 24x24, 1.7 stroke, round caps and joins. No
icon font, no sprite URL, no network.

Five placements. Nowhere else.

| Placement | Rule |
| --- | --- |
| KPI tiles | one glyph per metric, in `mut`, every tile treated the same |
| Findings rows | one rank glyph per row, in `mut` |
| Measure tables | one glyph per row, in `mut2`, on a table with `"measures": true` only |
| Entity mark | the rounded square of initials in the header |
| Callout | one glyph, the aha marker, in `accent` |

The line runs between a table of **named measures** (a liquidity block: nine distinct concepts,
where a glyph lets the eye find *days to collect*) and a table of **numbers** (a variance grid:
one measure repeated, where a glyph per row is texture). That is why it is opt-in per table and
never on for a P&L.

None in chart legends, section headers, or tabs, ever. Set `"icons": false` to drop all of them.
The layout holds without.

## Copy

The words are part of the look. A well-set report with machine-written prose still reads as
machine-written.

- **No em dashes and no en dashes in any deliverable.** Use a period, a comma, or rewrite. Never a
  spaced hyphen, which is the same tell wearing a hat. A hyphen inside a compound word is fine.
  This is the most recognizable signal that a model wrote the text.
- **No semicolons.** Two sentences.
- **No emoji.** Not in headings, findings, or status markers.
- **Vendors and customers, never counterparties.** `counterparty` is the system's word for the
  field, and a reader who sees it knows a database wrote the page. *Supplier*, *payee*, and
  *payor* are out for the same reason: one word per side, used everywhere.
- **The plain word, every time there is one.** The reader is the owner of the business, not an
  analyst. *Profit* not *contribution*, *top customers* not *concentration*, *cash tied up* not
  *cash cycle*, *cash available* not *liquidity*, *minimum balance* not *floor*, *profit per unit*
  not *unit economics*. Define the measure once in the note under the chart, then use the plain
  word everywhere. This is a labeling rule and never a measurement one: renaming contribution to
  profit on the face of a chart does not license computing it differently or dropping the
  unallocated row.
- **A label, its value, and its subtitle must agree.** A tile reading *Cash cushion*, `0.85x`,
  "months of spend covered" makes the reader work out which of the three is lying. Months are a
  number of months, multiples get `x`, percentages get `%`.
- **A title names its subject. No pronoun standing in for it.** *What moved net income*, never
  *What moved it*; a title is read first, so there is nothing for *it* to point back to. The
  same goes for *Why it happened* and *How we did*. Name the measure.
- **A title uses the same word as the thing under it.** A bridge anchored on `Q1 net income` under
  a tile labeled *Net income* is titled *What moved net income*, not *What moved profit*. Two words
  for one number reads as two numbers. Where the plain word and the anchor word differ, change the
  anchor and the title together, never just one.
- **Sentence case** in every heading, label, axis, and tab name.
- **Currency exact to the dollar** in tables and tiles. Abbreviate on chart axes only, where the
  label has no room. `$602,986` in a tile, `$600k` on an axis.
- **Percentages to one decimal.** Multiples to one decimal with a lowercase x, as in `1.4x`.

### The delta suppression rule

A percentage change means something only when both periods are comparable. Print one that is not,
and the report announces that nobody looked at it.

Suppress the percentage and print the absolute change plus the reason when any of these hold.

- The magnitude exceeds 300%
- The prior period is incomplete, partial, or a stub
- The prior period is zero, near zero, or negative, which makes the sign meaningless

Correct: `+$540,700 vs last year (2025 partial, no comparable period)`
Wrong: `▲ 4057.7% vs last year`

The same rule governs any ratio on a small or absent denominator. If the honest answer is that
there is no comparison, say that instead of computing one.

### The aha sentence

One sentence a non-finance owner reads once and remembers, carrying a dollar figure or a date.

Good: "Your third-largest location has lost money for six months running, $31,400 in total."
Useless: "Location performance presents an opportunity."

If that sentence cannot be written from what was pulled, the analysis is not finished. Go back to
the numbers rather than shipping a vague one. It lives as the first item of the ranked findings
where the artifact carries them, or as the first line of the chat message where it doesn't. The
dashboard carries no prose on the page. Never a paragraph floating above the KPI tiles. The one
exception is the `callout` block in an artifact whose entire answer is a single figure, such as a
cash forecast's shortfall date.

## Workbooks

Excel and Google Sheets follow the standard finance input convention, which exists so a reviewer
can tell at a glance which numbers a human typed and which the model computed. It is functional,
not decorative, and it is the one place the banker convention genuinely belongs.

| Format | Means |
| --- | --- |
| Blue font, yellow fill | a hardcoded input the reader may change |
| Black font, white fill | a formula |
| Green font | a link to another worksheet in the same workbook |

Training The Street adds red for a link to another file. Skip it. Cross-file links break the moment
a client moves the workbook, so a model that ships with them is a support ticket. If a cross-file
reference is unavoidable, hardcode the value and label it an input.

Number formats: `#,##0` for currency with no cents unless the account carries them, `(1,234)` in
parentheses for negatives, `0.0%` for percentages, `0.0"x"` for multiples. Tab names in sentence
case, no numeric prefixes.

Two construction rules matter enough to repeat here.

- **Formulas, never computed values.** A workbook of hardcoded numbers is a screenshot with extra
  steps.
- **One direction of flow.** Inputs and an actuals spine feed everything. Nothing feeds back. That
  is what makes a monthly refresh safe.

## Close deliverables

Close memos, findings registers, proposed entries, and workpapers take the copy rules in full, and
the workbook conventions wherever they are grids. Two additions.

**A statement is a statement, not a trial balance.** Anything headed "balance sheet" or "P&L"
carries the chart of accounts hierarchy with subtotals, in statement order. A flat account listing
under a statement heading is the fastest way for a close package to look unfinished, and it is what
a partner notices first. Derive the hierarchy from the GL when the ledger connection cannot supply
it.

**One entity per file, and name it.** A consolidation is a deliberate artifact with its own
heading, never the accidental result of mixing entities in one grid.

## Delivery

Name the file `{entity}-{skill}-{period}.{ext}`, lowercase, hyphens, no spaces.

Tell the reader the path, that the HTML opens in any browser with no internet, and that Cmd-P or
Ctrl-P prints a clean PDF. Multi-view reports print every tab, one per page.

The chat message is a pointer to the artifact, never a copy of it. Give the one-sentence story,
the top finding, the paths, and anything needing confirmation. A reader who receives the report
twice reads it zero times.

One-line footer in `mut` carrying the config `footer` string. No logo banners. No note boxes.

No preparer attribution anywhere: never invent or state a preparer name unless the inputs carry
one. No "Prepared {date}" line either; the period in the heading dates the report, and the
footer already says where it came from.

## What never changes

These hold regardless of the config, because breaking them breaks the artifact rather than
restyling it.

- **No network.** No CDN, no web font, no remote image, no analytics. The file works on a plane.
- **No dead controls.** Every pill, tab, and toggle does something. A period selector that cannot
  change the period is worse than no selector.
- **No new components.** Restyle what exists. A one-off card invented for a single report is how
  six skills drift into six different products.
- **Omit rather than pad.** A section with no real content is left out, not filled with a
  placeholder.
- **Raw numbers into the renderer.** `410220`, not `"$410,220"`. `0.262`, not `"26.2%"`. Formatting
  is the template's job, and pre-formatted strings defeat every locale and every chart axis.

---

# Applying it

## HTML reports

Do not hand-edit the HTML and do not restyle the template. Freehand markup is exactly why AI
reports look different, and worse, on every run.

`theme.py` ships with the plugin. Point it at this file and the report. It reads the config above
out of this very file, so the config and the code that applies it stay together.

```
python3 reference/templates/theme.py \
        SKILL.md report.html
```

It injects a `<style id="brand-theme">` override and a `<script id="brand-icons">` DOM pass, both
replaced rather than appended, so running it repeatedly is safe. It overrides the base `:root` by
cascade order and enhances the DOM after the template has drawn, so it never touches the renderer,
the payload, or a number.

### Generate first, brand second. Always two steps.

```
python3 reference/templates/build_report.py data.json out.html
python3 reference/templates/theme.py \
        SKILL.md out.html
```

There is deliberately no flag that does both. Building more than one file? Generate them all,
then pass the whole set to one `theme.py` call, which is what makes them come out identical.

After branding, confirm the following.

1. The file still opens with no network. Grep for `http://`, `https://`, and `@import`. Any hit is
   a defect, not a preference.
2. Every control still works. Click each tab and toggle. A theme pass that breaks the cumulative
   switch has made the report worse.
3. Icons rendered. If `icons` is true and the KPI tiles have no glyphs, the script did not inject.
   Fix that rather than shipping a half-branded page.
3. The brand actually landed. The header mark is Kick blue, the text is Inter rather than the
   system face, and the cards carry the soft lift. If the page looks the same after the pass as
   before it, the pass did not run.
4. The copy audit came back empty. The theme pass prints any em dash, en dash, semicolon, emoji, or
   ledger word such as *counterparty* or *supplier* it finds in the payload. *Counterparty*, *payee*,
   and *payor* stop the run outright, since they cannot be part of a company name and so are always
   prose. Everything else reports and leaves the call to you. It reports rather than rewrites,
   because deciding where a sentence ends is writing. Fix each one in the payload and rebuild.
5. Nothing overflows. Open every tab at a narrow window and at print width, and look at the card
   headers and the left gutter of every ranked chart. If a label is truncated, the containment
   backstop worked, but the payload string is still too long. Shorten it at the source.

### The screenshot test

The last check, and the one that catches what the others miss. Open the top of the report at
about 1200px wide and ask whether you would put that image in front of strangers. Four faults it
reliably catches:

- **A number broken across two lines,** or any label wrapping mid-word. The fit pass handles tile
  values. Nothing handles a 60-character section title.
- **A chart with one enormous bar and six invisible ones.** Technically accurate, useless to look
  at. Collapse the tail into an `Other (n)` row and say so in the note.
- **A tile that says nothing.** "Locations: 5" earns its place only next to tiles that carry a
  finding. Four tiles of trivia at the top is the fastest way to look automated.
- **Findings with no numbers.** The ranked list at the bottom is where the story lives now, and
  every item's title should carry a dollar figure or a date. A list of adjectives is homework.

If it fails, say so in chat and name the fault. Do not fix it by rewriting the analysis, which is
not this skill's job, and do not ship it quietly hoping the numbers carry it.

## Workbooks

Apply the input convention above, then sweep the number formats. Re-run `verify_model.py`
afterwards. A formatting pass can mask an error value behind a custom format, and a workbook
showing a clean zero over a circular reference is worse than one showing `#REF!`.

## The copy sweep

Run on every deliverable with prose in it, including the chat message that goes with it.

Em dashes and en dashes, semicolons, emoji, *counterparty* and its relatives, Title Case headings,
deltas breaching the suppression rule, and a lead finding with no dollar figure or date. Report
what changed, one line per class of change. Do not paste the diff.

Where the lead finding is vague, flag it in chat. Do not invent a better one from numbers you did
not pull.

## Staying in your lane

You do not compute, recompute, verify, or explain the numbers. You do not add, remove, or reorder
sections. You do not write the analysis.

If the artifact is missing something structural, a findings section, an entity name in the
header, say so in chat and let the skill that owns the content fill it. Filling it yourself means
the brand pass is quietly authoring financial commentary, which is the one thing it must never do.

## Known gaps

Template and pass limitations are tracked in `reference/KNOWN-GAPS.md`: the findings-row
icon, the copy audit's payload-only scope, the categorical ramp tuning, and label clamping
on hidden tabs.
