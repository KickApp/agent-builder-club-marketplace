---
name: ping-client-meeting
description: "With Ping connected, either prepares a brief for one upcoming client meeting (what was discussed last time, open action items, what the client cares about, recent calls and email, unusual swings in the Kick ledger, and upsell and cross-sell talking points from Ping Insights and the ledger) or writes an end-of-day recap of every client call and email from today with the commitments made. Read-only, nothing is sent. Use when someone who has Ping connected asks to prep for a client meeting or call, wants a brief before talking to a client, or asks for a recap of today's client calls and emails."
---

# Ping client meeting

## Purpose

Give the accountant what to say in a client meeting, or what happened today, from the
client's own words in Ping and the numbers in Kick. One skill, two modes:

1. Prep brief for one upcoming meeting: an agenda for the call, questions to ask, what
   is still open on each side, and what to watch out for
2. End-of-day recap: per client, what happened today, what is still open, and what to
   watch out for

Every line cites its source: the meeting, email, note, or Kick report it came from.

## Procedure

- [ ] 1. Pick the mode from the request.
      Prep: a client or meeting is named ("prep", "brief", "before my call with").
      Recap: "recap", "end of day", "what happened today", no client named.
      Unclear: ask once. No answer: a named client means prep, otherwise recap.
- [ ] 2. Discover the Ping tools, then load `references/ping.md`.
      Ping is a required connector. Not connected: say so and stop.
- [ ] 3. Prep: resolve the client in Ping and in Kick, then find the meeting.
      The next scheduled meeting with the client within 14 days. None: say so and
      brief anyway. Note the most recent past meeting and whether it has a transcript.
- [ ] 4. Prep: read the conversations.
      Window: the 90 days ending today, today included, plus the latest transcript
      even if older. Read every
      transcript in the window, every email body, the client notes, portal posts, and
      action items. Open each email in full, routine ones too; a snippet is not a read.
      Count meetings with and without a transcript.
- [ ] 5. Prep: pull the books per `references/kick.md`.
      Ledger and closed-through date, P&L by month, balance sheet at the end of the
      latest month and the day before the P&L window, expenses by vendor for 12 months. Check that both balance sheets balance.
- [ ] 6. Prep: find the swings and the opportunities with the thresholds in `references/kick.md`.
      At most three swings and five opportunities as candidates for the agenda. Each
      opportunity needs a ledger signal that meets its threshold, or a client's own
      words, and a service not in scope.
      A client's request for numbers ("bring the October numbers") becomes an agenda
      item, answered from the reads.
- [ ] 7. Recap: list today's meetings and find the clients in them.
      Read each transcript, and each email body from today for those clients, or for
      every client when Ping can list them. When it cannot, one Watch out for line says
      email from other clients was not read. Skip clients with no activity.
      Today only: older open items belong to the prep brief. A client with a meeting
      tomorrow gets one line naming it. A client request nobody answered today goes
      under "We owe" as "asked today, not yet confirmed".
- [ ] 8. Recap: pull a Kick figure only where today's conversation asked about a number
      or asked us to send or bring numbers. One report per request, from `references/kick.md`.
- [ ] 9. Write the deliverable in chat in the format of `references/examples.md`.
      Prep: three to five agenda items, the client's own asks first, then open items,
      then Kick numbers and opportunities. At most 40 words per item after its title. Pick the strongest; the rest stay out.
      Number every source and end each line with its number. Markdown, no file unless
      asked. End with the one-line Read note.

## Caveats

- **Quoted text has its own author.** Lines under "On ... wrote:" or starting with ">"
  belong to the quoted sender. A search snippet is never attribution. Open the full email
  or transcript line, and name the person who actually said it. In a client's email,
  "we" means the client's business, not the firm.
- **A meeting with no transcript is not read.** Say so, use the notes or email from that
  day, and label them as notes. Never reconstruct what was said.
- **Ping status can lag.** An action item marked open that a later email shows done is
  listed as "probably done, confirm and close in Ping", with the email date.
- **A ledger figure is not evidence about an action item.** Tie a number to an item only
  when a read names the link (an email, a note, a transaction memo). A swing that might
  relate to an item is raised as a swing, on its own line.
- **Ping confidence ratings are ignored.** A Ping Insight becomes a talking point only
  when a client contact's own words back it. "No mentions found" means no evidence.
- **Opportunities are questions, never advice.** Write "worth exploring whether ...". Never
  say the client qualifies, never estimate a credit or a saving, never give a tax position.
- **Seasonal is not unusual.** A swing that repeats in the same month last year is noted
  once as seasonal and is not raised.
- **Cloud spend means cloud platforms.** An Amazon marketplace purchase booked to
  supplies is not cloud spend. Count only the vendors and accounts `references/kick.md` names.
- **Figures come from reads.** Every number in the deliverable appears in a read. Show
  the read figures side by side and let the user compare them. No averages, ratios,
  percentages, or month counts the run worked out itself. Thresholds are checked, not
  printed.
- **Read-only.** Never draft, send, or create anything in Ping or Kick. The recap is text
  for the user to send or not.
- **Books that do not balance or are not closed** go under Watch out for, and their
  numbers are labeled unreviewed.
- **The deliverable has no em dashes.** Use a comma, colon, or period. Refer to people
  by name and to the user as "you", never "he" or "she". The mailbox owner and the
  author of the user's own notes are "you". Turn "by Monday" into a date.
- **No email addresses in the deliverable**, the Read note included. Name the person
  or the mailbox owner instead.
- **One Ping client, several businesses.** Tell: the Ping client is a person, and the
  conversation names several companies. Rule: use the Kick entity whose name matches the
  Ping client. None or several: ask which. Name the entity in the Read note, and tie its
  figures to a business the conversation names only when a read links them.
- **A tool the reference files do not list is not a defect.** Use it if it fits, and
  name it in the Read note once. Do not suggest adding it to the skill.

## Example

Prep, part of the agenda (full formats in `references/examples.md`):

```markdown
**Agenda for the call**
1. **Ask what drove the repairs spike.** Repairs were \$17,600 in September, against
   \$2,900, \$3,100, and \$3,300 in June to August.[K1]
2. **Explore taking payroll off Lena's plate.** "I do payroll every other Thursday
   night."[3] Payroll runs through a self-serve tool at \$1,980 a year.[K3] Payroll
   services are not in scope.

**Still open**
- *They owe:* Theo to send the new lease. Sam chased on Sep 30th, 2026.[3, 5]
```

## Completion

Done when:

- [ ] The mode matches the request, and the deliverable follows its format and limits in `references/examples.md`
- [ ] Every line ends with a source number that the Sources list resolves
- [ ] Every quote names its real speaker and date; no quoted reply text is misattributed
- [ ] Every meeting without a transcript is named as unread
- [ ] Every figure traces to a read; every swing and opportunity meets its stated threshold
- [ ] No write was attempted in either connector

Cleanup: the deliverable stays in chat. Unread meetings go under Watch out for. Any tool
that behaved differently from the reference files goes in the Read note, one line. The
Read note is the method note the reference files' drift rules point to.
