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

Install a creator plugin the same way, by its name, for example
`/plugin install quanto@agent-builder-club`.

Enable the plugin, then ask Claude to run the work. Sidekick is the entry point when you
have not named a skill. Ledger access requires a Kick account.

## Plugins

| Plugin | Built by | What it does |
| --- | --- | --- |
| `kick-abc` | Kick | The Agent Builder Club accounting suite: close, advisory, reporting, and skill-writer |
| `profit-first-instant-assessment` | Mike Michalowicz | Runs the Profit First Instant Assessment against a client's books |
| `client-meeting` | Josh Schneider | A one-page client meeting brief from the books |
| `vendor-price-variance-monitor` | Oscar Setiawan | Flags vendors billing above contract or creeping up in price |
| `coa-cleanup-and-reclass` | Glenn Hopper | Redesigns the chart of accounts and reclassifies the year, with approval on every write |
| `personal-business-deduction-scan` | Ramon Liriano Jr | Finds likely business deductions in personal accounts for CPA review |
| `quanto` | Anderson Petergeorge, CPA | Ranks a firm's clients by estimated margin and draws its ideal client profile |

Kick suite skills are connector-agnostic. Kick execution lives in each skill's
`references/kick.md`.
