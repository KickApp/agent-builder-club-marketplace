# Revenue finder: examples

Anonymized and illustrative. Never quote these figures or sentences as live data.

## A bad run

```markdown
# Revenue finder: Harbor Fabrication

Ping found 11 high-confidence opportunities:
1. Payroll (high confidence): client discussed payroll on 3 calls.
2. Tax planning (high confidence): "we had a good year" and "maybe we should look at the
   S-Corp thing, like you said" (Q2 call).
3. Cash flow forecasting (high confidence): cash is $17,250, under one month of expenses.
4. Sales tax (high confidence): Dana said "we need help with payroll and sales tax".
...
```

What is wrong:

- Eleven findings, and the tool's confidence rating doing the ranking. The cap is five
  and the rating is ignored.
- Payroll has no quote. "Discussed payroll" is a keyword match, cut one.
- Tax planning stitches two moments, and "like you said" means the firm raised it. Cut
  two. Agreement to a pitch is not a stated need.
- Cash flow forecasting has only a ledger figure. It belongs under From the books as a
  question, never ranked.
- One sentence serves payroll and sales tax. Cut three: evidence for neither.
- No coverage line, so the five calls with no transcript go unmentioned.

## A good run

```markdown
# Revenue finder: Harbor Fabrication (Nov 1st, 2025 to Oct 31st, 2026)

Result: 2 opportunities found, from 14 possibilities reviewed. Top finding: Payroll, named the need. Highest value:
Cash flow forecasting, about $4,800 a year.
Coverage: read 6 transcripts, 41 emails, 4 notes. 3 calendar meetings not read.
Ledger: Kick, accrual basis.

## Payroll · $3,600 a year · Named the need
> "Honestly I need someone to just take payroll off my plate before we hire the two welders."
> Dana Ruiz (owner), Call: August check-in, Aug 14th, 2026
Why: she asks for payroll processing, with new hires coming.
Books: Corroborated. Contractor labor $6,200 a month in Q1, $11,900 in Q3 (profit and
loss, monthly); no payroll provider paid.
Next: ask when the welders start and who runs payroll today.

## Cash flow forecasting · $4,800 a year · Described the situation
> "Every time a big job pays late I'm scrambling to make the supplier run."
> Dana Ruiz (owner), Email: Re: October close, Oct 9th, 2026
Why: late payments squeeze the supplier run, the shortfall forecasting projects.
Books: Corroborated. Receivables $61,300 at Oct 31st, 2026 against $38,500 average monthly
revenue (balance sheet; profit and loss, monthly).
Next: offer a 13-week cash view before the November supplier run.

## From the books: questions to ask
| Signal | Figure | Source | Question to ask |
| Sales tax payable growing | $4,120 at Oct 31st, 2026, $1,050 at Nov 1st, 2025 | Balance sheet | Are you collecting in a new state? |

## Raised before
| Service | Status | Date | Detail |
| Tax planning | Declined | Apr 2nd, 2026 | Firm proposed an S-Corp review; Dana declined until next year. |

## What I could not see
3 calendar meetings with no transcript (Jan 12th, 2026, Mar 18th, 2026, Jun 30th, 2026).
```

Why the late-payment quote went to cash flow forecasting and not AP and AR: her problem
is making the supplier run, not chasing the customer. Had she said "I can't get
customers to pay", it would go to AP and AR. The reasoning stays out of the report; the
Why line carries only the fit.

Chat handoff for the same run:

```markdown
2 opportunities found for Harbor Fabrication (Nov 2025 to Oct 2026), from 14 possibilities reviewed. Top finding:
Payroll, "I need someone to just take payroll off my plate" (Dana Ruiz, call, Aug 14th, 2026).
Could not read 3 calendar meetings. A discussion prompt, not a proposal.
File: harbor-fabrication-revenue-finder.pdf
```
