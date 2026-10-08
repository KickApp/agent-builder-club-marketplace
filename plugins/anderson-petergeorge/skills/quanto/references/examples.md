# Examples

One synthetic firm, Copperleaf Bookkeeping, four clients, cost rate $65/hr, thin below 20%,
period Sep 2025 to Aug 2026 (assumed). Every figure below reproduces from the stated fee,
hours, and rate.

## Good

The owner asks which clients to clone. Kick responds, so the detection line says Kick is
connected and the interview follows in the same turn. Turn 2 reads the owner's reply onto
the cards and the page below goes on screen, then one line offers the options. No books
are changed.

## Bad

Kick returns an auth error and the run stops, or the run invents client fees before the
owner answers. An auth error is one line in the detection message, and the run continues
on the files and answers the owner can give.

## The Turn 2 page

The rank section comes first, then the profile. The math lines cover every row here
because the firm has four clients.

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
- Pinecrest Dental Studio: 1,800 x 12 = 21,600 · hours 5 to 6 x 12 = 60 to 72 -> 60 to 70 · cost 60 x 65 = 3,900 to 70 x 65 = 4,550 · margin 21,600 - 3,900 = 17,700 to 21,600 - 4,550 = 17,050 (82% to 79%) · healthy at both ends.
- Vance Refrigeration: 1,400 x 12 = 16,800 · 58 hours actual (Karbon) · cost 58 x 65 = 3,770 · margin 16,800 - 3,770 = 13,030 (78%) · healthy.
- Tidewater Print Shop: 500 x 6 (Mar to Aug 2026) = 3,000 · hours 4 to 8 x 6 = 24 to 48 -> 25 to 50 · cost 25 x 65 = 1,625 to 50 x 65 = 3,250 · margin 1,375 to -250 (46% to -8%) · depends on hours.
- Larkin Event Rentals: 600 x 12 = 7,200 · hours 10 to 12 x 12 = 120 to 144 -> 120 to 145 · cost 120 x 65 = 7,800 to 145 x 65 = 9,425 · margin -600 to -2,225 (-8% to -31%) · negative at both ends.

Estimate. Hours are yours unless marked actual. Review with your partners before client conversations.

## Your ideal client (a hypothesis from 2 clients)
Pinecrest and Vance are established Scranton businesses with $1M to $5M in revenue, both on Gusto, both upload documents before every call, both asked for forecasting, and both have referred someone. Pinecrest is an LLC on Xero and Vance an S-corp on QuickBooks, so entity type and ledger software are not the pattern. Your hardest one, Larkin, is under $1M, mixes personal spending into the business account, and gets chased for statements. Larkin is one client, so the anti-profile is an observation.

Your grades against the data
- Pinecrest Dental Studio: clone agrees.
- Vance Refrigeration: clone agrees.
- Larkin Event Rentals: keep disagrees; see the ranking (books condition, fee age).
- Tidewater Print Shop: keep; not tested, the verdict depends on hours.

| Field | Your ideal client | Evidence |
| --- | --- | --- |
| Industry | not enough evidence | dental and HVAC |
| Business size | $1M to $5M revenue | Pinecrest, Vance |
| Location | Scranton area | Pinecrest, Vance |
| Entity type | not enough evidence | LLC and S-corp |
| Services they buy and ask for | monthly books, payroll review; asking for forecasts | Pinecrest, Vance |
| Books condition | clean | Pinecrest, Vance |
| How they work with you | documents before every call | Pinecrest, Vance |
| Who decides, how fast | the owner or office manager, within a week | Pinecrest, Vance |
| Tools | Gusto for payroll | Pinecrest, Vance |

Anti-profile, from one client: under $1M, personal and business spending mixed, statements chased.
Worth validating: Tidewater Print Shop, one month of tracked hours settles it.
What would sharpen this: a time export for all four clients.

## Three questions for the partners
1. Is Larkin's fee due for review, or should the cleanup be billed as its own work?
2. Would Pinecrest and Vance each make one introduction this quarter?
3. Do you want to package forecasting for clients like these two?
```

Then the one closing line from the Example in SKILL.md.

## The Turn 3 options table

```markdown
## Where to find more of them
Rests on: established Scranton businesses with $1M to $5M in revenue, clean books, documents before every call, asking for forecasts; a hypothesis from 2 clients. Capacity: 6 new clients this year (yours).

| # | Move | Rests on | Effort | Impact | First client in | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Ask Bob Vance for the introduction to the plumbing company he mentioned in March | Vance card, Mar 2026 note | low | high | weeks | a warm name already exists |
| 2 | Ask Pinecrest's office manager for a referral at the next quarterly review | Pinecrest card, no named introduction | low | medium | months | on-profile by construction, no name yet |
| 3 | Meet the Scranton lenders who finance businesses of this size | Business size field; Pinecrest came through a lender | medium | medium | months | lenders already see these clients' statements |
| 4 | Say it the same way every time: "a monthly close and a quarterly forecast you can hand your lender without rework" | what Pinecrest and Vance asked for | low | medium | weeks | built from the top group's own requests |
| 5 | Add an onboarding cleanup fee and a minimum books standard to the engagement letter | Larkin card (messy books, fee not raised since 2023) | low | medium | weeks | stops the next Larkin before it starts |
| 6 | Show up where Gusto users in the region meet | Tools field (both on Gusto) | medium | low | quarters | a channel the top group already uses |

No double-down move: Pinecrest came through a lender and Vance through a Chamber of Commerce contact, so no single source repeats.

If you could do two of these before 2026-10-14, which two, and who owns them?
Review with your partners before acting.

That is the engagement; one question before we finish.
```
