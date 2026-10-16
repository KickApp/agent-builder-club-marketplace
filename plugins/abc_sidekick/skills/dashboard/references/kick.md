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
- Classes need the Plus plan or above. On a workspace without it, a class read returns a
  plan error: treat that as no class tagging, skip the class cuts, keep any location or
  project cuts the books still carry, and say in the chat message that class cuts need
  the Plus plan. Never retry the call or report it as a failure.
- Coverage discipline (a cut ships only where tagging covers the line, per
  `references/DIMENSIONS.md`) is this suite's rule, not the platform's.
- When a step needs the file behind a Kick document, invoke the `download-kick-document`
  skill with the document id. It is a skill, not a Kick tool; the presigned URL
  stays inside it.
