# Kick binding: intake

How to execute this skill's reads on Kick. Kick publishes its own skill guides:
discover with `list_kick_skills`, load with `load_kick_skill`. The guides own the
tool call shapes; this file maps them to the Procedure and adds what no guide
carries. On a rejected call, trust the live error, fix, retry once, report the
discrepancy.

## Guides to load

| Procedure step | Published guide | For |
| --- | --- | --- |
| Readiness sweep | `kick/period-end-close-review` | uncategorized, unmatched transfers, unmemoed items, report swings |
| Statement reads | `kick/financial-reports` | the balances the readiness report cites |
| Detail behind a flag | `kick/find-and-query-transactions` | the rows behind each exception |

## What no guide carries

- The readiness guide produces a checklist; this skill's deliverable (the readiness
  report and request list, per its Example) stays the output contract. Guide
  findings feed it; they do not replace it.
