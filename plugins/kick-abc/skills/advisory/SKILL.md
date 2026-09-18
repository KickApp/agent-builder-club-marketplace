---
name: advisory
description: "Runs an advisory engagement end to end: works out what the data supports, picks the right skills, runs them in order, and applies the firm brand to every artifact before handing anything over. Use when someone drops in financials with no specific instruction, asks how the business is doing, asks for a report or a board pack, wants more than one deliverable, or is not sure which skill they want. Also the right entry point when several skills need to share one set of pulled figures so the deliverables agree with each other. Read-only. Routes to dashboard, management-report, flux, cashflow, and benchmark, and always finishes with brand. Not needed when the user has already named a single skill, in which case run that skill directly and still finish with the brand pass."
---

# Advisory

## Purpose

The front door for advisory engagements: it picks the right deliverables, runs each
owning skill in an order where each can use what the last one found, and puts every
artifact through the brand pass so the set leaves as one firm's work. It never
computes; the numbers belong to the skill that owns them, and duplicating a
calculation here is how two deliverables end up disagreeing on the same figure.

1. Orient on the data given
2. Choose the deliverables
3. Pull once into shared scratch
4. Generate every artifact, unbranded
5. Brand the whole set in one pass
6. Verify the set and hand over

Read `reference/HOUSE-RULES.md`, `reference/DATA.md`, `reference/ARTIFACTS.md`, and
`reference/DIMENSIONS.md` before starting.

## Procedure

- [ ] 1. Orient: read what you were given, name what it supports in one line, and move.
      On Kick: guides and pull mapping in `reference/kick.md`. Other connectors: discover at runtime, never guess names.
      No opening questionnaire. `reference/DATA.md` has the tier table.
- [ ] 2. Choose the deliverables and state the plan in one line.
      Default to one: a single report someone reads beats three they skim. "How are we doing" means the dashboard against the business's own history; "send me the financials" means the management report. The line between them: the dashboard is business segments at a point in time, the management report is statement lines over time. Dimensional cuts and rankings only ever go in the dashboard; the full statements only ever go in the management report.
      Benchmark is never the default answer to a vague ask. It runs on a genuinely comparative request, or as the reference layer under another skill's run.
      Run more than one only when the request genuinely spans them, ordered so the later skill inherits: flux after dashboard (inherits the line and the period rather than re-deriving them), cashflow after dashboard (carries the cash balance and burn across rather than recomputing), benchmark after dashboard (inherits the figures dashboard computed, so both state the same margin to the decimal), management-report then dashboard for the classic close-and-deliver pairing.
      If the ask is genuinely ambiguous, show the routing table and ask rather than guessing.
- [ ] 3. Pull the ledger once into scratch; every skill in the run reads from it.
      Fix before the first skill starts, and hold for the whole run: entity, period and comparison period, basis (accrual or cash), closed-through date, and which dimensions the books actually carry per `reference/DIMENSIONS.md`. Every artifact carries the same four in its header and footnote.
      When benchmark is in the plan, it runs its sourcing at pull time: classification and size band confirmed, tiers checked, the labeled reference set written into the same scratch. Skills carrying an external figure take it from that set and never source one themselves.
- [ ] 4. Generate every artifact, unbranded, context-setting skills before deep dives.
      Announce each in one line as you start it; never paste a report into chat between steps. One artifact per turn, per `reference/HOUSE-RULES.md`.
      Read `reference/brand-config.md` copy rules before writing any payload, not after: writing to them costs nothing, retrofitting them means rebuilding every artifact in the run.
      If a skill can't produce something worth reading from the data available, say so and skip it. A thin report is worse than a named gap.
- [ ] 5. Brand the whole set in one pass, after the last artifact is generated:
      `python3 reference/templates/theme.py reference/brand-config.md report1.html report2.html`
      The pass is idempotent; re-running it after a palette change is the supported way to re-skin a finished set. It reports banned punctuation and ledger words rather than rewriting; fix each in the payload, rebuild that file, and brand the set again.
      Workbooks have no script: apply the input convention and number formats from `brand` by hand, then re-run `verify_model.py`, because a formatting pass can hide an error value behind a custom format.
      The management report is the exception: its engine builds the PDF directly with brand tokens baked in and takes no `theme.py` pass, but its sentences follow the brand copy rules, so write them to those rules the first time.
- [ ] 6. Verify against Completion, then hand over the paths, the one-sentence story, the top finding, and what was skipped for missing data.

## Guardrails

- **Content is generated. Then, as a separate pass over the finished file, brand is
  applied. Never both in one step.** Fused, three things go wrong: a copy slip destroys
  the artifact (the audit lives in the brand pass), you cannot see what you built (the
  unbranded file is the honest check on structure), and re-branding stops being free (a
  palette change would mean rebuilding every payload). There is no flag that does both.
  And never brand file by file as each is generated: wait until the last artifact is
  written, then brand them together; one invocation over the set is what guarantees
  they come out identical.
- **This skill never computes.** No figures of its own, no reconciliation, no
  recomputation of what a skill produced. Read-only, like everything it routes to.
- **Two skills pulling the same period separately** is how one report says $4,205,000
  and the next says $4,204,880. Pull once.
- **Never state a dimensional cut is out of scope.** Say which skill does it and what
  coverage the data has.
- **If a skill file can't be found, say so** rather than improvising it from memory.

## Example

The routing table, the fastest honest answer to "which one":

| Skill | Answers | Deliverable |
| --- | --- | --- |
| `dashboard` | How are we doing, where do we make and lose money, what stands out | interactive HTML |
| `management-report` | The period's financials, stated and filed | paginated PDF, statements in full |
| `flux` | Why did this line move | HTML variance report |
| `cashflow` | Will we run out, and when | Excel or Sheets workbook |
| `benchmark` | Are we normal for our industry and size, how do we compare | HTML comparison, every figure source-labeled |

Orientation, one line and moving:

> "You've given me a P&L for two quarters and a balance sheet, which is enough for a full
> dashboard with margins and per-location profit against your own prior quarter. Running
> that now. An AR aging report would also let me show what's trapped in receivables."

## Completion

Done when:

- [ ] Where two artifacts state one figure, they agree to the dollar
- [ ] One period, one basis, one closed-through date across every header and footnote
- [ ] No two reports imply opposite conclusions from the same ledger; a genuine
      contradiction is raised as a finding, never papered over
- [ ] Every artifact was branded, the last file checked too (the unbranded tell: no Kick
      blue on the header mark, text in the system font rather than Inter)
- [ ] One artifact opened and worth a screenshot; if not, the reason is said in chat
      rather than shipped quietly

Cleanup: hand over every file path with the one-sentence story, the top finding, and what
was skipped for missing data. The chat message points at the artifacts and never
reproduces them.
