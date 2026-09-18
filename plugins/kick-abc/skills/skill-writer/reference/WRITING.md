# How we write a skill

Input: anything. An SOP, a pasted prompt, a transcript, a user's own skill folder.
Output: a skill in the `abc/TEMPLATE.md` shape. Same transformation every time:

1. **Template it.** Whatever structure the source has, the result is Purpose (+outline),
   Procedure, Caveats, Example, Completion (+cleanup).
2. **Move specialized knowledge into resources.** Code goes to `scripts/`. Connector
   execution (tool names, call shapes, endpoint traps) goes to `reference/<connector>.md`.
   Domain depth (report anatomy, mapping tables, format contracts) goes to its own
   `reference/` file. The body points; it never explains twice.
3. **Trim.** The body stays concise and prim: short declarative sentences, staff-accountant
   voice, every sentence either an instruction or a rule. Cut anything the reader can
   derive, keep anything a runner has gotten wrong.

## The steps

1. **Read everything, then write Purpose first.** The mission in one or two sentences plus
   the outline. If you cannot state Purpose in two sentences, the source describes two
   skills; split it.
2. **Convert the process into a verb-first checklist.** Every step checkable. Detail sits
   indented under its step, never in a paragraph. Prose that explains *why* is either cut
   or compressed into the step's one clarifying line.
3. **Pull execution knowledge out of the flow.** Any tool name, parameter, enum, script
   invocation detail, or API trap moves to a resource. The body says *what* ("pull the
   statements in one pass"); the binding says *how* (`reports_query`, exact `params`).
   Ground every binding claim in the connector pack; a connector with no binding gets
   runtime discovery, never guesses.
4. **Distill Caveats.** Every hard rule, anti-pattern, and degradation fallback in the
   source becomes one bullet: the mistake, the tell, the rule. Keep precision wording
   verbatim where the playground proved wording-sensitivity (an em-dash ban held only once
   it said "including the title tag"). Zero caveats is allowed; padding is not.
5. **Pick one load-bearing Example.** The output format block or one worked miniature.
   Models copy shape from examples more reliably than from rules, so the example carries
   the format and the rules keep only what an example cannot show.
6. **Write Completion as binary checks plus cleanup.** Every line answerable yes or no.
   Cleanup names where every artifact and open question lands.
7. **Iterate against the live connector.** First run is a pilot at the smallest scope (one
   settlement, one account, one report) before any batch. A rejected call trusts the live
   error over the binding, fixes, retries once, and the discrepancy goes back into the
   binding. Field traces beat fixtures.

Then, compare to the original skill, line by line:

- [ ] Did any specific accounting logic get dropped? It shouldn't.
- [ ] Did we add extra grammar or stylistic fat to any instructions? We shouldn't.

## What gets trimmed, what never does

Trim: motivation prose, restatements of house rules the suite already carries, explanations
of things the reference files own, any sentence the checklist step already implies.

Never trim: safety wording (previews, approvals, confirmation tokens, lock-date stops),
tie-out and re-sum rules, precision rules with proven wording-sensitivity, the tells that
catch anti-patterns, and degradation fallbacks. These relocate into Caveats; they do not
shrink away.

## Worked example: management-report

Source: `abc/published/management-report/SKILL.md`, 262 lines of sectioned prose.
Result: `abc/templated/management-report/SKILL.md`, 83 lines, plus a 64-line Kick binding.

| Source section (published) | Where it went |
| --- | --- |
| Opening prose + "The distinction that governs every decision" | Purpose: two sentences and the governing filter ("if a number cannot be traced to a statement line, it does not belong") |
| Workflow, five checkbox steps with long sub-sections | Procedure: the same five steps, detail compressed to one indented line each |
| Payload schema walkthrough, engine invocation, font files | Procedure step 3 and 4 pointers; depth stays where it always was, documented at the top of `scripts/build_mgmt_report.py` and `demo-payload.json` |
| How to pull the data from Kick | New resource: `reference/kick.md` (tools table, per-report `params`, `ledgerId` scoping, workflow mapping) |
| "The comparison spine" table | Example, with the year-to-date exception kept |
| Formatting rules (polarity color, percentage suppression, parentheses, sum-then-round) | Caveats, wording preserved: "Costs below prior are favorable and charcoal; income below prior is adverse and red" |
| "The narrative layer" (mechanical sentences) | One caveat carrying the fixed word order and the worked sentence |
| "What never appears" | Folded into the dimensional-content and formatting caveats |
| "Verification before handover", ten items | Completion: six binary checks (the engine's proofs already assert three of the ten, so they are not re-listed) |
| "Related skills" | Cut from the body; routing is the orchestrator's job, reading Purpose |

What the diff shows: nothing analytical was lost. The engine contract, every color and
formatting rule, the percentage-suppression cases, and the handover checks all survive.
What disappeared is explanation: why PDFs, why no budget column, why bars beat pies. The
reference files and the engine's own documentation still hold those arguments for whoever
asks; the running agent does not need them to execute.
