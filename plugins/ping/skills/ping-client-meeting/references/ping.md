# Ping binding: ping-client-meeting

Loaded at Procedure step 2 and used at steps 3, 4, 6, and 7. Ping holds the conversation
half: meetings and transcripts, client email, the client summary, action items, Slack,
and the firm's services and agreements. Every call is a read. Every tool and parameter
here comes from `connectors/ping/`.

## Status

Verified live 2026-11-09 on a firm account's sample client ("Camden Bean (Example)"),
3 runs of each mode, and 2026-11-11 on Ping's demo firm: a prep for Big W Construction
with a booked meeting, services, agreements, and Insights, and a recap with a client
call. Rows the runs could not exercise are named under Not verified.

## Tools used

| Data need | Tool | Step |
| --- | --- | --- |
| The client by name, its ID, contacts, and summary | `get_client_details` | 3, 4 |
| A fuzzy person or client name, or a participant email | `resolve_person` | 3, 7 |
| Upcoming and past meetings, each with `hasTranscript` | `list_meetings` | 3, 4, 7 |
| The client's transcribed meetings | `list_client_meetings` | 3, 4 |
| A meeting's participants and times | `get_meeting` | 3, 7 |
| The full transcript | `get_meeting_transcript` | 4, 7 |
| Email with the client, full bodies | `client_email_search` | 4, 7 |
| Commitments, with status | `list_action_items` | 4, 7 |
| Slack threads with the client | `get_recent_slack_messages`, `get_slack_thread` | 4 |
| The firm's services and prices | `get_org_services` | 6 |
| What is already in scope for the client | `get_org_agreements` | 6 |
| Ping Insights: per-service fit with evidence | `search_service_alignment` | 6 |

## Call shapes

- `get_client_details {clientName}`: partial match. Use the returned `client.name` and
  `client.id` from here on; a sample client's name carries "(Example)". No match returns
  `success: false`: try `resolve_person {name}` once, then say the client was not found
  in Ping and stop. `otherMatches` can hold a second client with a similar name: use the
  main match, do not open the other, and name it in the Read note. When an
  `otherMatches` name equals the name the user gave and the main match does not, ask
  which client before reading anything else.
- `list_meetings {timeframe: "upcoming", limit: 50}`: the whole account, soonest first.
  It has no client filter and no participants. Among rows in the next 14 days, open with
  `get_meeting {meetingId}` first the rows whose title names the client or a contact,
  then rows with `participantCount` of 5 or fewer, soonest first. Keep the first whose
  `participants` include a client contact email, and stop. Rows with more than 5
  participants and no client name in the title are not opened; give their count in the
  Read note. A title that names one contact while the invite goes to another still
  matches: name both in one Watch out for line and ask who is joining.
- `list_client_meetings {clientId, limit: 50}`: only meetings with transcripts, latest
  first. The first row is the latest transcript. Rows dated in the 90-day window are the
  transcripts to read. A transcript filed under the client with nothing about the client
  in it (the firm's own sales, setup, or product demo call) is misfiled, even when a client contact is
  on its participant list: skip it. The Read note counts it inside the transcript total
  and names it: "7 transcripts (2 skipped as misfiled)".
- Unread meetings: a client meeting with no transcript never appears in
  `list_client_meetings`. Find it through `list_action_items`: take each
  `effectiveMeetingId` not in `list_client_meetings` and call `get_meeting` once per ID.
  Ping keeps one meeting row per attendee, so one call can carry several IDs: when the
  `startTime` and title match a `list_client_meetings` row, it is that transcribed
  meeting, not an unread one. Only a meeting whose start time matches no transcribed row
  is unread. Name each one under Watch out for.
- Unread count: `get_client_details` returns `recentMeetingCount` for
  `recentMeetingWindowDays` (90). Report both read figures side by side: "Ping counts N
  meetings in the last 90 days; M have transcripts." Never subtract them. Meetings the
  count holds that no read identifies stay unnamed.
- `get_meeting_transcript {meetingId, maxUtterances: 2000}`: the default 200 cuts a long
  call off. A meeting with no transcript returns `success: false`; read
  `hasTranscript` first. Speaker labels can differ from the meeting's participants (Ping's
  sample data does this, and also scrambles names and dollar figures inside the text).
  When a label matches no participant, attribute by role from what was said, quote no
  figure the client summary or action items contradict, and say so under Watch out for.
  A label that is the client's name, with one client contact among the participants, is
  that contact. One label that asks and answers for both sides, or a generic label
  ("Speaker 0") whose words do not say who is talking, is unattributable: quote nothing
  from it as the client's words.
- `client_email_search {query, clientId, since, until, orderBy: "recent", limit: 50}`:
  `since` and `until` are YYYY-MM-DD in the Ping account's timezone, which the result
  reports as `timezone`. `query` is required; use the
  client's name plus "accounting, books, tax, payroll". `content` is the full message, so
  no second call. Without `clientId` it returns `searchStatus: "failed"` and no email:
  that is no read, not an empty inbox. `searchStatus: "complete"` with a `clientContext`
  of 0 contact addresses in scope, or a warning that the email index is still being
  built, is also no read. Say email was not read and why; never fall back to the user's
  own mailbox.
- `list_action_items {clientId, limit: 50}`: page with `offset: nextOffset` while
  `hasMore` is true. No owner field: take who owes what from the item's text or the
  transcript.
- `get_recent_slack_messages {clientId, daysToSearch: 90}`: `authorRole` `internal` is the
  firm talking, `contact` is the client. Open a thread with `get_slack_thread {threadTs,
  clientId}` before quoting it.
