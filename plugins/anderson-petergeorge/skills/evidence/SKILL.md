---
name: evidence
description: Builds one card per client for an accounting firm from Kick (volume, review backlog, accounts, tasks), practice and proposal tools (fees, agreed services, time by client), meeting notes (how the relationship runs, good and bad signals, books condition), and any fee list, invoice export, or time export the owner provides, with a source on every line. Use when the owner drops in notes or exports and asks what they say per client, or when /quanto needs the client list or the full cards. Read-only against every system.
argument-hint: "[period]"
---

# Evidence

## Summary

The data's side of the story, one card per client, a source on every line. Fees and hours
come from tools and exports, or from the owner when nothing else has them. How the
relationship runs comes from the notes. Books condition comes from Kick and the notes
together. Matching the same client across sources is the hard part and happens once. Two
passes: a cheap roster pass that gives the interview its names, and a full pass after the
owner has answered and confirmed scope.

## Inputs

Any subset, classified from contents rather than filenames:

- Kick, when `context_browse` responds: client workspaces and entities, transaction
  statistics, connected accounts, open tasks, and the firm's own books if the firm keeps
  them in Kick. See the Kick section below.
- Practice and proposal tools whose tools respond (Ignition, Karbon, Financial Cents, Canopy,
  TaxDome, Keeper, or any other): client list, agreed services, invoices or fees, time by
  client. Read whatever the tool's descriptors say it offers; never assume a field exists.
- Notes tools whose tools respond (Ping, Grain, Fathom, Fireflies, Notion): notes or
  summaries per client for the period, found by searching the client's name and aliases.
- Files or pasted text: meeting notes and transcripts (md, txt, docx, pdf), a fee list, an
  invoice or billing export, a time-by-client export, a client list.
- The owner's answers from the interview, once they exist.

The period is the trailing twelve months unless the owner or a `Firm notes` block names
one; label it assumed when defaulted.

## Workflow

Roster pass (before the interview; a standalone run with no cards yet does both passes):

1. If Kick responds, discover and load its current guides first: `list_kick_skills` with
   queries for financial reports, finding and querying transactions, and entity lookup, then
   `load_kick_skill` with the exact names returned. Read each tool's live descriptor before
   its first call. Do the same for any practice or notes tool: read its descriptors, never
   remembered field names.
2. Collect client names: `context_browse` and `entities_query` for Kick workspaces and
   entities with industry and location; the practice tool's client list; note filenames,
   headers, and opening lines (not full bodies yet); fee list rows; export client columns.
3. Match identities across sources: normalize (strip LLC, Inc, Ltd, punctuation, case), exact
   match, then token overlap. List every ambiguous or unmatched name under the list with the
   question that resolves it. Never merge silently. Set aside entities Kick marks as personal,
   by name.
4. Write the numbered client list (name, aliases seen, what they do, sources), ordered by
   monthly fee descending when fees are known and alphabetically otherwise, followed by one
   line naming the source classes found. Under the router, hand off to the interview in the
   same turn; standalone, stop here and offer it.

Full pass (after the interview and the scope decision; skip anything the owner excluded and
say so):

5. Fees per client for the months served, first source that exists: invoice export or
   practice tool (net of write-offs, say whether billed or collected); the owner's fee times
   months served (agreed basis); the firm's own books in Kick (see below). One source per
   client; two that disagree are both shown with a question mark.
6. Hours per client: a time export or practice tool gives actual hours for the period, marked
   actual; otherwise the owner's range, marked estimate. Never blend the two into one number.
7. Kick per client, every read scoped to the client and the period: transactions a month,
   share awaiting review, share missing a payee, connected accounts, open tasks, and, only
   if the guides expose them cheaply, uncategorized or unmatched counts. Optionally the
   client's own revenue for a size band, never mixed with fees. Before recording any zero,
   run one query known to return rows and quote its count.
8. Notes into the card's Business, Working with them, and Signals lines, per
   [reference/reading-notes.md](reference/reading-notes.md): plain words, dated, at most two
   short quotes per client cited to file and line.
9. Books condition, one word and its reasons, from the Kick figures, the notes, and the
   owner's remarks, per the card reference.
10. Write the cards (shape in `../quanto/reference/client-card.md`), then below them: the
    control query and its count ("Control query: none, Kick not connected" when Kick is
    absent), "Not available" (each absent source or exclusion in one line), and a method
    note only if a call behaved differently from this skill's text. Under
    the router, hand off to rank in the same turn; standalone, say "Next: the ranking" and
    stop.

