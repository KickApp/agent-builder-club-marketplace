# Kick binding: cashflow

How to execute this skill's reads on Kick. Kick publishes its own skill guides:
discover with `list_kick_skills`, load with `load_kick_skill`. The guides own the
tool call shapes; this file maps them to the Procedure and adds what no guide
carries. On a rejected call, trust the live error, fix, retry once, report the
discrepancy.

## Guides to load

| Procedure step | Published guide | For |
| --- | --- | --- |
| 1. Orient | `kick/chart-of-accounts-and-ledger-lookup`, `kick/financial-accounts-lookup` | ledger, basis, connected `accountIds` |
| 2. Pull history | `kick/financial-reports` | statements behind the model's drivers |
| 2. Inflow and outflow detail | `kick/cash-flow-forecast-13-week` (pull pattern only) | the historical cash-movement reads that guide documents |

## What no guide carries

- Kick's own 13-week guide is a full workflow; load it for its data-pull pattern,
  then build the model per this skill's method (the workbook contract in
  `reference/MODELS.md` stays the deliverable, not the guide's output).
