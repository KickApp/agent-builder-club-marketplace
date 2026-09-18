# Benchmark data sourcing

The retrieval manual for the benchmark skill's source tiers. This file contains no benchmark
figures, by design: figures are fetched live at run time and stamped with their vintage, so
nothing in this plugin can quietly age into a wrong number. What this file holds is the part
that stays true: where each source lives, how to read it, and what a citation must say.

Mechanics last verified 2026-08. If a live page or table differs from its description here,
trust the live source and add a method note to the deliverable, per the drift rule in
HOUSE-RULES.md.

## Contents

- Classification: resolving industry and size band
- Tier 1: user-supplied material
- Tier 2: the firm's own client book
- Tier 3: IRS Statistics of Income, and Census QFR
- Tier 4: SEC EDGAR public filings, then cited web sources
- The citation grammar
- Metric mapping notes

## Classification: resolving industry and size band

Resolve the plain-language industry to a NAICS code before touching any tier. The Census
Bureau's NAICS search at census.gov/naics takes keywords and returns candidate codes with
definitions. Rules:

- Classify by what the business earns most of its revenue doing, not by every activity it
  touches. A machine shop that also sells scrap is 332710, not two codes.
- Prefer the six-digit code when the data source carries it, and fall back to the four-digit
  industry group when it does not. Say which level the comparison uses.
- The size band comes from annual revenue or receipts, matched to whatever bands the source
  publishes. Never compare a $2M business against an industry-wide figure without the label
  saying the band was unavailable.
- Play the resolved code and band back to the user in one line before pulling anything. A
  wrong classification makes every downstream figure confidently wrong.

## Tier 1: user-supplied material

Whatever the user or their firm hands over: a licensed IBISWorld or RMA page, a lender's
covenant sheet, a franchise disclosure document, a trade association survey. Handling rules:

- Cite it exactly as given: publisher, document, and the date or edition printed on it. Do
  not restate its vintage as fresher than the document says.
- If the material names an industry or size band different from the confirmed classification,
  surface the mismatch rather than silently using it.
- Licensed material stays in this engagement. Never carry a user-supplied figure into another
  client's reference set.

## Tier 2: the firm's own client book

The sharpest comparison when it exists: other clients of the same firm, same code, same band.

- **Availability check first.** This tier requires a surface that can query across the firm's
  clients. Where the connected system exposes only the current client's books, the tier is
  unavailable: skip it silently and note the skip in the footnote. Never approximate it from
  memory of other engagements.
- **The floor is five comparable clients.** Below five, skip the tier: a median of three lets
  a reader guess who the peers are. At five or more, report the median, and quartiles when
  the count comfortably supports them.
- **Nothing reverse-readable ships.** No peer names, no figures so specific a reader could
  identify a peer (a maximum is one client's number; a median is not).
- Vintage is the period the peer figures were pulled for, stated as such: "your firm's book,
  6 comparable clients, Q2 2026". Firm-book figures go stale after a quarter.

## Tier 3: IRS Statistics of Income, and Census QFR

**IRS SOI, Corporation Complete Report (Publication 16).** Aggregate income statement and
balance sheet items for corporations, broken out by NAICS industry and by size of total
assets or business receipts. Free, public, citable. Landing pages are stable:
irs.gov/statistics, under corporation tax statistics. Reading rules:

- **Always find the latest published tax year.** Do not assume a year: check what the current
  release is, and put that tax year in the label. The publication lags roughly two years
  behind the calendar, and the label is what makes the lag honest.
- Match the industry at the finest NAICS level the tables carry, then the receipts band
  closest to the client's revenue. When the exact band does not exist, use the nearest and
  say so in the label.
- Derive ratios from the table's own lines (business receipts, cost of goods sold, salaries
  and wages, total assets, and so on) and show the operands, per the tie-out house rule.
  Name the derivation in the label when it is an equivalent rather than the same measure:
  a "gross margin equivalent" from receipts less cost of goods sold is not identical to the
  client's book margin, and the word "equivalent" carries that.
- S corporations and partnerships file differently and appear in separate SOI studies. For a
  pass-through client, prefer the matching study when its tables support the metric, and
  otherwise disclose that the comparison set is C corporations.

**Census Bureau, Quarterly Financial Report (QFR).** Quarterly income statement and balance
sheet aggregates, fresher than SOI but covering manufacturing, mining, trade, and selected
services, mostly at larger size classes. Use it when the client's industry and size fall
inside its coverage, and prefer it over SOI when both apply and recency matters. Same rules:
latest published quarter, exact table cited, band named.

