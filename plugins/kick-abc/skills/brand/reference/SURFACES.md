# Hover and controls

Loaded by `skills/brand/SKILL.md`. How the interactive furniture of an HTML report looks: the
tooltip, and the pills above the content. What those controls *do*, and which sections they act
on, is in `reference/ARTIFACTS.md` and belongs to the content skills, not here.

### Hover reveals, it does not decorate

Every chart shape is hoverable and the tooltip is a light card, not a dark chip: `card` background,
`line` border, 10px radius, the same soft lift as everything else on the page. A black tooltip on a
pale page is the one element that looks borrowed from somebody else's product.

Four parts, in this order, and a tooltip that has all four is doing its job:

| Part | Carries |
| --- | --- |
| Title | the series, behind an 8px dot in that series' own colour |
| Period | the column or date range, in `mut` |
| Rows | label left, figure right, tabular numerals |
| Total | the column's net, under a hairline |

The dot matters more than it looks. A stacked column is the one place a reader genuinely cannot
tell which band they are on, because the bands are one lightness apart by design. The dot answers
that before the label is read.

The figure in the tooltip is exact to the dollar even when the axis is abbreviated. The axis is for
shape; the tooltip is where the number lives.

### Controls look like Kick's

A period selector, a grouping selector, an entity filter. Each is a pill: `card` background, a 1px
`line` border, 9px radius, 12px label, and a chevron only where the control opens something. They
sit right-aligned above the content, never in the header block with the entity name.

An entity filter shows a stack of overlapping initial chips at 17px, each in its entity's colour
with a 1.5px `card` ring so the overlap reads as depth. The label beside them says *All entities*,
or the entity's name when one is chosen, or a count when it is some of them. Never a raw list of
names in the button: the chips already carry that and the button has to stay one line.

**A control with one option is not a control.** One entity, no entity filter. One period, no period
selector. The empty state of a filter is its absence.
