---
name: prep
description: "Runs the prep phase of a close as one call: the reconcile skill, then the categorize skill, both writing to the same exceptions register, with their open questions batched into one checkpoint. Use when prepping a period for close, or when reconciliation and categorization should run together."
---

# Prep

## Purpose

The prep phase as one call: prove the accounts, then clean the transactions. This skill
sequences two workers and owns nothing else.

1. Reconcile the period's accounts
2. Categorize the period's transactions

## Procedure

- [ ] 1. Run the reconcile skill for the period.
- [ ] 2. Run the categorize skill with the same close context.
      Both write to the same exceptions register.
- [ ] 3. Batch the two skills' open questions into one boundary checkpoint, not two.

## Guardrails

- A blocked worker stops prep. Route its exceptions to the phase that owns them and say where things stopped.

## Example

One checkpoint, both workers reported together:

```markdown
Prep: reconcile done (12 accounts proven), categorize done (3 items to the register).
Open questions (batched): 1. <reconcile question> 2. <categorize question>
```

## Completion

Done when:

- [ ] Reconcile reports its completion criteria met
- [ ] Categorize reports its completion criteria met
- [ ] Open questions from both were raised at one checkpoint

Cleanup: both workers' artifacts and exceptions sit on the shared exceptions register;
nothing else is produced here.
