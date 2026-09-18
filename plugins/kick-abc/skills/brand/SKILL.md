---
name: brand
description: "Applies the firm's visual identity and copy standards to a finished deliverable. Themes HTML reports, applies input conventions and number formats to Excel and Google Sheets workbooks, and enforces copy standards on anything with words in it. Runs last, as a pass over completed artifacts. Use when the user asks to brand, restyle, re-skin, theme, or clean up a report or workbook, when they change their palette or firm details, or automatically as the final step of an advisory or close run. Never computes, recomputes, or changes a number."
---

# Brand

## Purpose

The whole appearance layer: one config, the house rules, and the script applying them. Skills
compute; brand decides how it looks. The rule that outranks everything: **never change a
number**, not a rounding, not a sign, not a total. A wrong figure is flagged, never edited.

1. Config (the only part a firm edits)
2. Theme HTML reports with `theme.py`
3. Apply workbook conventions
4. Run the copy sweep, verify, hand over

## Procedure

The config, the only part a firm changes; everything after it is the house standard.
`theme.py` parses the first fenced json block from this file, so config and code stay together.
Every value is a Kick design token, not an approximation; if the tokens move, this block moves.
A second look: another fenced json block below a `preset:` line; first block wins unless named.

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

Read `reference/PALETTE.md` before changing any of it. Surfaces and tooltips:
`reference/SURFACES.md`. Statement presentation: `reference/ARTIFACTS.md`. Suite conduct:
`reference/HOUSE-RULES.md`. Known limitations: `reference/KNOWN-GAPS.md`.

- [ ] 1. Generate first, brand second, always two steps; there is deliberately no flag doing
      both. Multiple files: generate all, then one `theme.py` call over the whole set, which
      is what makes them come out identical.
- [ ] 2. Theme each HTML report. Never hand-edit the HTML and never restyle the template.

      ```
      python3 reference/templates/build_report.py data.json out.html
      python3 reference/templates/theme.py SKILL.md out.html
      ```

      It injects `<style id="brand-theme">` and `<script id="brand-icons">`, both replaced,
      so re-running is safe; it never touches the renderer, the payload, or a number.
- [ ] 3. Apply the workbook input convention to Excel and Google Sheets, sweep the number
      formats, re-run `verify_model.py`: formatting can mask an error value behind a format.
- [ ] 4. Run the copy sweep on every deliverable with prose in it, including the chat message
      that goes with it. Report one line per class of change; never paste the diff. A vague
      lead finding is flagged in chat, never replaced with numbers you did not pull.
- [ ] 5. Verify against Completion. If the screenshot test fails, say so in chat and name the
      fault; never fix it by rewriting the analysis and never ship it quietly.

## Guardrails

Palette semantics. Color carries meaning or it should not be there; every hue has one job.
- `accent` is the brand, the primary series, the largest ranked member. Never a positive result.
- `tint` marks the one callout to read first. Never general emphasis, never a KPI tile, since
  a tinted tile reads as an active selection.
- The `neg` family colors genuinely adverse fills only (a loss, an overrun, a covenant
  breach): bars, cell tints, chart marks. Never any negative number.
- Fills and text are different reds. Adverse text takes `lossInk`, which reads at 4.5:1 on
  every background and is never a fill. A pastel used as text ink fails contrast.
- `posbar` and `negbar` stay a matched pair at one lightness; the sign carries the meaning.
- `cats` are categorical, assigned by position, never ranking or scoring. `cmut` grey means
  unclassified or other, never a real member. Ramp rules, enforced by `brand_verify.js`: one
  lightness, chroma under 0.42, nothing in the red range `negbar` owns, at least 25 degrees
  of hue between neighbours.
- **No red versus green scoring, ever.** Adverse gets pastel red; good things get no color.
- **A negative number is not automatically bad.** Costs render in parentheses in charcoal. Set
  the plain tone on any cell whose negative is favorable, table cell or matrix row.
- **Color lands on signed numerals, never on worded deltas.** `($13,500)` may carry the tone;
  "Up $5,425" renders in body ink. The word already carries the direction.
- **This pass owns chart hues.** Incoming chart colors get restyled to this palette. Two
  ramps in one report is a defect, not a blend.

Layout and identity.
- `mark` left null shows the client entity's initials; set it to stamp the firm's mark.
  `markColor` is that square's fill, where a firm's one brand color lands. Always initials
  over a logo file: no network, and an embedded raster logo prints badly.
- **Annotations live inside the SVG, next to what they annotate**: axis labels in the plot,
  bar values on their bars, sparkline ranges at endpoints. Prose annotations die in print.
- Cap payload strings; the containment backstop is not permission. Limits: section note about
  90 characters (longer goes to a `text` section), title 40, `hbars` and `matrix` member
  labels 28, KPI label 22, sub 34. A long member name is a signal: shorten it, explain it in
  the note or a finding.
