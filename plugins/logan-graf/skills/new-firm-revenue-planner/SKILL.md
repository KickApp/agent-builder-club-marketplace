---
name: new-firm-revenue-planner
description: "Turns a new accounting firm owner's income goal, service prices, and delivery cost into a revenue plan PDF: clients needed for each price tier and a mix against capacity, the price floor, a fits or below-plan verdict on a proposal, and sensitivity tables for client mix, margin, and hiring. The engine carries the brand and derives the figures. Drafts the inputs from the firm's own connected books or a dropped-in export or plan when it has them, and asks only for what is missing. Use when a firm owner who is starting or early in a practice asks how many clients they need, what to charge, or whether a proposal price still hits their income goal."
---

# New Firm Revenue Planner

## Purpose

Produce a short scenario plan for a new accounting firm owner. It starts from what they want to make and ends with how many clients they need, the lowest monthly price that still hits the goal, and whether a specific proposal clears that price. Then the owner prices to the plan and does not talk themselves into a low number. The skill is read-only and does firm economics only. When the owner drops in a file or the firm's own books are connected, it drafts the inputs from that data and asks only for what is missing. It never changes the books, categorizes, or closes.

The plan has four parts:

1. Clients needed for each price tier, with the mix as the last bar, against the owner's capacity.
2. Price floor at capacity, and the proposal check: fits the plan or below the plan, with the gap.
3. Sensitivity tables: client mix, margin, and hiring.
4. Parameters and Sources: every input tagged Owner, Books, File, Default, or Placeholder.

Kick execution lives in [references/kick.md](references/kick.md). The payload and the page layout live in [references/report.md](references/report.md). Good and bad runs are in [references/examples.md](references/examples.md).

## Procedure

- [ ] 1. Confirm the request is firm economics for a new or early-stage firm.
    Bookkeeping, tax prep, a client's books, or benchmarking an established multi-staff firm do not run this skill. Say so and stop.
- [ ] 2. Look for the owner's data before asking anything.
    Check in this order. First, anything the owner attached or pasted: a P&L or income export from any ledger, a price sheet, a proposal, a contractor invoice, a business plan. Second, the firm's own books on a connected ledger (on Kick, follow references/kick.md). Read only the firm's own entity, never a client's, and confirm the entity name with the owner before reading. Usable history means at least three full months of revenue. With less, or no data at all, go to step 4. Do not say what was missing.
- [ ] 3. Draft the inputs from the data.
    Window: the last 12 full months, or from the first month with revenue if later. Draft each paying client's recurring monthly amount (the latest full month) and billing basis, delivery cost as a percent of revenue from the delivery expense lines, fixed overhead from the remaining operating expense lines, and the count of active recurring clients. A window under 12 months is annualized as window total / months x 12, and the plan says so. Show the owner's current take-home pace (net income, plus owner draws when the books carry them) beside the goal as context only. Tag every drafted figure "Books" or "File" with its period.
- [ ] 4. Open with a short projection conversation.
    Lead with "Let's plan out some projections." If step 3 drafted inputs, put that table under the line. Infer whatever the owner's words already settle, then ask only a gap they do not. "Make", "take home", or "profit" is take-home profit. "Revenue" or "billings" is gross revenue. A price that says monthly, annual, or one-time keeps that basis. A percent or a dollar cost per client is the delivery cost. Overhead defaults to $0. A bare goal with no basis defaults to take-home profit, and the plan says so. One or two sentences. Ask about a mixed expense line or a one-off payment only when it would change a number already on the table. Do the reading silently. The owner does not hear that a skill, a file, or the books are being checked.
- [ ] 5. Settle the income goal and its basis.
    The goal is the owner's number, never read from the books. Infer the basis from their words, as in step 4. Do not stop to confirm a basis the words already gave, and do not stop on a bare number that defaulted to take-home profit. Record the period. Convert a monthly goal to annual by multiplying by 12.
- [ ] 6. Settle the service offering and prices.
    For each service, record the name, the price, and the billing basis: monthly recurring, annual (for example a tax return), or one-time (for example onboarding or cleanup). Use the basis the price already states. Convert to annual revenue per client: monthly price x 12, annual fee x 1. Hold one-time fees aside. They do not count toward recurring revenue. Every plan shows tiers. Two or more owner prices, or tiers the owner named, are the tiers. One price, or none, goes in as the current price, and the engine builds Bronze (the current price, often over capacity), Silver (the floor rounded up to the next $100), and Gold (a premium at twice Silver). Only the current price is the owner's. Silver and Gold are placeholders: tagged Placeholder and named in chat as numbers to replace. Do not ask for tier prices first.
