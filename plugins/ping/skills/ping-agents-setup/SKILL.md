---
name: ping-agents-setup
description: "Connects Ping and Kick for the Ping Agents plugin and confirms each connection with one safe read, then names what to try first. Read-only. Use when someone installs or enables Ping Agents, asks how to connect Ping or Kick, reports missing Ping or Kick tools, a failed sign-in, the wrong Ping account or Kick workspace, or says \"set up Ping\" or \"connect Kick\"."
---

# Ping Agents setup

## Purpose

Gets Ping and Kick connected so the meeting brief, the end-of-day recap, and the revenue
finder can run, for the person who just installed the plugin.

1. Each connection, signed in
2. One safe read from each, said in one line
3. What to try first

## Procedure

- [ ] 1. Check which Ping and Kick tools are live.
      Load `references/ping.md` and `references/kick.md`.
- [ ] 2. For each connection with no tools, have the user sign in.
      The user runs `/mcp`, picks the server (Ping or Kick), and chooses Authenticate.
      Ping: the account that holds the firm's clients and meetings.
      Kick: the workspaces Claude may use.
- [ ] 3. Confirm Ping with one safe read: the next upcoming meeting.
      Say the title and date, or that none is booked.
- [ ] 4. Confirm Kick with one safe read: the workspaces Claude can see.
      Name them. Several: ask which one the firm works in.
- [ ] 5. Name what to try first, with the client's name in the ask.
      Prep: "Prep me for my next meeting with <client>".
      Recap: "Give me my end-of-day recap".
      Revenue: "What else should we be selling <client>".

## Caveats

- **Tools missing after sign-in.** The plugin is disabled, or sign-in did not finish.
  Have the user enable Ping Agents, then Authenticate again.
- **Ping answers "Not connected".** The session dropped. Retry the same read once. A second
  failure: Authenticate again.
- **Wrong Ping account.** The upcoming meetings belong to someone else, or the list is
  empty for a busy firm. Have the user sign out of Ping under `/mcp` and sign in with the
  firm account.
- **Wrong or missing Kick workspace.** The firm's workspace is not in the list. Have the
  user sign in to Kick again and select it.
- **Kick says the tools are not enabled.** The workspace is on a free plan, and Kick's
  tools need a paid one. Say so, and point to Kick support.
- **Duplicate connections.** Ping or Kick is also connected another way, so the same
  tools show twice. Prefer the plugin's connections, or turn the duplicate off.
- **A token or password in chat.** Never ask for one. If the user pastes one, tell them to
  remove it and sign in under `/mcp` instead.
- **Only one connection works.** Report what works. The recap and the meeting brief
  need Ping; the books half needs Kick.

## Example

See `references/examples.md`.

## Completion

Done when:

- [ ] Each connection is confirmed by a read, or named as not connected with the next step
- [ ] The Kick workspace is named, or the user was asked which one
- [ ] The user has one ask to try first, worded for their own client
- [ ] No write was attempted in either connector

Cleanup: the confirmation stays in chat. No token, password, or ID appears in it.
