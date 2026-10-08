---
name: personal-business-deduction-scan
description: "Scans an owner's personal bank and card accounts in Kick for likely business-deductible spend (software subscriptions, home office, professional services, business meals, phone and internet), estimates total potential deduction value, and produces a CPA-review shortlist grouped by deduction type. Use when a founder or owner asks to find business expenses paid from personal accounts, personal-to-business tax savings, mixed personal/business spend review, or a deduction shortlist before CPA review. Read-only. Every figure is an estimate, not filing advice."
---

# Personal-to-business deduction scan

## Purpose

Review the transactions in the owner's personal financial accounts, flag spend that is likely business-deductible, estimate totals by deduction type, and deliver a CPA-review shortlist. Read-only: nothing in the books changes, and every dollar figure is labeled `Estimate for review. Not filing advice.`

1. Scope: workspace, personal accounts, scan period, reclassification target entity.
2. Pull: personal-account outflows, one account at a time.
3. Screen: bucket each row; set aside uncertain items and suspected duplicates.
4. Estimate: totals by deduction type.
5. Deliver: the CPA shortlist.

On Kick, the calls behind each step are in [references/kick.md](references/kick.md).

Not for vendor 1099 shortlists from business vendor spend, categorizing business-account transactions, posting accruals or journal entries, or migration reconciliation.

## Procedure

- [ ] 1. Load the connector binding and its transaction guide.
      On Kick, follow [references/kick.md](references/kick.md); it loads the built-in transaction guide first. Follow the guide's query syntax alongside this skill.
- [ ] 2. Set scope, drafting on labeled defaults.
      Scope variables: workspace or entity, personal accounts to scan, scan period (start and end dates), reclassification target business entity when more than one exists. Skip any the message or a saved personalized copy already answers unambiguously.
      Direct read-only request: do not block the deliverable on setup answers. Proceed on the suggested defaults, label every assumed value inline (e.g. "_Assumed: prior calendar year scan, all personal accounts, primary business entity, tell me if any should change_"), and invite correction.
      Ask first only when scope or entity is ambiguous in a way that would change the answer materially. Unattended runs with no one to answer proceed on labeled defaults.
      Period not stated: suggest the tax year or period the user implied. Ask, unless the draft-first rule above applies.
      Several business entities: ask to confirm the reclassification target in one consolidated ask ("Reclassification target: suggest [sole business entity name], confirm or change?").
- [ ] 3. Resolve the workspace and entity.
      No name given: list the workspace candidates and ask. Name given: resolve it to its id. Entity named: resolve it too.
      Ambiguous match: list the candidates and ask. Never pick.
- [ ] 4. Identify the personal accounts.
      Find the entity marked personal, then keep only the accounts that belong to it. Personal is an entity attribute, not an account field.
      Account or institution named: verify it exists before scanning. Absent: stop, say so, list the actual personal accounts as candidates, and ask.
      Masks are not unique across entities. Confirm the accounts with the user and record the selected account ids.
- [ ] 5. Size each account, then pull its outflows.
      Count first: expect one count call plus ceil(count/100) pages per account. Over about 500 rows on one account: tell the user and offer to scan by quarter.
      Pull money-out rows only, scoped to the personal entity, one account per query so every row attributes to its account. Page to the end.
- [ ] 6. Screen each row into a deduction bucket.
      Apply the bucket signals and cautions in [references/deduction-buckets.md](references/deduction-buckets.md) to descriptions, counterparties, and amounts.
      Large recurring payments that look like housing or mortgage (large, monthly, to a bank): Uncertain / mixed-use with "home-office analysis required". Never in headline totals.
      Suspected duplicate-import pairs (same date, amount, description): flag in their own section and exclude from headline totals.
      Ambiguous merchant: prefer Uncertain / mixed-use over auto-flagging.
      Optional context: resolve unclear merchant names to vendors, look up similar business-account transactions as precedent, and check how similar business rows were categorized. Precedent is context only, not proof.
