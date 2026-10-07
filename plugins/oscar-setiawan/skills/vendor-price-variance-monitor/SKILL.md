---
name: vendor-price-variance-monitor
description: "Compares a vendor's contracted or expected monthly price (supplied by the user, since Kick has no field for a vendor contract) to what actually posted on the corporate card or bank feed this month, and flags any vendor charging more than the contracted amount or showing a silent price creep across recent months. Use when someone asks to check whether a vendor is billing more than the contracted rate, catch a silent price increase, ask \"did our SaaS vendors go up in price,\" or compare a contracted vendor price to what actually got charged this month. Read-only: it never edits, disputes, or pays a transaction. Not for a full vendor spend snapshot (see vendor-spend-snapshot), duplicate vendor names (see vendor-duplicate-merge), or duplicate/overpriced bill screening before a payment run (see vendor-bill-duplicate-guard)."
---

# Vendor price variance monitor

## Purpose

Compare each vendor's contracted monthly price, supplied by the user, to the charges that
actually posted on the card or bank feed, and flag vendors billing above contract or
creeping up across recent months. The output is advisory: the customer acts on the flags
outside the books, and nothing is written back.

1. Scope: entity, vendors, accounts, date window.
2. Contracted prices, from the user.
3. Actual charges per vendor, with period totals from the connector.
4. Variance and flags.
5. One comparison table.

On Kick, the calls behind each step are in [references/kick.md](references/kick.md).

Other vendor jobs belong elsewhere: a full spend picture (vendor-spend-snapshot), name
variants (vendor-duplicate-merge), AP bill screening before a payment run
(vendor-bill-duplicate-guard), and double payments of one invoice
(duplicate-payment-detection).

## Procedure

- [ ] 1. Load the connector's own vendor and transaction guides.
      Carry forward what they flag about vendor resolution and transaction filters. On
      Kick, the binding is [references/kick.md](references/kick.md).
- [ ] 2. Set the scope from the request.
      Three shapes: a monthly sweep across a vendor list, a one-off check on one vendor
      after a suspicious charge, or a trend check over 3 to 6 months to catch creep a
      single month would miss. "Each vendor" means every vendor in scope.
- [ ] 3. Resolve the entity, each vendor, and every account the charges post through.
      One clean vendor record per name. A vendor can split across a corporate card and a
      bank ACH pull, so check both.
- [ ] 4. Get the contracted price per vendor from the user.
      Use a supplied vendor and price table as given. Otherwise ask once for the
      contracted monthly amount per vendor, and say plainly it must come from their own
      contract log or memory, since the books hold no contract field.
- [ ] 5. Pull actual charges per vendor for the window.
      Scope each pull to the vendor's record and the resolved accounts. Take the period
      total from the connector's totals call. Trend check: one pull per month.
- [ ] 6. Compute variance and flag.
      Variance is the actual total minus the contracted price, in dollars and percent.
      Flag any vendor where actual exceeds contracted, or exceeds the user's stated
      tolerance (for example "flag anything more than 5% over"). Note any vendor with
      prior charge history and nothing posted this month.
- [ ] 7. Deliver the comparison table.
      Shape in Example. One line of guidance per flagged vendor. Label every assumption
      (period boundaries, which account counts as "the card", tolerance) and invite a
      one-line correction. Do not ask permission up front; nothing here is written back.

## Caveats

- **Read-only.** The skill never updates a transaction, disputes a charge, creates a
  bill, or messages a channel. Tell: a planned write of any kind. Rule: the deliverable
  is something the customer reviews and acts on themselves.
- **The books hold no contract price.** Tell: a contracted figure that came from a
  ledger field or a past charge. Rule: the contracted figure always comes from the user
  or their own document. Never invent one. With no price supplied for a vendor, say so
  and skip the comparison for that vendor.
- **Totals by hand.** Tell: a period total built by adding transaction rows. Rule: use
  the connector's totals call; figures shown to the user come from the tool response,
  not model arithmetic.
- **A second account missed.** Tell: "no charge found" after checking one account.
  Rule: list every connected account (personal card, corporate card, bank ACH) before
  concluding no charge posted. When charges sit on more than one account, include each
  in the actual total and name them in Scope.
- **Ambiguous vendor match.** Tell: more than one plausible record for a named vendor.
  Rule: surface the options and ask which one; do not pick.
- **Fragmented vendor history.** Tell: name variants for the same company as separate
  records. The actual total here then undercounts. Rule: flag it and point to
  vendor-duplicate-merge rather than silently summing across records you were not asked
  to merge.
- **Mismatched period boundaries.** Tell: a vendor billed mid-cycle (for example the
  15th) against a calendar-month window, producing a false variance. Rule: state which
  window was used and offer to re-run on the vendor's actual billing date if the user
  flags a mismatch.
- **Nothing posted this month.** Tell: a vendor with prior charges and no charge in the
  window. It can mean a paused subscription or a charge on an account this skill was not
  told to check. Rule: report it under Exceptions, never as within contract or flagged.
- **Corrections during a run.** When the user corrects an assumption, output, or
  preference (format, tolerance, account or entity choice), apply it immediately and keep
  it for the rest of the run. A correction never overrides the read-only rule or
  figures-from-reads.
- **Rejected calls.** Follow the drift rule in the connector binding.

## Example

> "We log each vendor's contracted monthly price in our vendor sheet. Compare that to
> what actually hit our Ramp corporate card this month for Acme Rocket Co, and flag
> anyone billing more than contracted. Vercel is contracted at $29, Notion at $96, Slack
> at $120."

Run: one clean record per vendor, the Ramp card as the only account, calendar July. Totals
from the connector: Vercel $29, Notion $96, Slack $156 (contracted $120, +$36, +30%).

```markdown
### Vendor price variance: Acme Rocket Co, July 2026

**Result:** 1 of 3 vendors billed above contract.

**Scope:** Vercel, Notion, Slack. Charges on the Ramp corporate card account only, July 1 to July 31, 2026 (calendar month).

**Details:**

| Vendor | Contracted | Actual (this month) | Variance | Status |
| --- | --- | --- | --- | --- |
| Vercel | $29.00 | $29.00 | $0.00 | Within contract |
| Notion | $96.00 | $96.00 | $0.00 | Within contract |
| Slack | $120.00 | $156.00 | +$36.00 (+30%) | Flagged: over contract |

**Status:** flagged 1 vendor (Slack) for review; the other two match their contracted price.

**Exceptions:** contracted prices came from you, not from Kick (Kick has no vendor-contract field). No charges were found on any other connected account for these three vendors; if Slack also bills to a bank account, ask me to check that too.

**Next step:** confirm the Slack increase with their billing page or account rep, or ask me to pull the last 3 months for Slack to see when the increase started.
```

## Completion

Done when:
- The table carries Result, Scope, Details, Status, Exceptions, and Next step.
- Every vendor has a user-supplied contracted price or sits under Exceptions as not checked.
- Every actual total came from the connector's totals call.
- Scope names the entity, the vendors, every account checked, and the window used.
- Every flagged vendor has one line of guidance.
- Period boundaries, the account that counts as "the card", and the tolerance are labeled.
- No write call was made.

Cleanup: the table goes to the user in chat and is the only artifact. Missing prices,
ambiguous matches, suspected name variants (handed to vendor-duplicate-merge), and
unchecked accounts sit under Exceptions. A rejected call and the shape that worked go in
a method note under the table. If someone shared this skill with the user, the method
note gets one plain line on what worked differently, for the user to forward to whoever
maintains the original.
