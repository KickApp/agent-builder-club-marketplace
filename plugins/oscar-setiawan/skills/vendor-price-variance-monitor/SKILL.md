---
name: vendor-price-variance-monitor
description: "Compares a vendor's contracted or expected monthly price (supplied by the user, since the books usually have no field for a vendor contract) to what actually posted on the corporate card or bank feed this month, and flags any vendor charging more than the contracted amount or showing a silent price creep across recent months. Use when someone asks to check whether a vendor is billing more than the contracted rate, catch a silent price increase, ask did our SaaS vendors go up in price, or compare a contracted vendor price to what actually got charged this month. Read-only: it never edits, disputes, or pays a transaction."
---

# Vendor price variance monitor

Important: this skill assists with vendor contract-vs-actual price monitoring and does not provide financial advice. It is read-only: the comparison table is for a qualified professional to review before disputing a charge or changing a subscription.

Goal: compare each vendor's contracted monthly price against the actual charge that posted this month, and flag vendors billing above contract or trending upward, so the customer can act on it outside the books.

## When to use

- "Did our SaaS vendors go up in price this month?"
- "Compare the contracted monthly price for each vendor in our vendor log to what actually hit the card, and flag anyone billing more than contracted."
- "Check if these named vendors charged more than what we agreed to pay."
- "Has any vendor quietly raised their price over the last few months?"
- Use cases: a monthly contract-vs-actual sweep across a vendor list; a one-off check on a single vendor after a suspicious charge; a trend check across 3-6 months to catch creep that a single-month check would miss.
- Not this skill: a full vendor spend snapshot, merging duplicate vendor names, or screening AP bills for duplicates before a payment run.

## Data you need

Everything here is read-only. You need:

- **Contracted prices**: each vendor's contracted monthly amount, supplied by the user or their own contract log (the books usually have no vendor-contract field).
- **The books and accounts**: which set of books, the vendor records, and the corporate card or bank accounts where charges post.
- **Actual charges**: period totals per vendor for the stated month (or several months for a trend check), from the system's own statistics or summary totals.

## Workflow

1. **Confirm the books and vendors.** Confirm which set of books. Resolve each named vendor, or list vendors in scope if the request says "each vendor." Resolve the card or bank account(s) the vendor's charges post to (a vendor can be split across a corporate card and a bank ACH pull; check both).
2. **Get the contracted price.** If the user already supplied a table of vendor and contracted-price pairs, use it as given. If not, ask once for the contracted monthly amount per vendor, stating plainly that this must come from their own contract log or memory, not from the books. Do not guess a contracted price and do not invent one from a single past charge.
3. **Pull actual charges.** Get each vendor's charges for the stated month (or the last several months, one period at a time, if the request implies a trend check). Prefer the system's period total per vendor rather than adding up rows manually.
4. **Compare and flag.** For each vendor: variance = actual total minus the user-supplied contracted price. Flag any vendor where actual exceeds contracted, or above a stated tolerance (for example "flag anything more than 5% over"). Note vendors with a prior charge history but nothing posted this month; that can mean a paused subscription or a charge landing on an account this skill was not told to check.
5. **Deliver.** Present the comparison table with one line of guidance per flagged vendor. This is advisory only: label every assumption (period boundaries, which account counts as "the card," tolerance threshold) and invite a one-line correction rather than asking permission up front, since nothing here gets written back.

## Working with your data

This skill reads from whatever accounting system is connected. If you have documented bindings for that system, use them. Otherwise:

**Unknown connector**

1. List the available tools and read their schemas and descriptions.
2. Map them to the data needs above (vendor records, card/bank accounts, period charge totals). Anything with no plausible tool is marked UNSUPPORTED.
3. STOP and show the user the mapping, and get confirmation, before any read beyond discovery. This skill performs no writes.
4. Never guess tool names. If the system exposes guide or skill discovery tools, load the relevant vendor and transaction guides first.

## Guardrails

- **Read-only.** This skill never updates a transaction, disputes a charge, creates a bill, or messages a channel; the deliverable is something the customer reviews and acts on themselves.
- **Tool errors and drift**: if a live call is rejected, trust the live error hint (and any loaded guide) over this skill's examples. Fix the call and retry once. If the working shape contradicts this skill's text, add a method note to the deliverable so it can be reported and fixed centrally. Never edit this skill file mid-run.
- **Never invent a contracted price.** If the user has not supplied one for a vendor, say so and skip the comparison for that vendor rather than approximating it from a past charge.
- Use the system's period totals, not manual addition of transaction rows; figures shown to the user come from the response, not model arithmetic.
- **Ambiguous vendor match**: surface the options and ask which one; don't pick.
- **Fragmented vendor history**: if the same company appears to have multiple vendor records (name variants), the actual total here will undercount. Flag it and point to a vendor-duplicate-merge workflow rather than silently summing across records you were not asked to merge.
- **Mismatched period boundaries**: a vendor billed mid-cycle will not line up with a calendar-month window. State which window was used and offer to re-run on the vendor's actual billing date if the user flags a mismatch.

