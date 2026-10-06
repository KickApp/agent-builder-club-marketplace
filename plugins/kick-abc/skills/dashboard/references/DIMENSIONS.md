# Dimensions

Read this before any skill that cuts the numbers by something other than a P&L line.

A P&L tells an owner *what* happened. A dimension tells them **where it happened and who it happened
with**, which is usually the part they can act on. "Opex rose $40,000" is a fact nobody can act on.
"Opex rose $40,000 and $31,000 of it is the Denver location, which opened in March" is a decision.

## The rule that governs all of this

**Detect, then include. Never require, never invent.**

Earlier versions of these skills refused dimensional cuts outright, on the reasoning that not every
business tracks them. That reasoning was wrong, and it is worth naming so it does not come back:
*not everyone has it* is an argument for detecting it, not for ignoring it. Nobody proposes dropping
runway because some clients have no cash balance. Dimensions work the same way as every other input
in `DATA.md`: the deliverable gets richer when the data is there, and stands on its own when it is
not.

So: look for what the ledger actually carries, build the cuts it supports, and say in one line what
tagging would unlock. A business with no dimensions at all still gets the full standard report and
should never see an empty "By location" card.

## The dimensions worth cutting by

Accounting systems name these differently. Map whatever the connected system calls it onto the
concept, and **label the artifact with the general word in the left column, always.**

| Use this word | Never label it | The question it answers |
| --- | --- | --- |
| **Customer** and **Vendor** | counterparty, supplier, payee, payor, contact, account | Who are we paying, and who pays us? |
| **Department** | class, cost center, team, division, program, fund, practice | Which part of the business earns and spends? |
| **Location** | branch, store, shop, outlet, site, property, office, region, market | Which places work and which drag? |
| **Project** | job, engagement, matter, case, campaign, production | Which pieces of work made money? |
| **Product** | SKU, item, service line, channel, offering | What do we sell that actually pays? |

### The general word for the axis, the client's own words for the members

This is one rule with two halves, and skipping the second half is what makes the first sound wrong.

**The axis is furniture.** Tab names, column headers, KPI labels, chart titles. These say *Location*
even when the client says branches, *Product* even when they say SKUs, *Vendor* even when their
system says suppliers. The furniture is the same in every report this plugin produces.

**The members are their data.** Riverside stays Riverside. A client with branches still reads every
one of their branch names, down the *Location* column, exactly as their books spell them.

Nothing is lost by generalizing the axis, because the specificity a reader wants was never in the
column header. It was in the rows, and it is still there.

An earlier version of this file said the opposite: use the client's own label, so a card said
*Branches*. It is worth naming why that was wrong, because it sounds client-friendly. The plugin
ships one set of skills to every business. *Branch profitability* is right for a bank and a paper
company, and quietly wrong for a design studio, a contractor, a clinic, a SaaS company, and most of
the people who will ever open one of these files. A word that fits one reader perfectly and excludes
the rest is a worse default than a word that fits everyone well. The same reasoning that killed
*counterparty* kills *branch*: pick the word the widest audience already knows, and spend the
specificity on the numbers instead.

Four owner questions sit behind these: **how did we do** (the P&L itself), **where did it happen**
(location, department, project), **what did we sell** (product), and **who was it with** (customers
and vendors). Organizing a deliverable by the question rather than by the field keeps it readable
when several dimensions are available: one view per question, not one view per field.

**Write *vendor* for someone the business pays and *customer* for someone who pays it. Never write
*counterparty* in a deliverable.** Most accounting systems name the field `counterparty` precisely
because it covers both directions at once, which is why the word leaks out of the schema and into
report copy. It is a database term. An owner has vendors and customers, and reading that they have
counterparties tells them a system wrote the page. *Supplier* and *payee* are out for the same
reason: pick one word for each side and use it everywhere. Where a section genuinely spans both
directions, say *customers and vendors*. The brand pass fails the build on *counterparty*, *payee*,
and *payor*, which never appear in a real company name and are therefore always prose. It reports
*supplier* rather than failing, because a vendor genuinely called Acme Supplier Co would otherwise
block a correct report.

A party name is present on essentially every transaction in every ledger, because money has to go to
someone. **It is the one dimension you can nearly always deliver**, and it is the one that most
reliably produces a reaction, because owners recognize the names. Start there.

