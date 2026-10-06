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

Creator plugins are named after the creator. Install one the same way, for example
`/plugin install anderson-petergeorge@agent-builder-club`.

Enable the plugin, then ask Claude to run the work. Sidekick is the entry point when you
have not named a skill. Ledger access requires a Kick account.

## Plugins

| Plugin | Built by | Skill | What it does |
| --- | --- | --- | --- |
| `kick-abc` | Kick | The full suite | The Agent Builder Club accounting suite: close, advisory, reporting, and skill-writer |
| `mike-michalowicz` | Mike Michalowicz | `profit-first-instant-assessment` | Runs the Profit First Instant Assessment against a client's books |
| `josh-schneider` | Josh Schneider | `client-meeting` | A one-page client meeting brief from the books |
| `oscar-setiawan` | Oscar Setiawan | `vendor-price-variance-monitor` | Flags vendors billing above contract or creeping up in price |
| `glenn-hopper` | Glenn Hopper | `coa-cleanup-and-reclass` | Redesigns the chart of accounts and reclassifies the year, with approval on every write |
| `ramon-liriano-jr` | Ramon Liriano Jr | `personal-business-deduction-scan` | Finds likely business deductions in personal accounts for CPA review |
| `anderson-petergeorge` | Anderson Petergeorge, CPA | `quanto` and its five steps | Ranks a firm's clients by estimated margin and draws its ideal client profile |

Kick suite skills are connector-agnostic. Kick execution lives in each skill's
`references/kick.md`.
