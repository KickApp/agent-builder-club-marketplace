---
name: skill-pr
description: "Kick-internal: contributes an approved skill to the agent-factory repo as a pull request, with gates run, provenance recorded, and the author credited. Use when a skill that came out of skill-writer (or any approved skill folder) should join the catalog. Requires repo access; not for customer environments."
---

# Skill PR

## Purpose

Take an approved skill folder and open the PR that puts it in the catalog, so a skill
proven in the field reaches review in minutes.

1. Verify it is ready
2. Place it in the repo
3. Run the gates
4. Open the PR

## Procedure

- [ ] 1. Verify: the skill was approved by its user (skill-writer's approval gate or
      equivalent), and it names its source material and author.
- [ ] 2. Place the folder at `abc/templated/<name>/` on a fresh branch
      `feature/skill-<name>` off main. One skill per PR.
      Write a CHANGES.md: source material, what the loop changed, iteration count, who authored and approved.
- [ ] 3. Run the gates and fix before pushing: five sections in order, zero em dashes,
      reference paths resolve, bindings reference published guides only, and **no
      client data anywhere**: fixtures synthetic, examples anonymized, no real names,
      balances, or account numbers.
- [ ] 4. Commit, push, open the PR: what the skill does, where it came from, the loop
      summary from CHANGES.md, author credit. Deliver the PR URL.

## Guardrails

- **No client data leaves the engagement.** A fixture with a real balance or vendor
  name blocks the PR; anonymize first. This gate has no override.
- Never commit to main directly, never force-push, one skill per PR.
- Credit is not optional: the PR body names the original author and approver.
- A skill that skipped the approval gate travels as a draft PR, labeled as untested.

## Example

```
git switch -c feature/skill-amazon-settlements main
# place abc/templated/amazon-settlements/, write CHANGES.md
# gates: sections, em dashes, paths, no client data
git push -u origin feature/skill-amazon-settlements
gh pr create --title "New skill: amazon-settlements" --body "<what, provenance, loop summary, credit>"
```

## Completion

Done when:

- [ ] The PR is open with gates green and the URL delivered
- [ ] CHANGES.md records provenance, the loop, author, approver
- [ ] No client data in the diff

Cleanup: nothing stays local; the branch is pushed and the working tree clean.