- [ ] 7. Estimate totals by bucket.
      Sum absolute outflows per bucket. Refunds stay out because only money-out rows are pulled. Round to cents.
      Mixed-use items: show the full amount. Add a suggested business-use range only when the user supplied a basis; otherwise write "business % TBD by CPA".
      Every subtotal and the grand total appends `Estimate for review. Not filing advice.`
- [ ] 8. Deliver the CPA shortlist.
      Use the Example structure and adapt its sections to what was found. Include transaction ids, dates, and descriptions so the CPA can verify.
      Offer drill-down on any bucket if the user asks. A worked run is in [references/examples.md](references/examples.md).

## Caveats

- **Read-only.** Never recategorize, split, post journal entries, or call any write or action tool. Tell: a step is about to "fix" a category. The deliverable is a review packet only.
- **Personal accounts only.** Scanning business accounts instead of personal is the costly mistake. Tell: a selected account belongs to an entity not marked personal. Attribute by the personal entity, then confirm with the user.
- **Never scan a substitute.** A named account that does not exist stops the run for that account. Tell: the scope line lists an account the user never named or confirmed.
- **No silent defaults.** Never apply a suggested value without showing it. Tell: a scope value in the deliverable that the user never stated and that carries no "Assumed" label.
- **Resolve ids with reads.** Never ask the user for UUIDs or account ids.
- **Empty is not zero.** Never conclude from an empty result until a known-positive control query with the same filter key returns rows.
- **Mixed-use software is not 100% deductible.** A SaaS charge with possible personal use goes in Uncertain / mixed-use unless the user confirmed business-only.
- **The disclaimer rides on every figure.** Every subtotal and grand total carries `Estimate for review. Not filing advice.` Tell: any dollar total without it.
- **Illustrative figures stay illustrative.** Numbers in this skill and its references are examples. Never quote them as live data; every delivered number comes from the current workspace.
- **Corrections apply at once.** When the user corrects an assumption, output, or preference mid-run, apply it for the rest of the run. A correction never overrides the read-only rule or the disclaimer.
- **Rejected calls.** Trust the live error hint and the loaded guide over the binding, fix the call, and retry once. Record any discrepancy in the deliverable's method notes. Never edit this skill file mid-run.

## Example

```markdown
# Personal-to-Business Deduction Scan: [Workspace] ([Period])

**Scope:** Personal accounts: [names/masks]. Reclassification target: [business entity name (**ask to confirm** when multiple business entities exist)].
**Disclaimer:** All amounts below are estimates for CPA review. Not filing advice.

## Summary by deduction type
| Deduction type | # items | Estimated spend | Notes |
| --- | --- | --- | --- |
| Software subscriptions | … | $X (*Estimate for review. Not filing advice.*) | … |
| … | … | … | … |
| **Grand total (flagged)** | … | **$Y (*Estimate for review. Not filing advice.*)** | Excludes uncertain/mixed-use and suspected duplicates |

## Detail: [Bucket name]
| Date | Amount | Account | Description | Why flagged | txn id |
| --- | --- | --- | --- | --- | --- |

## Suspected duplicate imports (excluded from totals)
…

## Uncertain / mixed-use (CPA judgment required)
…

## Recommended CPA follow-ups
- …

## Method notes
- Assumed defaults, and any step that worked differently than this skill describes. Omit when empty.
```

## Completion

Done when:
- Every scanned account belongs to the personal entity and was confirmed by the user or labeled as assumed.
- Every assumed default is labeled inline in the deliverable.
- Each account was pulled on its own, money-out only, paged to the end.
- Housing-like payments, mixed-use items, and suspected duplicates sit outside the headline totals.
- Every subtotal and the grand total carries `Estimate for review. Not filing advice.`
- Every flagged row shows date, amount, account, description, reason, and transaction id.
- Nothing in the books changed.

Cleanup: the shortlist goes to the user for their CPA. Business-use percentages, home-office analysis, meal limits, and unconfirmed scope land under Recommended CPA follow-ups. Drift discrepancies land in Method notes.
