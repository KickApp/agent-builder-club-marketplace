---
name: rank
description: Ranks an accounting firm's clients by estimated direct delivery margin (fee minus hours times the firm's cost rate), shows the math, books condition, and Kick volume beside each row, and names where the numbers disagree with the owner's grades. Use when the owner asks which clients make or lose money, which are below target margin, or which are more headache than they are worth, or when /quanto reaches the ranking. Never invents fees, hours, or rates.
argument-hint: "[period]"
---

# Rank

## Summary

The first output and the headline of the page: every client ranked by what it earns the firm
after the labor to serve it, the owner's grade beside every number, and one line for each
place the numbers and the grade disagree. Hours are actual when a time source exists and the
owner's range when not, and a client is called thin or negative only when the whole range
says so. Kick volume and books condition sit beside the estimate so the owner can see whether
their hours feel right.

## Inputs

The client cards and the `Firm` note from the conversation. Without them, ask for the
evidence step by name. A standalone question ("which clients lose me money?") with no cards:
ask the owner for the minimum in one message, fee and rough hours range per client and the
cost rate, then run on that alone and say so.

## How the estimate works

```
fees            = fee for the months served (source on the card)
hours           = actual for the period, or the owner's low and high per month x months served
cost            = hours x cost rate
margin          = fees - cost
margin %        = margin / fees               (fees 0: not applicable)
realized $/hr   = fees / hours                (hours 0: not applicable)
```

- The cost rate is the owner's loaded cost per hour and is never suggested. A salary and
  weekly hours become a rate with the operands shown (48 weeks, stated).
- Months served come from the card's Fee line. When the owner gave a "since" month, served
  months run from that month through the end of the period, both inclusive.
- Estimated hours are computed twice, at the low and the high end of the owner's range. The
  table shows the range and the margin at both ends. Actual hours are one figure.
- No formula turns Kick transactions into hours. Kick volume, review backlog, and books
  condition are shown beside the hours so the owner can judge the estimate. When a range
  looks out of line with the volume (5 hours a month for 340 transactions and a fifth
  awaiting review, next to 5 hours for 90 clean transactions), say so in one line and ask;
  never adjust the number. Without Kick, name instead the one or two ranges most worth a
  month of tracking.

Verdicts, from the threshold in the `Firm` note (20% unless the owner set one):

- Negative: margin below zero at both ends of the range. Thin: between zero and the
  threshold at both ends. Healthy: above the threshold at both ends.
- A range that crosses a line gets "depends on hours; worth a month of tracking" instead of
  a verdict, and the line names which end lands where.
- Rows with actual hours get the verdict outright.

## Workflow

1. Confirm the cost rate exists. None: ask once, in one line, offering the salary-and-hours
   route. Declined: rank by fee and realized rate per hour, "cost rate pending" in the
   margin columns.
2. For each card, take fees, hours (actual or range), months served, Kick volume, books
   condition, and the owner's grade. A card missing fees or hours goes to the bottom,
   unranked, with the missing input named.
3. Compute the table. Round estimated hours to the nearest 5 for the period first, compute
   cost and margin from the rounded hours so every row's arithmetic reproduces, and rank by
   margin percent at the midpoint of the rounded range (or the actual figure), highest
   first. Percentages and dollars per hour print as whole numbers; ranges print the low-hours
   end first. Keep exact operands in the math lines.
4. Write the disagreements first: every clone or keep that is negative or thin at both ends,
   every fire that is healthy at both ends, and every row that depends on hours. One line
   each, naming the driver from the card: pricing (fee low for the effort or volume), scope
   (unbilled work), books condition (messy books eating hours), delivery friction (chased
   documents, repeated questions), fee age (not raised in 18 months or more), or fit
   (disputes, slow payment, slow decisions). Cite the card line. Grades the numbers agree
   with get one short line each under a separate heading, "Where they agree".
5. Write the math for every flagged row and for the top and bottom three, one line each.
6. Deliver the section. Under the router, hand off to profile in the same turn; standalone,
   say "Next: your ideal client, if you want it" and stop.

