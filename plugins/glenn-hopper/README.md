# CoA Cleanup and Reclass

Built by [Glenn Hopper](https://www.linkedin.com/in/gbhopperiii/), author of AI Mastery for
Finance Professionals, for
[Agent Builder Club](https://www.agentbuilder.club/builders/glenn-hopper/coa-cleanup-and-reclass).

## Install

```text
/plugin marketplace add KickApp/agent-builder-club-marketplace
/plugin install glenn-hopper@agent-builder-club
```

## What it does

Reviews an entity's chart of accounts and a full year of transactions, proposes a cleaner
revenue and expense structure with an old-to-new mapping, then applies the approved account
changes and reclassifies the year's transactions into the new structure with a change log.

Say things like "clean up our chart of accounts" or "restructure the CoA and reclass the
year".

## Safety

This skill writes to the books. Each write phase (account changes, then the reclass) is
previewed separately and posts only after you approve it.
