---
name: deliver
description: "Assembles the close package: final statements, the close memo (a Word document opening with the executive summary), and a workpapers workbook. Use after review returns ready, or on the user's explicit choice to build a clearly labeled interim package when it has not."
---

# Deliver

## Purpose

Turn a reviewed close into the deliverable. Every figure in the package traces to the
adjusted trial balance; the package contains nothing the close did not prove.

1. Financial statements with prior-period comparatives
2. Close memo as a Word document, opening with the owner-facing executive summary
3. Workpapers workbook, one Excel file
4. Everything named and filed in `package/`, follow-ups and profile updates closed out

## Procedure

- [ ] 1. Verify the precondition: a review report from the review skill with a **ready**
      verdict that is current against the books and workpapers.
      Staleness is judged by content, not file dates: the report records the figures it reviewed and is stale when the books or the other workpapers (the report itself excluded) no longer match them. No report, a not-ready verdict, or a stale report: stop and say so.
      Gather the close folder (adjusted TB, workpapers, JE register, review report, exceptions register) and the client profile for deliverable preferences (naming, emphasis, recipients) when it exists.
- [ ] 2. Build the statements from the adjusted TB: P&L, balance sheet, and cash flow
      (indirect), each with prior-period comparatives when a prior TB exists.
      Formats in `reference/close-package-format.md`. Retained earnings proof: prior equity plus net income ties to the balance sheet.
- [ ] 3. Build the workpapers workbook, one Excel file: a summary tab listing every
      material account with its support, linked to one tab per area (each reconciliation
      proof, each schedule, the JE register, the cleanup list).
      Summary tab figures reference the detail tabs; nothing is retyped.
- [ ] 4. Write the close memo as a Word document (.docx), never markdown.
      It opens with the executive summary for the owner: plain language, the three to five things that mattered this period, flux highlights with their drivers, and cash position. Then the preparer's sections: scope and basis, what was reconciled, entries booked (count and total), open items and accepted exceptions, the review verdict, and a sign-off checklist with the preparer and reviewer lines. One document serves both readers; there is no separate executive summary file.
- [ ] 5. Name and file everything in `package/` per the file set in `reference/close-package-format.md`.
      If a cloud storage or docs connector is available (Drive, OneDrive, Notion, SharePoint), offer to save the package and the updated profile there too; a connected store is durable across sessions and visible to teammates, which the session workspace is not. The workspace copy remains the working copy; note where the shared copy went in the memo and the close log when one is kept.
- [ ] 6. Close out: note the delivery date and post-close follow-ups (accrual reversals
      due next period, aging investigate items, schedule updates such as new assets or
      new deferral contracts) in the memo, and in the close log when one is kept.
- [ ] 7. Offer the profile update: one short list of things learned this close (new
      recurring items, coding conventions, a threshold the user corrected). Save to the
      profile file only what the user explicitly approves.
- [ ] 8. In a single-client project, end with the knowledge sync list: the files worth
      adding or refreshing in the project's knowledge, each with a one-line reason.
      Typically the profile (if it changed) and the close memo. Agents cannot write to project knowledge; the user adds these, so name the exact files and paths to make it a ten-second job. Workpapers and the close log stay out of knowledge on purpose: per-period audit artifacts, not standing context.

## Guardrails

- Never package silently past a missing, failed, or stale review.
- **Delivering not ready is a real path, not an edge case.** On the user's explicit
  choice, build the interim package: the same artifacts, with the memo and cover leading
  with NOT READY and the blockers named, every statement labeled draft, and the memo's
  executive summary opening with what these numbers cannot yet prove rather than burying
  it. The override is recorded in the memo and the close log when one is kept. An interim
  package that reads like a finished one is the failure; the label is the product.
- The package reports the close as it is. No figure is adjusted, smoothed, or
  reclassified at packaging time; a late find goes back through adjustments and review.
- Statements come from the adjusted TB alone, never from partially updated sources.
- The executive summary simplifies language, never numbers.
- Degradation: no prior TB, statements without comparatives and the memo says so. No
  cash flow inputs (no prior balance sheet), deliver P&L and balance sheet and state why
  cash flow is omitted. No client profile, default naming and a standard package; offer
  setup afterward.
- Packaging is mechanical; the judgment already happened. The only questions worth
  asking are presentation preferences, and only when the profile does not answer them.
  Running unattended, use the defaults and note them.
- Voice, for every document this skill writes: a careful accountant's prose, not an
  assistant's. Short declarative sentences with varied length, sentence-case headings,
  concrete nouns and real figures. Banned tells: em dashes; filler words (delve, robust,
  seamless, leverage, comprehensive, crucial); the "not just X, but Y" construction;
  AI boilerplate ("It's important to note"); decorative emoji; bolded keyword openers
  in prose. If no accountant would say a sentence aloud to a client, rewrite it.

## Example

The handover block, posted in chat when the package is filed:

```markdown
### Close package: <client>, <period>

**Delivered:** <file list with paths>
**Statements:** <P&L net income, BS total assets, cash flow net change>
**Entries booked:** <count, total>
**Open items:** <disclosed exceptions and follow-ups, or none>
**Verdict packaged under:** <ready / user override, logged>
**Profile updates offered:** <saved / declined / none>
```

## Completion

Done when:

- [ ] Every statement line traces to the adjusted TB; statements foot and cross-foot
- [ ] Balance sheet balances, and retained earnings proves
- [ ] Workbook summary tab covers every material account with a link to its support
- [ ] Memo discloses every open item and accepted exception from the register
- [ ] The memo is a Word document that opens with the executive summary
- [ ] Files are named to convention and filed in `package/`

Cleanup: post the handover block with every path; offer the cloud save, the profile
update, and the knowledge sync list; follow-ups land in the memo and the close log when
one is kept. Nothing stays only in chat or working memory.