- `get_org_services {}` and `get_org_agreements {clientName}`: empty lists with
  `hasAnchorIntegration: false` mean the source is missing, not that the firm sells
  nothing. Say so under Watch out for. An empty agreements list with
  `hasAnchorIntegration: true` means no agreement is on file for the client: scope is
  still unknown, and the same Watch out for line covers it.
- `search_service_alignment {query, clientId}`: only when services came back. Use the
  evidence, never the confidence rating.
- Times: `list_meetings` `date` strings are in the Ping account's timezone, not the
  user's. Every time in the deliverable comes from `get_meeting` `startTime` and
  `endTime` (UTC), converted to the user's timezone.
- Recap: `list_meetings {timeframe: "past", limit: 50}`, latest first. Keep rows dated
  today and the day either side; once a row is older than yesterday, stop, even when
  `hasMore` is true. `get_meeting` then keeps only meetings whose `startTime` falls
  today in the user's timezone. A meeting whose `endTime` is after now is still
  running: name it in the Read note and do not recap it. A past row can still say
  `status: "SCHEDULED"`: it was held but not recorded.
- Recap, which meetings were with a client: `get_meeting {meetingId}` for every row
  from today, transcript or not. The firm's domain is the email domain the meeting's
  organizer shares with its other non-recorder participants. Participants all on it,
  plus any recorder address (a notetaker or capture service): internal, skip it. A
  public mail domain (gmail.com, outlook.com, yahoo.com, icloud.com) is never the firm's
  domain. Without a firm domain, the organizer is the firm side. Otherwise
  `resolve_person {name: <participant email>}` for each outside participant; a client
  match makes it a client meeting. An outside participant with no match is named in a
  Watch out for line on that meeting. A title that reads like a test or internal call
  still follows the rule; add one line asking the user to confirm.
  `hasTranscript: false` on a client meeting: unread, named under Watch out for. The
  meeting still counts as activity, so the client gets a block.
- Recap, tomorrow's meeting: `list_meetings {timeframe: "upcoming", limit: 50}`. For a
  row dated tomorrow whose title names a client met today, `get_meeting` confirms a
  client contact is invited. It goes under Still open beside what we owe for it, or
  under What happened as "Next: ..." when nothing is owed.
- Recap email: `client_email_search` with `since` the day before today and `until`
  today, in the account's timezone, once per client found through today's meetings.
  Keep only messages sent today in the user's timezone. Run `list_action_items
  {clientId}` for the same clients only. No tool lists clients, so email from any other client is not read.
  Say that in one Watch out for line after the last client block, not in the Read note;
  never search the user's own mailbox instead. Action items not created or updated
  today stay out of the recap.

## Not available

| Data need | What the skill does without it |
| --- | --- |
| Internal notes about the client | Use the client summary from `get_client_details`, cited to its own sources. |
| Questions the client posted in a portal | Say in the Read note that the portal was not read. |
| A list of every client | Recap covers clients met today. Email from a client with no meeting today is not read; one Watch out for line says so. |
| Who owns an action item | Take it from the item's text or the transcript; otherwise list it under Still open without a side. |

## Workflow mapping

| Procedure step | Calls |
| --- | --- |
| 3. Resolve, find the meeting | `get_client_details`; `list_meetings` upcoming; `get_meeting` per candidate; `list_client_meetings` |
| 4. Read the conversations | `get_meeting_transcript` per transcript in the window and the latest; `client_email_search`; `list_action_items`; `get_recent_slack_messages`, `get_slack_thread` |
| 6. Opportunities | `get_org_services`; `get_org_agreements`; `search_service_alignment` |
| 7. Recap | `list_meetings` past; `get_meeting`; `resolve_person`; `get_meeting_transcript`; `client_email_search` with `since` and `until` today; `list_action_items`; `list_meetings` upcoming for tomorrow |

## Without Ping

The skill stops at step 2. Ping is required.

## Tool errors and schema drift

A dropped connection ("Not connected", a session that failed to reinitialize) is not a
rejected call: wait, retry the same call, and name the drop once in the Read note.

**Tool errors and schema drift:** if a live call is rejected, trust the live error hint
over this file. Fix the call and retry once. If the working shape contradicts this
file, add a method note to the deliverable so it can be reported and fixed centrally.
Never edit this skill file mid-run.

This skill makes no writes. A Ping tool that sends, drafts, creates, or updates anything
is never called: `create_meeting_agenda`, `update_meeting_agenda`, `update_action_item`,
`add_client_contact`, `update_client_contact`, `remove_client_contact`,
`add_tag_to_meeting`, `link_meeting_to_client`, `remove_meeting_attendee`. Ping's bulk download of
every meeting is never called either. Offer the agenda as text in chat.

## Not verified

The test accounts had no data for these, so no run called them with results:

- `client_email_search` returning email inside the 90-day window: Big W's email was
  older. (revenue-finder's run on the same account read its email in full.)
- `get_recent_slack_messages` returning threads, and `get_slack_thread`: no channel was
  linked.
- `get_org_agreements` returning an agreement for the client: Big W had none on file.
- Recap with a transcribed client call today, and recap email that came back: the one
  client call that day had no transcript and no email.
- The rule for an exact-name match in `otherMatches`, and the 2026-11-11 rules (title
  naming another contact, misfiled transcripts, speaker labels, public mail domains,
  tomorrow's meeting) were written after the runs that found them.
