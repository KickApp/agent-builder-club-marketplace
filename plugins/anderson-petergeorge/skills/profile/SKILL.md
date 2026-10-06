---
name: profile
description: Derives an accounting firm's ideal client profile and anti-profile from its own clients, as a contrast with names, from the ranked table and the client cards, across revenue band, entity type, industry, tools, books condition, how they work with the firm, and what they buy, then states it as fields a lead source can use. Use when the owner asks who their ideal client is, what their best clients have in common, or who to stop taking, or when /quanto reaches the profile.
---

# Profile

## Summary

The second output. Take the clients at the top of the ranking that the owner also enjoys,
take the ones at the bottom or with the most headache, put their cards side by side, and say
in a paragraph what the top group shares that the bottom group lacks, and the reverse, with
names and exceptions in the same breath. Then state the result as fields a lead source can
match on. With fewer than three clients in the top group the heading says hypothesis.

## Inputs

The ranked table and the client cards from the conversation. Without a ranking, ask for the
rank step by name; this skill never builds its own numbers.

## Workflow

1. Sort every client into exactly one place, in this order:
   - Worth validating: any client whose verdict depends on hours, or whose fee or hours are
     unknown, whatever else the card says. Named at the end with what would settle each.
   - Bottom group: settled negative or thin, or settled healthy with messy books and several
     bad signals. One is enough; the anti-profile then says "from one client".
   - Top group: settled healthy, clean or fair books, no more than one bad signal, and not
     graded fire by the owner; from the top of the ranking down, two to four of them. A
     healthy client the owner would fire is middle, with its line in step 4.
   - Middle: everyone left. Not evidence either way.
2. Lay the cards side by side on these dimensions: what they do; revenue band; entity type
   and count; tools; books condition; how they work with the firm (documents, decisions,
   temperament); what they buy and what they have asked for; how they came to the firm if
   known.
3. Write the contrast as one paragraph of at most 120 words, with names: what all or nearly
   all of the top group share, what the bottom group shares, and each exception by name
   ("Vance is the one S-corp on QuickBooks, so entity type and software are not the
   pattern"). A trait held by one client is an observation, not a pattern; say which it is.
4. Under a short heading "Your grades against the data", one line per client whose grade
   the groups confirm or contradict, pointing back to the rank section's driver where they
   disagree. Keep it out of the paragraph.
5. State the profile as fields: industry, business size, location, entity type, services
   bought and asked for, books condition, how they work with you, who decides and how fast,
   tools. Each filled from the contrast or marked "not enough evidence". Then the
   anti-profile in one or two lines.
6. End with three questions for the partners and "what would sharpen this" in one line (a
   Kick connection, a time export, three more months of notes).
7. Under the router, hand off to the close or to options; standalone, say "Next: where to
   find more of them, if you want it" and stop.

## Degradation

| Missing | What happens |
| --- | --- |
| Fewer than three in the top group | Heading reads "a hypothesis from <n> clients"; the paragraph names them and the fields lean on observations, marked so |
| No notes | Profile rests on money, books condition from Kick, and the owner's words; the working-with-them and decisions fields read "not enough evidence" |
| No Kick | Books condition from notes and owner only; volume absent |
| Every row depends on hours | No groups; the page says one month of time tracking is the next step and stops the profile at "worth validating" |

## When to ask vs proceed

Never mid-run. Deliver with the exceptions named and the owner's disagreements pointed at;
questions go in the closing section.

## Completion criteria

- [ ] Every client is in exactly one place: top group, bottom group, middle, or worth validating
- [ ] Every shared trait names the clients behind it and every exception by name
- [ ] Every owner grade is checked against the groups in one line
- [ ] Every field is filled from the contrast or reads "not enough evidence"
- [ ] The heading says hypothesis when the top group has fewer than three

## Guardrails

- Only the firm's own clients are evidence. No market statistics, no industry averages, no
  assumptions about what a "typical" firm's ideal client is.
- Traits come from card lines with sources; the middle group and worth-validating clients
  never support a trait.
- Client names stay in the firm-internal version. Produce an anonymized version (fields
  kept, paragraph dropped) only when the owner asks for something to share outside the firm.
- Findings are questions for the partners, never a directive to fire anyone.

## Deliverable

Voice, for every document this skill writes: a careful accountant's prose, not an
assistant's. Short declarative sentences with varied length, sentence-case headings,
concrete nouns and real figures. Banned tells: em dashes; filler words (delve, robust,
seamless, leverage, comprehensive, crucial); the "not just X, but Y" construction; AI
boilerplate ("It's important to note", "In conclusion", "I hope this helps"); decorative
emoji; bolded keyword openers in prose. Read a sentence back; if no accountant would say
it aloud to a client, rewrite it.

```markdown
## Your ideal client (a hypothesis from <n> clients)
<Names> share <traits>. <Exception by name and what it rules out>. Your hardest <n>,
<names>, share <traits>.

Your grades against the data
- <Client>: <grade> agrees. / <Client>: <grade> disagrees; see the ranking (<driver>).

| Field | Your ideal client | Evidence |
| Industry | ... or not enough evidence | <names> |
| Business size | ... | |
| Location | ... | |
| Entity type | ... | |
| Services they buy and ask for | ... | |
| Books condition | ... | |
| How they work with you | ... | |
| Who decides, how fast | ... | |
| Tools | ... | |

Anti-profile: <one or two lines>.
Worth validating: <clients whose verdict depends on hours, and what settles each>.
What would sharpen this: <one line>.

## Three questions for the partners
1. ...
```

## Learned preferences

Apply an owner's correction immediately and keep it for the rest of the run. When a
correction should stick (fields to add or drop, the anonymized version by default), offer to
save it as a dated entry under this heading with the owner's approval. Preferences never
add outside data or loosen the evidence rule. If this file is not writable here, hand the
owner the text.
