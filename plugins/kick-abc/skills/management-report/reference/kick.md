# Kick binding: management report

How to execute this skill's pulls on Kick. Kick publishes its own skill guides:
discover with `list_kick_skills`, load with `load_kick_skill`. The guides own the
tool call shapes; this file only maps them to the Procedure and adds what no guide
carries. On a rejected call, trust the live error over any guide, fix, retry once,
and report the discrepancy.

## Guides to load, per Procedure step

| Procedure step | Published guide | For |
| --- | --- | --- |
| 1. Confirm books, period, basis | `kick/chart-of-accounts-and-ledger-lookup` | `entityId`, `ledgerId`, accounting basis |
| 2. Pull the data | `kick/financial-reports` | P&L, balance sheets, and the params each report requires |
| 2. The period's movements | `kick/find-and-query-transactions` | balance-sheet movement detail where the reports need backing |

## What no guide carries (this skill's pull list)

- **One pass, all periods**: P&L leaf accounts monthly, 24 months where they exist;
  balance sheets as of period end, prior period end, and prior year end; the period's
  balance-sheet movements. The guide documents how to call each report; this skill
  decides the set, and it is pulled once.
- Resolve `ledgerId` and basis once, reuse for every report this run, and state the
  basis in the deliverable.
- Real retained earnings come from the books where they exist; a derived plug prints
  itself (see the payload contract in the skill body).