## Kick

No request shapes live in this plugin. Which tool family gives what:

| Need | Tool family | Keep |
| --- | --- | --- |
| Workspaces and entities the firm can reach; the firm's own workspace; personal entities | `context_browse` | the client list |
| Industry, description, address per entity | `entities_query` | Business line |
| Transaction count; count awaiting review; count missing a payee, for the period and client | `transactions_query` (statistics) | Kick line, books condition |
| Connected bank, card, and processor accounts | `financial_accounts_query` | Kick line |
| Ledger and basis | `accounting_query` | basis; what report calls need |
| Open work items | `tasks_query` | Kick line, books condition |
| The client's own revenue for the period | `reports_query` (profit and loss) | size band only |
| Fee revenue by client from the firm's own books | `reports_query` (profit and loss by counterparty, if offered), else `counterparties_query` then `transactions_query` statistics scoped to that payee | Fee line, tagged Kick firm books |

Topology: many workspaces with one entity each means each workspace is a client; one
workspace with several entities means each non-personal entity is a client, said out loud.
Scope every read to the client and period with whatever the descriptor exposes; a
workspace-wide result is not a client figure. Anything whose descriptor creates, updates,
deletes, or reverts is out of scope. Data the plan does not include is one "Not available"
line. On a rejected call, trust the error and the loaded guide, fix that one call, retry
once, and add a one-line method note.

## Degradation

| Missing | What happens |
| --- | --- |
| Kick | Kick line reads "not connected"; books condition from notes and owner only; hours from the owner |
| Practice tool and exports | Fees from the owner's list; hours from the owner's range, marked estimate |
| Notes | Working with them and Signals lines read "no notes"; the profile later says it rests on money and the owner's words |
| Any fee source | Fee line unknown; rank ranks by effort and headache and names fees as the missing input |
| A connector that does not respond | One "Not available" line; files and pasted text are first class |
| Owner excluded a client or source | Card marked "excluded by owner"; nothing read for it |

A missing source shortens the card; it never stops the run.

## When to ask vs proceed

- A fact the data settles: derive it, never ask.
- An ambiguous name match: ask in one batch under the client list.
- Two sources that disagree on a fee: show both, ask which is current.
- Period not stated: trailing twelve months, labeled assumed.
- Scope: the interview carries the one checkpoint; this skill never asks again per query.
- Never ask for ids.

## Completion criteria

- [ ] Every name from every source is matched, set aside with a reason, or on the unmatched list with its question
- [ ] Every fee and hours line names its source and says actual or estimate
- [ ] Every Kick figure names the period
- [ ] Books condition on every card gives its reasons
- [ ] The control query is recorded before any zero appears
- [ ] "Not available" lists every absent or excluded source, or says none

## Guardrails

- Read-only. No write tool of Kick or any connector.
- Requests to Kick and to every connector are built from live descriptors and loaded
  guides, never from remembered field names.
- Never conclude from an empty result before a control query succeeds.
- Client financials never come from notes; a revenue remark is a size band, never a fee.
- On a rejected call, fix from the error, retry once, record a method note. Never edit
  this skill file mid-run.

## Deliverable

Voice, for every document this skill writes: a careful accountant's prose, not an
assistant's. Short declarative sentences with varied length, sentence-case headings,
concrete nouns and real figures. Banned tells: em dashes; filler words (delve, robust,
seamless, leverage, comprehensive, crucial); the "not just X, but Y" construction; AI
boilerplate ("It's important to note", "In conclusion", "I hope this helps"); decorative
emoji; bolded keyword openers in prose. Read a sentence back; if no accountant would say
it aloud to a client, rewrite it.

The client list and the cards are the deliverables, each under "Confidential, firm internal
use only", each ending with "This pass was read-only."

## Learned preferences

Apply an owner's correction immediately and keep it for the rest of the run. When a
correction should stick (a client to always set aside, a preferred fee source, a notes
folder), offer to save it as a dated entry under this heading with the owner's approval, or
into the `Firm notes` block when it is a firm fact. Preferences never change the guardrails
or how any connector is called. If this file is not writable here, hand the owner the text.

## Reference files

- [reference/reading-notes.md](reference/reading-notes.md): what to look for in a meeting
  note and how to write it onto the card.
