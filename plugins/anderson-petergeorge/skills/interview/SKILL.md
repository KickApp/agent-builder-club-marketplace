---
name: interview
description: Asks an accounting firm owner, in one message, what each client pays, how much effort each takes, which clients they would clone or fire and why, and the firm facts the analysis needs (cost rate, pricing model, where clients come from, capacity). Use when the owner wants to grade their clients, when /quanto starts, or when a margin or ideal-client question arrives with no owner input yet.
argument-hint: "[firm]"
---

# Interview

## Purpose

Get, in one message answered once, the three things only the owner knows: what each client
pays, roughly how hard each one is, and which ones they would clone or fire and why, about
named clients and in the owner's words. Every answer is a hypothesis the numbers then test,
and the gap between the two is the most useful thing the run produces.

1. The scope checkpoint.
2. Three clusters: what you charge and how hard they are; which ones you'd clone, and why;
   the firm.
3. The closing line, which ends the turn.
4. After the reply: the answers onto the cards, and a short playback.

## Procedure

- [ ] 1. Read what already answers a question, and skip that question.
      The client list from the evidence skill's roster pass; without one, ask the evidence
      skill for it. A `Firm notes` block (cost rate, hours per client, threshold,
      exclusions, confidentiality), each fact tagged "firm notes". A fee list, invoice
      export, or practice tool already surfaced: prefill the fees, show each with its
      source, ask only for corrections. A time export or practice tool with time by client:
      skip the hours question and say where the hours came from.
- [ ] 2. Open with the scope checkpoint in two or three lines.
      Which sources were found (Kick and how many client workspaces, which practice or
      notes tools responded, how many note files, a fee list), that the next step reads the
      full notes and books for the clients listed, and one question: "Use all of these, or
      leave any client or source out?"
- [ ] 3. Add the exports line when no practice tool responded and there is no time or
      invoice export.
      Verbatim: "If you track time or invoice from a practice tool, an export of hours by
      client and invoices by client for the period would replace your estimates below. Drop
      them in, or tell me the tool is connected and I will read it."
- [ ] 4. Ask what you charge and how hard they are, as a table.
      One row per client, numbered as in the list, fees prefilled where known: fee (confirm
      or correct), when last raised, pushback, the month service began if inside the
      period, how the client came to the firm (referral from whom, an event, the website),
      and a rough hours-a-month range for the team ("3 to 5"). Say why in one clause: fee
      age and pushback are the two biggest margin leaks, and without a time export the
      hours are the whole cost side.
- [ ] 5. Ask which ones they'd clone, and why.
      Grade each client clone, keep, or fire, with one line on why. Then, in one sentence,
      ask for what the books will not show: who pays late, who pushes back on fees or scope,
      who gets unbilled work, who is slow with documents or asks the same things
      repeatedly, whose books were a mess at the start or fall behind, who has referred
      someone, who has asked to buy more.
- [ ] 6. Ask about the firm, four short answers.
      What you sell and how you price it (fixed, hourly, mixed; the services you want more
      of and out of). Your loaded cost per hour for the people doing the work, blended is
      fine (a loaded salary and weekly hours will do instead). Where your last five clients
      came from and how many new ones you can take in the next twelve months. The margin
      percent below which you would call a client thin (suggest 20%), and who may see
      client-level results.
- [ ] 7. Close with the line that ends the turn.
      Verbatim: "Reply in any form; blanks are fine, I will label them."
- [ ] 8. After the reply, resolve any name that matches no listed client.
      Ask which number they meant, in one line, before writing the cards.
- [ ] 9. Read the answers onto the cards.
      Shape in [references/client-card.md](references/client-card.md).
      Fee line, with a "since" month turned into "served n months", counting that month
      through the end of the period. Hours line marked "owner's estimate", range as given.
      A "Came to you" line. Signals in the owner's words, tagged owner. The grade with its
      reason quoted. Firm answers go in a short `Firm` note above the cards: pricing model,
      cost rate, growth, threshold, confidentiality, and the scope decision (no answer
      means all sources are in).
