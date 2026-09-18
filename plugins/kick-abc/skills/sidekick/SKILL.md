---
name: sidekick
description: "Runs accounting work end to end: finds the relevant skills, plans which skills or portions of skills to use, executes them with their own resources, cleans every artifact with the brand skill, and tells the user only what they need to know. Use for any request over the books when no skill has been named, from a one-line question to a full deliverable. Read-only; writes happen only through a skill's own confirmation flow."
---

# Sidekick

## Purpose

Get the request done with the skills that exist. Sidekick discovers, plans, executes,
cleans up, reports. It owns the plan; the skills own their methods.

1. Discover the relevant skills
2. Plan
3. Execute
4. Brand pass
5. Report

## Procedure

- [ ] 1. Discover. Send a subagent to search the available skills for relevance:
      `list_kick_skills` for the catalog, `load_kick_skill` on the plausible matches.
      It returns a shortlist only: skill, what it covers, which steps apply to this request. The full skill texts stay out of the main context until the plan needs them.
- [ ] 2. Plan, in one stated line. The plan names skills or portions of skills:
      "flux steps 2 and 4 for the why, management-report end to end for the artifact."
      Smallest work that answers the request. One shared pull of figures across every skill in the plan. Ask only what the context cannot answer; take disclosed defaults for the rest.
- [ ] 3. Execute the plan with each skill's own resources: its reference files, scripts,
      and templates, under its own rules.
      A borrowed step keeps its owner's tie-outs, thresholds, and confirmation gates. Never restate a sibling's method; load it and run it.
- [ ] 4. Run the brand skill over every finished artifact, as its own pass, never fused
      with generation.
- [ ] 5. Report to the user: the answer or the artifact path, the figures with their
      sources, what needs their confirmation, one next step if there is one.

## Guardrails

- **The user sees results, never process.** No internal monologue, no narrated tool
  calls, no "let me check the data". One line when work starts (the plan), the report
  when it ends, a question only when the work cannot continue without it.
- **A skill is a library of steps.** Run the portion the plan names, not the whole file.
- **Never compute here.** Every figure comes from a skill's step or a read, tied out.
- **Nothing user-facing carries internal plumbing.** No entity IDs, tool names, or
  skill names the reader did not ask about; say the account, the client, the period.
- A wrong plan stated costs one correction; a wrong plan silent costs the deliverable.
- On a rejected tool call, trust the live error over any guide or skill text, fix, and
  retry once. A rejected write restarts its approval.
  Never edit this skill file mid-run; report the discrepancy with the deliverable.

## Example

Request: "How bad was August, and do I need to worry about cash?"

Plan line: "Pulling August actuals once; flux's decompose for the drivers; the cash
read from management-report; one branded summary."

Report: "August: revenue $60,200, down $13,500 from July, mostly project-fee timing
(August P&L vs July). Cash $191,430 across both accounts; the $12,780 dip is
receivables timing, not burn. Summary attached. Two card charges need your confirmation."

## Completion

Done when:

- [ ] The stated plan ran fully, or the report says exactly what stopped it
- [ ] Every artifact went through the brand pass
- [ ] The report carries only the answer, sources, open items, and next step

Cleanup: deliver artifact paths, list open questions once, and leave nothing important
in internal notes that the report did not say.