Department and location usually require the client to have set them up. Project and product often
live outside the GL in an operational system, so treat a supplied file as `user-supplied` and label
it.

## Detection

Do not ask the user whether they track dimensions. Read for it, then confirm what you found.

1. Pull a P&L or spend report grouped by the dimension, if the system offers one. That is the
   tie-out path and always beats aggregating transactions yourself.
2. If not, read the dimension field off GL transaction detail and aggregate.
3. Measure **coverage** before building anything: what share of the dollars carry a non-blank value?

Coverage decides the treatment:

- **Above ~90%**: build the cut normally, with the unassigned remainder shown as its own row.
- **Roughly 40 to 90%**: build it, lead with the coverage figure, and frame it as partial. A department
  view over 60% of spend is genuinely useful as long as nobody mistakes it for all of it.
- **Below ~40%**: do not build the card. Say the field exists but is too sparsely filled to cut by,
  and name it as the highest-value cleanup available. That sentence is often the most valuable line
  in the report.

Report coverage as dollars, not transaction count. One untagged payroll run outweighs four hundred
tagged coffee receipts.

## The integrity rules

These are the ones that make dimensional reporting trustworthy rather than merely colorful.

**Unassigned is a row, never a rounding difference.** Anything with a blank dimension goes in an
explicit `Unassigned` row that is visible in the table and included in the total. Dropping untagged
activity to make a chart look tidy silently misstates every share in it, and it is the single
easiest way to lose an owner's trust. If unassigned is the largest row, say so plainly.

**Parts sum to the P&L.** Every dimensional cut re-sums to the same total the P&L reports for that
line, and the tie-out rule in `HOUSE-RULES.md` applies without exception. Show it once: *"the five
locations plus unassigned total $1,240,000, matching reported revenue."*

**Never allocate a cost that is not tagged.** Margin by department only exists if costs actually
carry the department. Spreading overhead by a revenue share you chose invents the answer and then
reports it as fact. When revenue is tagged and costs are not, publish the revenue cut, say costs are
not tagged, and stop. If the client wants an allocation, they supply the basis and it is labeled as
their assumption.

**A dimension member is not a segment total.** Watch for members that overlap or double-count:
a "General" class that is a catch-all, a parent class whose children are also listed, a vendor that
appears under two spellings. Roll obvious duplicates together and note that you did.

**Merge spellings, never merge names.** `ACME HOLDINGS`, `Acme Holdings`, and `Acme Hldgs` are one
vendor and should be combined, with the merge disclosed. But two similar names are often two
genuinely different parties: a county government and that county's tax collector, a parent and its
subsidiary, a person and the company they own. Combining those corrupts every share in the table and
invents a concentration that does not exist. So merge only where the difference is capitalisation,
punctuation, spacing, or an obvious abbreviation; list anything else as a near-match for the client to
confirm and leave the rows separate meanwhile. Declining to merge is the safe error here.

## Contribution, not just revenue

A revenue split says which member is *biggest*. An owner wants to know which member is *worth
having*, and those are different questions with different answers. Answer the second one wherever
the costs carry the dimension.

**Contribution = revenue tagged to the member, less costs tagged to the member.** Then stop. Build
the ladder explicitly so the reader can see where you stopped:

```
revenue tagged to the member
  less direct cost of sales tagged to the member
  less operating costs tagged to the member      (rent, that site's payroll, its utilities)
= contribution
```

Shared overhead that carries no member (corporate payroll, group insurance, the audit fee) stays
out of the member columns and appears once as a single `Unallocated overhead` line. That line plus
every member's contribution re-sums to operating income, which is the tie-out to show.

**Why this restraint is the point, not a limitation.** A negative contribution is
allocation-free: the member does not cover the costs that exist *because of it*, so no assumption
you made can be argued with. The moment you spread head-office cost across members by a revenue
share you picked, the finding becomes a debate about your allocation instead of a fact about the
business. Contribution is the strongest defensible claim available, so make it and go no further.

Say what contribution is not, once, in the artifact: it is before shared overhead, so a member can
show positive contribution and still not carry its share of the company.

**What a negative member is worth, stated honestly.** Report the contribution shortfall and the
period it covers: *"Utica's contribution has been negative since July, $31,400 cumulatively."* Do
not claim that closing it adds that to profit. Some costs continue past a closure and some revenue
moves to another member. The finding is the shortfall and its persistence; the decision needs the
lease term and a view on whether the revenue transfers, and that is a question for the review
conversation.

