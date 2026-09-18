# Kick binding: review

How to execute this skill's reads on Kick. Kick publishes its own skill guides:
discover with `list_kick_skills`, load with `load_kick_skill`. The guides own the
tool call shapes; this file maps them to the Procedure and adds what no guide
carries. On a rejected call, trust the live error, fix, retry once, report the
discrepancy.

## Guides to load

| Procedure step | Published guide | For |
| --- | --- | --- |
| Swing and balance checks | `kick/financial-reports` | statements at close and prior |
| Exception re-checks | `kick/period-end-close-review` | anything the close might have left open |
| Spot detail | `kick/find-and-query-transactions` | the rows behind a questioned figure |

## What no guide carries

- The verdict logic (ready or not ready, the informed-consent acceptance protocol,
  the always-blocks pair) is entirely this skill's; the guides only supply reads.
