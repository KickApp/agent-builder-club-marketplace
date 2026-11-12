---
name: revenue-finder
description: "Reads what a client actually said in recorded meetings, email, chat, and notes (through Ping when it is connected), matches it against the services the firm sells, checks each match against the client's books on Kick, and delivers a PDF of at most five advisory and cross-sell opportunities, each backed by a quote where the client states the need. Read-only: never writes anything, never contacts a client. Use when someone asks what else they should be selling a client, which services fit a client's needs, where the revenue is hiding in a client relationship, or what a client has been asking for. Not for pre-meeting talking points, and not for anything that writes to the books."
---

# Revenue finder

## Purpose

Find the services a client already asked for in their own words, so the person who owns the relationship can decide whether to raise them. The filtering is the deliverable: search returns most of the catalog, and the value is in what gets cut. The report is a PDF.

1. Result and coverage, including the meetings that could not be read
2. At most five opportunities, each with the client's quote, the ledger check, and a next step
3. From the books: questions to ask, never ranked as opportunities
4. Raised before, referrals out, what I could not see

Ping execution lives in [references/ping.md](references/ping.md). Kick execution lives in [references/kick.md](references/kick.md). The payload and the page live in [references/report.md](references/report.md). Good and bad runs are in [references/examples.md](references/examples.md).

## Procedure

- [ ] 1. Confirm the client, the window, and the services catalog in one line, then move.
      Window default: 12 months ending today; state the default. The firm name comes from the connector's organization record or the firm profile; leave it blank otherwise. Catalog: the firm's own, with a description per service. On Ping, read it from Ping. Otherwise ask for a services document.
      A bare list of names is not enough; matching reads the client's sentence against the description, not the title.
      No catalog: offer [references/generic-services.md](references/generic-services.md) and label every result "generic catalog". Never invent or silently extend a catalog.
- [ ] 2. Discover sources. List the available tools and map them to three questions: what did the client say, when did we talk, what do they already pay for or have in scope.
      Ping connected: follow references/ping.md. Books on Kick: follow references/kick.md. Any other system: read the tool schemas and map them the same way.
      Anything with no plausible tool is UNSUPPORTED; name it and move on. Never guess a tool name.
- [ ] 3. State coverage before reading: count what is readable per source, and count the calendar meetings in the window that have no readable transcript. Show the mapping and the counts, and get confirmation.
      Name whose mailbox is connected. An email whose full body will not load counts as could-not-read, never as read.
- [ ] 4. Pull the corpus. Resolve the client's contacts first, then pull by contact address and client record, never by a keyword sweep of the whole mailbox.
      Read in this order: transcripts, then notes and portal questions, then email and chat. Read whole threads and the full transcript passage; a snippet can reverse in the clause not shown.
      Then search within the corpus per service, using words from each description.
- [ ] 5. Run every candidate through the four cuts, in order (see Caveats). If a tool returns a confidence rating or a match score, ignore it; score from the quote alone.
      A candidate is one service paired with one moment, from a tool's match list or your own search. Count every candidate that entered cut one; that count is the possibilities reviewed in "N opportunities found, from M possibilities reviewed". Referrals, lines no service was paired with, and support lines (a note or second quote backing a moment already counted for that service) are not candidates.
- [ ] 6. Pull the surrounding context for each survivor and confirm the quote means what the snippet suggested. Check the speaker in the transcript or the email's From line, not the thread title. A quote is up to three consecutive sentences from one speaker in one moment. Never stitch fragments from different moments into one quote.
- [ ] 7. Corroborate each survivor against the client's books where a ledger is connected, or mark it "no ledger signal". A contradiction is a finding, never a reason to drop the row.
      First check that the books tie (see Caveats). Books that do not tie corroborate and contradict nothing. A report that still fails after its one retry is unread: name it in What I could not see and mark the lines that needed it "no ledger signal".
      From the same reads, list at most three ledger signals with no client quote behind them as questions to ask. They are never opportunities.
      A second quote or a note that backs a survivor goes on that finding as support, never as its own candidate.
- [ ] 8. Score each survivor 3 (named the need) or 2 (described the situation). A 1 goes to the inference section or is cut.
      Rank by score, then by annual value from the firm's price list, never by value alone. Cap at five; more than five survivors means the cuts were too soft, so raise the bar and rerun step 5. Zero findings is a valid result.
- [ ] 9. Build the PDF. Write the payload in the user's working folder, never in this skill folder, named `<client>-revenue-finder.json` in kebab case. Follow references/report.md.
      Keep every field inside the word limits in references/report.md; the reader gives the report a minute.
      From the working folder, run `python3 <this skill folder>/references/templates/build_report.py <client>-revenue-finder.json`. A refused payload names the broken rule; fix the finding, never the engine.
- [ ] 10. Hand off in chat: the result line, the coverage line with the unread-meeting count, the top finding's service and quote, any work promised but not in scope, and the file. Say it is a discussion prompt, not a proposal. Do not paste the report into chat. Any method note goes last, after the file.

## Caveats

