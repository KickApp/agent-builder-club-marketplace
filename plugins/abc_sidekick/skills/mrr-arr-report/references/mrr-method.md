# MRR method

The rules behind every figure in the report. `scripts/mrr_build.py` implements them; the
report's "How I counted" line restates the ones that matter in plain words. The report is
a management metric, not GAAP revenue. Nothing is converted between currencies.

## Data scan

What the scan must establish. Calls live in `references/kick.md`. Without Kick, the same rows come from the user's export or spreadsheet (`references/other-sources.md`), and the rows of this table that need Kick (schedules, candidates, native invoices) are skipped.

| Question | Read |
|---|---|
| Which income accounts exist and how big are they | Chart of accounts; P&L for the window, monthly |
| Revenue per customer per month | P&L with customer breakdown, monthly, on the chosen ledger |
| What each customer pays for, and how often | Line descriptions: general ledger detail (`account_transactions`) for the revenue accounts, invoice lines, schedule policy names |
| What sits inside a mixed account | Account transactions for the chosen income accounts |
| Who pays and when | Cash-ledger revenue by customer; incoming deposits by counterparty when there's no cash ledger revenue |
| Do schedules exist and who they cover | Revenue policies; recognition waterfall grouped by customer (Advanced) |
| What should be on a schedule but isn't | Revenue recognition candidates (Advanced) |
| Does the entity invoice in Kick | Native invoice stats |
| How clean is the customer list | Counterparty search for likely duplicates among revenue customers |

Save the per-customer revenue rows as CSV (`customer`, `month` or `date`, `amount`,
optional `account`, `currency`, `description`, and `cadence` = `schedule` for scheduled
customers) and run:

```
python3 scripts/mrr_build.py scan --input revenue_rows.csv --currency USD --out scan.json
```

`description` is the line's bank description, invoice line, or schedule policy name. The
scan reads billing words in it (monthly, quarterly, annual, yearly, one-time, setup) and
marks those customers `described`, so they are never asked. It also keeps up to three
sample descriptions per customer: read them to name each customer's plan ("Basic annual"
is plan Basic, billed yearly) for the `plan` column.

The scan output gives the billing cycle per customer and how it was found, the questions
worth asking (similar unclear customers grouped, top 3 groups by revenue), the unclear
customers not asked, each account's repeat-customer share and default, likely duplicate
pairs, revenue with no customer, and other currencies.

## Defaults, decided without asking

Apply these silently, state them in one plain "How I counted" line, and change one only
when the user asks or the data clearly calls for it.

| Decision | Default |
|---|---|
| Where MRR comes from | Kick: best available for the plan (`references/kick.md`, Plan support). Otherwise: what the user sent, billing records over accounting over bank (`references/other-sources.md`) |
| Which revenue is recurring | Income accounts whose names suggest subscriptions, plus any account where 80 percent or more of revenue comes from repeat customers. If that leaves no revenue at all, use every revenue account and say so |
| Multi-month payments | Spread across the term (a $1,200 yearly payment is $100 a month for 12 months) when the term is known from a schedule, a description, the payment pattern, or the user |
| Minimum history | 2 months in a row, for customers with no known billing cycle |
| Churn | A customer with no revenue for a full month churns. Yearly and quarterly payers stay active until their term ends |
| Period | The last 12 full months, or since the first month with revenue if that's shorter. The script starts there by itself when `--months` isn't given, so no empty leading months appear in the trend, movements, or bridge. Monthly, or quarterly in the board shape |
| Names that differ only by case or spacing | Merged into one customer ("ACME CORP" and "Acme Corp"); listed in `merged_names` and mentioned in "How I counted". Punctuation, legal-suffix, and fuzzy pairs stay separate as duplicate candidates |
| Stopped or reversed schedules | Run-rate instead of the booked amount (rule C9); asked about only when the effect is 10 percent or more of the month's MRR |
| Current month | Left out. When it changes the picture (a new customer worth 10 percent or more of MRR), mention it and offer a month-to-date preview |
| Breakdown | By plan when descriptions, subscriptions, or schedules name plans; by class when Kick classes are set up (Plus and up); otherwise none |
| Currency | The primary currency; others listed apart, never converted |
| Likely duplicates | Kept separate and mentioned in what's missing, unless the user says to combine them |

