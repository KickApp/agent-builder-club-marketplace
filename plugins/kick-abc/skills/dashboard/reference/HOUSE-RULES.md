# House rules

Applies to every skill in this plugin. A skill states only what is true of *it*.

## Paths

Every path in a skill file is relative to that skill's own folder: `reference/DATA.md` means
the `reference/` directory sitting beside the SKILL.md you are running, which carries its own
copy of every document and script the skill needs. Resolve the skill folder to an absolute
path once, then prefix it onto every script and reference, because a script runs from the
user's working directory, not from the skill's.

## Working out loud

Progress narration is one line when an artifact starts and one when it is done and verified:
"Building the management report..." then "Management report done, all totals tie." Never
narrate individual file reads, script runs, payload edits, or fix-up cycles; work that hits a
snag gets fixed quietly and mentioned only if it changes the outcome or the timeline. The
transcript should read like a status board, not a lab notebook.

## One artifact per turn

In a run producing more than one deliverable, finish generating an artifact and stop: say it
is built in one line, give its top finding, and ask whether to continue ("Dashboard's built
and its numbers tie — continue with the management report?"). Never start artifact N+1 in
the same turn that finished artifact N. The brand-and-verify pass over the whole set, and
the handover of every file path, is its own closing turn. This keeps long runs inside the
platform's per-turn limits at natural finish lines instead of stopping mid-build.

## Tie out

Every figure in a deliverable traces to a line in a report you actually pulled this run, and the
report and period are named. Show the operands for anything derived: `gross margin = 511,000 /
1,240,000 = 41.2%`. A number you cannot tie out does not ship. The skill says which report line
was missing and moves on without that metric.

Prefer the accounting system's purpose-built report over rebuilding from raw transactions. Leaf
lines re-sum to reported section totals; income less expenses re-sums to reported net income. On a
mismatch, stop, show both numbers, and re-fetch rather than smoothing it over.

## So what

No number ships without its implication. A metric earns its place by changing what the reader
would do, and the deliverable says what that is in plain English a non-finance owner follows on
first read. "Gross margin is 41.2%" is data. "Gross margin is 9 points below comparable shops,
which is about $112,000 a year at your revenue" is advisory.

Write for someone who has never opened a P&L. No account codes, no `COGS`, no `DSO` without
saying what it means once.

## Read-only

These skills read. They never write transactions, journal entries, budgets, or files into the
accounting system. When a deliverable exposes something that needs fixing, name the follow-up and
stop.

## Benchmarks are never books data

External reference data enters a deliverable through the benchmark skill and nowhere else. That
skill owns the sourcing discipline: user-supplied, then the firm's own client book, then public
government data, in that strict order, with a cited web source as a loudly labeled last resort in
its standalone report only. Every external figure carries its source and vintage on its face,
sources are never blended into one number, and no comparison at all beats an unsourced one.

Presenting an invented industry average as fact is the one hard failure in this plugin, and the
doorway does not soften it: a figure no tier can produce does not exist. Benchmark by industry
*and* size band; when the size band is unknown, say so in the source label rather than quietly
comparing against an industry-wide figure. Every other skill takes external figures only from the
benchmark skill's reference set, already labeled, and never sources its own.

## Assumptions are labeled, always

Anything not read from the books is an **assumption** with its source named (user-stated, prior
deliverable, or a pattern observed in the ledger). Never present an assumption as system data, and
never invent a line to make a total work.

## Every claim is a discussion prompt

These deliverables read as authoritative, so they carry a review gate: a qualified professional
reviews before it reaches an owner, investor, board, or lender. Findings are framed as questions
for that conversation, such as *"worth establishing whether this is a pricing question or a cost
question,"* never as directives. No authoritative tax, financing, pricing, or investment advice.

## Tool errors and drift

If a live call is rejected, trust the live error over this plugin's examples. Fix the call and
retry once. If the working shape contradicts a skill's text, add a method note to the deliverable.
Never edit a skill file mid-run.

## Learned preferences

Apply a user's correction immediately and keep it for the rest of the run. When a correction should
stick, offer to save it as a dated entry under `## Learned preferences` at the end of that skill
file, with explicit approval. Preferences change style, defaults, and thresholds, never these
house rules. If the file is not writable where the skill runs, hand the user the entry text.
