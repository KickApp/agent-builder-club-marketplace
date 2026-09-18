# Agent Builder Club marketplace

Deployed catalog of Claude plugins for [Agent Builder Club](https://agentbuilder.club).

This repository is a publish target. Skill work happens in the private
[KickApp/agent-factory](https://github.com/KickApp/agent-factory) repo, under `abc/`.
A cleaned snapshot is copied here when a change is ready. Do not open pull requests
against this repo for skill edits.

## Install

In Claude Code or Cowork:

```text
/plugin marketplace add KickApp/agent-builder-club-marketplace
/plugin install kick-abc@agent-builder-club
```

Enable the plugin, then ask Claude to run the work. Sidekick is the entry point when you
have not named a skill. Ledger access requires a Kick account.

## Plugins

| Plugin | What it does |
| --- | --- |
| `kick-abc` | The Agent Builder Club accounting suite: close, advisory, reporting, and skill-writer |

Skills are connector-agnostic. Kick execution lives in each skill's `reference/kick.md`.
