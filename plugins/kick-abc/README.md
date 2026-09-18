# Kick Accounting Suite

The templated Agent Builder Club skill suite as one Claude plugin.

## Install

From this marketplace:

```text
/plugin marketplace add KickApp/agent-builder-club-marketplace
/plugin install kick-abc@agent-builder-club
```

Or load the plugin folder directly:

```bash
claude --plugin-dir /path/to/kick-abc
```

Enable the plugin, then complete Kick sign-in when a skill needs the ledger.

## What this plugin includes

- **sidekick**: the entry point. Plans which skills to run and at what scope, runs them with their own resources, finishes artifacts through brand, and reports results only.
- **Action skills**: adjust, advisory, benchmark, cashflow, close, close-setup, dashboard, deliver, intake, management-report, prep, review.
- **brand**: the appearance layer. Runs last over finished artifacts and never changes a number.
- **skill-writer / skill-pr**: turn your own workflows into new skills with clean-room test runs, and (Kick-internal) contribute them to the catalog.

Skills are connector-agnostic; Kick execution lives in each skill's
`reference/kick.md`, which loads Kick's published guides at runtime.

## License

Apache-2.0 (see the `license` field in `.claude-plugin/plugin.json`).
