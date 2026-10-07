# The client card

One card per client, written into the conversation by the evidence skill and read by rank,
profile, and options. Plain English, about ten lines, a source in parentheses on every line.
A newer card for the same client replaces an older one. Nothing is written to disk for the
run to work; an owner who wants a record can paste the cards anywhere.

## Shape

```markdown
### Vance Refrigeration (client 3 of 7)
Fee: $1,400 a month, last raised Jan 2026, no pushback; served all 12 months (owner, fee list)
Hours: 4 to 6 a month, owner's estimate (owner) | or: 58 hours in the period, actual (time export, Karbon)
Kick: 90 transactions a month, 2% awaiting review, 1% missing a payee, 3 connected accounts, no open tasks (Kick, Sep 2025 to Aug 2026)
Books condition: clean (Kick figures above; notes never mention chasing documents)
Business: HVAC services, about $2M revenue, S-corp, one entity, QuickBooks and Gusto, Scranton PA (notes Mar 2026; Kick)
Working with them: documents uploaded before every call; Bob decides on the spot (notes Mar and Jul 2026)
Signals: referred a plumbing company; asked for a quarterly forecast and a second entity; paid June the day the invoice landed (notes; owner)
Came to you: referral from a Chamber of Commerce contact, 2023 (owner)
Owner's grade: clone, "easiest client I have" (owner)
```

## Line by line

| Line | What goes there | Allowed sources |
| --- | --- | --- |
| Fee | Monthly or annual fee, when last raised, pushback, months served in the period | owner, fee list, invoice export, practice or proposal tool |
| Hours | Either an actual figure for the period, marked actual, or the owner's range, marked estimate. Never both collapsed into one number | time export, practice tool, owner |
| Kick | Transactions a month, share awaiting review, share missing a payee, connected accounts, open tasks, ledger basis if relevant. "Not connected" when Kick is absent | Kick, with the period |
| Books condition | One word, clean / fair / messy, then the reasons in a clause (see below) | Kick figures, notes, owner |
| Business | What they do, revenue band, entity type and count, tools, location | notes, Kick, practice tool |
| Working with them | How the relationship runs: documents on time or chased, who decides and how fast, how organized, whether they push back | notes, owner |
| Signals | Good and bad, in words: referred someone, asked for more, pays late, disputes invoices, unbilled work, repeated questions | notes, owner |
| Came to you | How the client arrived: referral and from whom, an event, the website, a directory; "unknown" when nobody knows | owner, notes, practice tool |
| Owner's grade | clone, keep, or fire, and the owner's one-line reason, quoted | owner |

A line with no source is left as "unknown", never guessed. A revenue figure in a note is a
band on the Business line, never a fee. Two sources that disagree are both shown with a
question mark.

## Books condition

The condition of the client's books is part of the headache and part of the cost, so it
gets its own line and, later, its own column. Judge it from whatever is present:

- Kick: share of transactions awaiting review (over a fifth is a mess), share missing a
  payee, open tasks piling up, uncategorized or unmatched items the guides expose.
- Notes: statements chased, receipts in a shoebox, personal spending mixed into the
  business account, months of catch-up when the engagement began, the same fix made twice.
- Owner: "the books were a mess when we started", "always behind".

Messy: two or more of the items above, or one of the two severe ones on its own (personal
spending mixed into the business account; a catch-up of three months or more). Fair: one
ordinary item. Clean: none. Say which items drove the word. The same rule is in the
evidence skill's `references/reading-notes.md` so the two never disagree.

## Source tags

Write them in parentheses at the end of each line: `owner`, `fee list`, `invoice export`,
`time export`, `Ignition` or the tool's name, `Kick`, `notes` with the month, `firm notes`,
`assumed`. A figure from Kick names the period it covers.