- **The four cuts, applied in order, every candidate.** One: the quote must contain the need; a sentence that merely contains a related word is not evidence. Two: the client is the speaker and the tense is present; cut firm staff, the client's past, and internal sales talk. Three: one quote serves one service. A moment that fits several services equally is evidence for none; when one service's description clearly fits it best, it serves that service and every other use is cut. Four: not already handled; in scope, promised, or declined gets cut and moves to Raised before. Raised before lists only services that came up as candidates, one row per moment; an in-scope service nobody mentioned is not listed.
- **What cut four means.** In scope: the client's agreements list the service, or, with no agreement on file, a transcript has both the firm and the client name it as the current regular work. Promised: firm staff said they will do the work, or an open action item says so; "I'll send details" is not a promise. Declined: the client said no. Pitched and left open ("let me think about it"): Raised before, and an opportunity only when the client also stated the need in their own words, with the earlier pitch named in the next step.
- **Promised but not in scope.** Tell: a promise or open action item for a service the agreements do not list. Rule: it goes to Raised before marked promised, not in scope, and the handoff names it. The work may be unbilled.
- **Books that do not tie.** Tell: expense lines or totals with the wrong sign, a balance sheet that does not balance, or P&L net income that differs from the change in total equity for the same period, after owner contributions and distributions (see references/kick.md). A negative bank balance alone is not a tie failure; it is a ledger signal. Rule: set `ledger_ties` to false, every ledger line reads "no ledger signal: the books did not tie", no ledger signals are listed, and What I could not see and the handoff say the books need review. Never mark a finding contradicted on books that do not tie.
- **Ignore tool confidence ratings.** Tell: a search returns most of the catalog as high confidence. A stress test returned 20 of 26 services as high confidence, including a row whose own evidence said no mentions were found. Rule: score from the quote and nothing else.
- **Ones do not ship.** A score of one means you are connecting the dots. It goes in the inference section labeled as yours, or it is cut.
- **Quotes are the only admissible evidence.** Every finding carries the client's own sentence, the speaker, the date, and a pointer to the source. A note is a colleague's summary, labeled as a note, and never scores three. Unsourced findings do not ship. Name speakers by name and role, never by email address.
- **Silent coverage.** Tell: a confident report on a client mostly reached by phone, with no note that the calls went unread. Rule: coverage and the unread-meeting count sit in the result block, never in a footnote.
- **Misattributed email.** Tell: a line attributed to the client sits under a quoted reply header, or the thread's last sender is the firm. Rule: quoted reply chains put the client's name above your own words. Read the whole thread and attribute from the line's own From header.
- **Firm staff speaking.** Tell: the quote is the firm's partner pitching a service, or the client only agreeing ("sure, maybe"). Rule: cut two removes it. Agreement to a pitch is not a stated need.
- **Never state a price the user did not supply.** Without prices, drop the dollar figures and rank on quote strength alone. A generic catalog never carries a price.
- **A service the firm does not sell is a referral**, never an opportunity.
- **Ledger-only signals.** Tell: an opportunity whose only evidence is a number in the books. Rule: the books corroborate or contradict what the client said. A signal with no quote goes under From the books as a question, with its figure and report, and is never ranked.
- **Figures from reads.** Every ledger figure comes from a named report and period. Never compute a figure the report did not return beyond a stated sum or ratio of returned figures.
- **This is a discussion prompt, not a proposal.** The reader decides what to raise and whether to raise it at all. Say so in the output.
- **Read-only.** No write call to any system, no drafted email sent, no task created, no client contacted.

## Example

The page, laid out as in references/report.md. Chat carries only the handoff.

```markdown
# Revenue finder: [Client] ([window])

**Result:** [N] opportunities found, from [M] possibilities reviewed. Top finding: [service], [strength]. Highest value: [service], about [$X]/year.
**Coverage:** read [n] transcripts, [n] emails, [n] notes. Could not read [n] meetings
on the calendar in this window. Ledger: [system and basis, or "not connected"].

## [Service name] · [$X]/year · [Named the need | Described the situation]
> "[the client's own words]"
> [Speaker], [source], [date]
**Why:** [under 15 words tying the quote to the service description]
**Books:** [Corroborated | Contradicted | No ledger signal]. [figure, report, period]
**Next:** [the conversation to have, under 15 words]

## From the books: questions to ask
| Signal | Figure | Source | Question to ask |

## Raised before / ## Referrals out / ## What I could not see
```

Handoff in chat:

```markdown
2 opportunities found for Harbor Fabrication (Nov 2025 to Oct 2026), from 14 possibilities reviewed. Top finding:
Payroll, "I need someone to just take payroll off my plate" (Dana Ruiz, call, Aug 14th, 2026).
Could not read 3 calendar meetings. A discussion prompt, not a proposal.
File: harbor-fabrication-revenue-finder.pdf
```

## Completion

Done when:

- [ ] Every finding carries a quote, speaker, date, and source pointer
- [ ] At most five findings; no score-one rows outside the labeled inference section
- [ ] The result block states coverage, including meetings that went unread
- [ ] A generic-catalog run is labeled "generic catalog" on its face and shows no prices
- [ ] Every ledger line and ledger signal names its report and period
- [ ] The PDF was written by references/templates/build_report.py into the user's working folder, and the build log has no Inter warning
- [ ] Nothing was written anywhere and no client was contacted

Cleanup: hand the PDF path and the handoff lines to the relationship owner in chat. Record the services catalog's location in the handoff so the next run reads it instead of asking. Tool discrepancies go in the method note at the end of the handoff, never in the PDF. Nothing else persists.
