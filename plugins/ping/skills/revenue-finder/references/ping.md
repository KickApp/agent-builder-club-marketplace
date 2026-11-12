# Ping binding: revenue-finder

Loaded at Procedure steps 1 to 6 when Ping is connected. Ping holds the conversation
half: meeting transcripts, client email, the client summary, action items, Slack, and
the firm's services and agreements. Every call is a read. Every tool and parameter here
comes from `connectors/ping/`.

## Status

Written 2026-11-09 from the live Ping pack (`connectors/ping/`). Run once live
2026-11-11 on Ping's demo firm (client "Big W Construction"): 35 Ping calls, one empty
transcript, no rejected call. Rows that run could not exercise are named under Not
verified.

## Tools used

| Data need | Tool | Procedure step |
| --- | --- | --- |
| The client by name, its ID, contacts, and summary | `get_client_details` | 1, 4 |
| A fuzzy client or person name | `resolve_person` | 1, 4 |
| The firm's service catalog, with descriptions and pricing | `get_org_services` | 1 |
| Meetings in the window, each with `hasTranscript` | `list_meetings` | 3 |
| The client's transcribed meetings | `list_client_meetings` | 3, 4 |
| The full transcript | `get_meeting_transcript` | 4, 6 |
| Email with the client, full bodies | `client_email_search` | 4, 6 |
| Slack threads with the client | `get_recent_slack_messages`, `get_slack_thread` | 4, 6 |
| A per-service sweep of the client's meetings | `search_service_alignment` | 4 |
| Searching the client's meetings by words from a description | `search_client_meetings` | 4 |
| What is already in scope for this client | `get_org_agreements` | 5 (cut four) |
| Commitments already made to the client | `list_action_items` | 5 (cut four) |
| A link to the moment in a recording | `format_timestamp_links` | 9 |

## Call shapes

- `get_client_details {clientName}`: partial match. Use the returned `client.name` and
  `client.id` from here on; a sample client's name carries "(Example)". No match returns
  `success: false`: try `resolve_person {name}` once, then say the client was not found.
- `get_org_services {}`: each service has a name, description, billing type, and price.
  An empty list with `hasAnchorIntegration: false` means Ping has no catalog: go to the
  no-catalog path in step 1.
- Coverage (step 3): `list_client_meetings {clientId, limit: 50}` lists only the
  transcribed meetings, latest first. `get_client_details` gives `recentMeetingCount` for
  `recentMeetingWindowDays` (90). Report both read figures: "Ping counts N meetings in
  the last 90 days; M have transcripts." M counts only `list_client_meetings` rows
  dated in the same 90 days. Never subtract them. For a window longer than
  90 days, say the untranscribed count covers the last 90 days only. Those two figures
  go in the Meeting transcripts coverage note. `unread_meetings` in the report counts
  only meetings a read named: an empty transcript, or an action item's
  `effectiveMeetingId` whose meeting has no transcript.
- A transcript filed under the client with nothing about the client in it (the firm's
  own sales, setup, or product demo call) is misfiled, even when a client contact is on
  its participant list: skip it, and give the count in a method note.
- `get_meeting_transcript {meetingId, maxUtterances: 2000}`: the default 200 cuts a long
  call off. Quote only from the full transcript, never from a summary or snippet. A
  transcript that comes back empty is could-not-read; it is missing data, not a rejected
  call, so no retry. A speaker label that is the client's name, with one client contact
  among the participants, is that contact. One label that asks and answers for both
  sides, or a generic label ("Speaker 0") whose words do not say who is talking, is
  unattributable: it fails cut two.
- `client_email_search {query, clientId, since, until, orderBy: "recent", limit: 50}`:
  the window's start and end as YYYY-MM-DD, read in the Ping account's timezone (the
  response's `timezone`). `query` is required: the client's name, then
  one search per service with words from its description. Services that share words can
  share a search; once searches stop returning new messages, the rest can be skipped,
  and coverage says how many searches ran. `content` is the full message
  with from, to, and cc, so no second call. Without `clientId` it returns
  `searchStatus: "failed"`: that is could-not-read. The search covers every connected
  mailbox in the firm; name each mailbox in coverage. The email count is the distinct
  messages read across every search, not one search's total.
- `search_service_alignment {query, clientId}` and `search_client_meetings {queries,
  clientId}`: candidates only. Open the full transcript before scoring, and ignore any
  confidence rating.
- `get_org_agreements {clientName}`: agreements with stage. Empty with
  `hasAnchorIntegration: false` means scope is unknown: say so, and cut four runs on
  promises and declines only. Empty with `hasAnchorIntegration: true` means no agreement
  is on file for the client: the same rule applies, and every promise becomes promised,
  not in scope. A service that a transcript has both the firm and the client name as the
  current regular work is in scope; cite that moment in Raised before.
- `list_action_items {clientId, limit: 50}`: page with `offset: nextOffset` while
  `hasMore` is true. No owner field: read who promised from the item's text.
- `get_recent_slack_messages {clientId, daysToSearch}`: `authorRole` `contact` is the
  client, `internal` is the firm. Open the thread with `get_slack_thread` before quoting.
- `format_timestamp_links {references: [{meetingId, timestamp}]}`: one link per quoted
  transcript moment.

## Not available

| Data need | What the skill does without it |
| --- | --- |
| Internal notes about the client | Use the client summary from `get_client_details` as a note, cited to its own sources. It never scores three. |
| Questions the client asked through a portal | Say the portal was not read, in the Portal coverage row. |
| Calendar meetings with no transcript, by client, for the whole window | Report Ping's 90-day meeting count beside the transcribed count, as above. |

## Workflow mapping

| Procedure step | Calls |
| --- | --- |
| 1. Client, window, catalog | `get_client_details` or `resolve_person`; `get_org_services` |
| 2-3. Discover, coverage | List the live tools; `list_client_meetings`; `get_client_details` meeting count |
| 4. Corpus | `get_meeting_transcript`; `client_email_search`; Slack tools; `search_service_alignment` and `search_client_meetings` per service |
| 5. Cut four | `get_org_agreements`; `list_action_items` |
| 6. Context | `get_meeting_transcript`; `client_email_search`; `get_slack_thread` |
| 9. Report | `format_timestamp_links` for each quoted transcript moment |

## Without Ping

The skill still runs on email, chat, notes, and any transcript the user drops in.
Coverage then says transcripts were not available, and every meeting on the calendar
counts as unread. Do not degrade into a ledger-only guess.

## Tool errors and schema drift

**Tool errors and schema drift:** if a live call is rejected, trust the live error hint
over this file. Fix the call and retry once. If the working shape contradicts this
file, add a method note to the deliverable so it can be reported and fixed centrally.
Never edit this skill file mid-run.

This skill makes no writes. A Ping tool that sends, drafts, creates, or updates anything
is never called: `create_meeting_agenda`, `update_meeting_agenda`, `update_action_item`,
`add_client_contact`, `update_client_contact`, `remove_client_contact`,
`add_tag_to_meeting`, `link_meeting_to_client`, `remove_meeting_attendee`. Ping's bulk download of
every meeting is never called either.

## Not verified

- `get_recent_slack_messages` returning threads, and `get_slack_thread`: no channel was
  linked.
- `get_org_agreements` returning an agreement for the client: Big W had none on file.
- The 2026-11-11 rules (unread count for the report, misfiled transcripts, empty
  transcripts, speaker labels, the email count, agreements with Anchor connected) were
  written after the run that found them.
