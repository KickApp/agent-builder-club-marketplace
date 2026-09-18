# Agent Builder Club marketplace

Catalog of Claude plugins for [Agent Builder Club](https://agentbuilder.club). Add this repository as a marketplace, then install the plugins you want.

## Install

In Claude Code or Cowork:

```text
/plugin marketplace add KickApp/agent-builder-club-marketplace
/plugin install kick-abc@agent-builder-club
```

If the repository is private, Claude uses your existing GitHub credentials. For Anthropic's public plugin directory, this repo needs to be public.

Enable the plugin, then ask Claude to run the work. Sidekick is the entry point when you have not named a skill.

## Plugins

| Plugin | What it does |
| --- | --- |
| `kick-abc` | The Agent Builder Club accounting suite: close, advisory, reporting, and skill-writer |

### kick-abc skills

- **sidekick**: plans which skills to run and at what scope, runs them with their own resources, finishes artifacts through brand, and reports results only
- **Action skills**: adjust, advisory, benchmark, cashflow, close, close-setup, dashboard, deliver, intake, management-report, prep, review
- **brand**: the appearance layer. Runs last over finished artifacts and never changes a number
- **skill-writer**: turn your own workflows into new skills with clean-room test runs
- **skill-pr**: Kick-internal. Opens the catalog PR for an approved skill. Not for customer environments

Skills are connector-agnostic. Kick execution lives in each skill's `reference/kick.md`, which loads Kick's published guides at runtime. Ledger access requires a Kick account.

## Layout

Claude marketplaces are a git repo with `.claude-plugin/marketplace.json` at the root. Each plugin is a folder with `.claude-plugin/plugin.json` and its `skills/` at the plugin root.

```text
.claude-plugin/marketplace.json
plugins/kick-abc/.claude-plugin/plugin.json
plugins/kick-abc/skills/<name>/SKILL.md
```

Users install with `/plugin install <plugin>@agent-builder-club`.

## Source

Assembled from `abc/templated/` in [KickApp/agent-factory](https://github.com/KickApp/agent-factory) (`kick-abc`).

## License

Apache-2.0. See `LICENSE`.