## Degradation

| Missing | What happens |
| --- | --- |
| Cost rate | Fee and realized rate per hour; "cost rate pending" in the margin columns |
| Hours for some clients | Those rows unranked at the bottom, "hours unknown" |
| Fees for some clients | Those rows unranked, "fee unknown" |
| Kick | Volume column blank; books condition from notes and owner only |
| Fewer than three clients with fees and hours | One short scorecard per client, no ranking |
| Every row depends on hours | The table still ships; the page says a month of time tracking is the next step |

## When to ask vs proceed

Draft first. Deliver with every assumption labeled and invite correction at the end. The
only question before delivery is the cost rate, once. Range-versus-volume mismatches are
raised as one line in the section, not as a blocking question.

## Completion criteria

- [ ] Every client has a row whose Verdict column reads healthy, thin, negative, "depends on hours", or a named missing input
- [ ] Every figure traces to a card line or the confirmed rate; math lines show operands
- [ ] Every disagreement with an owner grade has a driver and a cited source
- [ ] Books condition and Kick volume appear beside every estimated row
- [ ] The section ends with "Estimate. Hours are yours unless marked actual. Review with your partners before client conversations."

## Guardrails

- Figures from the cards, never from memory or from a note. A number the cards cannot
  support is "unknown", not an estimate.
- Call it estimated direct delivery margin. It is labor only unless the owner's cost rate
  demonstrably includes overhead, and then say what it includes.
- Assumptions (period, threshold, months served) are printed once in the section header.
- No external benchmarks or industry averages.
- Client names appear in the firm-internal version only. An anonymized version (Client A,
  B, C by fee, disagreements section dropped) is produced only when the owner asks for
  something to share outside the firm.
- No authoritative pricing, tax, or firing advice; findings are questions for the partners.

## Deliverable

Voice, for every document this skill writes: a careful accountant's prose, not an
assistant's. Short declarative sentences with varied length, sentence-case headings,
concrete nouns and real figures. Banned tells: em dashes; filler words (delve, robust,
seamless, leverage, comprehensive, crucial); the "not just X, but Y" construction; AI
boilerplate ("It's important to note", "In conclusion", "I hope this helps"); decorative
emoji; bolded keyword openers in prose. Read a sentence back; if no accountant would say
it aloud to a client, rewrite it.

```markdown
# Your clients, ranked: <firm>, <period>
Confidential, firm internal use only. Estimate: hours are your figures unless marked actual;
cost rate $<n>/hr (yours); thin below <n>%; <assumed items>.

## Where the numbers disagree with your gut
- <Client>: you said <grade>. <margin at low to high>, <verdict>. <Driver> (<card line>).
- <Client>: you said keep. Depends on hours: <n>% at 3 hours a month, <n>% at 6. A month of tracking settles it.

## Where they agree
- <Client>: you said clone. <n>% to <n>%, healthy at both ends.

## The table
| Client | Your grade | Fee/yr | Hours/yr | Books | Txns/mo (Kick) | Cost | Margin | Margin % | $/hr | Verdict | What the notes say |
| ... | clone | 21,600 | 50 to 70 (est.) | clean | 410 | 3,250 to 4,550 | 18,350 to 17,050 | 85 to 79% | 432 to 309 | healthy | never late; referred one; asked for forecasting |

## The math
- <Client>: 1,800 x 12 = 21,600 · hours 5 to 6 x 12 = 60 to 72 -> 60 to 70 · cost 60 x 65 = 3,900 to 70 x 65 = 4,550 · margin 17,700 to 17,050 (82% to 79%) · healthy at both ends.

Estimate. Hours are yours unless marked actual. Review with your partners before client conversations.
```

## Learned preferences

Apply an owner's correction immediately and keep it for the rest of the run. When a
correction should stick (columns, order, the anonymized version by default), offer to save
it as a dated entry under this heading with the owner's approval; rates and thresholds
belong in the `Firm notes` block instead. Preferences never loosen the guardrails or the
range rule. If this file is not writable here, hand the owner the text.
