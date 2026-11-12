# Revenue finder report

The deliverable is a PDF. Chat carries the handoff lines and the file. The engine carries
the brand and enforces the skill's hard rules. This file says what goes into the payload.

Run from the user's working folder, never from the skill folder, and keep the payload
there too. `pip install reportlab` if it is missing.

```
python3 <skill folder>/references/templates/build_report.py harbor-fabrication-revenue-finder.json
```

Name the payload `<client>-revenue-finder.json` in kebab case. The PDF takes the same name
beside it. A payload that breaks a rule prints `error:` with the reason and writes no file:
fix the finding (cut it, move it, or source it), never the engine. If the build warns that
Inter is missing, do not hand the file over. Quote the printed `result=` and
`unread_meetings=` lines in the handoff, and name every `promised_not_in_scope=` line;
do not recount them in chat. Each `method_note=` line goes last in the handoff, after
the file, as "Method note: ..."; the PDF never shows it.

## Payload

Dates in date fields are YYYY-MM-DD; the engine prints every date on the page as
"Dec 12th, 2025", in prose fields too, and leaves quotes as spoken. The chat handoff
writes dates the same way.

```
client          the client's name, as the firm knows them
firm            optional, the firm's name for the header
window          {start, end} as YYYY-MM-DD
catalog         {kind: "firm" or "generic", source, services}
                source is where the catalog came from ("Ping services catalog",
                "services.pdf"). services is the count of services matched against
candidates      how many candidates entered the four cuts (the M in "from M
                possibilities reviewed")
coverage        {sources: [{name, read, unread, note}], unread_meetings, ledger,
                 ledger_ties}
                one row per source: Meeting transcripts, Email, Notes, Portal, Chat.
                The Email note names whose mailbox it is; unread counts bodies that
                would not load. unread_meetings is the calendar meetings in the
                window with no readable transcript, 0 when none. ledger is "Kick,
                accrual basis, Nov 2025 to Oct 2026" or null when no books were read.
                ledger_ties is false when the books failed the tie check
opportunities   at most five, each:
                  service       the catalog's name for it
                  annual_value  from the firm's price list, or null. Monthly x 12,
                                annual x 1, one-time fees not counted. A per-unit
                                price counts one unit, and the why says "at one
                                unit". Always null on a generic catalog
                  score         3 named the need, 2 described the situation
                  quote         the client's own sentence, verbatim, no stitching
                  speaker       the person who said it, name and role: "Priya Nand
                                (owner)"
                  source_kind   transcript, email, chat, portal, or note
                  source        a pointer a person can follow ("Call, Q3 review",
                                "Email: Re: October close")
                  date          YYYY-MM-DD
                  link          optional, a timestamp link to the moment
                  why           one sentence tying the quote to the description
                  ledger        {state: corroborated, contradicted, or none,
                                 detail: figure, report, period}
                  next_step     the specific conversation to have
                  support       optional, at most two backing lines:
                                [{text, speaker, source_kind, source, date}]. A
                                second client quote or a colleague's note
inference       [{service, reason}], score-one rows, labeled as the runner's own
raised_before   [{service, kind, detail, date}]. kind is declined, pitched (left
                open), promised, promised_not_in_scope, or in_scope. The engine
                prints promised_not_in_scope first, in red, as possibly unbilled
referrals       [{need, quote, speaker, date, source}], needs the firm does not sell
ledger_signals  at most three [{signal, figure, source, question}], from the books,
                no client quote behind them
could_not_see   at most three [str], gaps the coverage table does not already show
                (an unreadable attachment, a report that failed). Never repeat a
                coverage row
method_notes    [str], any step that worked differently than the skill describes,
                including a Ping or Kick tool that differed from its binding. Not
                drawn on the page; the engine prints them for the chat handoff
```

## Word limits

The report is read in a minute. The engine refuses any field over its limit and names
the field; cut words, keep the fact and its source.

| Field | Words | Field | Words |
| --- | --- | --- | --- |
| quote | 40 | coverage note | 10 |
| why | 15 | ledger signal: signal / figure / question | 6 / 10 / 15 |
| next_step | 15 | raised_before detail | 15 |
| ledger detail | 20 | referral quote | 25 |
| support text | 20 | inference reason, could_not_see line | 15 |
| method note (at most five) | 20 | | |

Write a ledger detail as figure, report, period: "Construction in progress $185,000 at
2026-10-31; none a year earlier (balance sheet)."

## What the engine refuses

- More than five opportunities.
- A score of one, or a note scored three.
- An opportunity missing its quote, speaker, date, source, why, or next step.
- The same quote on two opportunities.
- A price on a generic catalog.
- A ledger line or ledger signal when no ledger is named in coverage.
- A coverage block without the unread-meeting count.
- Any ledger line other than none, or any ledger signal, when `ledger_ties` is false.
- More than three ledger signals, more than two support lines, or a raised-before row
  without a kind.
- An email address anywhere in the payload. Name people by name and role.
- Any field over its word limit, or more than five method notes.

## The page

In order:

1. Title "Revenue finder: <client>", then the window and the catalog line. A generic
   catalog says so here and in the result line.
2. The result line: "N opportunities found, from M possibilities reviewed", the top finding, and the highest value, or "ranked on
   quote strength alone" without prices.
3. Headline tiles: opportunities, combined annual value at the firm's prices (when priced),
   promises outside the agreements (when any), and calendar meetings not read.
4. A "Possibly unbilled" callout for each promised_not_in_scope row.
5. One card per opportunity: rank, service, and annual value; an evidence-strength badge
   and a books badge; the quote with speaker, source, and date; any support line; then
   Why, Books, Next.
6. Coverage: one row per source with read and could-not-read counts, the unread-meeting
   sentence, and the ledger line.
7. From the books: questions to ask. My inference, not the client's words.
8. Raised before (promised_not_in_scope rows appear in the callout instead), Referrals out,
   What I could not see.

The footer on every page: read only, nothing written, no client contacted, a discussion
prompt and not a proposal.
