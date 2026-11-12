# Ping binding: ping-agents-setup

Loaded at Procedure steps 1 to 3. Grounded in `connectors/ping/` (live Ping MCP at
`https://app.pingassistant.com/api/mcp`, read 2026-11-09 and 2026-11-11). Every call is a
read.

## Tools used

| Tool | Operation or params | Purpose |
| --- | --- | --- |
| `list_meetings` | `timeframe: "upcoming"`, `limit: 1` | Step 3: one safe read that proves Ping answers |

## Call shape

```json
{"timeframe": "upcoming", "limit": 1}
```

The response has `meetings` (each with `title`, `date`, `status`) and `hasMore`. `date`
is a display string in the Ping account's timezone, not always the user's. Quote it as
Ping shows it. An empty `meetings` list is a working connection with nothing booked.

## Tool errors and schema drift

A dropped connection ("Not connected", a session that failed to reinitialize) is not a
rejected call: retry the same call once, and say the drop happened.

**Tool errors and schema drift:** if a live call is rejected, trust the live error hint
over this file. Fix the call and retry once. If the working shape contradicts this
file, add a method note to the deliverable so it can be reported and fixed centrally.
Never edit this skill file mid-run.

This skill makes no writes. A Ping tool that sends, drafts, creates, or updates anything
is never called: `create_meeting_agenda`, `update_meeting_agenda`, `update_action_item`,
`add_client_contact`, `update_client_contact`, `remove_client_contact`,
`add_tag_to_meeting`, `link_meeting_to_client`, `remove_meeting_attendee`. Ping's bulk
download of every meeting is never called either.