"By entity" means one report per entity, run one after the other. The skill never adds
entities into one total.

## What's worth asking

Ask only what the books can't answer and the user can. At most two questions in a
message, in business words, each with what you'll assume if they don't know.

| Question | Ask when | If they don't know |
|---|---|---|
| What the report is for: a quick read, a board or investor update, running the business, or cleaning up the books | The request doesn't make it clear. "For the board" or "how much did we churn" already does | Quick read, then offer the others |
| How an unclear customer pays | The scan's `questions` list it: one payment or irregular payments, and no description says the cycle. Ask grouped customers together ("these 8 customers each paid $480 once") | Count it when paid, and say so |
| Whether a mixed account is recurring | An account holds 20 to 80 percent repeat-customer revenue and would move MRR by 10 percent or more | Leave it out and size it in what's missing |
| Whether two names are one customer | A likely duplicate pair would create a false churn and new customer in the trend | Keep them separate and mention the pair |

- A1. Ask the most important question first: purpose, then the data question that moves
  MRR most. Anything else waits until it matters, or goes in what's missing.
- A2. Never ask about a customer with a schedule or a described billing cycle, or one
  whose payments show a clear pattern.
- A3. A follow-up question is fine when an answer opens a new one. Keep each message short.
- A4. Answers hold for this conversation only and appear in "How I counted". Within it,
  the report's purpose carries across sources (a board update stays a board update when
  the user adds a second file or a Google Sheet); data answers (a customer's billing
  cycle, a duplicate pair) apply only to the data they were asked about.
- A5. The same rules apply on every plan and every source. For outside users, the one ask
  for their data (`references/other-sources.md`) comes first and counts as the first message's
  question.

## Calculation rules

- C1. Monthly recurring amount per customer: revenue in the chosen accounts for that
  month. With "spread", an amount paid for an N-month term counts as amount / N in each
  month of the term (cents rounded, remainder in the last month). Terms come from
  schedules first, then from descriptions, then from detected cadence, then from the
  user's answers.
- C2. Cadence detection (customers without a schedule or description): roughly the same amount every
  month is monthly, every 3 months is quarterly, every 12 months plus or minus 1 is
  annual. "Roughly the same" means every payment within 10 percent of the median. "At
  least 2 full cycles" means at least 2 payments at that interval, so a 13-month window can
  detect annual. Anything else is unclear and may be worth asking. Each customer's cadence
  is labeled schedule, described, detected, confirmed (by the user), or unconfirmed. These
  labels are internal: in chat and files, say "from the schedule", "the invoice says
  yearly", "from the payment pattern", "you confirmed", or "counted when paid".
- C3. Movements per month: new (no recurring revenue in any prior month), expansion,
  contraction, churn (per the churn rule), reactivation (had revenue, churned, now back).
- C4. Bridge check: opening MRR + new + expansion + reactivation - contraction - churn =
  closing MRR. The script fails with exit code 2 and writes nothing when it doesn't tie.
- C5. ARR = MRR of the reported month x 12. Never a sum of the year.
- C6. NRR and GRR over 12 months for the customers with MRR 12 months before the end
  month. NRR = their MRR now / their MRR then. GRR caps each customer at their starting
  MRR. State the cohort size. Needs 13 months of data.
- C7. ARPA = MRR / active customers in the month.
- C8. Every figure in the report comes from tool reads or from the script's output on
  those reads. The model does no arithmetic of its own.
