---
name: quanto
description: Runs the ideal-client engagement for one accounting firm in one conversation. Interviews the owner about their clients, gathers evidence from Kick, practice tools, and meeting notes, ranks every client by estimated margin and books condition, derives the ideal client profile, and offers acquisition options on request. Read-only. Use when a firm owner asks which clients to clone, who their ideal client is, or to run Quanto.
argument-hint: "[firm]"
disable-model-invocation: true
---

# Quanto

## Purpose

Answer one question for a firm owner: which of my clients should I clone, and where do I
find more of them. This skill sequences five read-only skills (evidence,
interview, rank, profile, options) over two turns, three if the
owner wants acquisition options, and nothing has to be saved to disk for a run to complete.
On Kick, the connection check follows [references/kick.md](references/kick.md).

```
Turn 1   evidence (names only), then interview       stop: the owner answers
Turn 2   evidence (full cards), rank, profile         stop: the owner reads the page
Turn 3   options, if the owner asks                   stop
Last     close: one retro question, one notes block
```

## Procedure

- [ ] 1. Parse `[firm]` if given.
      The evidence skill finds the firm's clients either way.
- [ ] 2. Detect the sources in one pass and say them in one line.
      Four checks, each present or absent, decided by whether the tools respond in this
      session, never by whether a tool is mentioned:
      - Kick, checked per [references/kick.md](references/kick.md). Absent: say "Kick is not
        connected; authorize the Kick connector to include your books (in Claude Code,
        `/mcp`)" and continue.
      - Practice and proposal tools (Ignition, Karbon, Financial Cents, Canopy, TaxDome,
        Keeper, or any other): fees, agreed services, and time by client.
      - Notes tools (Ping, Grain, Fathom, Fireflies, Notion).
      - Files in the workspace or pasted text: meeting notes, a fee list, a billing or
        invoice export, a time-by-client export, a client list. Classify by content, not
        filename.
      Example line: "Kick connected (one org, seven client workspaces); Ignition connected;
      no notes tool; 14 note files and a fee list in the folder; no time export."
- [ ] 3. Read any `Firm notes` block in project instructions or earlier messages.
      Every fact in it counts as answered and is tagged "firm notes".
- [ ] 4. Hold the scope checkpoint once, inside the interview's first lines.
      The lines name the sources found and ask whether to use them all or leave any client
      or source out. Before the reply, read only Kick's workspace and entity list with
      industries, note filenames, headers, and opening lines, and the owner's own fee list.
      Full note bodies, per-client Kick detail, and connector content wait for the reply.
      When no practice tool responds and no time or billing export is present, the
      interview names the two exports that would most improve the analysis (time by client
      for the period, invoices by client) and where they usually come from, so the owner can
      drop them in or say "read it from the tool".
- [ ] 5. Run Turn 1: evidence roster pass, then the interview.
      Done when the client list is on screen and the interview message ends the turn.
- [ ] 6. Run Turn 2: read the owner's reply into the cards, then evidence full pass, rank,
      profile.
      Done when the cards exist and the page (disagreements, table, profile, questions) is
      on screen. End with one line naming what was produced and offering the options.
- [ ] 7. Run Turn 3, options, only when the owner asks.
      Done when the options table is on screen. End with the options skill's own closing
      line.
- [ ] 8. Apply an owner's mid-run correction at once.
      A fee, an hours range, or a grade: reissue the affected rows and any profile line that
      moves, then offer to keep it in the `Firm notes` block.
- [ ] 9. Close in order: the run summary, the retro question, the notes block.
      Summary block as in Example. Then one question, verbatim: "What did this miss or
      over-flag?" Route the answer:

      | The answer is about | Where it goes | Condition |
      | --- | --- | --- |
      | Presentation: order, wording, columns, detail | A dated one-liner on the `Learned` line of the `Firm notes` block, applied for the rest of the run | Owner approves the text |
      | A firm fact: cost rate, hours per client, threshold, exclusions, who may see results | The `Firm notes` block | Owner approves; a feeling without an example goes on its `Open questions` line |
      | A Kick or connector call that behaved differently from a skill's text | Nowhere local; the page already carries a one-line method note; ask the owner to forward it to Kick support | none |
      | Nothing | Nowhere; the run ends | |

      Offer the `Firm notes` block once, to paste into project instructions.