- [ ] 10. Derive a cost rate from a salary and hours, showing the operands.
      `rate = loaded salary / (weekly hours x 48)`, with the 48 weeks stated as an
      assumption.
- [ ] 11. Play it back in one short paragraph, then hand off.
      How many graded, how many fees, whether a cost rate exists, what is blank. Under the
      router, hand off to the evidence skill's full pass in the same turn; standalone, say
      "Next: the evidence and the ranking" and stop.

## Caveats

- Owner answers are hypotheses, never findings, and always tagged owner.
- Never suggest a cost rate. Every other suggestion, such as the 20% threshold, is shown as
  a suggestion.
- Never ask what a file, a tool, or the conversation already answers.
- Ask once, in this message. No second round: rank labels every blank and invites
  correction at the end. The one exception is the unmatched client name.
- The scope checkpoint is the one permission question in the run.
- An interview without names is a survey. No client list from any source: ask the owner to
  list the clients and what each does.
- The message may be read live in front of an audience: plain words, no codes, no
  accounting theory, three clusters and nothing more.
- Blanks degrade the run without stopping it:
  - No grades: rank runs without the gut comparison and says so.
  - No fees and no other fee source: rank orders by effort and headache and names fees as
    the one missing input.
  - No cost rate: rank shows fee and realized rate per hour, "cost rate pending" in the
    margin columns.
  - No hours and no time source: hours unknown; rank shows fee and headache, no cost.
- Read-only. The message records the owner's words and changes no books.
- An owner's correction (question order, wording, a signal they want asked about) applies
  at once and can be kept in the `Firm notes` block. It never changes the three-cluster
  shape or the no-suggested-rate rule.

## Example

```markdown
Confidential, firm internal use only.
I found Kick with 4 client workspaces, Karbon, 14 note files, and your fee list. Next I read the full notes and books for the clients below. Use all of these, or leave any client or source out?

**What you charge and how hard they are.** Fee age and pushback are the two biggest margin leaks, and without a time export your hours are the whole cost side.

| # | Client | Monthly fee | Last raised | Pushback? | Since | Came to you via | Hours a month (a range is fine) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Pinecrest Dental Studio | $1,800 (fee list) | | | | | |
| 2 | Vance Refrigeration | $1,400 (fee list) | | | | | 58 in the period, actual (Karbon) |
| 3 | Larkin Event Rentals | $600 (fee list) | | | | | |
| 4 | Tidewater Print Shop | $500 (fee list) | | | | | |

**Which ones you'd clone, and why.** Grade each clone, keep, or fire, with a line on why. Then tell me who pays late, pushes back on fees or scope, gets unbilled work, is slow with documents or asks the same things twice, had messy books at the start or falls behind, has referred someone, or has asked to buy more.

**The firm.**
1. What do you sell, and how do you price it? Which services do you want more of, and out of?
2. Your loaded cost per hour for the people doing the work (blended is fine, or a loaded salary and weekly hours).
3. Where did your last five clients come from, and how many new ones can you take in the next twelve months?
4. Below what margin would you call a client thin (I suggest 20%), and who may see client-level results?

Reply in any form; blanks are fine, I will label them.
```

Playback after the reply: "Four clients graded, four fees confirmed, cost rate $65/hr.
Vance's hours are actual from Karbon; the other three are your ranges. Blank: who may see
client-level results."

## Completion

Done when:
- Every listed client has a row, filled or blank.
- Every firm answer is recorded in the owner's words or marked blank.
- Every prefilled value shows its source.
- The message ends with the closing line, and no second round of questions followed.
- The cards carry the owner's lines, and the playback paragraph names the blanks.

Cleanup: the owner's lines go onto the cards and the firm answers into the `Firm` note above
them, both in the conversation. Blanks stay blank for rank to label. The unmatched-name
question, if any, is answered before the cards are written.
