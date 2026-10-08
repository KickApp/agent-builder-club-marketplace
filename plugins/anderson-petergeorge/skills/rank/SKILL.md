---
name: rank
description: Ranks an accounting firm's clients by estimated direct delivery margin (fee minus hours times the firm's cost rate), shows the math, books condition, and Kick volume beside each row, and names where the numbers disagree with the owner's grades. Use when the owner asks which clients make or lose money, which are below target margin, or which are more headache than they are worth, or when /quanto reaches the ranking. Never invents fees, hours, or rates.
argument-hint: "[period]"
---

# Rank

## Purpose

Rank every client by what it earns the firm after the labor to serve it, with the owner's
grade beside every number and one line for each place the numbers and the grade disagree.
This is the first output and the headline of the page.

1. Header with every assumption.
2. Where the numbers disagree with your gut, then where they agree.
3. The table.
4. The math.
5. The closing line.

## Procedure

- [ ] 1. Gather the client cards and the `Firm` note from the conversation.
      No cards: ask for the evidence step by name. A standalone question ("which clients
      lose me money?") with no cards: ask in one message for the fee and a rough hours
      range per client and the cost rate, then run on that alone and say so.
- [ ] 2. Confirm the cost rate exists.
      None: ask once, in one line, offering the salary-and-hours route. Declined: rank by
      fee and realized rate per hour, "cost rate pending" in the margin columns.
- [ ] 3. Take from each card: fees, hours (actual or range), months served, Kick volume,
      books condition, and the owner's grade.
      A card missing fees or hours goes to the bottom, unranked, with the missing input
      named ("fee unknown", "hours unknown").
- [ ] 4. Compute every row.

      ```
      fees            = fee for the months served (source on the card)
      hours           = actual for the period, or the owner's low and high per month x months served
      cost            = hours x cost rate
      margin          = fees - cost
      margin %        = margin / fees               (fees 0: not applicable)
      realized $/hr   = fees / hours                (hours 0: not applicable)
      ```

      Estimated hours run twice, at the low and the high end of the owner's range. Round
      each end to the nearest 5 for the period first, then compute cost and margin from
      the rounded hours so every row reproduces. Actual hours are one figure, unrounded.
      Percentages and dollars per hour print as whole numbers. Ranges print the low-hours
      end first. Keep exact operands in the math lines.
- [ ] 5. Assign each verdict from the threshold in the `Firm` note (20% unless the owner
      set one).
      Negative: margin below zero at both ends. Thin: between zero and the threshold at
      both ends. Healthy: above the threshold at both ends. A range that crosses a line
      reads "depends on hours; worth a month of tracking" and names which end lands where.
      Rows with actual hours get the verdict outright.
- [ ] 6. Rank by margin percent at the midpoint of the rounded range, or the actual
      figure, highest first.
- [ ] 7. Check each estimated range against the Kick volume and books condition.
      A range out of line with the volume (5 hours a month for 340 transactions with a
      fifth awaiting review, next to 5 hours for 90 clean ones) gets one line and a
      question; the number is never adjusted. Without Kick, name the one or two ranges
      most worth a month of tracking.
- [ ] 8. Write the disagreements first.
      Every clone or keep that is negative or thin at both ends, every fire that is healthy
      at both ends, and every row that depends on hours. One line each, naming the driver
      from the card and citing the card line: pricing (fee low for the effort or volume),
      scope (unbilled work), books condition (messy books eating hours), delivery friction
      (chased documents, repeated questions), fee age (not raised in 18 months or more),
      or fit (disputes, slow payment, slow decisions). Grades the numbers agree with get
      one short line each under "Where they agree".
- [ ] 9. Write the math for every flagged row and for the top and bottom three, one line
      each.
- [ ] 10. Deliver the section with its closing line.
      Under the router, hand off to profile in the same turn; standalone, say "Next: your
      ideal client, if you want it" and stop.

## Caveats

- The cost rate is the owner's loaded cost per hour and is never suggested. A salary and
  weekly hours become a rate with the operands shown, 48 weeks stated.
- Months served come from the card's Fee line. A "since" month counts from that month
  through the end of the period, both inclusive.
- A client is thin or negative only when the whole range says so. The tell of a broken
  verdict is a range whose two ends land on different sides of zero or the threshold.
- No formula turns Kick transactions into hours. Volume and books condition sit beside the
  hours so the owner can judge the estimate.
- Figures come from the cards, never from memory or a note. A number the cards cannot
  support is "unknown", never an estimate.
- Call it estimated direct delivery margin. It is labor only, unless the owner's cost rate
  demonstrably includes overhead; then say what it includes.
- Assumptions (period, threshold, months served) print once, in the header.
- No external benchmarks or industry averages.
- Client names appear in the firm-internal version only. An anonymized version (Client A,
  B, C by fee; disagreements section dropped) is produced only when the owner asks for
  something to share outside the firm.
- No authoritative pricing, tax, or firing advice. Findings are questions for the partners.
- Draft first and deliver with every assumption labeled. The only question before
  delivery is the cost rate, once; a range-versus-volume mismatch is one line in the
  section, never a blocking question.
- Thin data degrades the section without stopping it:
  - No Kick: the volume column is blank; books condition from notes and owner only.
  - Fewer than three clients with fees and hours: one short scorecard per client, no
    ranking.
  - Every row depends on hours: the table still ships, and the page says a month of time
    tracking is the next step.
- An owner's correction applies at once. Columns, order, or the anonymized version by
  default can be kept in the `Firm notes` block, as can rates and thresholds. A correction
  never loosens the range rule.

## Example

```markdown
# Your clients, ranked: Copperleaf Bookkeeping, Sep 2025 to Aug 2026 (assumed)
Confidential, firm internal use only. Estimate: hours are your figures unless marked actual; cost rate $65/hr (yours); thin below 20% (suggested, you accepted); period assumed.

## Where the numbers disagree with your gut
- Larkin Event Rentals: you said keep. -8% to -31%, negative at both ends. Books condition: 22% of transactions awaiting review and personal spending in the business account (Kick line; notes Apr 2026). Fee age: not raised since 2023 (Fee line).
- Tidewater Print Shop: you said keep. Depends on hours: 46% at 4 hours a month, -8% at 8. A month of tracking settles it.

## Where they agree
- Pinecrest Dental Studio: you said clone. 82% to 79%, healthy at both ends.
- Vance Refrigeration: you said clone. 78% on actual hours, healthy.

## The table
| Client | Your grade | Fee/yr | Hours/yr | Books | Txns/mo (Kick) | Cost | Margin | Margin % | $/hr | Verdict | What the notes say |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pinecrest Dental Studio | clone | 21,600 | 60 to 70 (est.) | clean | 410 | 3,900 to 4,550 | 17,700 to 17,050 | 82 to 79% | 360 to 309 | healthy | never late; referred one; asked for forecasting |
| Vance Refrigeration | clone | 16,800 | 58 (actual) | clean | 90 | 3,770 | 13,030 | 78% | 290 | healthy | documents before every call; referred a plumbing company |
| Tidewater Print Shop | keep | 3,000 (6 months) | 25 to 50 (est.) | fair | 60 | 1,625 to 3,250 | 1,375 to -250 | 46 to -8% | 120 to 60 | depends on hours | statements chased twice |
| Larkin Event Rentals | keep | 7,200 | 120 to 145 (est.) | messy | 340 | 7,800 to 9,425 | -600 to -2,225 | -8 to -31% | 60 to 50 | negative | personal spending mixed in; receipts in bulk |

## The math
- Pinecrest Dental Studio: 1,800 x 12 = 21,600 · hours 5 to 6 x 12 = 60 to 72 -> 60 to 70 · cost 60 x 65 = 3,900 to 70 x 65 = 4,550 · margin 21,600 - 3,900 = 17,700 to 21,600 - 4,550 = 17,050 · 17,700 / 21,600 = 82%, 17,050 / 21,600 = 79% · $/hr 21,600 / 60 = 360 to 21,600 / 70 = 309 · healthy at both ends.
- Vance Refrigeration: 1,400 x 12 = 16,800 · 58 hours actual (Karbon) · cost 58 x 65 = 3,770 · margin 16,800 - 3,770 = 13,030 · 13,030 / 16,800 = 78% · $/hr 16,800 / 58 = 290 · healthy.
- Tidewater Print Shop: 500 x 6 (Mar to Aug 2026) = 3,000 · hours 4 to 8 x 6 = 24 to 48 -> 25 to 50 · cost 25 x 65 = 1,625 to 50 x 65 = 3,250 · margin 1,375 to -250 · 46% to -8% · $/hr 120 to 60 · depends on hours.
- Larkin Event Rentals: 600 x 12 = 7,200 · hours 10 to 12 x 12 = 120 to 144 -> 120 to 145 · cost 120 x 65 = 7,800 to 145 x 65 = 9,425 · margin -600 to -2,225 · -8% to -31% · $/hr 60 to 50 · negative at both ends.

Estimate. Hours are yours unless marked actual. Review with your partners before client conversations.
```

Ranked by midpoint margin percent: Pinecrest 80% (65 hours), Vance 78% (actual),
Tidewater 19% (37.5 hours), Larkin -20% (132.5 hours).

## Completion

Done when:
- Every client has a row whose Verdict reads healthy, thin, negative, "depends on hours",
  or a named missing input.
- Every figure traces to a card line or the confirmed rate, and the math lines show the
  operands.
- Every disagreement with an owner grade has a driver and a cited source.
- Books condition and Kick volume appear beside every estimated row.
- The section ends with "Estimate. Hours are yours unless marked actual. Review with your
  partners before client conversations."

Cleanup: the section stays in the conversation for the profile and options steps. Any
range-versus-volume question rides in the section for the owner to answer at the close.