## Caveats

- Only this skill decides turn boundaries. Inside a turn the skills hand off without
  stopping; a "stop" in a sub-skill applies only when it runs standalone.
- A step whose result already exists in the conversation is never rerun. Resume from the
  first missing one.
- A blank in the owner's reply stays blank and is labeled downstream. Never fill it with a
  guess.
- Blocked means no clients found anywhere, or no fees from any source and the owner
  declined to give any. A blocked step stops the run and names the one thing that unblocks
  it. A thin data set is not a block; the page degrades and says how.
- The cost rate has no default. If it is blank, Turn 2 still runs and the table shows fee
  and realized rate per hour with "cost rate pending" in the margin columns.
- One period, one cost rate, and the confidential header carry through everything. The
  period defaults to the trailing twelve months and is labeled assumed when the owner did
  not name one.
- The only shared shape is one client card per client, written by the evidence skill and
  read by rank, profile, and options: lines and rules in
  [references/client-card.md](references/client-card.md). A skill that cannot find the
  cards it needs asks for the evidence step by name, never guesses.
- This skill never computes and never pulls client data. The other skills do, and every
  figure they produce carries its source.
- Read-only. No write tool of Kick or any connector runs anywhere in the run. If a step
  appears to stage a change, stop and report it.
- A saved preference changes wording, order, and defaults. It never changes the read-only
  rule, the card shape, or how any connector is called.
- Never ask for ids of any kind. The evidence skill resolves names.
- Never claim a step ran when its skill file was unavailable. Stop and name what is
  missing.
- Client-level results are confidential to the firm. Every output carries "Confidential,
  firm internal use only", and findings are framed as questions for the partners.

## Example

The text this skill adds itself: the Turn 2 closing line, then the close. The Turn 2 page
and the Turn 3 options table, worked for the same synthetic firm, are in
[references/examples.md](references/examples.md).

```markdown
That is the ranking and your ideal client. Want options for finding more clients like Pinecrest and Vance?

### Quanto: Copperleaf Bookkeeping, Sep 2025 to Aug 2026 (assumed)

**Result:** delivered
**Sources used:** Kick, Karbon (time for one client), fee list, 14 note files · **Not available:** notes tool, invoice export
**Clients:** 4 analyzed, 1 left out (Vance Family Trust, personal)
**Top finding:** Larkin Event Rentals is negative at both ends of your hours range.
**Next step:** track one month of hours on Tidewater Print Shop.

What did this miss or over-flag?

## Firm notes (quanto)
Updated: 2026-09-14
- Cost rate: $65/hr blended, source: owner
- Hours by client: Pinecrest 5 to 6, Larkin 10 to 12, Tidewater 4 to 8 per month
- Thin margin threshold: 20%
- Period: trailing 12 months
- Exclusions: Vance Family Trust (personal entity)
- Confidentiality: partners only
- Learned: 2026-09-14, call clients by name in the interview, never by number alone
- Open questions: "Larkin feels worse than the numbers say" (no example yet)
```

A blocked run reads "**Result:** stopped at <step>" and names the one thing that unblocks
it.

## Completion

Done when:
- The detection line named every source class as present or absent.
- The scope checkpoint ran once, and no permission question followed per query.
- Each turn ended at its boundary with its named last line.
- Every output carries "Confidential, firm internal use only".
- No step was claimed for a skill file that was unavailable.
- The close ran in order: summary, the verbatim question, the `Firm notes` block offered
  once.

Cleanup: the list, cards, page, and options stay in the conversation; nothing is written to
disk or to any system. Firm facts, approved preferences, and open questions land in the
`Firm notes` block for the owner to paste. A connector discrepancy stays in the page's
method note for the owner to forward to Kick support.
