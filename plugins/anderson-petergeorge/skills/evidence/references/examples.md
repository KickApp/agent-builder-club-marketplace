# Examples

## Good

The owner supplies a client list and a fee export. Each card line names its source: Kick,
with the period, for transaction counts and open tasks; the export for the fee. A client
with no fee in either source stays blank. Two sources that disagree are both shown:

```markdown
Fee: $1,800 a month (fee list) or $1,650 a month (Ignition)? Served all 12 months (fee list)
```

A zero arrives only after the control query. The footer reads "Control query: all
transactions, Larkin Event Rentals, Sep 2025 to Aug 2026, 4,080 rows", and the card can
then say "0 open tasks (Kick, Sep 2025 to Aug 2026)".

One full card, in the shape of [client-card.md](client-card.md). Its 410 transactions a
month are the 4,920 rows of the control query over 12 months:

```markdown
### Pinecrest Dental Studio (client 1 of 4)
Fee: $1,800 a month, served all 12 months (fee list)
Hours: 5 to 6 a month, owner's estimate (owner)
Kick: 410 transactions a month, 3% awaiting review, 1% missing a payee, 4 connected accounts, no open tasks (Kick, Sep 2025 to Aug 2026)
Books condition: clean (Kick figures above; no chasing in the notes)
Business: dental practice, $1M to $5M revenue, LLC, Xero and Gusto, Scranton PA (notes; Kick)
Working with them: documents uploaded before every call; the office manager decides within a week (notes)
Signals: never late; referred one practice; asked for forecasting (notes; owner)
Came to you: referral from a lender (owner)
Owner's grade: clone (owner)
```

## Bad

The skill reads the client's own P&L revenue in Pinecrest's workspace and writes it on the
Fee line, or reads fees from a client workspace because it was the first one listed. Fees
from Kick come only from the firm's own workspace, named before the read.

The skill fills a blank fee from a meeting note ("we did about two million" becomes a fee),
or treats an empty transaction query as zero activity before a control query has
succeeded, or merges "Vance Refrigeration" and "Vance Family Trust" into one client
without asking.
