# Kick binding: advisory

How to execute this skill's reads on Kick. Kick publishes its own skill guides:
discover with `list_kick_skills`, load with `load_kick_skill`. The guides own the
tool call shapes; this file maps them to the Procedure and adds what no guide
carries. On a rejected call, trust the live error, fix, retry once, report the
discrepancy.

## Guides to load

| Procedure step | Published guide | For |
| --- | --- | --- |
| 1. Orient | `kick/entity-lookup`, `kick/chart-of-accounts-and-ledger-lookup` | entity, `ledgerId`, basis |
| 3. Pull once into shared scratch | `kick/financial-reports` | every statement the plan needs |
| 3. GL detail where a skill needs it | `kick/find-and-query-transactions` | transaction-level backing |

## What no guide carries

- **The shared pull is this skill's law**: one pull into scratch, every downstream
  skill reads scratch, nothing re-pulls. The guides describe single reports; the
  once-per-engagement discipline is advisory's own.
- Resolve `ledgerId` and basis once; every deliverable in the set states the same basis.