- [ ] 7. Settle the delivery cost.
    Accept a percent of revenue (for example 40%) or a dollar cost per client per month. Delivery cost covers contractor or staff time and per-client software to do the work. If neither the data nor the owner gives one, ask. Do not assume a percent.
- [ ] 8. Settle optional inputs.
    Fixed overhead per year not tied to a client (insurance, base software, marketing). Default 0, tagged as a default. Client capacity: how many clients the owner can serve at once. The current client count is a floor, not the capacity. Tier mix: the owner's client counts per tier, the start for the Mix bar. Without one, the engine starts from a placeholder split (40/40/20 of capacity for three tiers). When the start misses the goal at capacity, the engine fits the nearest mix that reaches it. Either way the bar's mix is tagged Placeholder and named in chat, and a fitted owner's mix is named as theirs needing more clients. Do not ask for a mix first, and do not fit one by hand. Services for the client mix table: two or more with their prices and billing, plus the owner's expected split when they have one. Without them, the engine fills Tax, Books, and Both as placeholders. Hires: salary and the clients each hire adds to capacity. Without them, the engine fills part-time and full-time hires as placeholders. Do not ask for services or hires first. The owner's first name sets the title, "<name>'s Road to <goal>". Never present a mix, a service price, or a hire as the owner's when they did not give it.
- [ ] 9. Compute required revenue.
    Profit goal with percent cost: required revenue = (goal + fixed overhead) / (1 - delivery cost %). Revenue goal: required revenue = goal. Dollar cost per client: skip this step and use step 10's contribution form.
- [ ] 10. Compute clients needed for each price scenario.
    Percent cost: clients = required revenue / annual revenue per client. Dollar cost: clients = (goal + fixed overhead) / ((monthly price - monthly cost per client) x 12). Always round up to a whole client. Show the check: clients x annual revenue per client x (1 - cost %) - fixed overhead is at least the goal.
- [ ] 11. Compute the price floor at capacity.
    If the owner gave capacity: monthly price floor = required revenue / capacity / 12, rounded up to the next whole dollar. Dollar cost form: floor = (goal + fixed overhead) / capacity / 12 + monthly cost per client. If any scenario's client count exceeds capacity, flag it: that price cannot reach the goal with the hours the owner has.
- [ ] 12. Check the proposal, if one is given.
    Take the proposal's recurring monthly price. If its scope differs from the base offer (more entities, payroll, a heavier cleanup), ask whether its delivery cost differs, and use that cost for this check. Compare the price to the floor. Verdict "Fits the plan" if price is at or above the floor, "Below the plan" if under. For below the plan, show the monthly and annual gap, the client count if every client were priced at this number, and the profit at capacity at this price. Report one-time fees in the proposal on their own line.
- [ ] 13. Build the PDF.
    Write the payload in the user's working folder, never in this skill folder, named after the report title (for example osher-road-to-100k.json). Follow references/report.md. From the working folder, run `python3 <this skill folder>/references/templates/build_plan.py osher-road-to-100k.json`. The PDF lands beside it with the same name. The engine derives the bars, the floor, the verdict, and the sensitivity tables. Tell the owner the floor, the verdict, and the file. Do not mention the engine, the script, or the skill. Do not paste the plan into chat.
- [ ] 14. Offer the next scenario.
    With the floor, the verdict, and the file, name a few follow-up questions the owner can ask. Draw them from what would move this plan: a higher price, a lower delivery cost, more capacity, or a hire. Then take one change at a time. Rerun steps 9 to 13, rebuild the same file, and say what moved.

## Caveats

