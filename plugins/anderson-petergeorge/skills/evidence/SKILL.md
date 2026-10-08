---
name: evidence
description: Builds one card per client for an accounting firm from Kick (volume, review backlog, accounts, tasks), practice and proposal tools (fees, agreed services, time by client), meeting notes (how the relationship runs, good and bad signals, books condition), and any fee list, invoice export, or time export the owner provides, with a source on every line. Use when the owner drops in notes or exports and asks what they say per client, or when /quanto needs the client list or the full cards. Read-only against every system.
argument-hint: "[period]"
---

# Evidence

## Purpose

Build the data's side of the story: one card per client, a source on every line. Fees and
hours come from tools and exports, or from the owner when nothing else has them; how the
relationship runs comes from the notes; books condition comes from Kick and the notes
together. On Kick, every read follows [references/kick.md](references/kick.md).

1. Roster pass, before the interview: the numbered client list the interview asks about.
2. Full pass, after the owner answers and confirms scope: the cards and their footer.

A standalone run with no cards yet does both passes.

## Procedure

Roster pass:

- [ ] 1. Classify the inputs from their contents, never their filenames.
      Any subset: Kick, when it responds; practice and proposal tools whose tools respond
      (Ignition, Karbon, Financial Cents, Canopy, TaxDome, Keeper, or any other) for the
      client list, agreed services, invoices or fees, and time by client; notes tools
      whose tools respond (Ping, Grain, Fathom, Fireflies, Notion); files or pasted text
      (meeting notes and transcripts in md, txt, docx, or pdf, a fee list, an invoice or
      billing export, a time-by-client export, a client list); the owner's interview
      answers once they exist.
- [ ] 2. Load the connector guidance before the first read.
      Kick: per [references/kick.md](references/kick.md). Any other tool: read its live
      descriptors first.
- [ ] 3. Collect client names from every source.
      Kick workspaces and entities with industry and location; the practice tool's client
      list; note filenames, headers, and opening lines (no full bodies yet); fee list rows;
      export client columns.
- [ ] 4. Match identities across sources.
      Normalize (strip LLC, Inc, Ltd, punctuation, case), exact match, then token overlap.
      List every ambiguous or unmatched name under the list with the question that
      resolves it. Set aside, by name, entities Kick marks as personal.
- [ ] 5. Write the numbered client list.
      Name, aliases seen, what they do, sources. Order by monthly fee descending when fees
      are known, alphabetically otherwise. Close with one line naming the source classes
      found. Under the router, hand off to the interview in the same turn; standalone,
      stop here and offer it.

Full pass (skip anything the owner excluded, and say so):

- [ ] 6. Take fees per client for the months served, from the first source that exists.
      Invoice export or practice tool (net of write-offs; say billed or collected); the
      owner's fee times months served (agreed basis); the firm's own books in Kick. One
      source per client.
- [ ] 7. Take hours per client.
      A time export or practice tool gives actual hours for the period, marked actual.
      Otherwise the owner's range, marked estimate.
- [ ] 8. Read Kick per client, every read scoped to that client and the period.
      Transactions a month, share awaiting review, share missing a payee, connected
      accounts, open tasks, and, only if the guides expose them cheaply, uncategorized or
      unmatched counts. Optionally the client's own revenue, for a size band. Before
      recording any zero, run one query known to return rows and quote its count.
- [ ] 9. Read the notes onto the Business, Working with them, and Signals lines.
      Per [references/reading-notes.md](references/reading-notes.md): plain words, dated,
      at most two short quotes per client, cited to file and line.
- [ ] 10. Judge books condition: one word and its reasons.
      From the Kick figures, the notes, and the owner's remarks, per the card reference.
