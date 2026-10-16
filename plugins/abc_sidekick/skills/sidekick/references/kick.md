# Kick binding: sidekick

How to run this skill's discovery step on Kick. On a rejected call, trust the live
error, fix, retry once, report the discrepancy.

## Discovery

| Procedure step | Call | For |
| --- | --- | --- |
| 1. Discover | `list_kick_skills` | the catalog of published guides, searched with the request's keywords |
| 1. Discover | `load_kick_skill` | the plausible matches from that list, loaded by name |

## What no guide carries

- Never load a guide by a guessed name. List first, then load what the list returned.
- The suite's own skills are found the same way the session finds any skill; Kick's
  catalog only covers Kick's published guides.
