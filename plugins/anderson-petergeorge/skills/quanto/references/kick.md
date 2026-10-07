# Kick binding: quanto

Loaded at Procedure step 2 when Kick is connected. Quanto reads only enough to say whether
Kick is connected and how many client workspaces it sees; the evidence skill does every
other Kick read under its own binding. Every tool and parameter here comes from the Kick
connector pack.

## When Kick has nothing to give

Skip this file and finish step 2 with the "Kick is not connected" line when no Kick tools
are in the session or the first call returns an auth error. The run continues on the files
and the owner's answers. When Kick responds but the only workspace is the firm's own, the
line reads "Kick connected (no client workspaces)" and the run continues the same way.

## Published guides

Discover with `list_kick_skills` (query "entity lookup", `includeHeader: true`), then
`load_kick_skill` the match. Guide names are not guessable; use the ones the list returns.
A response from `list_kick_skills` is itself the sign that Kick is connected.

| Guide | Serves |
| --- | --- |
| `kick/entity-lookup` | Listing workspaces and nested entities for the detection line (step 2) |

The evidence skill reuses this load; a guide already loaded in the conversation is not
loaded again.

## Tools used

| Tool | Operation / report | Purpose |
| --- | --- | --- |
| `list_kick_skills` | (no operation; `query`, `includeHeader`) | Find the entity lookup guide; first sign Kick responds |
| `load_kick_skill` | (no operation; `name`) | Load the guide the list returned |
| `context_browse` | `workspaces` (default; no required fields) | Count client workspaces and their entities for the detection line |

## Call shapes

- `list_kick_skills` `{ "query": "entity lookup", "includeHeader": true }`. Trap: an auth
  error here means Kick is absent for this run. Say so in one line and keep going; never
  stop the run on it.
- `load_kick_skill` `{ "name": "<exact name from the list>" }`. Trap: the name comes from
  the list's response, never from this table.
- `context_browse` `{ "operation": "workspaces", "limit": 100 }`. Trap: the default page
  is 25 and the maximum is 100. Page while `hasMore` is true, sending the returned
  `nextCursor` in the cursor field the live descriptor names. The count comes from the
  pages read, never from an estimate.

## From reads to skill inputs

| Skill input | Read from | Draft rule |
| --- | --- | --- |
| "n client workspaces" on the detection line | `context_browse` workspaces, all pages | Count workspaces other than the firm's own. The firm's own is the one whose workspace or entity name matches the firm's name (from `[firm]` or the conversation); it holds the firm's books, not a client's. No match: count every workspace and let the evidence skill settle it by name. |
| Entities per workspace | The nested entity summaries in the same response | One workspace with several entities: say "one workspace, n entities" so the owner sees each entity is treated as a client. |
| "one org" or similar | The same response, only if it carries an organization | The docs name no organization field on `context_browse`. Leave the org count out when the response does not show one. |

## Traps

- Detection is one pass. Never call `context_browse` per workspace, and never read a
  client's transactions, reports, or tasks from this skill.
- `context_browse` takes `operation`, not `target`; `context_resolve` (not used here)
  takes `target`.
- A plan-capability or "is not enabled for this workspace" error on one workspace is a
  fact about that workspace, not a sign Kick is absent. Count the workspace and let the
  evidence skill report it as "Not available".

## Workflow mapping

| Procedure step | Calls |
| --- | --- |
| 2. Detect the sources | `list_kick_skills` (query "entity lookup"), then `load_kick_skill`, then `context_browse` workspaces, paged |
| 4. Scope checkpoint (workspace and entity list) | The step 2 response, reused; no new call |
| 5 and 6. Evidence passes | The evidence skill's own Kick binding, not this file |

## Tool errors and schema drift

- **Tool errors and schema drift:** if a live call is rejected, trust the live error hint (and any loaded guide) over this skill's examples. Fix the call and retry once. For writes, a rejected call restarts the confirmation flow: re-preview, never resend a stale confirmation token. If the working shape contradicts this skill's text, add a method note to the deliverable so it can be reported and fixed centrally. Never edit this skill file mid-run.

This skill makes no writes.
