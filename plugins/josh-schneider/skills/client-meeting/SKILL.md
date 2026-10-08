---
name: client-meeting
description: "Prepares a one-page client meeting brief from the books: financial highlights since the last meeting, open bookkeeping items, anomalies, and suggested talking points, with optional enrichment from the user's calendar and email connectors when available. Use when the user asks to prep for a client meeting, meeting brief, what should I cover with this client, client check-in prep, or talking points before my call. Degrades gracefully to books-only mode when calendar or email connectors are absent. Read-only against the books."
---

# Meeting prep brief

## Purpose

Prepare a one-page, read-only meeting brief from the books for a qualified professional to
review before a client call, with every figure cited to its source; it is meeting prep, not
financial advice. Not for full management report packs, deep flux analysis, or firm-wide
morning digests.

1. Meeting context: last and next meeting.
2. Financial highlights for the window, against the prior equal-length window.
3. Bookkeeping health.
4. Anomalies to discuss.
5. Open items.
6. Suggested talking points.
7. Skipped (no connector), in books-only or partial mode.

## Procedure

Copy this checklist into the response and check items off.

- [ ] 1. Set defaults without blocking the brief.
      Defaults: 90-day lookback, $1,000 anomaly floor, one-page executive format (or bullet checklist, or narrative memo), open tasks and bookkeeping health included.
      Proceed on the defaults and label each inline: "_Assumed: 90-day lookback, $1,000 anomaly floor, one-page executive format, tell me if any should change_".
      Ask first only when scope or entity is ambiguous enough to change the answer. Unattended runs proceed on labeled defaults.
- [ ] 2. Detect connector mode before using any calendar or email data.
      Use the calendar or email connector only if it is present in the session. Absent, or an auth or availability error: books-only for that source, noted for the Skipped section.
      Books on Kick: follow [references/kick.md](references/kick.md).
      Unknown books connector: list the tools and read their schemas, map them to the data needs (P&L, balance sheet, transactions, tasks), mark anything unmatched UNSUPPORTED, and show the mapping for confirmation before any read beyond discovery. Load the system's financial-reports and transaction-query guides first when it offers guide discovery. Never guess tool names.
- [ ] 3. Orient to the books.
      Confirm the set of books and the ledger basis. More than one match: list candidates and ask. A single ledger: use it and state it.
- [ ] 4. Set the lookback window.
      User-named start ("since March", "from Q1", "last 60 days"): use it and skip the lookback default.
      Calendar returns a last meeting with this client: the day after that meeting through today, or through a user-named end date.
      Neither: the confirmed lookback ending today, labeled inline. Lookback still unanswered: ask once; never run a silent window.
      Also set the prior equal-length window for the P&L comparison when practical.
- [ ] 5. Pull financial highlights for both windows.
      Revenue, gross profit when available, and net income from the P&L; cash from the balance sheet.
      A large balance in a bank-transfer-clearing or transfer-in-transit account usually means an unmatched internal transfer: call it out separately and exclude it from the liquidity read.
      Note credit-card balance growth as a cash-flow driver when material.
- [ ] 6. Flag anomalies for the agenda.
      Material P&L line swings: |Δ| ≥ the confirmed anomaly floor, OR (|Δ%| ≥ 10% AND |Δ| ≥ $100).
      Large one-off transactions, sorted by amount.
      Suspected duplicate imports, flagged separately.
- [ ] 7. Check bookkeeping health and open items, unless the user turned them off.
      Unreviewed items and the review completion count.
      Missing or unverified counterparties.
      Opening-balances-ready and reports-ready flags when the system exposes them.
      Open tasks for the entity.
      Email connected: recent thread subjects with the client, paraphrased only.
- [ ] 8. Draft talking points.
      5 to 8 bullets in the confirmed format, mixing highlights, bookkeeping health, open items, and questions for the client. Every number comes from steps 5 to 7.
- [ ] 9. Deliver the brief in the Example format.
      End with: this run was read-only; nothing was changed in the books.

## Caveats

- **Failing on a missing connector:** the brief stops or errors because calendar or email is absent. Books-only output is complete and useful; always produce it.
- **Missing Skipped section:** the header says Books-only or partial, but no Skipped (no connector) section lists what was omitted and why. Add it every time.
- **Guessed last meeting date:** a last-meeting date appears with no calendar source and no user-named period. Write "Unknown" and use the confirmed lookback.
- **Clearing balance read as cash:** the cash figure includes a transfer-clearing or in-transit balance. Exclude it and call it out on its own line.
- **Silent defaults:** an assumed value appears with no inline label. Label every assumed default.
- **Premise mismatch:** the books contradict what the user expects. Report actuals, probe at most one adjacent period, then ask.
- **Writes:** read-only. No write or act call against the books, ever.
- **Advice:** no tax or filing advice presented as authoritative.
- **Precision:** round to cents; ignore variances below $0.01.
- **Illustrative figures:** numbers in [references/examples.md](references/examples.md) are never quoted as live data; every delivered number comes from the current books.
- **In-run corrections:** when the user corrects a default, format, threshold, or entity choice, apply it immediately and keep it for the rest of the run. A correction never loosens read-only or figures-from-reads.
- **Tool errors and drift:** a rejected live call follows the drift rule in [references/kick.md](references/kick.md). Record any discrepancy in the brief's Method note.

## Example

```markdown
# Meeting prep brief: [Entity] ([Meeting date or "Upcoming"])
Mode: [Books-only | Books + calendar | Books + calendar + email] · Lookback: [dates] · Basis: [cash|accrual]
**Read-only: figures cited below; nothing changed in the books.**
_Assumed: [each default used], tell me if any should change_

## Meeting context
- [Last meeting: date from calendar OR "Unknown (used confirmed [N]-day lookback)"]
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
- [Each omitted enrichment and why, only in books-only or partial mode]

## Method note
- [Only when a step worked differently than this skill describes]
```

A worked run, books-only, is in [references/examples.md](references/examples.md).

## Completion

Done when:
- The brief follows the Example format, with mode, lookback dates, and basis on the header line.
- Every figure cites its report and dates, or its source.
- Every assumed default is labeled inline.
- Clearing and transfer-in-transit balances sit outside the cash read and are called out.
- Books-only or partial mode carries a Skipped (no connector) section naming each omission.
- Anomalies apply the confirmed floor and the 10% and $100 rule.
- Talking points number 5 to 8, and every number traces to steps 5 to 7.
- No write call was made, and the brief ends with the read-only line.

Cleanup: the brief goes to the user in the response. Questions for the client sit in the talking points. Tool discrepancies go in the Method note. Nothing is saved to the books.
