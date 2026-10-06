---
name: interview
description: Asks an accounting firm owner, in one message, what each client pays, how much effort each takes, which clients they would clone or fire and why, and the firm facts the analysis needs (cost rate, pricing model, where clients come from, capacity). Use when the owner wants to grade their clients, when /quanto starts, or when a margin or ideal-client question arrives with no owner input yet.
argument-hint: "[firm]"
---

# Interview

## Summary

One message, answered once. The owner knows three things nothing else does: what each
client pays, roughly how hard each one is, and which ones they would clone or fire and why.
Get all of it in one reply, about named clients, in the owner's words. Everything they say
is a hypothesis the numbers then test, and the gap between the two is the most useful thing
this plugin produces.

## Sources first

Before asking, read what already answers a question and skip it:

- The client list from the evidence skill's roster pass. Without one, ask the evidence
  skill for it; an interview without names is a survey.
- A `Firm notes` block in project instructions or earlier in the conversation: cost rate,
  hours per client, threshold, exclusions, confidentiality. Tag each "firm notes".
- A fee list, invoice export, or practice tool already surfaced: prefill the fees and ask
  only for corrections. Prefilled values are shown with their source, never hidden.
- A time export or a practice tool with time by client: skip the hours question and say
  where the hours came from.

## The message

Open with the scope checkpoint in two or three lines: which sources were found (Kick and how
many client workspaces, which practice or notes tools responded, how many note files, a fee
list), that the next step reads the full notes and books for the clients listed, and one
question: "Use all of these, or leave any client or source out?" This is the one permission
question in the run.

When no practice tool responded and there is no time or invoice export, add one line: "If
you track time or invoice from a practice tool, an export of hours by client and invoices by
client for the period would replace your estimates below. Drop them in, or tell me the tool
is connected and I will read it."

Then three clusters. Keep each to plain words a firm owner reads in a minute.

**What you charge and how hard they are.** A table with one row per client, numbered as in
the list, fees prefilled where known:

| # | Client | Monthly fee | Last raised | Pushback? | Since | Came to you via | Hours a month (a range is fine) |

Ask for: the fee (confirm or correct), when it was last raised, whether they pushed back, the
month service began if inside the period, how the client came to the firm (referral from
whom, an event, the website), and a rough hours-a-month range for your team ("3 to 5"). Say why in one clause: fee age and pushback are the two biggest margin leaks,
and without a time export the hours are the whole cost side.

**Which ones you'd clone, and why.** Grade each client clone, keep, or fire, with one line on
why. Then ask for the things the books will not show, in a sentence: who pays late, who
pushes back on fees or scope, who you do unbilled work for, who is slow with documents or
asks the same things repeatedly, whose books were a mess when you started or fall behind,
who has referred someone, who has asked to buy more.

**The firm.** Four short answers: what you sell and how you price it (fixed, hourly, mixed;
the services you want more of and out of); your loaded cost per hour for the people doing the
work, blended is fine, and this is the one number never suggested (a loaded salary and weekly
hours will do instead); where your last five clients came from and how many new ones you can
take in the next twelve months; the margin percent below which you would call a client thin
(suggest 20%) and who may see client-level results.

Close with: "Reply in any form; blanks are fine, I will label them." That line ends the turn.

## After the reply

1. Read the answers onto the client cards (shape in `../quanto/reference/client-card.md`):
   fee line, with a "since" month turned into "served n months" counting that month through
   the end of the period; hours line marked "owner's estimate" with the range as given; a
   "Came to you" line; signals in the owner's words tagged owner; the grade with its reason
   quoted. Firm answers go into a
   short `Firm` note above the cards: pricing model, cost rate, growth, threshold,
   confidentiality, and the scope decision (no answer means all sources are in).
2. A salary and hours instead of a rate: derive it and show the operands, `rate = loaded
   salary / (weekly hours x 48)`, with the 48 weeks stated as an assumption.
3. A name the owner uses that matches no listed client: ask which number they meant, in one
   line, before writing the cards.
4. Play it back in one short paragraph: how many graded, how many fees, whether a cost rate
   exists, what is blank. Hand off to the evidence skill's full pass. Under the router that
   is the same turn; standalone, say "Next: the evidence and the ranking" and stop.

## Degradation

| Missing | What happens |
| --- | --- |
| No client list | Ask the evidence skill for the roster pass; if no source has names, ask the owner to list clients and what each does |
| Owner skips grades | Rank runs without the gut comparison and says so |
| Owner skips fees and no other fee source exists | Rank ranks by effort and headache only and names fees as the one missing input |
| Owner skips the cost rate | Rank shows fee and realized rate per hour, "cost rate pending" in the margin columns |
| Owner skips hours and there is no time source | Hours unknown; rank shows fee and headache, no cost |

## When to ask vs proceed

Ask once, in this message. No second round; rank labels every blank and invites correction
at the end. The single exception is the unmatched client name above.

## Completion criteria

- [ ] Every listed client has a row, filled or blank
- [ ] Every firm answer is recorded in the owner's words or marked blank
- [ ] Every prefilled value shows its source
- [ ] The cards carry the owner's lines and the playback paragraph names the blanks

## Rules

Voice, for every message this skill writes: a careful accountant's prose, not an
assistant's. Short declarative sentences with varied length, sentence-case headings,
concrete nouns and real figures. Banned tells: em dashes; filler words (delve, robust,
seamless, leverage, comprehensive, crucial); the "not just X, but Y" construction; AI
boilerplate ("It's important to note", "In conclusion", "I hope this helps"); decorative
emoji; bolded keyword openers in prose. Read a sentence back; if no accountant would say
it aloud to a client, rewrite it.

- Owner answers are hypotheses, never findings, and always tagged owner.
- Never suggest a cost rate. Every other suggestion is shown as a suggestion.
- Never ask what a file, a tool, or the conversation already answers.
- The message may be read live in front of an audience: plain words, no codes, no
  accounting theory, three clusters and nothing more.

## Learned preferences

Apply an owner's correction immediately and keep it for the rest of the run. When a
correction should stick (question order, wording, a signal they want asked about), offer to
save it as a dated entry under this heading with the owner's approval. Preferences never
change the three-cluster shape or the no-suggested-rate rule. If this file is not writable
where the skill runs, hand the owner the entry text.
