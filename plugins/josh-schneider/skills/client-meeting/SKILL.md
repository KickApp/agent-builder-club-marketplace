---
name: client-meeting
description: "Prepares a one-page client meeting brief from the books: financial highlights since the last meeting, open bookkeeping items, anomalies, and suggested talking points, with optional enrichment from the user's calendar and email connectors when available. Use when the user asks to prep for a client meeting, meeting brief, what should I cover with this client, client check-in prep, or talking points before my call. Degrades gracefully to books-only mode when calendar or email connectors are absent. Read-only against the books."
---

# Meeting prep brief

**Important:** this skill assists with client meeting preparation and does not provide financial
advice. It is read-only against the books: the brief is for a qualified professional to review
before the call.

**Goal:** deliver a one-page client meeting brief (financial highlights since the last meeting,
open items, anomalies, and suggested talking points), citing every figure to its source, degrading
gracefully when calendar or email connectors are unavailable, without changing anything in the
books.

## Setup (every run)

For a **direct advisory/read-only** request, do **not** block the deliverable on setup answers:
proceed immediately using the suggested defaults below, **label every assumed value inline** in
the deliverable (for example "_Assumed: 90-day lookback, $1,000 anomaly floor, one-page executive
format, tell me if any should change_"), and invite correction. **Ask first** only when scope or
entity is genuinely ambiguous in a way that would materially change the answer. On **unattended
runs** where no human can answer, proceeding with labeled defaults is the expected behavior.

| Variable | Suggested | Ask |
| --- | --- | --- |
| {{LOOKBACK_DAYS}} | 90 | "How many days back should financial highlights cover if no meeting date or period is named? (Suggested: 90, confirm or change?)" |
| {{BRIEF_FORMAT}} | One-page executive | "Format: one-page executive, bullet checklist, or narrative memo?" |
| {{MATERIALITY_FLOOR}} | $1,000 | "Minimum dollar swing to flag as an anomaly? (Suggested: $1,000, confirm or change?)" |
| {{INCLUDE_TASKS}} | Yes | "Include open tasks and bookkeeping-health checks?" |

## When to use

- "Prep for my client meeting", "meeting brief", "what to cover on the call", "client check-in
  prep", "talking points before my meeting with [client]".
- Use cases: pre-call accountant brief, quarterly client review prep, ad-hoc owner check-in agenda.
- **Not this skill:** full management report packs, deep flux analysis, or firm-wide morning
  digests.

## Data you need

Everything here is read-only against the books. You need:

- **The client's books and lookback window:** which set of books, basis, and the period since the
  last meeting (or a confirmed lookback).
- **Financial highlights:** profit and loss and cash position for the window, plus a prior
  equal-length window when practical.
- **Bookkeeping health signals:** unreviewed items, missing counterparties, open tasks, and
  readiness flags when available.
- **Optional calendar/email context:** last/next meeting date and recent thread subjects when those
  connectors are available.

## Workflow

Copy this checklist into the response and check items off:

```
Meeting prep progress:
- [ ] 1. Detect connector mode (books-only vs enriched)
- [ ] 2. Orient (books + basis)
- [ ] 3. Establish lookback window
- [ ] 4. Pull P&L + cash highlights for window
- [ ] 5. Flag anomalies (materiality applied)
- [ ] 6. Bookkeeping health + open items (if {{INCLUDE_TASKS}})
- [ ] 7. Draft talking points
- [ ] 8. Deliver one-page brief
```

1. **Detect connector mode (do this before assuming calendar/email data).** Attempt to use the
   calendar connector only if it is available in the session. Same for the email connector.
   **Books-only mode:** if either connector is absent or returns an auth/availability error,
   proceed with books data only. In the deliverable, add a **Skipped (no connector)** section
   listing what was omitted. Never fail the brief because calendar/email is missing.
2. **Orient.** Confirm which set of books and the ledger basis. If the name matches more than one,
   list candidates and ask. Single ledger → use and state it.
3. **Establish lookback window.**
   - **User-named period:** if the user names a start ("since March", "from Q1", "last 60 days"),
     use that and skip {{LOOKBACK_DAYS}}.
   - **Enriched mode:** if calendar returns a last meeting date for this client, set the window
     from the day after that meeting through today (or a user-named end date).
   - **Books-only fallback:** when no period or meeting date is available, use confirmed
     {{LOOKBACK_DAYS}} ending today, labeled inline. If lookback is still unanswered, ask once; do
     not proceed with a silent window.
   - For P&L highlights, also pull the **prior equal-length window** for comparison when practical.
4. **Pull financial highlights.** Summarize revenue, gross profit (if available), net income, and
   cash from the profit and loss and balance sheet for both windows when comparing. A large balance
   in a bank-transfer-clearing or transfer-in-transit account usually means an unmatched internal
   transfer: call it out separately and **exclude it from the liquidity read**. Note credit-card
   balance growth as a cash-flow driver when material.
5. **Flag anomalies** for the meeting agenda:
   - Material P&L line swings: |Δ| ≥ confirmed {{MATERIALITY_FLOOR}} OR (|Δ%| ≥ 10% AND |Δ| ≥ $100).
   - Large one-off transactions sorted by amount.
   - Suspected duplicate imports, flagged separately.
6. **Bookkeeping health + open items** (when {{INCLUDE_TASKS}} is Yes):
   - Unreviewed field suggestions / review completion count.
   - Missing or unverified counterparties.
   - Opening-balances / reports-ready flags when the system exposes them.
   - Open tasks relevant to the entity.
   - Email connector (if available): recent thread subjects with the client, paraphrase only.
7. **Draft talking points** in confirmed {{BRIEF_FORMAT}}: 5-8 bullets mixing financial
   highlights, bookkeeping health, open items, and questions for the client. Ground every number in
   steps 4-6.
8. **Deliver the brief** using the template. End with: this run was **read-only**, nothing was
   changed in the books.

### Output template

```markdown
# Meeting Prep Brief: [Entity] ([Meeting date or "Upcoming"])
Mode: [Books-only | Books + calendar | Books + calendar + email] · Lookback: [dates] · Basis: [cash|accrual]
**Read-only: figures cited below; nothing changed in the books.**

## Meeting context
- [Last meeting: date from calendar OR "Unknown (used confirmed {{LOOKBACK_DAYS}}-day lookback)"]
- [Next meeting: from calendar OR "Not scheduled in connected calendar"]

## Financial highlights (from [start date] to [end date])
| Metric | Current window | Prior window | Δ | Source |
| --- | --- | --- | --- | --- |
| Revenue | … | … | … | profit and loss [dates] |
| Net income | … | … | … | profit and loss [dates] |
| Cash (as of [date]) | … | n/a | n/a | balance sheet [date] |
- [Clearing / transfer-in-transit balances excluded from liquidity read, if any]

## Bookkeeping health
| Check | Count / status | Source |
| --- | --- | --- |
| Unreviewed items | … of … reviewed | statistics |
| Missing / unverified counterparties | … | statistics |
| Opening balances ready | Yes / No | entity metadata |
| Reports ready | Yes / No | entity metadata |

## Anomalies to discuss
| Item | Amount / count | Why it matters | Source |
| --- | --- | --- | --- |

## Open items
- Tasks: …

## Suggested talking points
1. …
2. …

## Skipped (no connector)
- [List each omitted enrichment and why (only in books-only or partial mode)]
```

## Working with your data

This skill reads from whatever accounting system is connected, and may enrich from calendar/email
when available. If you have documented bindings for those systems, use them. Otherwise:

### Unknown connector

1. List the available tools and read their schemas and descriptions.
2. Map them to the data needs above (P&L, balance sheet, transactions, tasks, optional
   calendar/email). Anything with no plausible tool is marked UNSUPPORTED.
3. STOP and show the user the mapping, and get confirmation, before any read beyond discovery.
   This skill performs no writes to the books.
4. Never guess tool names. If the system exposes guide or skill discovery tools, load the relevant
   financial-reports and transaction-query guides first.

## Guardrails

- **Draft first, ask second (advisory reads):** deliver with labeled default assumptions rather
  than blocking on a parameter interview; ask first only for material ambiguity.
- **No silent defaults:** label every assumed default inline in the deliverable.
- **Read-only.** No write or act tools against the books.
- **Graceful degradation:** calendar/email enrichments are optional; books-only output is complete
  and useful.
- **Premise mismatch:** if books contradict the user's expectation, report actuals, probe at most
  one adjacent period, then ask.
- **No tax or filing advice** presented as authoritative.
- Round to cents; ignore variances below $0.01.
- **Tool errors and drift:** if a live call is rejected, trust the live error hint (and any loaded
  guide) over this skill's examples; fix the call and retry once. If the working shape contradicts
  this skill's text, record the discrepancy in the deliverable's method notes. Never edit this
  skill file mid-run.

## Worked example

_Figures below are illustrative: never quote them as live data; every delivered number must come
from the current books._

> "Prep me for tomorrow's client meeting with Birch & Co, what moved in the books since March and
> what should I ask about?"

**Setup ask (partial, user already named period):** "Materiality floor for anomalies? (Suggested:
$1,000.) Include open tasks and bookkeeping health? Format?" → User: "$1,000, yes, one-page
executive." → proceed (skip {{LOOKBACK_DAYS}}, user said "since March").

