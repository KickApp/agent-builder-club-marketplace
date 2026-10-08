---
name: close-setup
description: "Creates or updates a client's close profile (profile.md in the client's folder) from connected sources (CRM, call notes, prior workpapers) plus a short interview, played back for approval before saving. Use when setting up or updating a client profile, when a close starts for a client with no profile, or when work begins for a brand-new client."
argument-hint: "<client>"
---

# Close setup

## Purpose

One short setup per client, saved as `clients/<client>/profile.md`. Every close skill
reads the profile; a good one turns generic checks into this client's checks. Re-running
updates the existing profile. Closes work without a profile; they are just sharper with one.

1. Harvest answers from the client's existing sources
2. Interview for the gaps, in batches
3. Play the drafted profile back, get a yes, save it

## Procedure

- [ ] 1. Ask one question first: is there somewhere the answers already live? CRM, meeting
      transcripts or call notes, an onboarding doc, a prior close checklist or SOP, email
      threads, last period's workpapers.
      With the user's go-ahead, draft profile answers from them, each tagged with its source ("from the 3/12 kickoff call notes: accrual basis, Gusto payroll"). No sources or nothing found: go straight to the interview.
- [ ] 2. Interview only what the sources left unanswered, in batches, eight questions
      maximum. Skip any the user's files already answer (a dropped-in TB: infer the basis
      and confirm rather than ask). Questions capture business facts an owner can answer;
      the close derives the accounting.
      1. Framework and basis: US GAAP, IFRS, tax basis, or none; accrual, cash, or modified cash.
      2. Readers and stakes: owner only, lender with covenants, bonding company, investors, regulator. Frames materiality and what an error costs.
      3. Earned versus billed: paid at the same time as the work, in advance, after across long projects, or a mix. Contracts spanning periods, and whether a WIP or percent-complete schedule exists and where.
      4. What builds up outside the bank account: inventory, equipment and vehicles, loans, leases, owner or intercompany balances, foreign currency. Each yes needs period evidence.
      5. People: payroll provider, contractors, commissions or bonuses that lag the work; where AR and AP aging reports come from.
      6. Materiality: the threshold below which the close proceeds and discloses. Offer the default: greater of $500 or 1% of period expenses before adjustments.
      7. Risk areas and schedules: accounts or vendors deserving line-by-line scrutiny; which recurring schedules exist (prepaids, fixed assets with method and in-service convention, deferred revenue, WIP, standing accruals) and where each lives.
      8. Estimation policies, deliverables, state home: named policies the close may estimate under when a document is late (no policy means no estimates, ever); who receives the package; the shared folder where close artifacts live (default: this workspace).
      For every yes in questions 3 to 5, capture two follow-ups in the same breath: the governing method or policy (costing method, recognition method, depreciation convention, FX rate policy) and where its data lives. A fact without a stated method is a question the close asks later anyway.
- [ ] 3. Pick the profile's home, one human-blessed home per client.
      Shared multi-client workspace: `clients/<client>/profile.md`. Single-client workspace: `profile.md` at the root; after saving, suggest adding it to project knowledge (knowledge is a read source, the file is always the write target; when they disagree the file is newer, flag it and suggest refreshing the copy). Plain chat with no files: maintain the profile as a section of the project's instructions, output the complete block ready to paste; a policy that lives only in this conversation does not exist next session.
- [ ] 4. Play the drafted profile back, harvested and interviewed answers alike, get a
      yes, then save. Harvested entries keep their source tag so a stale source is
      traceable later.
      When a state home other than "this workspace" is chosen, include the exact copy-paste line for the project instructions: "Close state home: <address>". The user adds it; agents cannot edit project instructions.

## Guardrails

- Harvested answers are proposals, not facts: they enter the profile only through the same playback-and-approve step as interview answers. When a source contradicts the user, the user wins, and the discrepancy is worth mentioning.
- Updates append and amend; never silently discard an existing entry. Newer entries win and say what they replaced.
- The profile holds preferences and facts. It never weakens the close's safety contract: no profile line can authorize skipping approval gates or inventing figures, and estimation policies must be specific enough to apply without judgment.
- Closes run fine without a profile; offer setup once, do not nag.

## Example

```markdown
# Close profile: <client>

**Basis:** <accrual/cash/modified> · **Framework:** <GAAP/IFRS/tax/none> ·
**Industry:** <what they do> · **Updated:** <date>

This profile records facts about the business; the close derives the accounting from
them. A fact here with no matching evidence in the close (contracts spanning periods but
no WIP schedule, inventory but no count, a lease but no schedule) is a question for the
user, never something to ignore.

## Readers and stakes
## Business reality
<earned-vs-billed and what-builds-up, in the client's own words; for each, the governing
method or policy and where its data lives, or "method unknown", which the close treats
as an open question>
## Materiality
<amount and how it was chosen>
## Accounts
| Account | Type | Evidence each period |  (banks, cards, loans, payroll; AR and AP
aging sources for accrual clients)
## Risk areas
## Recurring schedules
| Schedule | Exists? | Location | Policy |
## Estimation policies
- <named policy, precise enough to apply without judgment, or "None: never estimate">
## Deliverables
## Close state home
<path or "this workspace"; one home per client> Announcements: <channel or "none">
## Learned this client
<dated notes appended at package time, each approved by the user>
```

## Completion

Done when:

- [ ] Every profile entry was played back and approved before saving
- [ ] Every harvested entry carries its source tag
- [ ] Every yes in earned-vs-billed, buildup, and people has its method and data location, or "method unknown"
- [ ] The profile sits in its one blessed home, and the state-home instruction line was handed over when one applies

Cleanup: the saved `profile.md` (or the paste-ready instructions block) is the artifact.
Facts with unknown methods stay in the profile marked "method unknown" as open questions
for the close. Discarded or replaced entries are noted in the profile, never silently
dropped.