- Inter at 14px, embedded (about 25 KB Latin subset); `"embed": false` only for a hard size
  limit. Weights 400 body, 500 labels, 600 title and KPI headlines. Numbers always
  `font-variant-numeric: tabular-nums`, tracking `-0.005em`. Charts are inline SVG, never
  canvas, which prints fuzzy or blank.
- Icons are identifiers, not decoration: inline Lucide paths, 24x24, 1.7 stroke, no icon font
  or sprite URL. Five placements only: KPI tiles, findings rows, measure tables (opt-in via
  `"measures": true`, never on for a P&L), the entity mark, one accent glyph on the callout.
  None in chart legends, section headers, or tabs, ever.
- **A control with one option is not a control.** One entity, no entity filter. Tooltips are
  light cards, never dark chips.

Copy. The words are part of the look.
- No em dashes, no en dashes, no spaced hyphens in any deliverable. No semicolons. No emoji.
- *Vendors* and *customers*, never *counterparty*, *supplier*, *payee*, or *payor*. The plain
  word every time (*profit* not *contribution*, *cash tied up* not *cash cycle*); define the
  measure once in the note. A labeling rule only: renaming never licenses computing
  differently or dropping a row.
- A label, its value, and its subtitle must agree: months are a number of months, multiples get
  `x`, percentages get `%`. A title names its subject, no pronoun standing in for it, and uses
  the same word as the thing under it; where they differ, change both together.
- Sentence case everywhere. Currency exact to the dollar in tables and tiles, abbreviated on
  chart axes only. Percentages to one decimal; multiples one decimal with a lowercase x.
- Delta suppression: when the magnitude exceeds 300%, the prior period is incomplete or a stub,
  or the prior is zero, near zero, or negative, suppress the percentage and print the absolute
  change plus the reason. Same rule for any ratio on a small or absent denominator.
- The copy audit reports, never rewrites. *Counterparty*, *payee*, and *payor* stop the run
  outright: always prose, never part of a company name. Fix each hit in the payload, rebuild.

Workbooks and close deliverables.
- Input convention: blue font on yellow fill for hardcoded inputs, black on white for formulas,
  green font for in-workbook links. No cross-file links; hardcode the value and label it an
  input. Formats: `#,##0`, `(1,234)` negatives, `0.0%`, `0.0"x"`. Tabs sentence case.
- **Formulas, never computed values.** Hardcoded numbers are a screenshot with extra steps.
  **One direction of flow**: inputs and an actuals spine feed everything; nothing feeds back.
- **A statement is a statement, not a trial balance.** Anything headed "balance sheet" or "P&L"
  carries the chart of accounts hierarchy with subtotals, in statement order; derive it from
  the GL when the connection cannot supply it. **One entity per file, and name it.**

Delivery and lane.
- File name `{entity}-{skill}-{period}.{ext}`, lowercase, hyphens, no spaces. The chat message
  points at the artifact, never copies it. One-line footer in `mut` with the config `footer`
  string; no logo banners or note boxes. **No preparer attribution, no "Prepared {date}"
  line**: the period in the heading dates the report.
- What never changes, regardless of config: no network (no CDN, web font, remote image, or
  analytics), no dead controls, no new components (restyle what exists), omit rather than pad,
  raw numbers into the renderer (`410220`, not `"$410,220"`).
- Stay in your lane: never compute, verify, or explain the numbers; never add, remove, or
  reorder sections. A missing structural piece is flagged in chat for the skill that owns the
  content; filling it yourself is authoring financial commentary.

## Example

```
Correct: +$540,700 vs last year (2025 partial, no comparable period)
Wrong:   ▲ 4057.7% vs last year
```

The lead finding the copy sweep accepts carries a dollar figure or a date: "Your third-largest
location has lost money for six months running, $31,400 in total." Adjectives get flagged.

## Completion

Done when:

- [ ] No number, section, or ordering changed anywhere in the pass
- [ ] The file opens with no network: grep for `http://`, `https://`, and `@import` is clean
- [ ] Every control still works (each tab and toggle clicked) and the copy audit came back empty
- [ ] Icons rendered where `icons` is true; a glyphless KPI row means the script did not inject
- [ ] The brand landed: header mark Kick blue, text in Inter, cards carry the soft lift
- [ ] Nothing overflows at a narrow window or print width; no truncated labels in the payload
- [ ] The screenshot test at about 1200px passed: no number broken across lines, no chart
      with one enormous bar (collapse the tail into `Other (n)`), no trivia tiles, no
      findings without numbers
- [ ] Workbooks: `verify_model.py` re-run and green after formatting

Cleanup: hand over the file paths, note the HTML opens in any browser offline and Cmd-P prints
clean, report the copy sweep one line per class of change. Anything the pass could not fix (a
vague lead finding, a missing structural section) is named in chat for its owning skill.
