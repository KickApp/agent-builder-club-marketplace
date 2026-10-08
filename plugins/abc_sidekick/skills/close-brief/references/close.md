# Close binding

This skill does not restate the close. Load the installed close plugin. If it is not installed, say so and stop. Do not reconstruct the phases from memory.

## Skills to load

| Procedure step | Installed skill | For |
| --- | --- | --- |
| 1 | `close:close` | Client and period, folder layout, state from evidence, conflicting sources, approvals, the exceptions register, defaults when no profile exists, guardrails |
| 3 | `close:intake`, `close:prep`, `close:adjust`, `close:review`, `close:deliver` | The five phases, in that order |

## The four overrides

Replace only these. Everything else in `close:close` stands.

| Close skill rule | Replaced by |
| --- | --- |
| A phase boundary is a turn boundary | Procedure step 3: print the phase line and continue |
| Every `### ...` template the close skill and the stage skills print | The phase line and the run-end block in the Example |
| The narrative shape of the written deliverables | Procedure step 4 |
| State playback in prose | The state line in the Example |
