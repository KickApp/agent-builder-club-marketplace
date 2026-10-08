# Worked example

Figures below are illustrative. Never quote them as live data; every delivered number comes from the current workspace. The business is fictional.

> "Find business expenses paid from my personal accounts, scan my personal Amex and personal checking in Acme LLC for 2025, software, home office, meals, phone. Group for my CPA."

1. The user named the workspace, accounts, period, and buckets, so none of those get re-asked. One consolidated ask covers the rest: "Reclassification target: suggest [sole business entity name], confirm or change?" User: "That entity."
2. Load the connector's transaction guide.
3. Resolve Acme LLC to its workspace.
4. Find the entity marked personal and the accounts that belong to it. The user confirms Amex ••1234 and Personal Checking ••5678.
5. Size each account for 2025-01-01 to 2025-12-31, money-out only: about 420 rows each.
6. Pull each account on its own, 100 rows per page, to the end.
7. Bucket the rows:
   - Adobe, Slack, AWS: Software subscriptions, $4,820 (*Estimate for review. Not filing advice.*)
   - AT&T: Phone / internet, $1,440 (*Estimate for review. Not filing advice.*)
   - Sweetgreen: Uncertain / mixed-use, meals
   - One duplicate pair flagged in its own section, out of the totals
8. Deliver the summary table, detail sections, and CPA follow-ups: document the business-use % for phone, and apply the 50% meal rules.

The Kick call sequence for this run is in [kick.md](kick.md).
