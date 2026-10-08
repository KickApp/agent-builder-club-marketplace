---
name: close-brief
description: "Runs one client's close for one period with minimal reading: straight through the phases, one-line phase reports, compressed written artifacts. Use when someone asks for a concise, brief, or low-narration close, or invokes /close-brief. Requires the close plugin."
---

# Close brief

## Purpose

Run the installed close for one client and one period, and change only how much the user has to read. The accounting stays with the close skill.

1. State line, once
2. Intake, prep, adjust, review, deliver, without a stop between phases
3. Same files and figures, shorter prose
4. Six-line run end

## Procedure

- [ ] 1. Load the installed close skill and follow it for the work itself: client and period, folder layout, state from evidence, conflicting sources, approvals, the exceptions register, defaults when no profile exists, and its guardrails.
      Do not restate those rules and do not re-derive them. If the close plugin is not installed, say so and stop. Do not reconstruct the phases from memory.
      Which skills to load, and the four overrides, are in `references/close.md`.
- [ ] 2. Print the state line once, before the first phase, in the Example format.
- [ ] 3. Run intake, prep, adjust, review, and deliver in order. Print the phase line and continue.
      Stop and wait only for the JE approval gate, a phase that cannot meet its own completion criteria, an acceptance, override, or judgment call at or above materiality, or two sources that disagree and need an arbiter document or a basis decision from the user. Carrying blocked items is not itself blocked. Present a material judgment alone, with its consequence in one sentence.
      Everything below materiality takes the proceed-and-disclose default, gets a row on the exceptions register, and appears in the final counts. When the aggregate of those small judgments crosses materiality, it becomes a question.
      A stop is three lines: what is blocked, what you need, what you recommend. Then stop. Do not pre-write the work the answer would unblock.
- [ ] 4. Write the same file set, the same figures, and the same tie-outs. Compress only the prose.
      Every artifact leads with its table. No paragraph introduces a table, restates one, or summarizes what the reader can read. A section with no findings is deleted, not filled with "none". Report that absence once, in the run summary.
      Rank findings by amount. Narrate those at or above materiality. Below it, one line with the count and a pointer to the workpaper tab.
      Close memo: the executive summary is six sentences at most. Result, the two or three drivers with their figures, entries booked, open items. The remaining sections are tables. No commentary or outlook section.
      Full detail stays in the statements, the workbook tabs, the reconciliation proofs, the JE register, and the import CSV.
- [ ] 5. End on the run-end block in the Example, and nothing after it.

## Guardrails

- **No entry enters an import CSV or the books without explicit confirmation.** Nothing is marked approved, and no close is called complete, without that confirmation under the close skill's approvals rules.
- **Shortening deletes words.** It never drops a finding, an exception, or a disclosure. An exception gets its register row whatever its size.
- **Every figure traces to provided data or a user-approved calculation.** A gap is an exception, never an estimate, and never a rounder number because it reads better short.
- **A derived figure comes from an executed computation**, never arithmetic performed in prose.
- **A correction propagates to every artifact that quoted the old figure**, or it did not happen.
- Never narrate a step before taking it. Never restate what a stage skill just reported. Never explain a tool call the user can see. No closing offer of further help.
- Voice: short declarative sentences, sentence-case headings, concrete nouns, real figures. No em dashes, no filler (delve, robust, seamless, leverage, comprehensive, crucial), no "not just X, but Y", no AI boilerplate, no decorative emoji.

## Example

State line, once:

`<client> <period> | intake <state> | prep <state> | adjust <state> | review <state> | deliver <state> | resuming at <phase>`

Phase line, no preamble:

`<phase>: <verdict>. <the one figure or count that matters>. <n exceptions, or nothing>`

`Reconcile: 6 of 7 tied. One account off, statement requested. 1 exception.`

Run end, this block and nothing after it:

```markdown
### Close: <client>, <period>

**Result:** <delivered / stopped at <phase>>
**Phases:** <five words, one per phase>
**Entries:** <count, total, approved by whom>
**Exceptions:** <n open, with owners, or none>
**Files:** <paths>
**Next:** <one action>
```

## Completion

Done when:

- [ ] The close skill was loaded, and this skill overrode only rhythm, reports, artifacts, and state playback
- [ ] The run stopped only for an approval gate, a blocked phase, a material judgment, or a source conflict
- [ ] Each phase printed one line, and the run ended on the six-line block with nothing after it
- [ ] Artifacts lead with tables, omit empty sections, and keep full detail in the statements, workbook, proofs, JE register, and import CSV
- [ ] Every figure traces to data or an approved calculation, and every exception has a register row
- [ ] No entry was written, and the close was not called complete, without explicit confirmation

Cleanup: leave the close folder where the close skill files it. Hand forward the six-line block and the file paths. Do not add a follow-up offer.