**Rank on contribution, and report where the two rankings disagree.** The disagreement is usually
the finding: the member with the second-highest revenue and the lowest contribution is a pricing or
cost question nobody has asked. When only revenue carries the dimension, rank on revenue and say
plainly that margin by member is not available.

## Persistence is what makes a member finding land

One bad month is noise. **Six consecutive bad months is a decision the owner has been postponing**,
and it is a much stronger sentence for the same data.

So for any member on the wrong side of zero, count the **consecutive periods** it has been there,
name the period it crossed, and say whether it is still there. Needs at least six periods of history
to claim a run; with three, say the trend is early. Then look at what changed in the crossing
period. A member usually goes negative because revenue fell while a fixed cost held, and naming
that pairing turns the finding into an explanation.

A `matrix` of members against the last six to twelve periods shows a run at a glance, which is why
it is the right section for this rather than a single-period bar.

## Product and SKU economics

When the books carry items (an invoicing system with products, or revenue and cost both tagged to a
service line), this is usually the highest-leverage cut available, because the actions it implies are
immediate: reprice, push, or drop.

Per item, from the books only: **units, revenue, realized price** (`revenue ÷ units`), **unit cost**,
**unit margin**, **margin %**, **contribution dollars** (`units × unit margin`), and share of both
revenue and contribution.

Four questions, four different answers, and the gaps between them are the findings:

| Question | Rank by | The finding it produces |
| --- | --- | --- |
| What sells most? | units | The volume leader, which is often not the profit leader |
| What earns most? | contribution dollars | Where the profit actually comes from |
| What earns best? | margin % | The item to sell more of |
| What loses money? | unit margin below zero | The item to reprice or retire |

The two crossings worth writing up every time: **high margin and low volume** is the "sell more of
this" finding, and **high volume with thin or negative margin** is the "you are busy losing money"
finding. An item selling below its own cost is the single most actionable line in a product report.
Quote the loss per unit and the annualized total.

Guardrails specific to items:

- **Unit cost comes from the books.** An item cost field or cost of sales tagged to the item. Never
  infer a unit cost from a blended margin, and never estimate one to complete a table.
- **Revenue tagged and cost not** means you publish units, revenue, and mix, and say margin by item
  is unavailable. That is a complete deliverable, not a failed one.
- **Below cost may be deliberate.** A loss leader, a contractual price, a clearance run. Report the
  economics and ask, rather than asserting a mistake.
- **Realized price below list, consistently, is discount leakage**: see below.

## Making it readable

**Top N plus a real Other row.** Rank by dollars, show the top 8 to 12, and collapse the tail into
`Other (n members)` with its count. A forty-row vendor table gets skimmed and discarded. Never let
`Other` hide a member large enough to belong in the ranking.

**Rank by dollars, not by percentage change.** A vendor that went from $80 to $400 is a 400% increase
and it does not matter. Sort by the size of the money, always.

**Show share, not just amount.** The useful column beside "$186,000" is "15% of spend." That is what
makes a number a finding.

**Normalize only on supplied denominators.** Revenue per location is fair. Revenue per square foot,
per head, per bed, per seat is often the number that actually decides something, but only when the
client supplies the denominator. Never estimate one.

**Same-store before total.** When a location or department opened or closed mid-comparison, growth
across the whole set is not comparable. Report the like-for-like set separately from the total and
name which members were excluded. A chain that opened two stores has not "grown 40% per location."

## The findings dimensions actually produce

Cut the data so these fall out of it. This is the payoff, and it is why the cuts belong in the
report rather than in an appendix.

**Concentration.** The largest vendor as a share of total spend, and the top five together. On the
revenue side the same math is customer concentration, which is a real risk finding: one customer at
40% of revenue is a going-concern question, not a fun fact. Say the share and what it means, and
frame it as a question for review rather than a verdict.

**Spend that grew without a decision.** Rank vendors by dollar increase against the prior
comparable period. This is where price creep, seat-count drift, and a renewal nobody reviewed all
surface, and it dovetails with the found-money scan in `dashboard`.

**Dead and dormant.** A vendor that billed steadily and stopped, or one still billing against
a project that closed. Both are worth a look, in opposite directions.