## Human deliverable

Every run ends with a single markdown table structure:

- **Result**: one-line headline (how many vendors flagged out of how many checked).
- **Scope**: books, vendor list, account(s) checked, date window.
- **Details**: a table of vendor, contracted price, actual charge, variance ($ and %), status.
- **Status**: which vendors are flagged versus within contract.
- **Exceptions**: anything that could not be checked (no contracted price supplied, no charge found this month, ambiguous vendor match, more than one account carrying the vendor's charges).
- **Next step**: what the user can do with a flagged vendor.

## Worked example

"We log each vendor's contracted monthly price in our vendor sheet. Compare that to what actually hit our corporate card this month for Acme Rocket Co, and flag anyone billing more than contracted. Vercel is contracted at $29, Notion at $96, Slack at $120."

1. Confirm the books for Acme Rocket Co.
2. Resolve three vendor records: Vercel, Notion, Slack (one clean record each).
3. Resolve the corporate card account.
4. Pull July 2026 period totals per vendor.
5. Results: Vercel $29 (matches), Notion $96 (matches), Slack $156 (contracted $120, variance +$36 / +30%). (Illustrative.)
6. Deliver the table below, flagging Slack.

```markdown
### Vendor price variance: Acme Rocket Co, July 2026

**Result:** 1 of 3 vendors billed above contract.

**Scope:** Vercel, Notion, Slack. Charges on the corporate card account only, July 1 to July 31, 2026 (calendar month).

**Details:**

| Vendor | Contracted | Actual (this month) | Variance | Status |
| --- | --- | --- | --- | --- |
| Vercel | $29.00 | $29.00 | $0.00 | Within contract |
| Notion | $96.00 | $96.00 | $0.00 | Within contract |
| Slack | $120.00 | $156.00 | +$36.00 (+30%) | Flagged: over contract |

**Status:** flagged 1 vendor (Slack) for review; the other two match their contracted price.

**Exceptions:** contracted prices came from you, not from the books (no vendor-contract field). No charges were found on any other connected account for these three vendors; if Slack also bills to a bank account, ask me to check that too.

**Next step:** confirm the Slack increase with their billing page or account rep, or ask me to pull the last 3 months for Slack to see when the increase started.
```

## Common pitfalls

- Assuming the books store a vendor's contract price. They usually do not; the contracted figure always comes from the user or their own document.
- Missing part of a vendor's actual spend because charges land on more than one connected account (personal card, corporate card, bank ACH). Check all relevant accounts before concluding "no charge found."
- Summing raw transaction rows by hand instead of using the system's period total.
- Comparing a calendar month to a vendor that bills on a different cycle date, producing a false variance.
- Treating scattered vendor name variants for the same company as separate vendors, which understates the real total.
- Picking a vendor match without asking when more than one plausible row comes back.

## Related skills

- **Vendor spend snapshot**: full vendor picture instead of a contract-vs-actual price check.
- **Vendor duplicate merge**: merge scattered vendor name variants that would otherwise fragment the actual total here.
- **Vendor bill duplicate guard**: screens AP bills for duplicates or above-average pricing before a payment run, a different check on a different data set (bills, not card charges).
- **Duplicate payment detection**: hunts for double payments of the same invoice or amount, not a price-per-month comparison.

## Feedback and improvement

This copy of the skill belongs to the person running it, and it should get better with use.

- **During a run**: when the user corrects an assumption, an output, or a preference (tone, format, thresholds, account or entity choices), apply the correction immediately and keep it for the rest of the run. A correction never overrides the safety contract: previews, confirmations, and figures-from-reads always stand.
- **Between runs**: when a correction should stick, offer to save it. With the user's explicit approval, add a dated entry under `## Learned preferences` at the end of this file, creating that section if it is missing. Newer entries beat older ones. Never edit this skill file mid-run, and never change the Guardrails, Tools used, or safety wording: preferences and defaults only. A preference is declined, not saved, when honoring it on a future run would loosen any Guardrails line or the safety contract, even though it leaves their text untouched. If this file is not writable where the skill runs, give the user the entry text to save wherever they keep their instructions.
- **Improving the original**: if someone sent the user this skill, end the deliverable with one plain-English line describing what worked differently or which preference was saved (inside the deliverable's method notes, when this skill's output template has them), and ask them to forward it to whoever maintains the original copy.