1. Detect connectors → calendar unavailable → **Books-only mode** (note in deliverable).
2. Confirm the books for Birch & Co; accrual basis.
3. Lookback: user said "since March" → March 1 through today.
4. Revenue up 12%; flag Software +$3,400 vs prior window; transfer-clearing $8,200 called out and
   excluded from cash read.
5. Bookkeeping health: 18 unreviewed field rows; 42 missing counterparties; reports ready = true.
6. One open "Map new Amex account" task.
7. Brief with highlights, health table, anomalies, talking points, and **Skipped:** calendar
   last-meeting date, email threads.

## Common pitfalls

- Failing the brief when calendar/email is missing: always produce books-only output.
- Treating bank-transfer-clearing balances as spendable cash.
- Omitting the **Skipped (no connector)** section in books-only mode.
- Guessing last meeting date without calendar data when the user did not name a period.

## Related skills

- Custom management report: full monthly pack.
- Client dashboard snapshot: point-in-time metrics card.
- Period P&L flux analysis: deep variance memo.

## Feedback and improvement

This copy of the skill belongs to the person running it, and it should get better
with use.

- **During a run:** when the user corrects an assumption, an output, or a preference
  (tone, format, thresholds, account or entity choices), apply the correction
  immediately and keep it for the rest of the run. A correction never overrides the
  safety contract: previews, confirmations, and figures-from-reads always stand.
- **Between runs:** when a correction should stick, offer to save it. With the user's
  explicit approval, add a dated entry under `## Learned preferences` at the end of
  this file, creating that section if it is missing. Newer entries beat older ones.
  Never edit this skill file mid-run, and never change the Guardrails, Tools used, or
  safety wording: preferences and defaults only. A preference is declined, not saved,
  when honoring it on a future run would loosen any Guardrails line or the safety
  contract, even though it leaves their text untouched. If this file is not writable
  where the skill runs, give the user the entry text to save wherever they keep their
  instructions.
- **Improving the original:** if someone sent the user this skill, end the deliverable
  with one plain-English line describing what worked differently or which preference
  was saved (inside the deliverable's method notes, when this skill's output template
  has them), and ask them to forward it to whoever maintains the original copy.