Coarse beats invented. When neither source covers the industry at a usable band, the tier
returns nothing, and that is a valid result.

## Tier 4: SEC EDGAR public filings, then cited web sources

Standalone report only, never the reference set. Only when tiers 1 to 3 produced nothing for
a metric. Within this tier, check EDGAR before any web search: audited filings with exact
provenance beat any article restating them.

**SEC EDGAR (data.sec.gov).** Free, keyless JSON APIs over every SEC filer's XBRL data. The
peer set is public companies, which is the tier's defining caveat: filers are systematically
larger than a private small business, with public-company cost structures, so the comparison
is directional context, never a small-business benchmark. Mechanics:

- Every request declares a User-Agent with a contact address, and stays under ~10 requests a
  second; EDGAR blocks anonymous or hammering clients.
- Find peers by SIC code (EDGAR predates NAICS): browse
  `sec.gov/cgi-bin/browse-edgar?action=getcompany&SIC={code}&type=10-K` and prefer the
  smallest handful of filers in the industry. Five to ten peers, median and range, peer count
  in the label. One filer is an anecdote, not a benchmark.
- Pull figures from `data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{Tag}.json` per
  company, or `data.sec.gov/api/xbrl/frames/us-gaap/{Tag}/USD/CY{year}.json` for one concept
  across all filers in a calendar period.
- Tag names drift by filer: revenue may be `Revenues`,
  `RevenueFromContractWithCustomerExcludingAssessedTax`, or `SalesRevenueNet`; `GrossProfit`
  is often absent and must be derived from revenue less `CostOfRevenue`. Show the operands.
  Fiscal years vary; the frames API's CY windows or a named fiscal year keep periods honest.
- The label always carries "public-company peer set" alongside the weakest-tier sentence, and
  the finding says why the gap might exist (scale, stock compensation, public-company
  overhead) before inviting any conclusion.
- Know when to refuse: a main-street industry with no genuine public analog (a dental
  practice is not a dental support organization roll-up) gets "no citable comparison
  available", not a forced peer set.

**Cited web sources.** When EDGAR has no genuine peers either. Requirements:

- The citation names the publisher, the page or report title, and its publication date. A
  figure with no publication date does not ship.
- Prefer publishers with a methodology to name: a trade association's member survey, a
  government agency's release, a bank's published industry study. A blog restating an unnamed
  source is not a source.
- The label carries the sentence "this is the weakest source tier in this report, treat it as
  directional", in full, every time.

## The citation grammar

Every external figure's label, one line, on the figure's face:

```
{value} ({source}, {scope}, {vintage})
```

- Tier 1: `41% (RMA Annual Statement Studies, NAICS 332710, 2025 edition, user-supplied)`
- Tier 2: `31% (your firm's book, 6 comparable clients, Q2 2026)`
- Tier 3: `29% (IRS SOI Corporation Complete Report, NAICS 332710, $1M to $5M receipts, tax year 2024)`
- Tier 4 (EDGAR): `34% (SEC EDGAR XBRL, median of 7 public filers, SIC 3541, FY2025, public-company peer set, weakest tier, directional)`
- Tier 4 (web): `27% (Precision Machining Association member survey, published 2026-03, weakest tier, directional)`

The label is data, not decoration: it travels with the figure into the reference set, the
report table's column header, and any sentence quoting the figure. A figure separated from
its label is a defect.

## Metric mapping notes

Public aggregates rarely match a small-business chart of accounts one for one. The honest
mappings, and the ones to refuse:

- Gross margin: receipts less cost of goods sold, over receipts. Label as an equivalent.
- Operating margin equivalents require the source to break out operating costs; where it
  carries only total deductions, say net margin instead of pretending.
- Liquidity ratios need balance sheet tables at the same industry and band as the income
  figures, and QFR carries them more usably than SOI at the sizes it covers.
- Payroll as a share of receipts is usually available and usually useful.
- Anything requiring owner compensation normalization (true small-business profitability)
  cannot be read from public aggregates. Refuse the metric rather than approximating, and
  say why in the footnote: pass-through owner pay makes the public figure incomparable.
- EDGAR filers carry full audited income statements, so margins there are direct reads
  rather than equivalents; the incomparability is the peer set, not the arithmetic, and the
  label carries it.
