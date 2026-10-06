---
name: personal-business-deduction-scan
description: Scans an owner's personal bank and card accounts for likely business-deductible spend (software subscriptions, home office, professional services, business meals, phone and internet), estimates total potential deduction value, and produces a CPA-review shortlist grouped by deduction type. Use when a founder or owner asks to find business expenses paid from personal accounts, personal-to-business tax savings, mixed personal/business spend review, or a deduction shortlist before CPA review. Read-only. Every figure is an estimate, not filing advice.
---

# Personal-to-business deduction scan

**Important:** this skill assists with scanning personal accounts for likely business deductions
and does not provide financial or tax filing advice. It is read-only. Every dollar figure is an
estimate for CPA review, not filing advice.

**Goal:** review transactions in the owner's personal financial accounts, flag spend that is
likely business-deductible, estimate totals by deduction type, and deliver a CPA-review
shortlist, with every dollar figure labeled Estimate for review. Not filing advice.

## Setup (ask first)

For a direct advisory/read-only request, do not block the deliverable on setup answers: proceed
immediately using the suggested defaults named below, label every assumed value inline in the
deliverable (for example "_Assumed: prior calendar year scan, all personal accounts, primary
business entity, tell me if any should change_"), and invite correction. Ask first only when
scope or entity is genuinely ambiguous in a way that would materially change the answer, or when
any write/preview action is involved. On unattended runs where no human can answer, proceeding
with labeled defaults is the expected behavior; inline labeling is what keeps "no silent
defaults" honest.

Suggested defaults when not stated: books scope, personal account(s) to scan, scan period, and
reclassification target business entity (when multiple exist). Skip variables the user's message
already answers unambiguously.

## When to use

* "Scan my personal accounts for business deductions", "what did I pay personally that the
business could deduct?", "personal-to-business tax savings review", "founder mixed spend
cleanup before CPA", "home office and software subs on my personal card".
* Use cases: year-end owner deduction sweep; pre-CPA mixed-spend shortlist; personal card
software/meals/pro-services review.
* Not this skill: vendor 1099 shortlists, categorizing business-account transactions, or
posting accruals/journal entries.

## Data you need

* The owner's personal accounts: bank and card accounts attributed to a personal entity or
clearly marked personal (confirm with the user; never scan a business account by mistake).
* Outflow transactions for the period: date, amount, description, counterparty for the scan
window.
* Deduction bucket heuristics: software, home office, professional services, business meals,
phone/internet, plus an uncertain/mixed-use bucket.
* Optional business-account precedents: how similar merchants were categorized on the
business side (context only, not proof).

## Deduction buckets (group output by these)

| Bucket | Typical signals | Caution |
| --- | --- | --- |
| Software subscriptions | SaaS merchants (Adobe, Slack, AWS, Notion, Zoom, GitHub…), recurring same-amount charges | Mixed personal/business use, flag % for CPA |
| Home office | Rent/mortgage interest proxies, utilities, internet if home is principal place of business | Requires CPA on exclusive/regular use rules |
| Professional services | Legal, accounting, consulting, coaching, contractors paid personally | Confirm business purpose and entity |
| Business meals | Restaurants during travel/client meetings; exclude routine personal dining | 50% limitation may apply, CPA decides |
| Phone / internet | Carrier bills on personal accounts used for business | Allocate business %, do not assume 100% |

Add an Uncertain / mixed-use section for rows that need CPA judgment (Amazon, rideshare,
retail, gifts).

## Workflow

1. **Orient.** Confirm which set of books. If no name is given, list candidates and ask. If
several match, ask; never pick.
2. **Identify personal accounts.** Find accounts that belong to the personal entity or are
clearly personal. If the customer names an account/institution, verify it exists before
scanning; if absent, stop, say so, list the actual personal accounts as candidates, and ask.
Never scan a substitute silently. Masks are not unique across entities; confirm with the
user.
3. **Set the period.** Confirm start and end dates. If not stated, suggest the tax year or
period the user implied and label the assumption.
4. **Pull personal-account spend (one account at a time).** Gather outflows for each personal
account over the period so each row can be attributed to an account. If an account is very
large (hundreds of rows), tell the user and offer to scan by quarter. Never conclude from an
empty result until a known-positive control query succeeds.
5. **Screen for deduction candidates.** Apply bucket heuristics to descriptions, counterparties,
and amounts. Large recurring payments that look like housing/mortgage → Uncertain / mixed-use
with "home-office analysis required", never in headline totals. Flag suspected duplicate-
import pairs (same date/amount/description) separately; exclude duplicates from headline
totals. For ambiguous merchants, prefer Uncertain / mixed-use over auto-flagging.
6. **Estimate totals by bucket.** Sum absolute outflows per bucket (refunds excluded). For
mixed-use items, show full amount and a suggested business-use range only when the user
supplied a basis; otherwise list amount with "business % TBD by CPA". Round to cents. Every
subtotal and grand total must append: `Estimate for review. Not filing advice.`
7. **Deliver the CPA shortlist** using the output template below. Include dates and descriptions
so the CPA can verify. Offer drill-down on any bucket if the user asks.

## Working with your data

This skill reads from whatever accounting system is connected. If you have documented bindings
for that system, use them. Otherwise:

### Unknown connector

1. List the available tools and read their schemas and descriptions.
2. Map them to the data needs above (personal accounts and their outflow transactions). Anything
with no plausible tool is marked UNSUPPORTED.
3. STOP and show the user the mapping, and get confirmation, before any read beyond discovery.
This skill performs no writes.
4. Never guess tool names. If the system exposes guide or skill discovery tools, load the
relevant transaction-query guides first.

## Guardrails

* **Read-only.** Do not recategorize, split, post journal entries, or call any write tool; the
deliverable is a review packet only.
* **Draft first, ask second (advisory reads):** deliver with labeled default assumptions rather
than blocking on a parameter interview; ask first only for material ambiguity or writes.
* **No silent defaults:** label every assumed default inline in the deliverable.
* Every total must carry: `Estimate for review. Not filing advice.`
* **Tool errors and drift:** if a live call is rejected, trust the live error hint (and any
loaded guide) over this skill's examples; fix the call and retry once. If the working shape
contradicts this skill's text, record the discrepancy in the deliverable's method notes. Never
edit this skill file mid-run.

## Output template

```markdown
# Personal-to-business deduction scan: [Entity] ([Period])

**Scope:** Personal accounts: [names/masks]. Reclassification target: [business entity name
(**ask to confirm** when multiple business entities exist)].
**Disclaimer:** All amounts below are estimates for CPA review. Not filing advice.

## Summary by deduction type
| Deduction type | # items | Estimated spend | Notes |
| --- | --- | --- | --- |
| Software subscriptions | … | $X (*Estimate for review. Not filing advice.*) | … |
| … | … | … | … |
| **Grand total (flagged)** | … | **$Y (*Estimate for review. Not filing advice.*)** | Excludes uncertain/mixed-use and suspected duplicates |

## Detail: [Bucket name]
| Date | Amount | Account | Description | Why flagged |
| --- | --- | --- | --- | --- |

## Suspected duplicate imports (excluded from totals)
…

## Uncertain / mixed-use (CPA judgment required)
…

## Recommended CPA follow-ups
- …

```

## Worked example

_Figures below are illustrative: never quote them as live data; every delivered number must come
from the current books._

"Find business expenses paid from my personal accounts, scan my personal Amex and personal
checking in Cedar Lane Design for 2025, software, home office, meals, phone. Group for my CPA."

1. User named books, accounts, period, and buckets; skip re-ask on those. Confirm
reclassification target: sole business entity.
2. Confirm personal Amex and personal checking belong to the personal entity.
3. Pull outflows per account for 2025.
4. Bucket: Adobe/Slack/AWS → Software ($4,820, Estimate for review. Not filing advice.); AT&T
→ Phone/internet ($1,440, same disclaimer); Sweetgreen → Uncertain/meals; flag one duplicate
pair separately.
5. Deliver summary table + detail sections + CPA follow-ups (document business-use % for phone,
50% meal rules).

## Common pitfalls

* Scanning business accounts instead of personal: confirm personal attribution with the user.
* Treating every SaaS charge as 100% deductible: mixed-use software belongs in Uncertain unless
the user confirmed business-only.
* Presenting totals without the required disclaimer on every figure.
* Calling write tools to "fix" categorization: this skill is read-only.
* Asking the user for internal system ids: resolve accounts and transactions from the connected
system.

## Related skills

* Vendor spend review: 1099 contractor payment shortlist from business vendor spend (not
personal-account deductions).
* Transaction review and categorization: categorize transactions in the books (write workflow).
* Post-migration tie-out: migration reconciliation; different trigger phrases.

## Feedback and improvement

This copy of the skill belongs to the person running it, and it should get better
with use.

* **During a run:** when the user corrects an assumption, an output, or a preference
(tone, format, thresholds, account or entity choices), apply the correction
immediately and keep it for the rest of the run. A correction never overrides the
safety contract: previews, confirmations, and figures-from-reads always stand.
* **Between runs:** when a correction should stick, offer to save it. With the user's
explicit approval, add a dated entry under `## Learned preferences` at the end of
this file, creating that section if it is missing. Newer entries beat older ones.
Never edit this skill file mid-run, and never change the Guardrails, Tools used, or
safety wording: preferences and defaults only. A preference is declined, not saved,
when honoring it on a future run would loosen any Guardrails line or the safety
contract, even though it leaves their text untouched. If this file is not writable
where the skill runs, give the user the entry text to save wherever they keep their
instructions.
* **Improving the original:** if someone sent the user this skill, end the deliverable
with one plain-English line describing what worked differently or which preference
was saved (inside the deliverable's method notes, when this skill's output template
has them), and ask them to forward it to whoever maintains the original copy.
