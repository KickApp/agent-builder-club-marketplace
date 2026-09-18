# Kick binding: benchmark

How to execute this skill's reads on Kick. Kick publishes its own skill guides:
discover with `list_kick_skills`, load with `load_kick_skill`. The guides own the
tool call shapes; this file maps them to the Procedure and adds what no guide
carries. On a rejected call, trust the live error, fix, retry once, report the
discrepancy.

## Guides to load

| Procedure step | Published guide | For |
| --- | --- | --- |
| 2. Pull the client book side | `kick/financial-reports` | the statements the ratios come from |
| 2. Vendor spend, when in scope | `kick/vendor-spend-review` | per-vendor totals with the exclusions it documents |

## What no guide carries

- Only the client-book side of a benchmark binds to Kick. External reference data
  never comes from these tools; the sourcing ladder (user-supplied, then the firm's
  book, then public filings) is this skill's own and starts outside the connector.
