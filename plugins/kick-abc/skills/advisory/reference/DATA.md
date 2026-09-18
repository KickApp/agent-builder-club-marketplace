# Getting the data

## Never block on a full data set

The first run is usually someone dropping in whatever they have. **Build the best deliverable the
available data supports, then name what was missing and what it would have added.** A skill that
refuses until it has AR aging produces nothing, and the user concludes skills don't work.

What each input unlocks:

| You have | You can produce |
| --- | --- |
| P&L, one period | Narrative recap, margin table, expense mix |
| P&L, two or more periods | Everything above plus trend, variance, top movers, found money |
| \+ Balance sheet | Liquidity and leverage ratios, working-capital read |
| \+ Cash balance | Burn rate and runway |
| \+ AR / AP aging | Cash trapped in receivables, collection timing, a real weekly forecast |
| \+ GL transaction detail | Found money: duplicate subscriptions, price creep, dead recurring spend |
| \+ Customer and vendor names on transactions | Spend by who you pay, customer and vendor concentration, a customer who stopped buying, spend that grew without a decision, a revenue bridge of lost / new / retained |
| \+ Class, department, location, or project tagging on revenue | Revenue and mix by that dimension, and variances located to the member that caused them |
| \+ The same tagging on costs | **Contribution by member**: which branch, team, or job actually pays for itself, and how long a loss-maker has been one |
| \+ Items or SKUs with price and cost | Unit economics per product: margin, contribution, the item to sell more of, and anything selling below cost |
| \+ Several closed months, split by revenue stream and expense line | A driver model that projects forward, carries scenarios, and refreshes each month |

A P&L with two periods carries a real report. Say what the next input would add, in one line, in
both the chat message and the artifact footnotes: *"Add an AR aging report and this becomes a
week-by-week cash forecast instead of a monthly average."* That line is honest about the limits
and it tells the user what to do next.

The party on a transaction is worth singling out: a customer or vendor name sits on nearly every
transaction in nearly every system, so the cuts it unlocks are usually available on a first run
without asking for anything. Read for it before concluding a data set is thin. Whatever the field is
called in the source, the report says vendor or customer, never counterparty. `DIMENSIONS.md` covers
detection and the coverage bands that decide whether a cut ships.

## Confirm before you compute

Confirm in one round of questions, taking everything you can from the request first:

- **Which books and which entity.** If reporting isn't set up, say what you see and stop. Don't
  improvise statements from unreconciled transactions.
- **Period and basis.** One basis, cash or accrual, across every period shown. State it in the
  artifact. Never mix bases across a comparison.
- **Which months are closed.** A model or forecast that treats a partial month as a full one is
  wrong in a way nobody notices. Take the boundary from the books, never from the calendar.

Everything else has a stated default. Ask about it only when getting it wrong would change the
deliverable, and never ask a question whose answer you can read.

## Unknown connector

This plugin reads from whatever accounting system is connected: QuickBooks, Xero, a Kick
connector, a pasted trial balance, an uploaded CSV or PDF. If documented bindings exist for the
connected system, use them. Otherwise:

1. List the available tools and read their schemas.
2. Map them to the inputs above. Anything with no plausible tool is `UNSUPPORTED`.
3. Show the user the mapping and get confirmation before reading beyond discovery.
4. Never guess a tool name. If the system exposes guide or discovery tools, load the relevant
   financial-report guide first.

With no connector at all, work from what the user pastes or uploads and label it `user-supplied`.
That path is the normal one for a first run and it should feel like a first-class path, not a
fallback.