- C9. Stopped and reversed schedules. A schedule that stops early recognizes the rest at
  once, which looks like expansion; a go-live or true-up reversal makes a month
  negative, which looks like churn. The script detects an acceleration month (a schedule
  customer's last positive month at `--accel-multiple` times the prior month, default 3)
  and a reversal month (a negative month whose description says reversal, go-live,
  true-up, or catch-up, or a schedule customer's negative month followed by revenue) and
  uses the prior month's amount for it. Each is listed in `schedule_adjustments` with
  the booked and used amounts; `needs_question` is true when the effect reaches
  `--ask-share` (10 percent) of the month's MRR, and only then is the user asked.
  `--adjust no` keeps the booked amounts. Genuine refunds keep the negative-month rule.

Data-quality figures the script adds to the JSON:

- `coverage`: the share of revenue in the window with a customer (`assigned_pct`), the
  total with none, and the source mix (schedule, billing, ledger, cash) with each
  source's customers and MRR share.
- `data_quality`: the gate. It fires when the entity or workspace name, or customer or
  policy names, read like test or QA data (`test`, `testing`, `QA`, `dummy`; the names
  are listed in `test_names`), when coverage is below `--min-coverage` (80 percent), or
  when most revenue has no customer. When it fires, the first look leads with it and
  asks once whether to continue and how to treat the unassigned revenue; every board or
  investor shape carries a data-quality line; the dashboard shows a "Test or incomplete
  data" banner. Never build a polished report silently on failing data.
- When no row has a customer at all, `build` writes the JSON with `summary: null` and
  `excluded.no_customer` sized, and exits with code 3. Report the sizing and ask one
  question; don't build an all-zero report.

Details the script applies:

- Minimum history applies only to customers with no schedule, no multi-month
  term, and no confirmed or unconfirmed label. A customer still running at the end month
  but too young to pass it is counted and listed as `new_not_yet_confirmed`.
- Churn rule: with "after a 2-month grace period" (`--churn-after-months 2`), a one-month
  gap followed by revenue is filled with the prior month's MRR. A gap at the end of the
  window inside the grace period is held and listed as `in_grace`.
- Annual payers stay active until term end. When the user chose "count in the month
  booked", the drop after the booked month is contraction, not churn.
- A negative customer month (refunds above revenue) counts as zero and is listed under
  `excluded.negative_months`.
- KPIs: logo churn = churned customers / opening customers. Gross MRR churn = (churn +
  contraction) / opening MRR. Net MRR churn = (churn + contraction - expansion) / opening
  MRR. Quick ratio = (new + expansion + reactivation) / (contraction + churn).
- Cohorts: customers grouped by the quarter of their first active month (customers active
  in the first month of data are left out, since their start is unknown). Each column is
  the share of starting MRR still there N months after each customer's start, shown only
  when every customer in the cohort has reached month N. Needs 9 months of history, and
  cohorts under 5 customers are left out (`--cohort-min-customers`).
- Retention under 10 customers is flagged `small_sample`. Mention it as context, never as
  a headline.
- Next renewal per active customer: the schedule's term end, or else the month the last
  multi-month payment runs out (a yearly payment in March 2026 renews March 2027).
  Monthly payers have none. Renewals lists those due within 60 days of the read date.
- When the end month is the current month, `meta.end_partial` is true and
  `meta.end_label` reads "Oct 2026 (to Oct 8)". Use that label everywhere.

## Build input contract

One row per booked amount, after applying the user's choices (accounts, combined
duplicates, answers). Columns:

| Column | Required | Meaning |
|---|---|---|
| `customer` | yes | Customer name as the source shows it; blank means no customer (excluded and sized) |
| `month` | yes | `YYYY-MM` the amount was booked or recognized |
| `amount` | yes | Amount in that currency |
| `term_months` | no | Months the amount covers (12 annual, 3 quarterly; default 1) |
| `cadence` | no | `schedule`, `described`, `detected`, `confirmed`, `unconfirmed`, or `one_time` (excluded) |
| `source` | no | `schedule`, `ledger`, `cash`, `invoice`, or `billing` (a billing system such as Stripe) |
| `plan` | no | Plan or product name from descriptions, policy names, or the user ("Basic", "Plus") |
| `class` | no | Kick class name (Plus and up); not used for other sources |
| `currency` | no | Default is the primary currency; others are listed apart |
| `term_end` | no | `YYYY-MM-DD` schedule end, for renewals |
| `report_as` | no | Customer name to report under, when the user said two customers are one |
| `description` | no | The line's text; used to spot payouts and C9 reversals |

For schedule customers, feed the recognized amount per month with `term_months` 1 and
`term_end` set. In Sheets mode, `scripts/sheet_sources.py rows` writes this file from
the chosen tabs. Run:

```
python3 scripts/mrr_build.py build --input grid_rows.csv --end-month 2026-09 \
  --as-of 2026-10-08 --currency USD --spread yes --min-history 2 --churn-after-months 1 \
  [--entity-name "Acme Inc"] [--adjust yes] [--collected deposits.csv] \
  [--money-in money_in.csv] --out-dir out
```

Exit codes: 0 built; 2 the bridge didn't tie (nothing written); 3 no row has a customer
(JSON written with `summary: null`).

`--collected` (customer, month, amount) adds the booked versus collected gap. `--money-in`
(month, total_in, uncategorized_in) flags months that look unclosed. Every threshold is a
flag; `--help` lists defaults. Outputs: `mrr_report.json`, `customer_detail.csv`,
`movements.csv`, `trend.csv`.

`customer_detail.csv` is the file offered to the user: one row per customer with Customer,
Plan, Class, Billing, Started, Last billed, Next renewal, MRR for each month, Status (New,
Upgraded, Downgraded, Churned, Came back, Active, or "Churned in <month>"), and the change
vs the prior month, plus a Total row. Columns that are blank for every customer are left
out. `mrr_report.json` has the same rows under `customers`.

## Report shapes

Every shape starts the same way:

1. Headline: MRR, ARR, active customers, change vs the prior month (`summary`).
2. "How I counted", one or two plain sentences: where the numbers come from, how
   multi-month payments count, the user's answers, anything left out that matters, and
   "a management metric, not GAAP revenue". Basic and bank files add that MRR follows when
   customers paid. Outside Kick, name the file and its date range.

And ends the same way:

- What stands out: two or three insights, most useful first.
- What's missing: only the gaps that change the numbers or the user's next step, each
  with a size and one next step. Minor ones go in a single closing line or the CSV.
- An offer of two or three next steps (SKILL.md step 6).
- A method note, only when a call worked differently than `references/kick.md` says.

In between, by purpose:

| Purpose | Body | Leave out |
|---|---|---|
| Quick read | The last 6 months' trend, the latest month's movements in a sentence or a small table | KPI ratios, cohorts, the full bridge |
| Board or investor update | KPI scorecard, quarterly ARR bridge, 12-month NRR and GRR (only without `small_sample`), concentration, trend chart | Customer names beyond the biggest movers |
| Running the business | Latest month bridge with names, every active customer when there are 25 or fewer (else the top 10), MRR by plan, renewals coming up, customers at risk (downgraded, or late on a yearly or quarterly renewal) | Ratios like quick ratio, cohorts |
| Cleaning up the books | What's missing first and in full, the source mix, booked vs collected, customers counted when paid, likely duplicates; then the headline numbers | Narrative insights |

If the user asks for a specific view ("show me churn", "just the ARR bridge"), give that
view and skip the shape.

The views read the same build JSON, so they always agree: KPI scorecard (`summary`,
`kpis`, `retention`), monthly movement waterfall (`movements`), quarterly ARR bridge
(`arr_bridge_quarterly`), customer view (`customers`, `customer_detail.csv`), MRR by plan
or class (`plans`, `classes`), cohort retention (`cohorts`), renewals (`renewals`), trend
chart (Mermaid `xychart-beta` from `trend`). Layouts are in `references/examples.md`.

### Insights

- I1. MRR trend and month-over-month growth.
- I2. Movement drivers for the latest month, with the top customers behind each movement.
- I3. Concentration: share of MRR from the top customer and the top 10.
- I4. Renewals coming up: customers due in the next 60 days (from schedules, or from when
  a yearly or quarterly payment runs out), with their MRR.
- I5. Booked versus collected gap for the window, when both sources were read.
- I6. Seasonality or a trend break, only with at least 12 months of data, with the
  script's confidence note.
- I7. Plan mix: when ARPA moves, say which plans new and lost customers were on (`plans`).
- I8. Dependence on one customer: say it plainly when one customer is 25 percent or more
  of MRR.

Pick the two or three that matter most for this business and purpose. An insight says
what happened, why (named customers or plans), and what it means, in one or two
sentences. "Average revenue per customer fell from $91 to $68 because every new customer
since January chose Basic ($40) over Plus ($100)" beats "ARPA decreased 26%".

### Gaps

Each gap has a size (count and amount) and one concrete next step.

Fixable in the books:

- G1. Incoming deposits with no counterparty in the window (`excluded.no_customer`).
- G2. Income accounts that mix recurring and one-time revenue (repeat-customer share
  between 20 and 80 percent), with how much MRR they could add.
- G3. Likely duplicate customers that split one customer's MRR.
- G4. Revenue recognition candidates with no schedule (Advanced): annual invoices or
  payments counted when booked instead of spread.
- G5. Months that look unclosed: an unusually high share of uncategorized money in
  (`unclosed_months`). Not in GL-first workspaces, where the category field is unused.
- G9. Accrual books far behind cash (Advanced and Plus): accrual revenue well below cash
  revenue for the window, draft schedules, or payments with no schedule. Size it as the
  two totals and the count of drafts, and say which source the report used instead.
- G10. Stale source: a ledger or report whose lines stop before its header's end date,
  or a source that doesn't cover the requested window. Size it as the missing months
  and say exactly which report, basis, entity, and dates to pull again.
- G11. Sources that don't agree: Waterfall totals against the P&L revenue line, ledger
  lines against the account's balance change, Rollforward recognized against the
  Waterfall. Size the difference and name the source the report used.
- G12. Schedule months adjusted under C9 (`schedule_adjustments`), with the booked and
  used amounts, and processor payouts left out (`excluded.payouts`).

Outside the user's control today:

- G6. Plan limits from the plan support table, mentioned once as a fact.
- G7. Kick has no plan, interval, or cancel-date data for subscriptions billed outside
  Kick, and cannot read Stripe, QuickBooks, or imported invoices, so churn timing follows
  when revenue stops. Outside Kick, G7 is what the user's file doesn't include, and G4,
  G5, G6, and G9 don't apply (`references/other-sources.md`).
- G8. Other currencies left out of the totals (`excluded.other_currency`).

Also listed when present: unconfirmed customers (`unconfirmed`), unclear customers not
asked (scan `unclear_not_asked`), one-time revenue excluded, customers below the minimum
history, negative months.

## Dashboard contract

Used when the user picks the dashboard file (the live Google Sheet has its
own contract in `references/google-sheets.md`). One self-contained HTML page built by
`scripts/build_dashboard.py` from `mrr_report.json`, injected into
`references/templates/dashboard.html`.

```
python3 scripts/build_dashboard.py --report out/mrr_report.json --entity "<entity>" \
  --plan Advanced --definitions "<chosen definitions in words>" --gaps gaps.json \
  --generated <read date> --out-dir <where the surface saves files>
```

Sections, top to bottom. A section whose data is missing is left out, not shown empty.

| Section | Shows | Needs |
|---|---|---|
| Header | Entity, period, generated date, currency, source and definitions line | Always |
| Hero tiles | MRR, ARR, net new MRR, net revenue retention, each with its change | Always (retention needs 12 months) |
| KPI strip | Customers, ARPA, logo churn, gross revenue retention, quick ratio | Always |
| MRR by month | Bar chart, latest month highlighted | Always |
| Latest month bridge | Waterfall from opening to closing MRR | Always |
| Movements by month | Stacked bars, gains above zero, losses below, net labeled | 2+ months |
| MRR by plan | Donut plus table (MRR, share, ARPA) | Plans named in the rows, or classes (Plus and up) |
| Customers | Every active customer when there are 25 or fewer, else the top 5, with plan, share bars, latest movement, and a note when one customer is 25 percent or more of MRR | Always |
| Cohort retention | Heatmap by start quarter | 3+ quarters, cohorts of 5+ customers |
| Up for renewal | Customers due in the next 60 days | Schedules or multi-month billing |
| What's missing | The sized gaps from the report | Always |
| Footer | "Every figure comes from Kick data read on <date>. Snapshot, not live." plus definitions | Always |

- DB1. Only the build script writes figures into the page. Gap amounts come from the build
  JSON (`from` keys) or are copied unchanged from a Kick read.
- DB2. One self-contained file: inline CSS, inline SVG, no external scripts, fonts, or
  network calls. It opens offline and survives email.
- DB3. File name `<entity>-mrr-dashboard-<YYYY-MM>.html`, written where the surface saves
  files.
- DB4. Metrics only on the page. Insights and narrative stay in the chat message.
- DB5. Labeled as a snapshot with its generated date. It never claims to be live.
- DB6. Customer names are escaped in the payload and when rendered.
- DB7. If the surface can't write files, say so and give the KPI scorecard and Mermaid
  trend chart in chat instead.
- DB8. The template's look is used as is. No firm branding.