- **Ignoring delivery cost in the client count.** Tell: clients = goal / annual price (a $100,000 goal at $6,000 per client gives 17, not 28). Rule: a profit goal always passes through (1 - delivery cost %) first.
- **Profit goal read as revenue, or the reverse.** Tell: the owner said "make $100K" and the plan treats it as revenue, or they said "revenue" and the plan treats it as profit. Rule: infer the basis from the words. A bare number defaults to take-home profit and the plan says so.
- **Rounding clients down.** Tell: 27.78 shown as 27 or "about 28" with no check line. Rule: round clients up, round the price floor up, and show the check line.
- **One-time fees inflating the monthly price.** Tell: a $1,500 onboarding fee spread into the monthly rate to clear the floor. Rule: recurring price alone is compared to the floor. One-time fees are reported, not blended.
- **Invented service mix or cost percent.** Tell: a blended price appears that the owner never gave a split for, or "a typical 40%" fills a blank. Rule: ask. A number that did not come from the owner, their file, or their books is tagged Default or Placeholder in Parameters and Sources, or it is not used. The goal, delivery cost, and capacity are never placeholders.
- **A placeholder passed off as the owner's.** Tell: engine-filled tier prices, a mix, or a hire salary tagged Owner or Derived when the owner never gave them, or a chat message that quotes the Mix bar as the plan without saying its split was filled in. Rule: tag it Placeholder, and name every placeholder in chat as a number to replace.
- **Reading a client's books as the firm's.** Tell: the entity carries a client's name, or the income lines look like a client's sales rather than service fees. Rule: confirm the firm's own entity by name before any read. An owner whose only books are clients' has no firm history; ask instead.
- **Reading the goal off the books.** Tell: the income goal equals last year's net income and the owner never stated it. Rule: the books show the current pace, as context. The goal is the owner's number.
- **Annual or one-time payments read as monthly.** Tell: a client with one $1,200 payment in the window shows as $100 a month. Rule: a billing basis drafted from payment history is a draft. One payment in the window is annual or one-time, and the owner says which.
- **Mixed expense lines counted whole.** Tell: all payroll lands in delivery cost while the owner also pays an admin from it. Rule: a line that may serve both delivery and overhead goes to the owner to split. It is not counted until they do.
- **Cash-basis lag.** Tell: a client signed last month shows no revenue yet. Rule: state the books' basis. On cash basis, ask about clients signed but not yet paid.
- **A checklist opening.** Tell: "Nothing was attached," a numbered list of every input, or "put every answer in one reply." Rule: open with "Let's plan out some projections" and ask only the few gaps in step 4, in a sentence or two.
- **Narrating the work.** Tell: "I'll read the planner skill first," "I'll check the report rules," or "I'll see if your books have prices before I ask." Rule: do that work without saying so. The owner hears the projection, a drafted number, a question still open, and later the floor, the verdict, and the file.
- **One question per turn.** Tell: the owner answers five messages to give five numbers. Rule: those few gaps go out together. Do not save each one for its own message.
- **Talking the owner into the low number.** Tell: the verdict on a below-floor proposal softens to "close enough" or lists reasons the discount is fine. Rule: state the gap plainly. The owner may still choose to send it, but the plan shows what it costs.
- **Speaking for Logan Graf.** Tell: a quote, a named rule, or "Logan recommends" that is not in this file. Rule: do not attribute statements to Logan Graf or Counter. The framework wording is pending his review and approval.
- **Drifting into tax or bookkeeping advice.** Tell: the run starts estimating the owner's income tax or changing ledger data. Rule: the goal is pre-tax. Point tax questions to the owner's tax advisor and stay in firm economics.
- **A hand-styled page.** Tell: a PDF drawn outside the engine, a palette typed into the skill, or a file handed over after a Helvetica warning. Rule: the engine carries the brand. This PDF never passes through theme.py. Never restyle it, swap fonts, or draw outside the engine.

## Example

Anonymized. A solo owner starting a firm. Goal: take home $100,000 a year (owner confirmed profit, not revenue). Bookkeeping at $500 or $1,000 a month. Delivery cost 40% of revenue. No fixed overhead given. Capacity 20 clients. Proposal about to go out: $550 a month plus a $1,200 one-time cleanup.

