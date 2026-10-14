# Skill template

Every workflow skill has five sections, in this order. An operator reads the whole file
in two minutes. Voice: staff accountant. Short declarative sentences. Active voice.
Every figure has a source. No em dashes, no filler, no AI boilerplate.

```markdown
---
name: <kebab-case, matches the folder>
description: "<third person: what it produces, when to use it. Human readable, specific, and concise.>"
---

# <Name>

## Purpose

The mission in one or two sentences: what this produces and for whom. Then the
outline: the deliverable's parts or the work's phases, as a short numbered list.

## Procedure

A checklist. Detail sits in an indented line under its step.

- [ ] 1. <verb> <step>
- [ ] 2. ...

## Caveats

Pitfalls, one bullet each: the tell and the response. As many as this workflow
can meet. Zero is allowed.

## Example

One worked miniature or the output format block.

## Completion

Done when: <a state that is true or false>.
Cleanup: <the file> is in <the place>.
Cleanup: <the open questions> are in the hand-off.
Cleanup: <what must not remain> is gone.
```

Rules of the template:

- **Purpose earns the run.** If the request does not match Purpose, the skill does not
  run. The orchestrator reads only this section to route.
- **Procedure is the spine.** A step the operator cannot check off is not a step.
- **Caveats are variable length.** Categorization has many. A sequencer may have none.
  Each failure this workflow can meet gets one caveat: the tell and the response.
  An empty period is one of those when the procedure reads a period. Ask only when
  the answer is the user's to give. Skip a failure the workflow cannot meet.
- **Example is load-bearing.** Models copy shape from examples more reliably than from
  rules. Make the example carry the format; keep the rules for precision cases.
- **Completion is binary.** Every line is a state that is yes or no. Done when is the
  work. Cleanup is where the file, the open questions, and anything that must not
  remain now are. Nothing ends in working memory.

## Connector bindings

The skill body never names a tool. How to execute on a specific system lives in an
optional resource per connector, `references/<connector>.md` (`references/kick.md`,
`references/gusto.md`), loaded only when running on that system. A binding carries:

- **Tools used**: a table of tool, operation or report, purpose.
- **Exact call shapes**: required params per operation, field names verbatim, the
  mistakes the API punishes (wrong date field names, entityId vs entityIds). Leave out
  a shape only when a published guide already gives it (below).
- **Workflow mapping**: which binding call serves which Procedure step.

Every tool name and param in a binding comes from that connector's pack
(`connectors/<name>/`), never from memory. On a connector with no binding file:
discover tools at runtime, never guess names. On a rejected call: trust the live
error over the binding, fix and retry once, report the discrepancy.

**Never restate what the connector publishes.** Where the connector ships its own
skill guides (Kick does: `list_kick_skills`, then `load_kick_skill`), the binding
points at the published guide for whatever the guide covers and loads it at runtime.
The binding carries what no guide holds: which guide serves which Procedure step, the
skill-specific pull list, the call shapes no guide gives, and any trap the guides have
not absorbed yet. A binding that copies a guide's tables goes stale the day the guide
updates.

When the guides cannot be loaded to check what they cover (no live connector), keep
the call shapes in the binding. A stale shape is rejected at run time and the drift
rule reports it; a missing one gets guessed.
