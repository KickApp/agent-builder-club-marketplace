# Known gaps

Template and pass limitations, tracked so nobody rediscovers them.

**Findings rows have no icon yet.** `ol.fnd` numbers itself with a CSS counter, so a glyph needs
the counter replaced rather than prepended. It is a template edit of a few minutes and the only one
of the four placements not wired.

**The copy audit reads the payload, not the chat message.** A deliverable built outside
`build_report.py`, and the message you write to go with it, still need the sweep by eye.

**The categorical ramp changed and charts were not re-tuned for it.** A report with seven or more
members is worth eyeballing. Six or fewer is fine.

**Label clamping measures rendered geometry, so it cannot run on a hidden tab.** It re-runs on tab
click, before print, and on resize. A tab revealed by some other route keeps its full labels until
one of those fires.
