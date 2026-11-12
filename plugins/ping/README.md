# Ping Agents

Built by [Kick](https://kick.co) for firms that run client conversations through
[Ping](https://www.pingassistant.com), for
[Agent Builder Club](https://www.agentbuilder.club/builders/ping/ping-agents).

## Install

```text
/plugin marketplace add KickApp/agent-builder-club-marketplace
/plugin install ping@agent-builder-club
```

The plugin connects to Ping and to Kick. Sign in to each when Claude asks. No sign-in
prompt? Run `/mcp`, pick the server, and choose **Authenticate**. Then say "set up Ping
Agents": Claude checks both connections and suggests what to try first.

## What it does

Reads what your clients said in Ping (meetings, transcripts, email, and action items) next
to their books in Kick, and turns it into three things you can use right away.

**Before a call**, a one-page brief: an agenda built from the client's own asks, the
questions to ask, what is still open on each side, the swings in the books worth raising,
and what to watch out for. Every line names the meeting, email, or report it came from.

**At the end of the day**, a recap of every client you met: what happened, what is still
open, and tomorrow's meeting when there is one. A call with no transcript is named as
unread, never guessed at.

**When you want to grow a client**, a PDF of up to five things they have asked for that you
sell, each backed by their own words, the speaker, and the date. It also lists work you
promised that no agreement covers, so it may not be billed.

Say things like "prep me for my next meeting with Harbor Dental", "give me my end-of-day
recap", or "what else should we be selling Harbor Dental".

## Safety

Read-only. It never sends an email, drafts in Ping, contacts a client, or changes the books.
Opportunities are questions to raise, not advice.

## Feedback

Tell us what to fix at support@kick.co.
