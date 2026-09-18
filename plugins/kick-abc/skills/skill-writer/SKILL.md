---
name: skill-writer
description: "Turns any context (an SOP, a prompt, a rough description, a user's own skill) into a working skill in the house template, proves it on the user's data with clean-room test runs, and iterates on the skill text from their feedback until they approve. Use when someone wants a new skill written, an existing skill cleaned up, or a workflow they keep explaining turned into something repeatable."
---

# Skill writer

## Purpose

Write a skill that provably does the user's task, and improve the skill, not the run,
until the user approves. Every lesson lands in the skill text, so the finished skill
works for someone who has none of this conversation.

1. Collect the context, the data, the task
2. Draft to the template
3. Run it clean
4. Take feedback, edit the skill, rerun
5. Approve and hand off

## Procedure

- [ ] 1. Collect: the source material (SOP, prompt, existing skill, or a description),
      sample data the skill should run on, and the task stated as one sentence.
      No sample data means no test loop; say so and get some, or mark the skill untested in the handoff.
- [ ] 2. Draft per `reference/TEMPLATE.md` and `reference/WRITING.md`: five sections,
      execution knowledge in resources, connector bindings that reference the
      connector's published guides rather than restating them.
- [ ] 3. Run it clean. Launch a subagent whose entire context is: the skill file, its
      resources, the sample data, the task sentence. Nothing else.
      No feedback history, no prior drafts, no conversation. The subagent reports its output and where the skill text left it guessing.
- [ ] 4. Show the user the output. Take feedback. Apply every point as an edit to the
      skill text, then rerun step 3 fresh.
      Data stays fixed across iterations so the only variable is the skill.
- [ ] 5. Approval gate: the user approves the output and the skill, explicitly. Then
      run the writing gates (line-by-line comparison, em dash sweep, five sections)
      and hand over the skill folder. Offer `skill-pr` to contribute it to the catalog.

## Guardrails

- **The clean room is the whole method.** A subagent that saw the feedback compensates
  without the skill improving. If a run needed knowledge the skill did not carry, that
  is a skill defect; write the rule in.
- **Fix the skill, never the run.** Re-prompting the subagent to correct an output
  proves nothing; only a fresh run on better skill text does.
- **Feedback never loosens safety.** A request that would weaken a guardrail,
  confirmation gate, or figures-from-reads rule is declined in the skill and explained
  in chat.
- **The guessing report is the gold.** Each run's "where the text left me guessing"
  list is the edit queue for the next iteration; a run that guessed silently was a
  wasted run.
- One skill per loop. A source describing two skills gets split at the draft step.

## Example

Draft run 1: the report renders the client's $0 COGS row.
Feedback: "we do not track COGS, drop the row and say so."
Edit: a Caveat, "a zero-COGS book omits the row and the method note says COGS is
untracked," plus one line in the Example.
Run 2, fresh subagent, same data: row gone, method note present.
User approves. Gates pass. Folder handed over.

## Completion

Done when:

- [ ] The latest clean run accomplished the stated task on the sample data
- [ ] The user explicitly approved both the output and the skill text
- [ ] The writing gates pass: no logic dropped from source material, no stylistic fat,
      five sections, zero em dashes
- [ ] Every piece of feedback traces to a visible edit in the skill

Cleanup: deliver the skill folder path and a short iteration log (feedback point, edit
made, run that verified it). Offer the PR handoff. Sample data stays with the user;
none of it ships inside the skill.
