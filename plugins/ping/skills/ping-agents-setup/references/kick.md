# Kick binding: ping-agents-setup

Loaded at Procedure steps 1, 2, and 4. Grounded in `docs/kick-mcp-tool-inventory.md` and
Kick's public tool reference. Every call is a read.

## Tools used

| Tool | Operation | Purpose |
| --- | --- | --- |
| `context_browse` | `workspaces` | Step 4: one safe read that lists the workspaces Claude can see |

## Call shape

```json
{ "operation": "workspaces", "limit": 25 }
```

The response lists the accessible workspaces under `workspaces`, each with its `name`
and entities, plus `hasMore` (observed on live Kick, 2026-11-11). Name each workspace as
Kick returns it. Several: ask which one the firm works in. `hasMore` true: say the list
is longer and ask the user to name their workspace. None: the sign-in did not grant a
workspace, so have the user sign in again and select one.

Kick's tools work only for workspaces on a paid plan. In a free workspace a call returns a
non-retryable `403` saying the tool isn't enabled. Say so; do not retry.

## Tool errors and schema drift

**Tool errors and schema drift:** if a live call is rejected, trust the live error hint
over this file. Fix the call and retry once. If the working shape contradicts this
file, add a method note to the deliverable so it can be reported and fixed centrally.
Never edit this skill file mid-run.

This skill makes no writes. No Kick tool that creates, updates, or deletes is called.
