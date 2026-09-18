---
name: benchmark
description: "Compares a business against an external reference and delivers the comparison as an HTML report: the client's own margins, liquidity, and efficiency beside a benchmark the user supplied, the firm's own client book, or public government data (IRS Statistics of Income), checked in that strict order. Every external figure carries its source and vintage on its face, sources are never blended into one number, and a metric with no citable comparison says so rather than estimating one. Also maintains the benchmark reference set that dashboard and flux may carry as labeled context. Read-only. Use when someone asks how they compare to the industry, whether their margins are normal, how they stack up against competitors or peers, or for an industry or peer comparison. Not for comparing the business against its own prior period, and not a valuation or comps analysis of public companies."
---

# Benchmark

## Purpose

Compares the business against the world outside its books, under the provenance contract:
an external figure is only as good as its source, and a plausible range nobody licensed is
worse than no range at all. Two modes:

1. Reference set: `benchmarks.json` in the run's shared scratch, tiers 1 to 3 only, one
   labeled row per metric for other skills to carry.
2. Standalone report: the full comparison as a branded HTML file.

## Procedure

- [ ] 1. Confirm books, period, basis. Read `reference/HOUSE-RULES.md`, `reference/DATA.md`,
      and `reference/BENCHMARK-DATA.md` (the retrieval manual for every tier: where each
      source lives, how its tables read, the citation grammar) before touching any tier.
- [ ] 2. Take the client's own figures from the run's shared pull, or compute them with the
      On Kick: guides and pull mapping in `reference/kick.md`. Other connectors: discover at runtime, never guess names.
      same formulas dashboard uses, so one margin never reads two ways.
- [ ] 3. Resolve the classification (NAICS or equivalent, from the ledger and the user's
      description) and the size band from revenue or receipts. Play both back in one line
      and let the user correct them before pulling: "Comparing as NAICS 332710, machine
      shops, $1M to $5M receipts. Right?" A business that does not classify cleanly gets
      told plainly, and the skill stops rather than forcing a peer group.
- [ ] 4. Check the tiers in strict order, per metric, stopping at the first usable figure:
      user-supplied, then the firm's own client book, then public government data, then
      (standalone report only) SEC EDGAR before any general web source.
- [ ] 5. Build the reference set, or the report payload, with every figure labeled.
- [ ] 6. Verify label coverage before building: walk the payload and check every external
      value against the citation grammar in `BENCHMARK-DATA.md`: a source, a scope, and a
      vintage, on the figure itself. One bare external figure fails the run; fix the label
      or drop the figure. The client's own figures need no label beyond the run's header.
- [ ] 7. For the standalone report, write `data.json`, then build in two steps, always in
      this order, and hand over the path:

      ```
      python3 reference/templates/build_report.py data.json {entity}-benchmark-{period}.html
      python3 reference/templates/theme.py \
              reference/brand-config.md {entity}-benchmark-{period}.html
      ```

      Step one writes the report, step two applies the firm brand and runs the copy audit;
      never fuse them, and never hand over after only step one.

## Guardrails

- **The tier order is trust, never re-ranked case by case.** The first tier producing a
  usable figure wins for that metric.
- **Every external figure carries its source and vintage on its face**, where the reader
  meets it, never in a footnote alone: "31% (your firm's book, 6 comparable clients,
  Q2 2026)", "29% (IRS SOI, NAICS 332710, $1M to $5M receipts, tax year 2024)".
- **Sources are never blended.** Two tiers with figures for one metric sit side by side,
  each labeled; averaging them manufactures a number with no source. The tell: a benchmark
  column whose header names no single source.
- **A missing comparison is a complete answer.** A metric no tier supports reads "no citable
  comparison available", never an estimate dressed as one, and the metric stays in the table.
- **The confident misclassification.** The tell: no classification line in chat before the
  pull. Confirm first, always. Size band matters: a $2M shop against an industry-wide
  average dominated by $500M companies misleads politely; with no band match, use the
  industry-wide figure with the band named as unavailable in its label.
- **The immortal vintage.** The tell: a label with a source but no date. Vintage is part of
  the label. Tier 3 lag is disclosed, never hidden: always the latest published tax year,
  found at run time rather than assumed.
- **The firm book is anonymous or absent.** Five comparable clients is the floor; below it,
  skip tier 2 silently and say so in the footnote. Medians and quartiles only, no names,
  nothing reverse-readable.
- **Tier 4 never enters the reference set.** EDGAR figures are labeled "public-company peer
  set" and directional; an industry with no genuine public analog gets no comparison. A
  general web source ships only under its full label: publisher, title, date, and "this is
  the weakest source tier in this report, treat it as directional".
- **The reference set has a shelf life.** Firm-book figures go stale after a quarter, public
  data after its publication year; a stale set is rebuilt, never silently reused. Other
  skills carry a row as one labeled line and never recompute or re-source it.
- **Nothing at any tier for every metric**: say so in chat and produce no report. An empty
  benchmark is not a deliverable.

## Example

The report opens on kpi tiles carrying the client's own headline figures: the client is the
subject, the benchmarks are context. Then the table, `"measures": true`: measure, you, one
column per source tier that produced figures, each headed with its source and vintage,
`null` where a tier had nothing.

| Measure | You | Your firm's book, 6 comparable clients, Q2 2026 | IRS SOI, NAICS 332710, $1M to $5M receipts, tax year 2024 |
| --- | --- | --- | --- |
| Gross margin | 34.2% | 31% (quartiles 27% to 35%) | 29% |
| Current ratio | 1.6 | | 1.4 |

Top finding, a question: "You run 3 points above your firm's comparable clients and 5 above
the industry. Worth confirming that is pricing or mix rather than an undercounted cost."

## Completion

Done when:

- [ ] The classification and size band were confirmed in chat before any pull
- [ ] Every external value carries source, scope, and vintage on its face; no blended column
- [ ] At most five findings, each a question carrying a number and naming its source
- [ ] Footnote carries the classification, each tier consulted and what it returned or why
      skipped, every vintage, and the review gate
- [ ] Both build steps ran, in order, for a standalone report

Cleanup: hand over `{entity}-benchmark-{period}.html`, or `benchmarks.json` in the run's
shared scratch (tiers 1 to 3 only). Name the tier trail in one line of chat.
