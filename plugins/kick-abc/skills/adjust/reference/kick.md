# Kick binding: adjust

How to execute this skill's reads on Kick. Kick publishes its own skill guides:
discover with `list_kick_skills`, load with `load_kick_skill`. The guides own the
tool call shapes; this file maps them to the Procedure and adds what no guide
carries. On a rejected call, trust the live error, fix, retry once, report the
discrepancy.

## Guides to load

| Procedure step | Published guide | For |
| --- | --- | --- |
| 1. Check what is already booked | `kick/journal-entries-lookup` | an entry posted with this period and memo is done, not drafted twice |
| Evidence pulls | `kick/find-and-query-transactions` | activity behind an accrual or reversal |

## What no guide carries

- **This skill never posts.** Its contract ends at the approved entry plus the
  import CSV. Kick's `kick/manual-journal-entry` guide can post entries under its
  own preview and confirm flow, but that is a separate decision the user makes
  outside this skill, and this binding deliberately does not wire it in.
