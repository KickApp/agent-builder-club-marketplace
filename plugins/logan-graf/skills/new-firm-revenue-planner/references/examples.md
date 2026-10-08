# Good and bad runs

Each bad case names the failure and the rule in SKILL.md that prevents it.

## Bad: goal read off the books

```
Income goal: $26,400 / yr (Books)
```

The owner never stated a goal; the run used the annualized net income. The books show the
current pace, as context. The goal is the owner's number (Caveats: reading the goal off the
books).

## Bad: a client's books read as the firm's

```
From your books (Harbor Bakery LLC): revenue $410,000, 1,900 customers
```

The user sees client workspaces; this one is a bakery's sales. Confirm the firm's own
entity by name before any read. An owner whose only books are clients' has no firm history
(Caveats: reading a client's books as the firm's).

## Bad: annual fee read as monthly

```
| Client A | $100 / mo | Books |
```

Client A paid $1,200 once. One payment in the window is annual or one-time, and the owner
says which (Caveats: annual or one-time payments read as monthly).

## Bad: narrating the work

```
I'll build a one-page revenue plan from your income goal, price, cost, and capacity.
Reading the planner skill first so the figures come from its engine.
Your numbers are enough to start. I'll check the report rules and whether your
books already have prices or costs before I ask for anything else.
```

The owner hears the agent's process. Do the reading silently. Open with the
projection, or with the drafted numbers (Caveats: narrating the work).

## Bad: a checklist opening

```
No file was attached, and Kick is not connected.
To finish the plan, put every input in one reply:
1. Income goal
2. Prices
3. Delivery cost
4. Overhead
5. Capacity
6. Service mix
7. Proposal
```

The miss is announced, and every input is listed. Open with "Let's plan out some
projections" and ask only the few gaps in step 4 (Caveats: a checklist opening).

## Bad: one question per turn

```
What's your income goal?
```

followed by four more single-question turns. The few gaps go out together (Caveats: one
question per turn).

## Bad: one-time fee blended to clear the floor

```
Proposal: $550 / mo + $1,200 cleanup = $650 / mo effective. Fits the plan.
```

Recurring price alone is compared to the floor. The $1,200 is reported on its own line, and
the verdict is Below the plan (Caveats: one-time fees inflating the monthly price).

## Bad: clients rounded down

```
$500 / mo: about 27 clients
```

27.78 rounds up to 28, with a check line showing 28 x 6,000 x 0.60 = $100,800 meets the
goal (Caveats: rounding clients down).

## Good: the report

The plan is a PDF from references/templates/build_plan.py, titled "<owner>'s Road to
<goal>" and saved in the user's working folder under the same name (for example
osher-road-to-100k.pdf). The tier chart comes first: one soft bar per price, the mix as the last bar, a
dotted line at capacity. Under it sit the floor and the verdict, then client mix, margin,
and hiring where they apply, then Parameters and Sources. Chat is the floor, the verdict,
the placeholders to replace, and the file path.

## Good: one price still gets tiers

The owner wants $100,000, charges $4,000 a year, pays $700 a year per client, and serves
25. They gave one price and never mentioned tiers. The payload carries `current_price`
and no `tiers`, and the engine builds the ladder:

```
| Bronze tier | $4,000 / yr | Owner, current price                       |
| Silver tier | $400 / mo   | Placeholder, floor rounded up to the next $100 |
| Gold tier   | $800 / mo   | Placeholder, premium at twice Silver           |
| Tier mix    | 10 Bronze / 10 Silver / 5 Gold | Placeholder, 40/40/20 split of capacity |
```

Bronze needs 31 clients, 6 over capacity. Silver needs 25. Gold needs 12. The mix needs
22 and makes $118,500 with all 25. Client mix (Tax $2,000 a year, Books $333 a month, Both
$500 a month) and hiring (part-time adds 13, full-time adds 25) appear with placeholder
numbers. Chat gives the $392 floor and names Silver, Gold, the mix, the services, and the
hires as placeholders to replace with the owner's real numbers.

## Bad: one price, one bar

```
tiers: [{"name": "Annual engagement", "billing": "annual", "price": 4000}]
```

A single owner price passed as the only tier gives a one-bar chart. Pass it as
`current_price` and leave `tiers` out (Procedure step 6).

## Bad: a placeholder tagged as the owner's

```
| Tier mix | 10 Bronze / 10 Silver / 5 Gold | Owner |
```

The owner never gave a mix; the engine filled it. Leave `mix` out of the payload so the
engine tags it Placeholder, and name it in chat as a number to replace (Caveats: a
placeholder passed off as the owner's).

## Bad: a hand-styled page

```
Drew the plan in HTML and ran theme.py, with a blue header added in the skill.
```

The engine carries the brand and writes the PDF. It never passes through theme.py
(Caveats: a hand-styled page).