```
NEW FIRM REVENUE PLAN

Parameters and Sources
| Input              | Value             | Source        |
|--------------------|-------------------|---------------|
| Income goal        | $100,000 / yr     | Owner, profit |
| Delivery cost      | 40% of revenue    | Owner         |
| Fixed overhead     | $0                | Default       |
| Client capacity    | 20                | Owner         |

Required revenue = ($100,000 + $0) / (1 - 0.40) = $166,667

Scenarios
| Price / mo | Revenue / client / yr | Clients needed        | Check (profit)               |
|------------|-----------------------|-----------------------|------------------------------|
| $500       | $6,000                | 27.78 -> 28 (over 20) | 28 x 6,000 x 0.60 = $100,800 |
| $1,000     | $12,000               | 13.89 -> 14           | 14 x 12,000 x 0.60 = $100,800|

At $500 the goal needs 28 clients. Capacity is 20. That price cannot reach the goal.

Price floor at 20 clients = $166,667 / 20 / 12 = $694.44 -> $695 / mo

Proposal check: $550 / mo recurring
Verdict: Below the plan
- Gap to floor: $145 / mo, $1,740 / yr for this client
- If every client paid $550: $166,667 / $6,600 = 25.25 -> 26 clients (6 over capacity)
- Profit at 20 clients at $550: 20 x 6,600 x 0.60 = $79,200 ($20,800 short)
- One-time cleanup $1,200: reported separately, not counted toward the floor

Carry into the proposal: $695 / mo minimum recurring.
Next scenario? Change one input: price, cost %, or capacity.
```

Those figures are what the PDF shows. The page puts the tier chart first, then the summary and verdict, then the sensitivity tables in references/report.md. Chat does not repeat this block.

When the firm's own books are connected, the same opening puts the drafted inputs under the first line. Anonymized. A solo firm eight months in, books on cash basis.

```
Let's plan out some projections. From your books (Feb to Sep 2026, cash basis, 8 full months):
| Input             | Value                                     | Source               |
|-------------------|-------------------------------------------|----------------------|
| Recurring clients | 9: six at $500 / mo, three at $750 / mo   | Books, Sep 2026      |
| Delivery cost     | 40% ($14,400 of $36,000 revenue)          | Books, Feb-Sep 2026  |
| Fixed overhead    | $6,000 / yr ($4,000 / 8 x 12)             | Books, annualized    |
| Current pace      | $17,600 net income in 8 months (context)  | Books, Feb-Sep 2026  |

Delivery cost lines: contractor $12,000, client software $2,400.
Overhead lines: insurance, base software, marketing.

What do you want to take home this year? How many clients can you serve at once? Client A paid $1,200 once in March. Was that an annual fee or a one-time cleanup?
```

With no file and no books, the same opening is just the questions:

```
Let's plan out some projections.

What do you want to make this year? What are you charging, and what does it cost you to deliver the work?
```

## Completion

Done when:
- The owner's data was checked first (attachments, then the firm's own connected books). A draft is shown. A miss is not announced. Chat does not mention the skill, the engine, or the search.
- The opening asks only for a gap the owner's words do not already settle.
- The goal basis is inferred from their words, or a bare number is defaulted to take-home profit and the plan says so. The period is recorded.
- Every input is in the table with a source of Books, File, Owner, Default, or Placeholder, and every Books or File figure shows its period.
- Required revenue shows its formula.
- Each price scenario shows clients needed, rounded up, with a check line that meets the goal.
- The price floor is shown when capacity was given, rounded up to a whole dollar.
- Every scenario over capacity is flagged.
- A given proposal has a verdict of Fits the plan or Below the plan, and below-plan verdicts show the gap.
- One-time fees appear on their own line and never in the floor comparison.
- The PDF was written by references/templates/build_plan.py into the user's working folder, named after the report title, and the build log has no Inter warning. Nothing was written inside the skill folder.
- The page leads with the tier chart: soft horizontal bars, the mix as the last bar, and a dotted capacity line. The sensitivity tables that apply follow, then Parameters and Sources.
- Client mix always appears, margin appears on a profit goal, and hiring appears on a profit goal with capacity. Engine-filled services and hires are tagged Placeholder.
- The chart has tiers even when the owner gave one price: the owner's, or the Bronze, Silver, Gold ladder. With two or more tiers it ends with a Mix bar that reaches the goal at capacity whenever any mix can.
- Every placeholder is tagged Placeholder on the page and named in chat.
- No figure is attributed to Logan Graf or Counter, no tax estimate was made, and nothing in the books was changed.
- The handoff names the floor, the verdict, the file, and a few follow-up questions the owner can ask.

Cleanup: Hand over the PDF's path with the floor and the verdict, and name a few follow-up questions the owner can ask. Do not paste the plan into chat. Open inputs (unconfirmed overhead, unknown capacity, unknown service mix, an unsplit expense line, an unclear billing basis, a placeholder) are listed in the notes under Parameters and Sources. Feedback on the framework wording goes to the Kick engineer for Logan Graf's review.