**A customer that stopped.** The same math pointed at revenue, and far more consequential than any
vendor finding. A customer with revenue in prior periods and none now has churned: name them, their
run rate before they left, the share of revenue they were, and the period they went quiet. When that
customer was one of the top few, this outranks everything else in the report: a book that was 40%
concentrated and has just lost its number two has a different shape than it did last quarter.

Do not read one quiet period as churn for a customer who buys seasonally or in campaigns. Check the
buying pattern across the full history first, and say which reading you took.

**Discount and price leakage.** Where invoicing carries a list price, a discount line, or a realized
price you can compute, total the discount by customer. The finding is almost never the average rate.
It is **concentration**: most of the discounting landing on one account, or a promotion that was
meant to be occasional running all year on the largest customer. Quote the dollars given up and
against which account. This is the revenue-side twin of found money, and owners rarely see it,
because a discount never appears as an expense.

**The same name on both sides.** One party can be both a customer and a vendor: a tenant you also
buy services from, a vendor who buys from you. Report both sides at full size and **never net
them**, because netting hides two real relationships and understates both. Flag the dual role once;
it also changes how concentration reads on each side.

**The member that carries the business, and the one that eats it.** Ranked contribution by
department, location, or project, with the loss-makers named and their run of bad periods counted.
See *Contribution, not just revenue* above for the ladder and *Persistence* for the run; together
they turn a bar chart into the finding an owner acts on.

**Where a variance actually came from.** When a P&L line moves, the dimensional cut of that same
line usually explains it in one row. This is the most efficient thing in `flux` when it is available.

## Rendering

Use the section vocabulary in `ARTIFACTS.md`. Conventions that keep dimensional views consistent:

- **hbars** for ranked members, **donut** for mix, **share** for the table with a share column, and
  **matrix** for members against periods when the trend per member is the point.
- **`hbars` is the only chart that shows a negative member.** Its axis goes diverging on its own when
  any value is below zero: a zero line appears, loss-makers grow left in pastel red, and widths stay
  proportional. So contribution rankings belong in `hbars`, never in `donut`. A donut drops negative
  slices entirely, because a share of a mix cannot be negative. Put mix in the donut and profit in the
  bars.
- Hold color assignment stable for a member across a recurring report, so the reader learns the
  colors. Set `color` explicitly for that; otherwise let position assign it.
- **Always set `Unassigned` and `Other` to the neutral grey `#d2d2d8` explicitly.** Positional color
  assignment will otherwise hand a real member the grey and give the catch-all a vivid one, which
  reads as though the leftovers were a headline segment. This is the single easiest dimensional chart
  to get subtly wrong.
- **Give a numeric `table` cell the section's `fmt`** or set it per cell. A currency column that
  renders as `186,000` instead of `$186,000` looks like a bug to a client.
- **Use the full-width chart for long member names.** A half-width `hbars` gives labels about 108px.
  Vendor and product names rarely fit, and a ranked list past about six rows is cramped at half width.
- **A falling cost is not bad news.** In a change column, set `tone:"plain"` on the negative cells so a
  reduction in spend does not render in the same pastel red as a loss.
- **Sort catch-alls last, not by value.** `Unassigned` and `Other` belong at the bottom of a ranked
  table even when their total would place them mid-list, and a member with no tagged costs shows `n/m`
  for its margin rather than a rate computed against a cost of zero. In a `"sort": true` table the
  renderer holds this for you: it pins catch-alls below the real members whichever column the reader
  sorts on, and it keeps the total row and everything under it in payload order, so a reconciliation
  footer such as `Total`, `Unallocated overhead`, `Operating income` cannot be shuffled into nonsense.
- **Use `currency-short` on a matrix wider than about six periods.** Twelve months of full dollar
  amounts fits on screen but crowds on paper; `$194k` reads fine and keeps the grid inside the page.
- Pastel red marks a genuine negative: a loss-making member, a below-cost item. It never marks
  "biggest," and dimensional views never score members red-versus-green.
- Name the dimension and its coverage in the section `note`, not in a callout box.
- One dimension per card. A department card and a location card, never a single card trying to be
  both.

## What to say when a dimension is missing

One line, specific about the payoff, in both the chat message and the artifact footnotes:

> "Your ledger has no department tagging. Tagging payroll and rent alone would show which side of
> the business actually carries its own cost. That is the cut most owners find hardest to get."

Name the cheapest useful next step, not a full tagging project. The point is to make the next report
better, not to sell a cleanup engagement.
