# Revenue plan report

The deliverable is a PDF. Chat names the floor, the verdict, and the file. The
engine carries the brand. This file says what goes into the payload. It does not
restyle the page.

Run this from the user's working folder, never from the skill folder, and keep
the payload there too. `pip install reportlab` if it is missing. The
engine derives every plan figure from the inputs. A check that misses the goal
prints the reason and writes no file. Do not edit the engine. Do not draw a
second version of the page. If the build warns that Inter is missing, do not
hand the file over.

```
python3 <skill folder>/references/templates/build_plan.py osher-road-to-100k.json
```

Name the payload after the report title in kebab case. The PDF takes the same
name beside it, so one plan never overwrites another. The engine refuses to
write inside the skill folder.

Quote the printed `floor=` and `verdict=` lines. Do not recompute them in chat.

## Payload

Raw numbers. `0.40`, not `"40%"`.

```
title         optional. Leave it out for "<owner>'s Road to <goal>"
owner         the owner's first name, when they gave it
entity        the firm's name, or leave it out
period        the goal year
goal          annual number
goal_basis    "profit" or "revenue"
overhead      annual fixed overhead. 0 when it is the default
capacity      client count, or leave it out
delivery      {kind: "percent" or "dollars", value, per: "month" or "year"}
              percent is a fraction. dollars is cost per client, per month
              unless per says year
tiers         [{name, billing: "monthly" or "annual", price}], one bar each.
              Only when the owner gave two or more prices or named tiers
current_price {billing, price}, the owner's one price. With tiers left out,
              the engine builds the Bronze, Silver, Gold ladder from it
mix           optional {tier name: client count}, the owner's mix. Leave it
              out otherwise; the engine draws a placeholder mix
services      optional [{name, billing, price}], two or more. Leave out for
              placeholder Tax, Books, and Both. [] drops the table
service_mix   optional {service name: percent}, the owner's expected split
cost_cuts     optional [percent]. Default 5, 10, 15, 20
hires         optional [{label, salary, adds}]. adds is clients of capacity.
              Leave out for placeholder hires. [] drops the table
proposal      optional {monthly, one_time, one_time_label, delivery}
              delivery here replaces the plan delivery for that check only
parameters    [{name, value, source}], every input on the page
notes         [string], printed under Parameters and Sources
```

Source is one of Owner, Books, File, Default, or Placeholder. Books and File
values carry their period or file name in the value. The engine appends the
ladder tiers, a placeholder mix, and placeholder services and hires to parameters
itself; do not list them twice,
and do not list the current price as its own row.

## The tier ladder

Every plan shows tiers. When the owner gave one price, or none, leave `tiers`
out and the engine fills three. Only the owner's current price is theirs. Every
other tier price is a placeholder: a starting point picked by a fixed rule,
tagged Placeholder with that rule, and named in chat as a number to replace.

- Silver: the floor rounded up to the next $100, the cheapest round price that
  reaches the goal at capacity.
- Bronze: the owner's current price. It is often over capacity, and that is the
  point of the bar.
- Gold: the premium tier at twice Silver, rounded up to the next $100.

When the current price already clears Silver, it becomes Silver and Bronze is
60% of it, rounded down to $50. With no current price, Bronze is 60% of Silver.
A ladder needs a capacity or a current price.

## The mix

With two or more tiers, the chart always ends with a Mix bar, and the mix it
shows reaches the goal at capacity whenever one can. The engine starts from the
owner's mix when they gave one. Otherwise it starts from 60/40 for two tiers,
40/40/20 for three (10 / 10 / 5 at 25 clients), or an even split past that.
Without a capacity it splits 10 clients and stops there.

When the starting mix needs more clients than capacity, the engine replaces it
with the nearest mix of exactly capacity that reaches the goal. Nearest means the
smallest squared change per tier, so every tier tilts up a little instead of one
emptying, with ties going to the smallest overshoot. The bar shows the fitted
mix, the summary line says what the owner's own mix would need, and a Tier mix
row tagged Placeholder names the start it was fitted from. When even a full book
in the best tier misses, the starting mix stays and the bar shows it over.

Put the owner's tier mix in `mix` as they gave it. Do not fit it by hand; the
engine does. Every mix the engine draws or fits is a guess at how clients land
across tiers, not a fact about this firm.

The Mix bar's label is two lines: the split, then the average price a month.

## The page

In order:

1. Title and a one-line subtitle: goal, capacity, delivery cost, overhead.
2. Clients needed by tier. Horizontal bars in soft fills, one per tier. Bronze,
   Silver, Gold, and Platinum get their named colors; other names get the soft
   palette in order. The mix is the last bar, split by tier share. A dotted line
   marks capacity. A bar past the line shows its count in red with "N over".
3. A summary line: the floor at capacity, which bars cannot reach the goal,
   what the owner's mix needs when it was fitted, and what the shown mix needs
   and makes. The proposal verdict sits under it, with the gap
   and the one-time fee on its own line.
4. Client mix, always unless services is []. One row per scenario: the owner's
   split first (shaded) when given, then "Mostly <service>" at 60 percent for
   each service, then an even split. Columns: monthly vs annual share, the split
   by service, profit per client, clients needed, profit at capacity.
5. Margin, on a profit goal. Today (shaded), then each cost cut. Columns: cost
   per client, price floor, clients needed, profit at capacity. The note under it
   says how much of the price the cost is and whether the cuts move the client
   count.
6. Hiring, on a profit goal with capacity, unless hires is []. Solo (shaded),
   then each hire. Salary is fixed
   overhead and adds to the goal. Capacity grows by adds. Columns: salary,
   capacity, clients needed, price floor, profit at capacity.
7. Parameters and Sources, then the notes.

Margin and hiring run on the mix. With a single owner tier and no mix, they run
on that tier.
Client counts round up. Floors round up to a whole dollar. Red is only for a miss.

## What may be a placeholder

The goal, delivery cost, and capacity are never placeholders. The floor and every
client count are computed from the owner's numbers. Everything else the owner did
not give is a placeholder: ladder tier prices, the default mix, the default
services, and the default hires. Each is tagged Placeholder in parameters and
named in the chat message as a number to replace.

Without owner services, the engine fills Books at the owner's monthly price, Tax
at $2,000 a year, and Both as the two together. A service set is skipped when one
would not cover its delivery cost. Without owner hires, it fills a part-time hire
($30,000, half the owner's capacity), a full-time hire ($60,000, the owner's
capacity), and two full-time hires. Cost cuts and
the client mix scenario rows are what-if rows, labeled as such, and not anyone's
claim.

Ladder worked figures: $100,000 profit, $700 a year per client, 25 clients,
current price $4,000 a year. Floor $392. Bronze $4,000 a year needs 31 (6 over).
Silver $400 a month needs 25. Gold $800 a month needs 12. The 10 / 10 / 5 mix
needs 22 and makes $118,500 with all 25.

Fitted mix worked figures: $150,000 profit, $18,000 overhead, $100 a month per
client, 30 clients, tiers Books $450 a month, Tax $2,500 a year, Both $600 a
month, owner's mix 15 / 6 / 9. Floor $567. The owner's mix needs 41, 11 over. The
fitted 6 Books / 24 Both mix needs 30, averages $570 a month, and makes $151,200.

Worked figures, the anonymized plan in SKILL.md with tiers at $500 and $1,000.
Floor $695. $500 needs 28 clients, 8 over. $1,000 needs 14. The $550 proposal is
below the plan by $145 a month. A 20% delivery cost cut (40% to 32% of revenue)
moves the $500 tier from 28 clients to 25.
