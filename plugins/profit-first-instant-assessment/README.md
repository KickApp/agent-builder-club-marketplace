# Profit First Instant Assessment

Built by [Mike Michalowicz](https://mikemichalowicz.com/), author of Profit First, for
[Agent Builder Club](https://www.agentbuilder.club/builders/mike-michalowicz/profit-first-instant-assessment).

## Install

```text
/plugin marketplace add KickApp/agent-builder-club-marketplace
/plugin install profit-first-instant-assessment@agent-builder-club
```

Installs one skill: `profit-first-instant-assessment`.

## What it does

Turns a client's trailing-12-month books (P&L, comparative Balance Sheet, Statement of Cash
Flows) into Mike Michalowicz's Profit First Instant Assessment table, showing the gap between
actual allocations and the Target Allocation Percentages for Profit, Owner's Pay, Tax, and
Operating Expenses.

## Triggers

Say things like:

- "Run a Profit First Instant Assessment for [client] for the last 12 months."
- "Check how this client is tracking to their Profit First targets."
- "What are the TAPs for a firm doing about $420K, and where are they bleeding?"

## Requirements

An accounting connector that can return a trailing-12 P&L, a comparative Balance Sheet with a
dollar-change column, a Statement of Cash Flows, and the chart of accounts. The skill discovers
and maps available tools, then confirms the mapping with you before reading further.

## Safety

Read-only. It never writes to the books, moves money, or schedules a transfer. It confirms the
ledger-to-Profit-First mapping before computing anything, and it does not provide financial
advice: the output is an assessment table for a qualified professional to review.

## Credit

Method: Mike Michalowicz's Profit First Instant Assessment. Category locations follow the
Profit First Professionals Profit Assessment Worksheet.
