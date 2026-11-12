# Output formats: ping-client-meeting

Both deliverables go in chat as markdown. Copy the shape, not the facts. The client,
people, and figures below are fictional.

Every line ends with a source number. Numbers run in order of first use and point to the
Sources list: a meeting, an email, a note, a portal post, or an action item, with its
date. Kick reads are sources too, as K1, K2. A line with no source does not ship.

Dates read like "Oct 13th, 2026", with the weekday in front for a meeting or a deadline
("Tue Oct 13th, 2026, 2:00 pm"). Months alone stay short ("Sep 2026"). Tool calls keep
YYYY-MM-DD; only the deliverable changes.

## Prep brief

Limits: three to five agenda items, at most three questions, at most three watch-outs.
Sources that returned nothing (email, Slack, services, agreements) share one watch-out.
Each agenda item is a bold title that says what to decide or discuss, then one or two
sentences, at most 40 words. Pick the one or two figures that make the point. Order the agenda by the client's own asks first, then the open items, then
Kick numbers and opportunities. A check that did not fire stays out.

```markdown
# Kestrel Design Co.: Q3 check-in, Tue Oct 13th, 2026, 2:00 pm
With Lena Ross (owner) and Theo Park (office manager). From our side: you and Sam.[1]

**Agenda for the call**
1. **Walk through the September numbers.** Lena asked for them before this call.[1]
   September revenue was $112,300, against $98,700 in August.[K1]
2. **Plan cash for the second designer.** Lena wants to hire in Q4.[2] Cash was $48,000
   at September 30, against net losses of $14,000, $9,000, and $16,000 in July to
   September.[K1, K2] Worth asking how they plan to fund the hire.
3. **Ask what drove the repairs spike.** Repairs were $17,600 in September, against
   $2,900, $3,100, and $3,300 in June to August.[K1]
4. **Explore taking payroll off Lena's plate.** "I do payroll every other Thursday
   night."[3] Payroll runs through a self-serve tool at $1,980 a year.[K3] Payroll
   services are not in scope.

**Questions to ask**
- When does the second designer start, and at what salary?[2]
- Are product sales taxable where they ship? From the books only: no sales tax payable balance.[K2]

**Still open**
- *We owe:* Sam to set up the new card feed. Probably done: Sam's email says it is live.
  Confirm and close it in Ping.[3, 4]
- *They owe:* Theo to send the new lease. Sam chased on Sep 30th, 2026.[3, 5]

**Watch out for**
- The Sep 22nd, 2026 quick call has no transcript. Its points come from Sam's note only.[2]

**Sources**
[1] Lena's email, Oct 8th, 2026 · [2] Sam's note, Sep 22nd, 2026 quick call (no transcript) ·
[3] Q2 review, Aug 5th, 2026 (transcript) · [4] Sam's email, Aug 20th, 2026 ·
[5] Sam's email to Theo, Sep 30th, 2026 ·
K1 Kick P&L by month, May 2025 to Sep 2026 · K2 Kick balance sheet, Sep 30th, 2026 ·
K3 Kick expenses by vendor, Oct 2025 to Sep 2026
Read: 2 meetings (1 with a transcript), 7 emails, 3 notes. Kick accrual ledger. Kick
returned no closed-through date; September 2026 used as the latest month. Both balance
sheets balance. Nothing was drafted or sent.
```

No meeting booked in the next 14 days: the header says so, and the rest keeps the same
shape.

```markdown
# Kestrel Design Co.: no meeting booked
No meeting with Kestrel is on the calendar through Tue Oct 27th, 2026, so this brief is for
whenever you next talk.[1] Last call: Q2 review, Wed Aug 5th, 2026, with Lena Ross.[2]
```

## End-of-day recap

One block per client with activity today, most activity first. A client call with no
transcript is activity. The header counts the clients found today; "of N clients" only
when the connector can list clients. Each block has the same
three headings; drop a heading with nothing under it. At most three lines under What
happened. Sources go at the end of each block. Meeting counts in the header and the
Read note split client and internal meetings.

```markdown
# End of day, Wed Oct 14th, 2026
3 clients had activity: 2 client meetings (1 with a transcript), 6 emails.

## Kestrel Design Co.
**What happened**
- Q3 check-in: Lena wants payroll off her plate and asked about the repairs spike.[1]
  Kick shows repairs of $17,600 in September.[K1]
**Still open**
- *We owe:* Sam sends the repairs detail by Fri Oct 16th, 2026.[1]
- *We owe:* you send a payroll proposal, no date set.[1]
- *They owe:* Theo sends the lease by Fri Oct 16th, 2026.[1]

Sources: [1] Q3 check-in, 2:00 pm (transcript) · K1 Kick P&L, Sep 2026

## Alder Street Dental
**What happened**
- Planning call: Dr. Vance wants to buy a second chair before December 31.[1]
**Still open**
- *We owe:* you send the purchase comparison by Oct 23rd, 2026. Not in Ping action items.[1]
**Watch out for**
- The 4:30 pm call has no transcript. This comes from your follow-up email only.[1]

Sources: [1] your email to Dr. Vance, 5:10 pm

## Birch and Vine Florists
**What happened**
- Ana asked you to bring the Q3 numbers to tomorrow's review.[1] Kick shows Q3 sales
  of $61,200.[K1]
**Still open**
- *We owe:* the Q3 numbers at tomorrow's 9:00 am review. Asked today, not yet
  confirmed.[1] Ask for a prep brief before it.

Sources: [1] Ana's email, 11:40 am · K1 Kick P&L, Jul to Sep 2026

**Watch out for**
- Email from clients with no meeting today was not read: Ping searches email one client
  at a time.[1]

Sources: [1] Ping meetings list, read Oct 14th, 2026

Read: 3 meetings (2 client, 1 with a transcript; 1 internal), 6 emails. Nothing was
drafted or sent.
```

A day with no client activity: the header says so, one watch-out names what was not
read, and the sources are the reads that came back empty.

```markdown
# End of day, Thu Oct 15th, 2026
No client calls today. All 2 meetings were internal.[1]

**Watch out for**
- Client email was not read: email is searched only for clients met today.[1]

Sources: [1] Ping meetings list, read Oct 15th, 2026

Read: 2 meetings (both internal), 0 emails. Nothing was drafted or sent.
```

A client whose only activity is a call with no transcript: one What happened line
names the call and says it was not read, one Watch out for line says nothing else from
today covers it, and the header reads "(0 with a transcript)".

No meetings at all today: the header reads "No meetings today.[1]", and the Read note
reads "Read: 0 meetings, 0 emails. No Kick figure was needed."
