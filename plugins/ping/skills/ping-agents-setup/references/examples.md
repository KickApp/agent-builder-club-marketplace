# Examples: ping-agents-setup

The confirmation is short, in chat, in the user's words. Dates read like "Nov 17th, 2026".
The method note, when there is one, is the last line.

## Both connected

```markdown
You're set up.

- **Ping:** connected. Your next meeting is "Quarterly review, Harbor Dental" on
  Tue Nov 17th, 2026, 10:00 am.
- **Kick:** connected. Claude can see one workspace, Harbor Dental Books.

Try: "Prep me for my next meeting with Harbor Dental". At the end of the day, try "Give
me my end-of-day recap". To grow a client, try "What else should we be selling Harbor
Dental".
```

## Kick not signed in

```markdown
Ping is connected, and Kick is not yet.

- **Ping:** connected. Nothing is booked in the coming days.
- **Kick:** not connected. Run `/mcp`, choose Kick, then Authenticate, and pick the
  workspace your firm works in. Then ask me to check again.

The meeting brief and the recap work now. The numbers from the books come once Kick is
connected.
```

## Several Kick workspaces

```markdown
- **Ping:** connected. Your next meeting is "Onboarding call" on Wed Nov 18th, 2026,
  2:30 pm.
- **Kick:** connected. Claude can see three workspaces: Harbor Dental Books, Lakeside
  Movers, and Firm Operations. Which one should I use for your clients?
```