- [ ] 11. Write the cards, then the footer.
      Card shape in [references/client-card.md](references/client-card.md).
      Below the cards: the control query and its count ("Control query: none, Kick not
      connected" when Kick is absent); "Not available", one line per absent source or
      exclusion, or none; a method note only if a call behaved differently from this
      skill's text. Under the router, hand off to rank in the same turn; standalone, say
      "Next: the ranking" and stop.

## Caveats

- Never merge two names silently. Ambiguous matches are asked in one batch under the client
  list.
- Two sources that disagree on a fee are both shown with a question mark, and the owner is
  asked which is current.
- Never blend actual hours and an owner's range into one number.
- Client financials never come from notes. A revenue remark is a size band on the Business
  line, never a fee, and the client's own revenue is never mixed with fees.
- An empty result proves nothing until a control query succeeds. The tell is a zero with no
  control count in the footer.
- A firm-wide or workspace-wide figure is not a client figure. A read that cannot be scoped
  to the client leaves that figure "Not available" for the client.
- A fact the data settles is derived, never asked. Scope is asked once, by the interview,
  and never again per query. Never ask for ids.
- The period is the trailing twelve months unless the owner or a `Firm notes` block names
  one. Label it assumed when defaulted.
- Read-only against every system. Anything whose descriptor creates, updates, deletes, or
  reverts is out of scope.
- Connectors other than Kick have no binding here. Build each request from the tool's live
  descriptor, never from remembered field names. On a rejected call, trust the live error,
  fix and retry once, add a method note, and never edit this skill file mid-run.
- A missing source shortens the card and never stops the run:
  - No Kick: the Kick line reads "not connected"; books condition from notes and owner
    only; hours from the owner.
  - No practice tool or exports: fees from the owner's list; hours from the owner's range,
    marked estimate.
  - No notes: Working with them and Signals read "no notes"; the profile later says it
    rests on money and the owner's words.
  - No fee source at all: the Fee line reads unknown; rank orders by effort and headache
    and names fees as the missing input.
  - A connector that does not respond, or data the plan does not include: one "Not
    available" line. Files and pasted text are first class.
  - A client or source the owner excluded: the card reads "excluded by owner", and nothing
    is read for it.
- An owner's correction applies at once for the rest of the run. One that should stick (a
  client always set aside, a preferred fee source, a notes folder) is offered for the
  `Firm notes` block. It never changes how any connector is called.

## Example

The roster pass output, then the footer under the full-pass cards. Each card between them
follows the card reference. More cases in [references/examples.md](references/examples.md).

```markdown
## Your clients: Copperleaf Bookkeeping, Sep 2025 to Aug 2026 (assumed)
Confidential, firm internal use only.

1. Pinecrest Dental Studio (also "Pinecrest Dental") · dental practice · Kick, fee list, notes
2. Vance Refrigeration (also "Vance Refrig LLC") · HVAC services · Kick, fee list, Karbon, notes
3. Larkin Event Rentals · event rentals · Kick, fee list, notes
4. Tidewater Print Shop · commercial printing · Kick, fee list, notes

Unmatched: "T. Marsh" appears in two notes and no other source. Is this a client, and which one?
Set aside: Vance Family Trust (Kick marks it personal).
Sources found: Kick (4 client workspaces), Karbon, 14 note files, a fee list.

This pass was read-only.
```

```markdown
Control query: all transactions, Pinecrest Dental Studio, Sep 2025 to Aug 2026, 4,920 rows.
Not available: notes tool (none responded); invoice export (none provided).

This pass was read-only.
```

## Completion

Done when:
- Every name from every source is matched, set aside with a reason, or on the unmatched
  list with its question.
- Every fee and hours line names its source and says actual or estimate.
- Every Kick figure names the period.
- Books condition on every card gives its reasons.
- The control query is recorded before any zero appears.
- "Not available" lists every absent or excluded source, or says none.
- The list and the cards each sit under "Confidential, firm internal use only" and end
  with "This pass was read-only."

Cleanup: the list and the cards stay in the conversation for the interview and for rank,
profile, and options. Unmatched names wait under the list for the owner's answer. A method
note rides on the page for the owner to forward to Kick support.
