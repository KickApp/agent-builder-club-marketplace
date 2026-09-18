# Kick binding: dashboard

How to execute this skill's reads on Kick. Kick publishes its own skill guides:
discover with `list_kick_skills`, load with `load_kick_skill`. The guides own the
tool call shapes; this file maps them to the Procedure and adds what no guide
carries. On a rejected call, trust the live error, fix, retry once, report the
discrepancy.

## Guides to load

| Procedure step | Published guide | For |
| --- | --- | --- |
| 1. Orient | `kick/chart-of-accounts-and-ledger-lookup` | `entityId`, `ledgerId`, basis |
| 2. Pull statements | `kick/financial-reports` | P&L, balance sheet over the trailing periods |
| 2. Dimensional cuts | `kick/class-tracking-and-splits` (reads only) | class, location, project tagging |
| 3. Member detail | `kick/find-and-query-transactions`, `kick/counterparty-lookup` | customer and vendor rollups |

## What no guide carries

- This skill is read-only; the class guide is loaded for its query surface, never
  its write operations.
- Coverage discipline (a cut ships only where tagging covers the line, per
  `reference/DIMENSIONS.md`) is this suite's rule, not the platform's.
