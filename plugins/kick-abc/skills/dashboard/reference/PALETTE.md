# The categorical palette

Loaded by `skills/brand/SKILL.md`. The seven-entry `cats` ramp in that file's config block is the
source of truth for the values; this is why they are what they are. `reference/templates/brand_verify.js`
enforces every rule below, so changing one here without changing it there will fail the build.

`cats` is the categorical ramp, assigned by position. The first four entries are sampled from the
Kick product's own charts rather than invented here, and the other three are built to match them.
Four rules hold it together, and each one is load-bearing.

**One lightness across the whole ramp.** Every entry sits at L 0.82 to 0.84. This is the rule that
makes a chart read as one family instead of a carnival, and it is the one that measuring the real
product settled. An earlier ramp mixed four vivid hues with three tints, so a nine-bar chart went
loud, loud, loud, loud, soft, soft, soft and then wrapped back to loud. Categorical color exists to
separate members, not to rank them, and a ramp that varies in weight ranks them whether you meant
it or not.

**Lightness is the constraint, not saturation.** Kick's own chart blue is `#a8deff`, which is fully
saturated in HSL and still unmistakably a pastel, because at L 0.83 saturation stops describing how
loud a color is. Chroma does: the spread between the strongest and weakest channel. Every entry
here sits under 0.35, against roughly 0.64 for the accent blue. So the verifier checks lightness and
chroma, and a rule that reads "keep saturation low" will reject the actual brand color.

**The ramp opens on the Kick chart blue,** so the largest member of a ranked chart lands in the
brand family. It is lighter than `prior` on purpose, so a categorical blue and a prior-period series
are never mistaken for each other.

**No red, pink, coral, or salmon, ever.** `negbar` owns that range. On a diverging chart a pink bar
means a loss, and a reader who has to work out whether pink meant "category five" or "lost money"
has been failed by the palette. This is the one constraint worth refusing a pretty color over.

**Grey is absent** so it can mean "unclassified" without colliding with a real member, which is how
`Unassigned` and `41 others` are shown.

Hues are ordered so neighbors sit far apart on the wheel, because adjacent bars are the ones a
reader actually compares. The closest neighboring pair here is 80 degrees apart. Reordering the
ramp for looks will put two greens next to each other.

### Segments are separated by paper, not by borders

Touching shapes are separated by a 2px gap that shows `card` through: the bands of a stacked
column, the arcs of a donut. There is no token for it, because it is not a color, it is the absence
of one, and it should always be whatever the card is. Change `card` and the separators follow.

The gap is why a stack of four pastels at one lightness still reads as four things. Without it the
bands blur into one another exactly where they are closest in tone, which is the failure mode of a
single-lightness ramp and the reason the gap is not optional.

A darker outline would do the same job and cost more: at this weight a stroke draws more attention
than the fill it separates, and eight of them turn a quiet chart into a grid. Use the gap.
