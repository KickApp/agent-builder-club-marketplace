#!/usr/bin/env python3
"""Management report engine. Feed it a payload, never edit this file.

Read skills/management-report/SKILL.md before using this. The short version:
statement lines over time, compared against prior period and prior year, delivered
as a paginated PDF. No dimensional cuts of any kind, those belong to the dashboard.

Usage:    python3 build_mgmt_report.py payload.json output.pdf [--strict]
Requires: pip install reportlab
Example:  demo-payload.json beside this script (regenerate with make_demo_payload.py)

The payload carries the leaves and the movements; the engine derives every total:
  - every subtotal is summed from its leaves, never hardcoded
  - the closing balance sheet is the opening one plus the period's P&L and cash
    movements, so assets equal liabilities and equity by construction
  - the cash flow statement is built from those same movements, so net cash
    movement equals the change in bank accounts automatically
  - every period label is derived from the declared months, so a caption can
    never disagree with the data (labels{} overrides exist for edge cases)

Validation runs first and fails loudly on shape problems. The tie-out proofs run
after derivation and fail loudly on arithmetic. If the engine cannot prove a
statement ties, it does not emit the file.

Payload schema (see demo-payload.json for a worked example):
  entity                str, required
  meta                  {prepared_by, basis, disclaimer?} optional
  period.months         contiguous ["YYYY-MM", ...], oldest first, required
  period.current        "YYYY-MM", required; needs prior month, same month prior
                        year, both fiscal-YTD windows, and a trailing 12 present
  period.fiscal_year_start_month  int, default 1
  labels                optional string overrides (period_label, cur, prv, pyr,
                        prv_long, pyr_long, ytd_cur, ytd_pyr, month_ended,
                        ytd_ended, as_of, ytd_sentence, pyr_ytd_phrase)
  coa                   [{section, group, line, polarity}], statement order;
                        section in Income / Cost of goods sold / Expense /
                        Other income / Other expense; polarity 1 or -1
  ledger                {"YYYY-MM": {line: number}}, every line every month
  balance_sheet         optional; null or absent = P&L-only report
    .lines              [{key, label, bucket, snapshot?}] in statement order;
                        bucket in cash / current_asset / fixed_asset_cost /
                        accum_dep / other_asset / current_liability /
                        lt_liability / equity_other / equity_retained
    .open               {key: number}; retained optional (derived plug if absent)
    .prior_year         {key: number}; retained optional likewise
    .movements          [{bs_key, amount, cf: {section, label?, noncash?}}];
                        amount is a number or {"ledger_line": name}; section in
                        operating / investing / financing; investing and
                        financing movements require a label
    .series             {cash: [12 numbers], working_capital: [12 numbers]}
    .cf_note            optional sentence appended to the cash flow narrative
"""

import argparse
import calendar
import json
import os
import re
import sys
from collections import OrderedDict
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, PageBreak, Flowable,
                                KeepTogether, NextPageTemplate)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group

# ----------------------------------------------------------------------------
# Palette. The Kick brand tokens, verbatim from skills/brand/SKILL.md. This PDF
# never passes through theme.py, so the engine carries the brand itself. If the
# brand config moves, this block moves with it.
# Note: no red versus green. Adverse is red, favorable is plain charcoal. Bars
# are pastel; saturation is reserved for the accent, used sparingly.
# ----------------------------------------------------------------------------
INK      = colors.HexColor("#0f1826")
INK2     = colors.HexColor("#515d71")
MUT      = colors.HexColor("#949ba7")
MUT2     = colors.HexColor("#b7bcc5")
LINE     = colors.HexColor("#e9ecf0")
LINE2    = colors.HexColor("#f3f5f7")
CARD     = colors.HexColor("#ffffff")
BG       = colors.HexColor("#fafbfc")
ACCENT   = colors.HexColor("#3793da")
PRIOR    = colors.HexColor("#94c9f1")
NEG      = colors.HexColor("#d4343c")
NEGBAR   = colors.HexColor("#faa4ab")
POSBAR   = colors.HexColor("#a8deff")
TINT     = colors.HexColor("#f2faff")
CMUT     = colors.HexColor("#d9dde2")
# The categorical ramp: pastels at one lightness, so composition reads as shape
# rather than as a score.
CATS = [colors.HexColor(h) for h in
        ("#a8deff", "#d9c1e3", "#c4f2b2", "#b5ecf2", "#f9e3ae", "#bcb9f4", "#b8efd0")]

# ----------------------------------------------------------------------------
# Type. Inter, the product's face, shipped as two pre-instanced TrueType files
# beside this script (built once from inter-latin.woff2; see make_demo_payload.py
# era notes in the repo). Runtime needs reportlab only. Helvetica is the
# fallback so the engine runs anywhere, but a report in the fallback is visibly
# off-brand: keep inter-latin-400.ttf and inter-latin-640.ttf next to this file.
# ----------------------------------------------------------------------------
FONT   = "Helvetica"
FONTB  = "Helvetica-Bold"


def _register_inter():
    global FONT, FONTB
    here = os.path.dirname(os.path.abspath(__file__))
    dirs = [here,
            os.path.join(here, "..", "reference", "templates"),
            os.path.join(os.environ.get("PLUGIN_ROOT", ""),
                         "reference", "templates")]
    found = None
    for d in dirs:
        if d and os.path.isfile(os.path.join(d, "inter-latin-400.ttf")) \
                and os.path.isfile(os.path.join(d, "inter-latin-640.ttf")):
            found = d
            break
    if not found:
        print("warning: inter-latin-400.ttf / inter-latin-640.ttf not found beside "
              "this script, falling back to Helvetica. Copy both from "
              "reference/templates so the report carries the brand face.")
        return
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont as RLFont
        pdfmetrics.registerFont(RLFont("Inter", os.path.join(found, "inter-latin-400.ttf")))
        pdfmetrics.registerFont(RLFont("Inter-Semibold", os.path.join(found, "inter-latin-640.ttf")))
        FONT, FONTB = "Inter", "Inter-Semibold"
    except Exception as e:
        print(f"warning: could not embed Inter ({e}), falling back to Helvetica.")


_register_inter()


def bar(c, x, y, w, h, color, r=None, stroke=None):
    """A rounded bar. Square-cornered rectangles are what makes a chart read as
    a spreadsheet export; every bar in this report comes through here."""
    if w <= 0.1 or h <= 0.1:
        return
    rr = min(1.8 if r is None else r, w / 2, h / 2)
    c.setFillColor(color)
    if stroke is not None:
        c.setStrokeColor(stroke)
        c.setLineWidth(0.8)
    if rr < 0.4:
        c.rect(x, y, w, h, stroke=1 if stroke is not None else 0, fill=1)
    else:
        c.roundRect(x, y, w, h, rr, stroke=1 if stroke is not None else 0, fill=1)

# ============================================================================
# PAYLOAD. Load, validate, derive. The engine's only inputs are the payload's
# leaves, movements, and registries; everything below computes from them.
# ============================================================================
_ap = argparse.ArgumentParser(description="Build the management report PDF from a payload.")
_ap.add_argument("payload", help="payload.json (see demo-payload.json)")
_ap.add_argument("out", help="output PDF path")
_ap.add_argument("--strict", action="store_true",
                 help="promote validation warnings to errors")
_args = _ap.parse_args()
OUT = _args.out

_WARNINGS = []


def fail(msg):
    sys.stderr.write(f"payload error: {msg}\n")
    sys.exit(1)


def warn(msg):
    _WARNINGS.append(msg)


def _num(v, where):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        if isinstance(v, str):
            fail(f"{where}: amounts must be raw JSON numbers, got '{v}'. "
                 "The engine does all formatting.")
        fail(f"{where}: expected a number, got {type(v).__name__}")
    return float(v)


try:
    with open(_args.payload) as _f:
        PAYLOAD = json.load(_f)
except FileNotFoundError:
    fail(f"cannot read {_args.payload}")
except json.JSONDecodeError as e:
    fail(f"{_args.payload} is not valid JSON: {e}")
if not isinstance(PAYLOAD, dict):
    fail("payload must be a JSON object")

# ---- entity and meta --------------------------------------------------------
ENTITY = PAYLOAD.get("entity")
if not ENTITY or not isinstance(ENTITY, str):
    fail("entity is required")
if len(ENTITY) > 40:
    warn(f"entity name is {len(ENTITY)} characters; the page header caps near 40")
META = PAYLOAD.get("meta") or {}
PREPARED_BY = META.get("prepared_by", "Kick")
BASIS = META.get("basis", "accrual")
DISCLAIMER = META.get("disclaimer") or (
    "Prepared from the client ledger for management use. Read only. "
    "Review before distribution. Not a substitute for professional "
    "accounting, tax, or financial advice.")

# ---- period -----------------------------------------------------------------
_period = PAYLOAD.get("period") or {}
_mre = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
_mlist = _period.get("months")
if not _mlist or not isinstance(_mlist, list):
    fail("period.months is required")
for m in _mlist:
    if not isinstance(m, str) or not _mre.match(m):
        fail(f"period.months entry '{m}' is not YYYY-MM")
MONTHS = [(int(m[:4]), int(m[5:7])) for m in _mlist]
for a, b in zip(MONTHS, MONTHS[1:]):
    nxt = (a[0] + (1 if a[1] == 12 else 0), 1 if a[1] == 12 else a[1] + 1)
    if b != nxt:
        fail(f"period.months must be contiguous and ascending; "
             f"{a[0]:04d}-{a[1]:02d} is followed by {b[0]:04d}-{b[1]:02d}")
_cur_s = _period.get("current")
if not _cur_s or not _mre.match(str(_cur_s)):
    fail("period.current is required as YYYY-MM")
CUR_YM = (int(_cur_s[:4]), int(_cur_s[5:7]))
if CUR_YM not in MONTHS:
    fail(f"period.current {_cur_s} is not in period.months")
FY_START = _period.get("fiscal_year_start_month", 1)
if FY_START not in range(1, 13):
    fail("period.fiscal_year_start_month must be 1-12")

MN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MN_FULL = ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"]
_MIDX = {ym: i for i, ym in enumerate(MONTHS)}


def month_label(i):
    y, m = MONTHS[i]
    return f"{MN[m-1]} {str(y)[2:]}"


def _shift(ym, k):
    """ym plus k months."""
    y, m = ym
    t = y * 12 + (m - 1) + k
    return (t // 12, t % 12 + 1)


def _need(ym, why):
    if ym not in _MIDX:
        fail(f"ledger month {ym[0]:04d}-{ym[1]:02d} is required ({why}) "
             "but missing from period.months")
    return _MIDX[ym]


_ci = _MIDX[CUR_YM]
M_CUR = [_ci]
M_PRV = [_need(_shift(CUR_YM, -1), "prior month comparison")]
M_PYR = [_need(_shift(CUR_YM, -12), "prior year comparison")]

# Fiscal year to date: from the latest fiscal-year start at or before current.
_fy_year = CUR_YM[0] if CUR_YM[1] >= FY_START else CUR_YM[0] - 1
_fy_start = (_fy_year, FY_START)
_n_ytd = (CUR_YM[0] * 12 + CUR_YM[1]) - (_fy_start[0] * 12 + _fy_start[1]) + 1
YTD_CUR = [_need(_shift(_fy_start, k), "fiscal year to date") for k in range(_n_ytd)]
YTD_PYR = [_need(_shift(_fy_start, k - 12), "prior fiscal year to date")
           for k in range(_n_ytd)]
T12 = [_need(_shift(CUR_YM, k - 11), "trailing twelve months") for k in range(12)]
if len(MONTHS) < 24:
    warn(f"period.months has {len(MONTHS)} months; 24 gives the fullest comparisons")

# ---- labels, derived then overridden ---------------------------------------
_NUMWORD = ["zero", "one", "two", "three", "four", "five", "six", "seven",
            "eight", "nine", "ten", "eleven", "twelve"]


def _abbr(ym):
    return f"{MN[ym[1]-1]} {ym[0]}"


def _full(ym):
    return f"{MN_FULL[ym[1]-1]} {ym[0]}"


def _eom(ym):
    return f"{MN_FULL[ym[1]-1]} {calendar.monthrange(ym[0], ym[1])[1]}, {ym[0]}"


_pyr_ym = _shift(CUR_YM, -12)
_prv_ym = _shift(CUR_YM, -1)
L = {
    "period_label": _full(CUR_YM),
    "cur": _abbr(CUR_YM),
    "prv": _abbr(_prv_ym),
    "pyr": _abbr(_pyr_ym),
    "prv_long": _full(_prv_ym),
    "pyr_long": _full(_pyr_ym),
    "ytd_cur": f"{MN[_fy_start[1]-1]} to {MN[CUR_YM[1]-1]} {CUR_YM[0]}",
    "ytd_pyr": f"{MN[_fy_start[1]-1]} to {MN[CUR_YM[1]-1]} {CUR_YM[0]-1}",
    "month_ended": f"Month ended {_eom(CUR_YM)}",
    "ytd_ended": (f"{_NUMWORD[_n_ytd].capitalize()} months ended {_eom(CUR_YM)}"
                  if _n_ytd > 1 else f"Month ended {_eom(CUR_YM)}"),
    "as_of": f"As of {_eom(CUR_YM)}",
    "ytd_sentence": f"{MN[_fy_start[1]-1]} {_fy_year} to {MN[CUR_YM[1]-1]} {CUR_YM[0]}",
    "pyr_ytd_phrase": f"the same period of {CUR_YM[0]-1}",
}
_overrides = PAYLOAD.get("labels") or {}
for k, v in _overrides.items():
    if k not in L:
        warn(f"labels.{k} is not a recognized label and was ignored")
        continue
    L[k] = str(v)
PERIOD_LABEL = L["period_label"]
CUR, PRV, PYR = L["cur"], L["prv"], L["pyr"]
YTD_N_LOWER = _NUMWORD[_n_ytd]
PYR_YEAR = CUR_YM[0] - 1

# ---- chart of accounts and ledger -------------------------------------------
_SECTIONS = ("Income", "Cost of goods sold", "Expense", "Other income", "Other expense")
_coa_in = PAYLOAD.get("coa")
if not _coa_in or not isinstance(_coa_in, list):
    fail("coa is required")
COA = []
_seen_lines = set()
for e in _coa_in:
    s, g, l, p = e.get("section"), e.get("group"), e.get("line"), e.get("polarity")
    if s not in _SECTIONS:
        fail(f"coa line '{l}': section '{s}' must be one of {', '.join(_SECTIONS)}")
    if not l or not isinstance(l, str):
        fail("every coa entry needs a line name")
    if l in _seen_lines:
        fail(f"coa line '{l}' appears twice; line names must be unique")
    _seen_lines.add(l)
    if p not in (1, -1):
        fail(f"coa line '{l}': polarity must be 1 or -1")
    COA.append((s, g, l, p))

_ledger_in = PAYLOAD.get("ledger")
if not _ledger_in or not isinstance(_ledger_in, dict):
    fail("ledger is required")
LEDGER = []
for i, (y, m) in enumerate(MONTHS):
    key = f"{y:04d}-{m:02d}"
    row_in = _ledger_in.get(key)
    if row_in is None:
        fail(f"ledger is missing month {key}")
    row = {}
    for _, _, l, _ in COA:
        if l not in row_in:
            fail(f"ledger[{key}] is missing line '{l}'. Write an explicit 0 "
                 "rather than omitting a line; an absent line is a pull error.")
        row[l] = _num(row_in[l], f"ledger[{key}]['{l}']")
    for l in row_in:
        if l not in _seen_lines:
            fail(f"ledger[{key}] carries line '{l}' that is not in the coa")
    LEDGER.append(row)


# ----------------------------------------------------------------------------
# Statement aggregation. Every subtotal is summed from leaves.
# ----------------------------------------------------------------------------
def agg(lines, months):
    """Sum a set of ledger lines across a list of month indices."""
    return sum(LEDGER[i][l] for i in months for l in lines)


def sec_lines(section):
    return [l for s, _, l, _ in COA if s == section]


def pnl(months):
    """Return an OrderedDict of every statement figure for a set of months."""
    o = OrderedDict()
    o["income"] = agg(sec_lines("Income"), months)
    o["cogs"] = agg(sec_lines("Cost of goods sold"), months)
    o["gross"] = o["income"] - o["cogs"]
    o["expense"] = agg(sec_lines("Expense"), months)
    o["noi"] = o["gross"] - o["expense"]
    o["oth_inc"] = agg(sec_lines("Other income"), months)
    o["oth_exp"] = agg(sec_lines("Other expense"), months)
    o["net"] = o["noi"] + o["oth_inc"] - o["oth_exp"]
    o["gm"] = o["gross"] / o["income"] if o["income"] else 0
    o["nm"] = o["net"] / o["income"] if o["income"] else 0
    return o


P_CUR, P_PRV, P_PYR = pnl(M_CUR), pnl(M_PRV), pnl(M_PYR)
Y_CUR, Y_PYR = pnl(YTD_CUR), pnl(YTD_PYR)
TREND = {k: [pnl([i])[k] for i in T12] for k in
         ("income", "cogs", "gross", "expense", "net", "gm", "nm")}
T12_LABELS = [month_label(i) for i in T12]

# ----------------------------------------------------------------------------
# Balance sheet and cash flow, derived from the registry so they tie.
# ----------------------------------------------------------------------------
_BUCKETS = ("cash", "current_asset", "fixed_asset_cost", "accum_dep",
            "other_asset", "current_liability", "lt_liability",
            "equity_other", "equity_retained")
_ASSET_SIDE = {"current_asset", "fixed_asset_cost", "other_asset"}

_bs_in = PAYLOAD.get("balance_sheet")
HAS_BS = bool(_bs_in)

BS_LINES = []
NI = P_CUR["net"]

if HAS_BS:
    _lines_in = _bs_in.get("lines")
    if not _lines_in:
        fail("balance_sheet.lines is required when balance_sheet is present")
    _keys = set()
    for e in _lines_in:
        k, lab, b = e.get("key"), e.get("label"), e.get("bucket")
        if not k or not lab:
            fail("every balance_sheet line needs key and label")
        if k in _keys:
            fail(f"balance_sheet line key '{k}' appears twice")
        _keys.add(k)
        if b not in _BUCKETS:
            fail(f"balance_sheet line '{k}': bucket '{b}' must be one of "
                 f"{', '.join(_BUCKETS)}")
        if len(lab) > 34:
            warn(f"balance_sheet label '{lab}' is {len(lab)} characters; "
                 "statement rows cap near 34")
        BS_LINES.append(dict(key=k, label=lab, bucket=b,
                             snapshot=e.get("snapshot")))
    _cash_keys = [e["key"] for e in BS_LINES if e["bucket"] == "cash"]
    if not _cash_keys:
        fail("balance_sheet needs at least one line with bucket 'cash'")
    _ret_keys = [e["key"] for e in BS_LINES if e["bucket"] == "equity_retained"]
    if len(_ret_keys) != 1:
        fail("balance_sheet needs exactly one line with bucket 'equity_retained'")
    RET_KEY = _ret_keys[0]

    def _read_position(d_in, name):
        if d_in is None:
            fail(f"balance_sheet.{name} is required")
        d = {}
        for e in BS_LINES:
            k = e["key"]
            if k == RET_KEY and k not in d_in:
                d[k] = None      # derived plug
                continue
            if k not in d_in:
                fail(f"balance_sheet.{name} is missing key '{k}'")
            d[k] = _num(d_in[k], f"balance_sheet.{name}['{k}']")
        for k in d_in:
            if k not in _keys:
                fail(f"balance_sheet.{name} carries unknown key '{k}'")
        return d

    def _plug(d, name):
        """Derive retained earnings as the balancing figure, or verify it."""
        sides = 0.0
        for e in BS_LINES:
            k, b = e["key"], e["bucket"]
            if k == RET_KEY:
                continue
            v = d[k]
            if b in ("cash",) or b in _ASSET_SIDE:
                sides += v
            elif b == "accum_dep":
                sides -= v
            else:
                sides -= v
        if d[RET_KEY] is None:
            d[RET_KEY] = sides
            warn(f"balance_sheet.{name}.{RET_KEY} was absent; derived the "
                 f"balancing figure {sides:,.2f}. Supplying the real retained "
                 "earnings turns the balance proof into a genuine tie-out.")
        elif abs(d[RET_KEY] - sides) > 0.01:
            fail(f"balance_sheet.{name} does not balance: {RET_KEY} is "
                 f"{d[RET_KEY]:,.2f} but the other lines imply {sides:,.2f}")
        return d

    OPEN = _plug(_read_position(_bs_in.get("open"), "open"), "open")
    PY = _plug(_read_position(_bs_in.get("prior_year"), "prior_year"), "prior_year")

    # ---- movements ----------------------------------------------------------
    _mov_in = _bs_in.get("movements") or []
    MOVES = []
    for e in _mov_in:
        k = e.get("bs_key")
        if k not in _keys:
            fail(f"movement references unknown bs_key '{k}'")
        amt = e.get("amount")
        if isinstance(amt, dict):
            ll = amt.get("ledger_line")
            if ll not in _seen_lines:
                fail(f"movement on '{k}': ledger_line '{ll}' is not in the coa")
            amt = LEDGER[_ci][ll]
        else:
            amt = _num(amt, f"movement on '{k}'")
        cf = e.get("cf") or {}
        sec = cf.get("section")
        if sec not in ("operating", "investing", "financing"):
            fail(f"movement on '{k}': cf.section must be operating, investing, "
                 "or financing")
        lab = cf.get("label")
        if sec in ("investing", "financing") and not lab:
            fail(f"movement on '{k}': investing and financing movements need cf.label")
        bucket = next(x["bucket"] for x in BS_LINES if x["key"] == k)
        if not lab:
            lab = next(x["label"] for x in BS_LINES if x["key"] == k)
        # Cash flow sign: an asset growing absorbs cash, a liability growing
        # releases it. Contra-assets and equity sit on the release side.
        cfv = -amt if bucket in _ASSET_SIDE else amt
        MOVES.append(dict(key=k, amount=amt, section=sec, label=lab,
                          noncash=bool(cf.get("noncash")), cf_value=cfv))

    CF_OPERATING_ROWS = [(m["label"], m["cf_value"]) for m in MOVES
                         if m["section"] == "operating"]
    CF_INVESTING_ROWS = [(m["label"], m["cf_value"]) for m in MOVES
                         if m["section"] == "investing"]
    CF_FINANCING_ROWS = [(m["label"], m["cf_value"]) for m in MOVES
                         if m["section"] == "financing"]
    OPERATING = NI + sum(v for _, v in CF_OPERATING_ROWS)
    INVESTING = sum(v for _, v in CF_INVESTING_ROWS)
    FINANCING = sum(v for _, v in CF_FINANCING_ROWS)
    NET_CASH = OPERATING + INVESTING + FINANCING

    # ---- closing position ---------------------------------------------------
    CLOSE = dict(OPEN)
    for m in MOVES:
        CLOSE[m["key"]] = CLOSE[m["key"]] + m["amount"]
    CLOSE[RET_KEY] = CLOSE[RET_KEY] + NI
    CLOSE[_cash_keys[0]] = CLOSE[_cash_keys[0]] + NET_CASH

    def bs(d):
        """Totals for one position, from the registry buckets."""
        o = OrderedDict()
        def bsum(*buckets):
            return sum(d[e["key"]] for e in BS_LINES if e["bucket"] in buckets)
        o["bank"] = bsum("cash")
        o["current_assets"] = bsum("cash", "current_asset")
        o["fixed_assets"] = bsum("fixed_asset_cost") - bsum("accum_dep")
        o["other_assets"] = bsum("other_asset")
        o["assets"] = o["current_assets"] + o["fixed_assets"] + o["other_assets"]
        o["current_liabilities"] = bsum("current_liability")
        o["lt_liabilities"] = bsum("lt_liability")
        o["liabilities"] = o["current_liabilities"] + o["lt_liabilities"]
        o["equity"] = bsum("equity_other", "equity_retained")
        o["liab_equity"] = o["liabilities"] + o["equity"]
        o["working_capital"] = o["current_assets"] - o["current_liabilities"]
        o["current_ratio"] = (o["current_assets"] / o["current_liabilities"]
                              if o["current_liabilities"] else 0.0)
        return o

    B_CUR, B_PRV, B_PYR = bs(CLOSE), bs(OPEN), bs(PY)
    VALS_CUR, VALS_PRV, VALS_PYR = CLOSE, OPEN, PY

    # ---- snapshot stacked-bar series, from the registry ---------------------
    def _snap_bands(vals, side_buckets, bank_first):
        bands = []
        if bank_first:
            bands.append(("Bank", sum(vals[e["key"]] for e in BS_LINES
                                      if e["bucket"] == "cash")))
        pooled = 0.0
        for e in BS_LINES:
            if e["bucket"] not in side_buckets:
                continue
            if e.get("snapshot"):
                bands.append((e["snapshot"], vals[e["key"]]))
            else:
                pooled += vals[e["key"]]
        bands.append(("Other", pooled))
        return bands

    SNAP_A = [(CUR, [("Current assets", B_CUR["current_assets"]),
                     ("Fixed assets", B_CUR["fixed_assets"]),
                     ("Other assets", B_CUR["other_assets"])]),
              (PYR, [("Current assets", B_PYR["current_assets"]),
                     ("Fixed assets", B_PYR["fixed_assets"]),
                     ("Other assets", B_PYR["other_assets"])])]
    SNAP_L = [(CUR, [("Current liabilities", B_CUR["current_liabilities"]),
                     ("Long-term liabilities", B_CUR["lt_liabilities"]),
                     ("Equity", B_CUR["equity"])]),
              (PYR, [("Current liabilities", B_PYR["current_liabilities"]),
                     ("Long-term liabilities", B_PYR["lt_liabilities"]),
                     ("Equity", B_PYR["equity"])])]
    SNAP_CA = [(CUR, _snap_bands(CLOSE, {"current_asset"}, bank_first=True)),
               (PYR, _snap_bands(PY, {"current_asset"}, bank_first=True))]
    SNAP_CL = [(CUR, _snap_bands(CLOSE, {"current_liability"}, bank_first=False)),
               (PYR, _snap_bands(PY, {"current_liability"}, bank_first=False))]

    # ---- trend series, supplied ---------------------------------------------
    _series_in = _bs_in.get("series") or {}
    def _read_series(name):
        s = _series_in.get(name)
        if not isinstance(s, list) or len(s) != 12:
            fail(f"balance_sheet.series.{name} must be a list of 12 numbers "
                 "(one per trailing month)")
        return [_num(v, f"balance_sheet.series.{name}[{i}]")
                for i, v in enumerate(s)]
    CASH_SERIES = _read_series("cash")
    WC_SERIES = _read_series("working_capital")

    CF_NOTE = _bs_in.get("cf_note")
    if CF_NOTE is not None and not isinstance(CF_NOTE, str):
        fail("balance_sheet.cf_note must be a string")
else:
    OPEN = PY = CLOSE = None
    B_CUR = B_PRV = B_PYR = None
    VALS_CUR = VALS_PRV = VALS_PYR = None
    CF_OPERATING_ROWS = CF_INVESTING_ROWS = CF_FINANCING_ROWS = []
    OPERATING = INVESTING = FINANCING = NET_CASH = None
    SNAP_A = SNAP_L = SNAP_CA = SNAP_CL = None
    CASH_SERIES = WC_SERIES = None
    CF_NOTE = None

for _w in _WARNINGS:
    print(f"warning: {_w}")
if _WARNINGS and _args.strict:
    fail(f"{len(_WARNINGS)} warning(s) with --strict set")

# ---- Proofs. Fail loudly rather than shipping a report that does not tie. ----
def close_to(a, b, tol=0.01, what=""):
    assert abs(a - b) < tol, f"TIE FAILURE {what}: {a:,.2f} vs {b:,.2f}"

close_to(P_CUR["gross"], P_CUR["income"] - P_CUR["cogs"], what="gross profit")
close_to(P_CUR["net"], P_CUR["noi"] + P_CUR["oth_inc"] - P_CUR["oth_exp"], what="net profit")
close_to(Y_CUR["income"], sum(pnl([i])["income"] for i in YTD_CUR), what="YTD income sums")
if HAS_BS:
    close_to(B_CUR["assets"], B_CUR["liab_equity"], what="closing BS balances")
    close_to(B_PRV["assets"], B_PRV["liab_equity"], what="opening BS balances")
    close_to(B_PYR["assets"], B_PYR["liab_equity"], what="prior year BS balances")
    close_to(NET_CASH, B_CUR["bank"] - B_PRV["bank"], what="CF ties to cash movement")
    close_to(CASH_SERIES[-1], B_CUR["bank"], what="cash chart closes on the balance sheet")
    close_to(CASH_SERIES[-2], B_PRV["bank"], what="cash chart opens on the balance sheet")
    close_to(CASH_SERIES[-1] - CASH_SERIES[-2], NET_CASH,
             what="cash chart final step equals net cash movement")
    close_to(WC_SERIES[-1], B_CUR["working_capital"], what="working capital chart closes")


# ============================================================================
# ENGINE. Formatting, suppression, charts, tables, page templates. Keep as is.
# ============================================================================

# ----------------------------------------------------------------------------
# Formatting. Parentheses on negatives. Currency on the first row of a section.
# ----------------------------------------------------------------------------
def money(v, dollar=False, blank_zero=True):
    if v is None:
        return ""
    r = int(round(v))
    if r == 0 and blank_zero:
        return "—"
    s = f"{abs(r):,}"
    if dollar:
        s = "$" + s
    return f"({s})" if r < 0 else s


def pct(v, dp=1):
    if v is None:
        return ""
    s = f"{abs(v)*100:.{dp}f}%"
    return f"({s})" if v < 0 else s


def pts(v, dp=1):
    """Percentage point movement. A margin change is points, never percent."""
    if v is None:
        return ""
    s = f"{abs(v)*100:.{dp}f} pts"
    return f"({s})" if v < 0 else s


def variance(cur, prior):
    return None if (cur is None or prior is None) else cur - prior


def pct_var(cur, prior):
    """Suppression rule. Returns None where a percentage would be meaningless.

    Four cases are suppressed:
      - the prior period is zero or near zero, so there is no base
      - the result crosses zero, which makes "113% lower" nonsense
      - the prior period is negative, which flips the sign of the ratio
      - the magnitude exceeds 300%
    """
    if cur is None or prior is None:
        return None
    if abs(prior) < 1:
        return None
    if prior < 0:
        return None
    if (cur < 0) != (prior < 0):
        return None
    r = (cur - prior) / abs(prior)
    if abs(r) > 3.0:
        return None
    return r


def is_adverse(var, polarity, min_mag=1.0):
    """Adverse means the variance worked against the result, whatever its sign.

    min_mag suppresses colour on immaterial movements. A $68 line in a report
    totalling half a million does not earn the loudest colour on the page.
    """
    if var is None or abs(var) < min_mag:
        return False
    return (var * polarity) < 0


def sentence(label, period, cur, prior, prior_label, polarity=1):
    """The mechanical restatement. One sentence, fixed word order, no interpretation."""
    def val(v):
        s = "$" + f"{abs(int(round(v))):,}"
        return f"({s})" if v < 0 else s

    def mag(v):
        return "$" + f"{abs(int(round(v))):,}"

    delta = cur - prior
    direction = "higher" if delta >= 0 else "lower"
    p = pct_var(cur, prior)
    if p is None:
        if (cur < 0) != (prior < 0):
            why = "the result crossed zero, so no percentage is shown"
        elif abs(prior) < 1:
            why = "no comparable base in the prior period"
        elif prior < 0:
            why = "the prior period was negative, so no percentage is shown"
        else:
            why = "the change exceeds the reporting threshold for a percentage"
        return (f"{period}: {label} was {val(cur)} against {val(prior)} in "
                f"{prior_label}, a movement of {mag(delta)} {direction}. "
                f"Percentage suppressed, {why}.")
    return (f"{period}: {label} ({val(cur)}) was {abs(p)*100:.0f}% {direction} "
            f"({mag(delta)}) than {prior_label} ({val(prior)}).")


def compact(v, bare=False):
    """Abbreviated currency for chart labels. Parentheses on negatives."""
    a = abs(v)
    if a >= 1_000_000:
        s = f"${a/1_000_000:.1f}m"
    elif a >= 1_000:
        s = f"${a/1_000:.0f}k"
    else:
        s = f"${a:.0f}"
    if v < 0:
        return s if bare else f"({s})"
    return s


# ----------------------------------------------------------------------------
# Chart flowables, hand drawn for control over fills and the variance strip.
# ----------------------------------------------------------------------------
class TrendChart(Flowable):
    """Twelve period bars with a variance strip beneath, on a shared axis."""

    # Vertical budget, bottom up. Every band is explicit so nothing collides.
    AXIS_H  = 9     # month labels
    STRIP_H = 46    # variance strip, zero line centred
    GAP_H   = 10
    CAP_H   = 0     # the page note explains the strip once, so no per-chart caption
    MAIN_H  = 70    # main bars
    LBL_H   = 9     # value labels above main bars

    def __init__(self, values, labels, polarity=1, width=6.9*inch,
                 projected_from=None):
        Flowable.__init__(self)
        self.values, self.labels, self.polarity = values, labels, polarity
        self.width = width
        self.projected_from = projected_from
        self.height = (self.AXIS_H + self.STRIP_H + self.CAP_H + self.GAP_H
                       + self.MAIN_H + self.LBL_H)

    def wrap(self, aw, ah):
        return self.width, self.height

    def draw(self):
        c = self.canv
        n = len(self.values)
        slot = self.width / n
        bw = slot * 0.60
        pad = (slot - bw) / 2

        # ---- band 1, month labels at the very bottom
        c.setFillColor(MUT)
        c.setFont(FONT, 5.6)
        for i, lab in enumerate(self.labels):
            c.drawCentredString(i * slot + slot/2, 1.5, lab)

        # ---- band 2, variance strip
        var = [None] + [self.values[i] - self.values[i-1] for i in range(1, n)]
        vals = [v for v in var if v is not None]
        vmax = max((abs(v) for v in vals), default=1) or 1
        half = (self.STRIP_H - 16) / 2          # room for a label at each end
        zero = self.AXIS_H + 8 + half
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.line(0, zero, self.width, zero)
        for i, v in enumerate(var):
            if v is None:
                continue
            x = i * slot + pad
            hgt = max(1.0, abs(v) / vmax * half)
            adverse = is_adverse(v, self.polarity)
            fill = NEGBAR if adverse else CMUT
            if v >= 0:
                bar(c, x, zero, bw, hgt, fill, r=1.4)
                ly = zero + hgt + 1.8
            else:
                bar(c, x, zero - hgt, bw, hgt, fill, r=1.4)
                ly = zero - hgt - 6.0
            c.setFillColor(NEG if adverse else MUT)
            c.setFont(FONT, 5.2)
            c.drawCentredString(x + bw/2, ly, compact(v))

        # ---- band 3, main bars. Axis starts at zero, so bars are to scale.
        y0 = self.AXIS_H + self.STRIP_H + self.CAP_H + self.GAP_H
        lo = min(0, min(self.values))
        hi = max(self.values)
        span = (hi - lo) or 1
        for i, v in enumerate(self.values):
            x = i * slot + pad
            base = y0 + (0 - lo) / span * self.MAIN_H
            hgt = (v - 0) / span * self.MAIN_H
            top, bot = max(base, base+hgt), min(base, base+hgt)
            projected = self.projected_from is not None and i >= self.projected_from
            if projected:
                c.setFillColor(colors.white)
                c.setStrokeColor(PRIOR)
                c.setLineWidth(0.6)
                c.roundRect(x, bot, bw, max(abs(hgt), 1.2), 1.8, stroke=1, fill=1)
                c.setStrokeColor(PRIOR)
                c.setLineWidth(0.5)
                yy = bot
                while yy < top:
                    c.line(x, yy, x + min(bw, top - yy), min(yy + bw, top))
                    yy += 3.0
            else:
                # Level bars are pastel, a negative level takes the pastel red,
                # a loss month should read at a glance without shouting.
                bar(c, x, bot, bw, abs(hgt), NEGBAR if v < 0 else POSBAR, r=1.8)
            c.setFillColor(NEG if v < 0 else INK2)
            c.setFont(FONT, 5.6)
            c.drawCentredString(x + bw/2, top + 2.4, compact(v))


class CompareBars(Flowable):
    """Actuals against prior month and prior year. Horizontal, to scale."""

    def __init__(self, title, rows, width=3.32*inch):
        Flowable.__init__(self)
        self.title, self.rows = title, rows
        self.width = width
        self.height = 20 + len(rows) * 17 + 12

    def wrap(self, aw, ah):
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(MUT)
        c.setFont(FONT, 7.4)
        c.drawString(0, self.height - 9, self.title)

        labw = 0.62*inch
        avail = self.width - labw - 0.62*inch
        mx = max(abs(v) for _, v, _ in self.rows) or 1
        y = self.height - 26
        for lab, v, kind in self.rows:
            c.setFillColor(MUT)
            c.setFont(FONT, 6.2)
            c.drawString(0, y + 2.6, lab)
            w = abs(v) / mx * avail
            # The current period carries the pastel accent, the comparisons sit
            # back in grey, one series to look at, two to compare against.
            fill = NEGBAR if v < 0 else (POSBAR if kind == "actual" else CMUT)
            bar(c, labw, y, w, 8.4, fill, r=2.4)
            c.setFillColor(NEG if v < 0 else INK2)
            c.setFont(FONT, 6.4)
            c.drawString(labw + w + 3, y + 2.4, compact(v))
            y -= 17


class StackBar(Flowable):
    """Composition bar. Current against prior year."""

    BAR_H = 19
    PITCH = 38

    def __init__(self, title, series, width=3.32*inch):
        Flowable.__init__(self)
        self.title, self.series = title, series
        self.width = width
        self.height = 26 + len(series) * self.PITCH + 20

    def wrap(self, aw, ah):
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(MUT)
        c.setFont(FONT, 7.6)
        c.drawString(0, self.height - 9, self.title)
        # Kick's stacked bar: pastel segments off the categorical ramp, separated
        # by a thin sliver of paper so neighbours never merge. Labels sit inside
        # in ink, white type on a pastel fill is unreadable.
        labw = 0.56*inch
        avail = self.width - labw - 6
        mx = max(sum(p for _, p in parts) for _, parts in self.series) or 1
        y = self.height - 26 - self.BAR_H
        for lab, parts in self.series:
            total = sum(v for _, v in parts) or 1
            c.setFillColor(MUT)
            c.setFont(FONT, 6.4)
            c.drawString(0, y + self.BAR_H/2 - 2, lab)
            x = labw
            for k, (nm, val) in enumerate(parts):
                w = val / mx * avail
                bar(c, x, y, w, self.BAR_H, CATS[k % len(CATS)], r=2.2,
                    stroke=colors.white)
                if w > 26:
                    c.setFillColor(INK2)
                    c.setFont(FONT, 5.8)
                    c.drawString(x + 3.4, y + self.BAR_H/2 + 1.4, compact(val))
                    c.setFillColor(MUT)
                    c.setFont(FONT, 5.0)
                    c.drawString(x + 3.4, y + self.BAR_H/2 - 6.0,
                                 f"{val/total*100:.0f}%")
                x += w
            y -= self.PITCH
        # Legend
        c.setFont(FONT, 5.8)
        x = labw
        ly = y + self.PITCH - self.BAR_H - 8
        for k, (nm, _) in enumerate(self.series[0][1]):
            c.setFillColor(CATS[k % len(CATS)])
            c.roundRect(x, ly, 5.4, 5.4, 1.4, stroke=0, fill=1)
            c.setFillColor(MUT)
            c.drawString(x + 8, ly + 0.6, nm)
            x += 8 + c.stringWidth(nm, FONT, 5.8) + 11


class Rule(Flowable):
    def __init__(self, width=6.9*inch, thickness=0.5, color=LINE, space=0):
        Flowable.__init__(self)
        self.width, self.thickness, self.color, self.space = width, thickness, color, space
        self.height = thickness + space

    def wrap(self, aw, ah):
        return self.width, self.height

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.space, self.width, self.space)


# ----------------------------------------------------------------------------
# Styles
# ----------------------------------------------------------------------------
S = {
    "h1": ParagraphStyle("h1", fontName=FONTB, fontSize=19, leading=23,
                         textColor=INK, spaceAfter=2),
    "h2": ParagraphStyle("h2", fontName=FONTB, fontSize=11, leading=14,
                         textColor=INK, spaceBefore=10, spaceAfter=5),
    "h3": ParagraphStyle("h3", fontName=FONT, fontSize=8.4, leading=11,
                         textColor=MUT, spaceBefore=7, spaceAfter=3),
    "body": ParagraphStyle("body", fontName=FONT, fontSize=8, leading=11.6,
                           textColor=INK2, spaceAfter=5),
    "note": ParagraphStyle("note", fontName=FONT, fontSize=7.2, leading=10,
                           textColor=MUT, spaceAfter=4),
    "sent": ParagraphStyle("sent", fontName=FONT, fontSize=7.6, leading=10.4,
                           textColor=INK2, spaceBefore=2, spaceAfter=3),
    "coverbig": ParagraphStyle("coverbig", fontName=FONTB, fontSize=30, leading=34,
                               textColor=INK),
    "coversub": ParagraphStyle("coversub", fontName=FONT, fontSize=12, leading=16,
                               textColor=MUT),
    "tocL": ParagraphStyle("tocL", fontName=FONT, fontSize=8.6, leading=17,
                           textColor=INK2),
    "tocR": ParagraphStyle("tocR", fontName=FONT, fontSize=8.6, leading=17,
                           textColor=MUT, alignment=TA_RIGHT),
}

PW, PH = letter
LM = RM = 0.75*inch
CW = PW - LM - RM


# ----------------------------------------------------------------------------
# Statement table builder
# ----------------------------------------------------------------------------
STMT_COLS = [2.55*inch, 0.87*inch, 0.87*inch, 0.87*inch, 0.87*inch, 0.87*inch]


def to_two_period(rows):
    """Recast five-column rows as current against prior year only.

    A year to date statement compared against the preceding six months invites
    the reader to compare a first half with a second half, which is not a
    like for like period. Prior year is the only honest comparison, so the
    sequential column is dropped and a percentage variance takes its place.
    """
    out = []
    for r in rows:
        v = r["values"]
        k = r.get("kinds") or ["money"] * len(v)
        if k[0] == "pct":
            nv, nk = [v[0], v[3], v[4], None], ["pct", "pct", "pts", "pts"]
        else:
            c, y = v[0], v[3]
            p = pct_var(c, y) if (c is not None and y is not None) else None
            nv, nk = [c, y, v[4], p], ["money", "money", "money", "pct"]
        nr = dict(r)
        nr["values"], nr["kinds"], nr["var_idx"] = nv, nk, (2, 3)
        out.append(nr)
    return out


def statement_table(rows, group_headers, sub_headers, col_widths=None):
    """rows: list of dicts with label, level, values[5], bold, rule, polarity, dollar, pctrow."""
    data = [group_headers, sub_headers]
    style = [
        ("FONTNAME", (0, 0), (-1, 1), FONT),
        ("FONTSIZE", (0, 0), (-1, 1), 6.4),
        ("TEXTCOLOR", (0, 0), (-1, 0), MUT),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        # Sub-header band
        ("BACKGROUND", (1, 1), (-1, 1), colors.HexColor("#eef0f3")),
        ("TEXTCOLOR", (1, 1), (-1, 1), INK2),
        ("LINEBELOW", (1, 1), (-1, 1), 0.5, LINE),
    ]
    ncol = len(sub_headers)
    if ncol == 6:
        style += [("LINEBELOW", (1, 0), (2, 0), 0.5, LINE),
                  ("LINEBELOW", (3, 0), (4, 0), 0.5, LINE)]
    else:
        style.append(("LINEBELOW", (1, 0), (-1, 0), 0.5, LINE))

    r = 2
    for row in rows:
        indent = " " * (row["level"] * 3)
        cells = [indent + row["label"]]
        # kinds runs parallel to values: money, pct, or pts. Defaults to money.
        kinds = row.get("kinds") or ["money"] * len(row["values"])
        for k, v in enumerate(row["values"]):
            kind = kinds[k]
            if kind == "pct":
                cells.append(pct(v) if v is not None else "")
            elif kind == "pts":
                cells.append(pts(v) if v is not None else "")
            elif kind == "ratio":
                cells.append("" if v is None else
                             (f"({abs(v):.2f})" if v < 0 else f"{v:.2f}"))
            else:
                cells.append(money(v, dollar=row.get("dollar", False)))
        data.append(cells)

        fn = FONTB if row.get("bold") else FONT
        style += [("FONTNAME", (0, r), (-1, r), fn),
                  ("FONTSIZE", (0, r), (-1, r), 6.9),
                  ("TEXTCOLOR", (0, r), (-1, r), INK if row.get("bold") else INK2)]

        if row.get("rule"):
            style.append(("LINEABOVE", (0, r), (-1, r), 0.5, LINE))
        if row.get("rule") == "heavy":
            style.append(("LINEABOVE", (0, r), (-1, r), 0.9, MUT2))
        if row.get("space_before"):
            style.append(("TOPPADDING", (0, r), (-1, r), 6))

        # Adverse tone on the variance columns only. Never on a level column.
        pol = row.get("polarity", 1)
        for vi in row.get("var_idx", (2, 4)):
            v = row["values"][vi]
            # Percentage-point movements are fractions, so they need a much
            # smaller materiality floor than a dollar variance.
            floor = 0.0005 if kinds[vi] in ("pts", "pct") else (
                0.005 if kinds[vi] == "ratio" else 1.0)
            if v is not None and is_adverse(v, pol, floor):
                style.append(("TEXTCOLOR", (vi + 1, r), (vi + 1, r), NEG))
        r += 1

    # A statement group never splits across a page break. A page that opens on
    # one orphaned line and its total reads as data overflowing the layout, and
    # it is the first thing a reviewer flipping pages notices. Each block runs
    # from a header row (no values) to its total row (the rule); blocks longer
    # than 14 lines split naturally rather than forcing an oversize page.
    start = None
    for k, row in enumerate(rows):
        tr = k + 2  # two header rows above the data
        if all(v is None for v in row["values"]):
            if start is None:
                start = tr
            continue
        if start is None:
            start = tr
        if row.get("rule") and (tr - start) <= 14:
            style.append(("NOSPLIT", (0, start), (-1, tr)))
        if row.get("rule"):
            start = None

    if col_widths is None:
        num = ncol - 1
        col_widths = [CW - num * 0.87*inch] + [0.87*inch] * num
    t = Table(data, colWidths=col_widths, repeatRows=2)
    t.setStyle(TableStyle(style))
    return t


def build_pnl_rows(cur_months, prv_months, pyr_months):
    """Full P&L with hierarchy. Subtotals summed from leaves."""
    rows = []
    first_money = [True]

    def val(lines, months):
        return agg(lines, months)

    def add(label, level, lines, bold=False, rule=None, polarity=-1,
            space_before=False, explicit=None):
        if explicit is not None:
            c, p, y = explicit
        else:
            c = val(lines, cur_months)
            p = val(lines, prv_months)
            y = val(lines, pyr_months)
        dollar = first_money[0]
        if dollar:
            first_money[0] = False
        rows.append(dict(label=label, level=level,
                         values=[c, p, variance(c, p), y, variance(c, y)],
                         bold=bold, rule=rule, polarity=polarity,
                         dollar=dollar, space_before=space_before))

    pc, pp, py = pnl(cur_months), pnl(prv_months), pnl(pyr_months)

    # Income
    rows.append(dict(label="Income", level=0, values=[None]*5, bold=True))
    for s, g, l, pol in COA:
        if s == "Income":
            add(l, 1, [l], polarity=pol)
    add("Total income", 1, sec_lines("Income"), bold=True, rule=True, polarity=1)

    # COGS
    rows.append(dict(label="Cost of goods sold", level=0, values=[None]*5,
                     bold=True, space_before=True))
    cogs_groups = []
    for s, g, l, _ in COA:
        if s == "Cost of goods sold" and g not in cogs_groups:
            cogs_groups.append(g)
    for grp in cogs_groups:
        gl = [l for s, g, l, _ in COA if s == "Cost of goods sold" and g == grp]
        rows.append(dict(label=grp, level=1, values=[None]*5))
        for l in gl:
            add(l, 2, [l], polarity=-1)
        add(f"Total {grp.lower()}", 2, gl, bold=True, rule=True, polarity=-1)
    add("Total cost of goods sold", 1, sec_lines("Cost of goods sold"),
        bold=True, rule=True, polarity=-1)

    add("Gross profit", 0, None, bold=True, rule="heavy", polarity=1,
        space_before=True, explicit=(pc["gross"], pp["gross"], py["gross"]))
    rows.append(dict(label="Gross profit margin", level=1,
                     values=[pc["gm"], pp["gm"], pc["gm"]-pp["gm"],
                             py["gm"], pc["gm"]-py["gm"]],
                     kinds=["pct", "pct", "pts", "pct", "pts"], polarity=1))

    # Expense
    rows.append(dict(label="Expense", level=0, values=[None]*5,
                     bold=True, space_before=True))
    groups = []
    for s, g, l, _ in COA:
        if s == "Expense" and g not in groups:
            groups.append(g)
    for grp in groups:
        gl = [l for s, g, l, _ in COA if s == "Expense" and g == grp]
        rows.append(dict(label=grp, level=1, values=[None]*5))
        for l in gl:
            add(l, 2, [l], polarity=-1)
        add(f"Total {grp.lower()}", 2, gl, bold=True, rule=True, polarity=-1)
    add("Total expense", 1, sec_lines("Expense"), bold=True, rule=True, polarity=-1)

    add("Net operating income", 0, None, bold=True, rule="heavy", polarity=1,
        space_before=True, explicit=(pc["noi"], pp["noi"], py["noi"]))

    rows.append(dict(label="Other income", level=0, values=[None]*5,
                     bold=True, space_before=True))
    for s, g, l, pol in COA:
        if s == "Other income":
            add(l, 1, [l], polarity=1)
    add("Total other income", 1, sec_lines("Other income"), bold=True,
        rule=True, polarity=1)

    rows.append(dict(label="Other expense", level=0, values=[None]*5,
                     bold=True, space_before=True))
    for s, g, l, pol in COA:
        if s == "Other expense":
            add(l, 1, [l], polarity=-1)
    add("Total other expense", 1, sec_lines("Other expense"), bold=True,
        rule=True, polarity=-1)

    add("Net profit", 0, None, bold=True, rule="heavy", polarity=1,
        space_before=True, explicit=(pc["net"], pp["net"], py["net"]))
    rows.append(dict(label="Net profit margin", level=1,
                     values=[pc["nm"], pp["nm"], pc["nm"]-pp["nm"],
                             py["nm"], pc["nm"]-py["nm"]],
                     kinds=["pct", "pct", "pts", "pct", "pts"], polarity=1))
    return rows


def bs_rows():
    """Balance sheet rows from the payload's line registry. Sections and
    subtotals are emitted generically, so a client's own chart of accounts
    renders without touching the engine."""
    rows = []
    first = [True]

    def add(label, cv, pv, yv, level=2, bold=False, rule=None, polarity=1,
            space_before=False, neg=False):
        if neg:
            cv, pv, yv = -cv, -pv, -yv
        dollar = first[0]
        if dollar:
            first[0] = False
        rows.append(dict(label=label, level=level,
                         values=[cv, pv, variance(cv, pv), yv, variance(cv, yv)],
                         bold=bold, rule=rule, polarity=polarity, dollar=dollar,
                         space_before=space_before))

    def header(label, level, space_before=False, bold=False):
        rows.append(dict(label=label, level=level, values=[None]*5, bold=bold,
                         space_before=space_before))

    def lines_in(*buckets):
        return [e for e in BS_LINES if e["bucket"] in buckets]

    def addline(e, polarity=1, neg=False):
        add(e["label"], VALS_CUR[e["key"]], VALS_PRV[e["key"]], VALS_PYR[e["key"]],
            polarity=polarity, neg=neg)

    def addtotal(label, key, level=2, rule=True, polarity=1, space_before=False):
        add(label, B_CUR[key], B_PRV[key], B_PYR[key], level=level, bold=True,
            rule=rule, polarity=polarity, space_before=space_before)

    header("Assets", 0, bold=True)
    header("Current assets", 1)
    for e in lines_in("cash", "current_asset"):
        addline(e)
    addtotal("Total current assets", "current_assets")
    if lines_in("fixed_asset_cost", "accum_dep"):
        header("Fixed assets", 1, space_before=True)
        for e in lines_in("fixed_asset_cost"):
            addline(e)
        for e in lines_in("accum_dep"):
            addline(e, polarity=-1, neg=True)
        addtotal("Total fixed assets", "fixed_assets")
    if lines_in("other_asset"):
        header("Other assets", 1, space_before=True)
        for e in lines_in("other_asset"):
            addline(e)
    addtotal("Total assets", "assets", level=1, rule="heavy", space_before=True)

    header("Liabilities and equity", 0, bold=True, space_before=True)
    header("Current liabilities", 1)
    for e in lines_in("current_liability"):
        addline(e, polarity=-1)
    addtotal("Total current liabilities", "current_liabilities", polarity=-1)
    if lines_in("lt_liability"):
        header("Long-term liabilities", 1, space_before=True)
        for e in lines_in("lt_liability"):
            addline(e, polarity=-1)
    addtotal("Total liabilities", "liabilities", level=1, polarity=-1)
    header("Equity", 1, space_before=True)
    for e in lines_in("equity_other"):
        addline(e)
    for e in lines_in("equity_retained"):
        addline(e)
    addtotal("Total equity", "equity")
    addtotal("Total liabilities and equity", "liab_equity", level=1,
             rule="heavy", space_before=True)
    return rows


# ----------------------------------------------------------------------------
# Page furniture
# ----------------------------------------------------------------------------
class Anchor(Flowable):
    """Zero-height marker. The document records which page each anchor lands
    on, which is what lets the contents page carry real page numbers."""

    def __init__(self, name):
        Flowable.__init__(self)
        self.name = name
        self.width = self.height = 0

    def wrap(self, aw, ah):
        return 0, 0

    def draw(self):
        pass


class Doc(BaseDocTemplate):
    def __init__(self, path):
        BaseDocTemplate.__init__(self, path, pagesize=letter,
                                 leftMargin=LM, rightMargin=RM,
                                 topMargin=0.72*inch, bottomMargin=0.66*inch,
                                 title=f"Management report, {PERIOD_LABEL}, {ENTITY}",
                                 author=PREPARED_BY)
        self.section_pages = {}
        frame = Frame(LM, 0.66*inch, CW, PH - 0.72*inch - 0.66*inch, id="n",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        cover = Frame(LM, 0.66*inch, CW, PH - 0.72*inch - 0.66*inch, id="c",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[cover], onPage=self.cover_page),
            PageTemplate(id="body", frames=[frame], onPage=self.body_page),
        ])

    def afterFlowable(self, fl):
        if isinstance(fl, Anchor) and fl.name not in self.section_pages:
            # The footer numbers body pages from 1, one behind the physical page.
            self.section_pages[fl.name] = self.page - 1

    def cover_page(self, c, d):
        c.setFillColor(ACCENT)
        c.rect(0, 0, 0.24*inch, PH, stroke=0, fill=1)

    def body_page(self, c, d):
        c.saveState()
        # Header
        c.setFont(FONT, 7)
        c.setFillColor(MUT)
        c.drawRightString(PW - RM, PH - 0.48*inch,
                          f"Management report  |  {ENTITY}  |  {PERIOD_LABEL}")
        # Entity mark, in the brand accent. Initials come from the entity name.
        initials = "".join(w[0] for w in ENTITY.split()[:2]).upper()
        c.setFillColor(ACCENT)
        c.roundRect(LM, PH - 0.585*inch, 15, 15, 3.4, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont(FONTB, 7)
        c.drawCentredString(LM + 7.5, PH - 0.535*inch, initials)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.line(LM, PH - 0.64*inch, PW - RM, PH - 0.64*inch)
        # Footer
        c.setFont(FONT, 5.6)
        c.setFillColor(MUT2)
        c.drawString(LM, 0.42*inch, DISCLAIMER)
        c.setFont(FONT, 7)
        c.setFillColor(MUT)
        c.drawRightString(PW - RM, 0.42*inch, str(c.getPageNumber() - 1))
        c.restoreState()


# ----------------------------------------------------------------------------
# Story. Built twice: the first pass records which page each section lands on,
# the second pass writes the real contents page from those numbers.
# ----------------------------------------------------------------------------
SECTIONS = ["About this report", "Profitability summary", "Profitability trends"]
if HAS_BS:
    SECTIONS += ["Cash management", "Cash flow statement", "Balance sheet snapshot"]
SECTIONS += ["Profit and loss, month", "Profit and loss, year to date"]
if HAS_BS:
    SECTIONS += ["Balance sheet", "Ratio appendix"]


def build_story(pages):
    st = []

    # ---- 1. Cover
    st += [Spacer(1, 2.5*inch),
           Paragraph("Management report", S["coverbig"]),
           Spacer(1, 6),
           Paragraph(PERIOD_LABEL, S["coversub"]),
           Spacer(1, 30),
           Rule(2.2*inch, 0.8, ACCENT),
           Spacer(1, 14),
           Paragraph(ENTITY, ParagraphStyle("e", fontName=FONT, fontSize=13,
                                            textColor=INK2)),
           Spacer(1, 4),
           Paragraph(f"Prepared by {PREPARED_BY}", S["note"]),
           Spacer(1, 3.0*inch),
           Paragraph(DISCLAIMER, ParagraphStyle("d", fontName=FONT, fontSize=6,
                                                leading=8.4, textColor=MUT2))]

    # ---- 2. Contents
    st.append(PageBreak())
    st += [Paragraph("Contents", S["h1"]), Spacer(1, 4), Rule(CW, 0.7, LINE),
           Spacer(1, 14)]
    toc_rows = [[Paragraph(n, S["tocL"]),
                 Paragraph(str(pages.get(n, "")), S["tocR"])] for n in SECTIONS]
    t = Table(toc_rows, colWidths=[CW - 0.6*inch, 0.6*inch])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE2),
                           ("TOPPADDING", (0, 0), (-1, -1), 4),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    st.append(t)

    # ---- 3. About
    st.append(PageBreak())
    st.append(Anchor("About this report"))
    st += [Paragraph("About this report", S["h1"]), Spacer(1, 4),
           Rule(CW, 0.7, LINE), Spacer(1, 12)]
    st += [Paragraph("What this covers", S["h3"]),
           Paragraph(f"This report covers the financial results of {ENTITY} for "
                     f"{PERIOD_LABEL} and for the "
                     f"{L['ytd_ended'][0].lower()}{L['ytd_ended'][1:]}.",
                     S["body"])]
    st += [Paragraph("Basis of preparation", S["h3"]),
           Paragraph(f"{BASIS.capitalize()} basis, prepared from the general "
                     f"ledger. The month is compared against {L['prv_long']} and "
                     f"against {L['pyr_long']}. The year to date is compared "
                     f"against the same {YTD_N_LOWER} months of {PYR_YEAR}. No "
                     "budget or forecast is held in the ledger, so no budget "
                     "column is shown.",
                     S["body"])]
    elements = ("Profit and loss statement. Balance sheet. Cash flow statement. "
                "Statement-derived ratios." if HAS_BS else
                "Profit and loss statement. No balance sheet data was provided, "
                "so the balance sheet, cash flow, and ratio pages are omitted.")
    st += [Paragraph("Elements of the analysis", S["h3"]),
           Paragraph(elements, S["body"])]
    st += [Paragraph("Legend", S["h3"])]
    leg = [["Solid fill", "Actual, closed period"],
           ["Hatched fill", "Not yet closed"],
           ["Charcoal figure", "No adverse effect on result"],
           ["Red figure", "Adverse effect on result"],
           ["Figures in parentheses", "Negative amount"],
           ["Em rule", "Nil balance or no activity"]]
    t = Table(leg, colWidths=[1.5*inch, CW - 1.5*inch])
    t.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), FONT),
                           ("FONTSIZE", (0, 0), (-1, -1), 7.4),
                           ("TEXTCOLOR", (0, 0), (0, -1), INK2),
                           ("TEXTCOLOR", (1, 0), (1, -1), MUT),
                           ("TEXTCOLOR", (0, 3), (0, 3), NEG),
                           ("TOPPADDING", (0, 0), (-1, -1), 2.6),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE2)]))
    st.append(t)
    st += [Spacer(1, 10),
           Paragraph("A note on direction", S["h3"]),
           Paragraph("Colour marks the effect on the result, not the sign of the "
                     "number. A fall in cost of goods sold is a negative variance and "
                     "a favourable one, so it is shown in charcoal. A rise in cost of "
                     "goods sold is a positive variance and an adverse one, so it is "
                     "shown in red.", S["body"])]

    # ---- 4. Profitability summary
    st.append(PageBreak())
    st.append(Anchor("Profitability summary"))
    st += [Paragraph("Profitability summary", S["h1"]), Spacer(1, 4),
           Rule(CW, 0.7, LINE), Spacer(1, 12)]

    def cmp_rows(key):
        return [(CUR, P_CUR[key], "actual"), (PRV, P_PRV[key], "prior"),
                (PYR, P_PYR[key], "prior")]

    g1 = Table([[CompareBars("Total income", cmp_rows("income")),
                 CompareBars("Cost of goods sold", cmp_rows("cogs"))],
                [CompareBars("Total expense", cmp_rows("expense")),
                 CompareBars("Net profit", cmp_rows("net"))]],
               colWidths=[CW/2, CW/2])
    g1.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
                            ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    st.append(g1)

    st += [Spacer(1, 6), Paragraph("Summary", S["h2"])]

    SUM_LINES = [("Income", "income", 1), ("Cost of goods sold", "cogs", -1),
                 ("Gross profit", "gross", 1), ("Total expense", "expense", -1),
                 ("Net profit", "net", 1)]
    hdr1 = ["", CUR, "", "", L["ytd_cur"], "", ""]
    hdr2 = ["", "Actuals", f"+/- {PRV}", f"+/- {PYR}", "Actuals", "+/- prior year", ""]
    data = [hdr1, hdr2]
    sty = [("FONTNAME", (0, 0), (-1, 1), FONT), ("FONTSIZE", (0, 0), (-1, 1), 6.4),
           ("TEXTCOLOR", (0, 0), (-1, 0), MUT),
           ("BACKGROUND", (1, 1), (5, 1), colors.HexColor("#eef0f3")),
           ("TEXTCOLOR", (1, 1), (-1, 1), INK2),
           ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
           ("LINEBELOW", (1, 1), (5, 1), 0.5, LINE),
           ("TOPPADDING", (0, 0), (-1, -1), 2.4),
           ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4),
           ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]
    r = 2
    firstd = True
    for lab, key, pol in SUM_LINES:
        vm, vp, vy = P_CUR[key], P_PRV[key], P_PYR[key]
        yv, yp = Y_CUR[key], Y_PYR[key]
        data.append([lab, money(vm, firstd), money(variance(vm, vp)),
                     money(variance(vm, vy)), money(yv, firstd),
                     money(variance(yv, yp)), ""])
        firstd = False
        bold = lab in ("Gross profit", "Net profit")
        sty += [("FONTNAME", (0, r), (-1, r), FONTB if bold else FONT),
                ("FONTSIZE", (0, r), (-1, r), 7.2),
                ("TEXTCOLOR", (0, r), (-1, r), INK if bold else INK2)]
        if bold:
            sty.append(("LINEABOVE", (0, r), (5, r), 0.5, LINE))
        for col, (a, b) in ((2, (vm, vp)), (3, (vm, vy)), (5, (yv, yp))):
            if is_adverse(variance(a, b), pol):
                sty.append(("TEXTCOLOR", (col, r), (col, r), NEG))
        r += 1
    data.append(["Net profit margin", pct(P_CUR["nm"]),
                 pts(P_CUR["nm"] - P_PRV["nm"]),
                 pts(P_CUR["nm"] - P_PYR["nm"]),
                 pct(Y_CUR["nm"]), pts(Y_CUR["nm"] - Y_PYR["nm"]), ""])
    sty += [("FONTNAME", (0, r), (-1, r), FONT), ("FONTSIZE", (0, r), (-1, r), 7.2),
            ("TEXTCOLOR", (0, r), (-1, r), INK2),
            ("LINEABOVE", (0, r), (5, r), 0.5, LINE)]
    for col, d in ((2, P_CUR["nm"]-P_PRV["nm"]), (3, P_CUR["nm"]-P_PYR["nm"]),
                   (5, Y_CUR["nm"]-Y_PYR["nm"])):
        if d < 0:
            sty.append(("TEXTCOLOR", (col, r), (col, r), NEG))

    t = Table(data, colWidths=[1.62*inch, 0.95*inch, 0.95*inch, 0.95*inch,
                               0.95*inch, 1.05*inch, 0.03*inch])
    t.setStyle(TableStyle(sty))
    st.append(t)
    st += [Spacer(1, 9),
           Paragraph(sentence("net profit", PERIOD_LABEL, P_CUR["net"], P_PRV["net"],
                              L["prv_long"]), S["sent"]),
           Paragraph(sentence("net profit", L["ytd_sentence"], Y_CUR["net"],
                              Y_PYR["net"], L["pyr_ytd_phrase"]), S["sent"])]

    # ---- 5 and 6. Trends
    def trend_block(title, key, polarity):
        out = [Paragraph(title, S["h2"]),
               Paragraph(sentence(title.lower(), PERIOD_LABEL, TREND[key][-1],
                                  TREND[key][-2], L["prv_long"], polarity), S["sent"]),
               Spacer(1, 2),
               TrendChart(TREND[key], T12_LABELS, polarity=polarity)]
        return KeepTogether(out)

    st.append(PageBreak())
    st.append(Anchor("Profitability trends"))
    st += [Paragraph("Profitability trends", S["h1"]), Spacer(1, 4),
           Rule(CW, 0.7, LINE),
           Paragraph(f"Twelve months to {PERIOD_LABEL}. Each chart carries the "
                     "level above and the change against the prior month below, "
                     "on the same axis.",
                     S["note"]), Spacer(1, 6)]
    st.append(trend_block("Total income", "income", 1))
    st.append(Spacer(1, 8))
    st.append(trend_block("Cost of goods sold", "cogs", -1))
    st.append(Spacer(1, 8))
    st.append(trend_block("Gross profit", "gross", 1))

    st.append(PageBreak())
    st += [Paragraph("Profitability trends", S["h1"]), Spacer(1, 4),
           Rule(CW, 0.7, LINE), Spacer(1, 8)]
    st.append(trend_block("Total expense", "expense", -1))
    st.append(Spacer(1, 8))
    st.append(trend_block("Net profit", "net", 1))
    st.append(Spacer(1, 10))
    st.append(Paragraph("Margins", S["h2"]))
    mg = [["", *T12_LABELS], ["Gross profit margin", *[pct(v, 0) for v in TREND["gm"]]],
          ["Net profit margin", *[pct(v, 0) for v in TREND["nm"]]]]
    t = Table(mg, colWidths=[1.35*inch] + [(CW-1.35*inch)/12]*12)
    sty = [("FONTNAME", (0, 0), (-1, -1), FONT), ("FONTSIZE", (0, 0), (-1, -1), 6.2),
           ("TEXTCOLOR", (0, 0), (-1, 0), MUT), ("TEXTCOLOR", (0, 1), (-1, -1), INK2),
           ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
           ("LINEBELOW", (0, 0), (-1, 0), 0.5, LINE),
           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
           ("LEFTPADDING", (0, 0), (-1, -1), 1.5), ("RIGHTPADDING", (0, 0), (-1, -1), 1.5)]
    for col in range(1, 13):
        if TREND["nm"][col-1] < 0:
            sty.append(("TEXTCOLOR", (col, 2), (col, 2), NEG))
    t.setStyle(TableStyle(sty))
    st.append(t)

    if HAS_BS:
        # ---- 7. Cash management
        st.append(PageBreak())
        st.append(Anchor("Cash management"))
        st += [Paragraph("Cash management", S["h1"]), Spacer(1, 4),
               Rule(CW, 0.7, LINE), Spacer(1, 12)]

        tiles = []
        for lab, cv, pv, fmtf in (
                ("Bank accounts", B_CUR["bank"], B_PRV["bank"], lambda v: compact(v)),
                ("Working capital", B_CUR["working_capital"], B_PRV["working_capital"],
                 lambda v: compact(v)),
                ("Current ratio", B_CUR["current_ratio"], B_PRV["current_ratio"],
                 lambda v: f"{v:.2f}")):
            d = cv - pv
            col = NEG if d < 0 else INK2
            tiles.append([Paragraph(lab, ParagraphStyle("tl", fontName=FONT, fontSize=7.4,
                                                        textColor=MUT)),
                          Paragraph(fmtf(cv), ParagraphStyle("tv", fontName=FONTB,
                                                             fontSize=17, leading=21,
                                                             textColor=INK)),
                          Paragraph(("down " if d < 0 else "up ") + fmtf(abs(d)) +
                                    f" vs {L['prv_long']}",
                                    ParagraphStyle("ts", fontName=FONT, fontSize=6.6,
                                                   leading=9, textColor=col))])
        t = Table([[tiles[0], tiles[1], tiles[2]]], colWidths=[CW/3]*3)
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                               ("TOPPADDING", (0, 0), (-1, -1), 0)]))
        st.append(t)
        st.append(Spacer(1, 16))

        st.append(KeepTogether([
            Paragraph("Bank accounts", S["h2"]),
            Paragraph(sentence("bank accounts", PERIOD_LABEL, CASH_SERIES[-1],
                               CASH_SERIES[-2], L["prv_long"]), S["sent"]),
            Spacer(1, 2),
            TrendChart(CASH_SERIES, T12_LABELS, polarity=1)]))
        st.append(Spacer(1, 10))
        st.append(KeepTogether([
            Paragraph("Working capital", S["h2"]),
            Paragraph(sentence("working capital", PERIOD_LABEL, WC_SERIES[-1],
                               WC_SERIES[-2], L["prv_long"]), S["sent"]),
            Spacer(1, 2),
            TrendChart(WC_SERIES, T12_LABELS, polarity=1)]))

        st.append(Spacer(1, 12))
        liq_rows = [
            dict(label="Current assets", level=1, values=[
                B_CUR["current_assets"], B_PRV["current_assets"],
                variance(B_CUR["current_assets"], B_PRV["current_assets"]),
                B_PYR["current_assets"],
                variance(B_CUR["current_assets"], B_PYR["current_assets"])],
                polarity=1, dollar=True),
            dict(label="Current liabilities", level=1, values=[
                B_CUR["current_liabilities"], B_PRV["current_liabilities"],
                variance(B_CUR["current_liabilities"], B_PRV["current_liabilities"]),
                B_PYR["current_liabilities"],
                variance(B_CUR["current_liabilities"], B_PYR["current_liabilities"])],
                polarity=-1),
            dict(label="Working capital", level=0, values=[
                B_CUR["working_capital"], B_PRV["working_capital"],
                variance(B_CUR["working_capital"], B_PRV["working_capital"]),
                B_PYR["working_capital"],
                variance(B_CUR["working_capital"], B_PYR["working_capital"])],
                bold=True, rule=True, polarity=1),
            dict(label="Current ratio", level=1, values=[
                B_CUR["current_ratio"], B_PRV["current_ratio"],
                B_CUR["current_ratio"] - B_PRV["current_ratio"],
                B_PYR["current_ratio"],
                B_CUR["current_ratio"] - B_PYR["current_ratio"]],
                kinds=["ratio", "ratio", "ratio", "ratio", "ratio"], polarity=1),
        ]
        st.append(KeepTogether([
            Paragraph("Liquidity", S["h2"]),
            statement_table(liq_rows, ["", CUR, PRV, "Variance", PYR, "Variance"],
                            ["", "Actuals", "Actuals", "$", "Actuals", "$"])]))

        # ---- Cash flow statement, its own page
        st.append(PageBreak())
        st.append(Anchor("Cash flow statement"))
        st += [Paragraph("Cash flow statement", S["h1"]),
               Paragraph(L["month_ended"], S["note"]), Spacer(1, 2),
               Rule(CW, 0.7, LINE), Spacer(1, 10)]
        # The third field is "tone eligible". Investing and financing outflows are
        # normal business activity, not adverse, so they are never toned. Only a
        # negative operating cash flow and a negative net movement are adverse.
        cf_disp = [("Net income", NI, False, False, None)]
        for lab, v in CF_OPERATING_ROWS:
            cf_disp.append((lab, v, False, False, None))
        cf_disp.append(("Net cash from operating activities", OPERATING,
                        True, True, True))
        for lab, v in CF_INVESTING_ROWS:
            cf_disp.append((lab, v, False, False, None))
        if CF_INVESTING_ROWS:
            cf_disp.append(("Net cash from investing activities", INVESTING,
                            False, True, True))
        for lab, v in CF_FINANCING_ROWS:
            cf_disp.append((lab, v, False, False, None))
        if CF_FINANCING_ROWS:
            cf_disp.append(("Net cash from financing activities", FINANCING,
                            False, True, True))
        cf_disp.append(("Net cash movement", NET_CASH, True, True, "heavy"))
        data = [["", CUR]]
        sty = [("FONTNAME", (0, 0), (-1, 0), FONT), ("FONTSIZE", (0, 0), (-1, 0), 6.4),
               ("TEXTCOLOR", (0, 0), (-1, 0), MUT), ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
               ("LINEBELOW", (0, 0), (-1, 0), 0.5, LINE),
               ("TOPPADDING", (0, 0), (-1, -1), 1.9), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.9),
               ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]
        r, firstd = 1, True
        for lab, v, tone_ok, bold, rule in cf_disp:
            data.append([("" if bold else "   ") + lab, money(v, firstd)])
            firstd = False
            sty += [("FONTNAME", (0, r), (-1, r), FONTB if bold else FONT),
                    ("FONTSIZE", (0, r), (-1, r), 7.0),
                    ("TEXTCOLOR", (0, r), (-1, r), INK if bold else INK2)]
            if rule == "heavy":
                sty.append(("LINEABOVE", (0, r), (-1, r), 0.9, MUT2))
            elif rule:
                sty.append(("LINEABOVE", (0, r), (-1, r), 0.5, LINE))
            if tone_ok and v < 0:
                sty.append(("TEXTCOLOR", (1, r), (1, r), NEG))
            r += 1
        t = Table(data, colWidths=[CW - 1.15*inch, 1.15*inch])
        t.setStyle(TableStyle(sty))
        st.append(t)
        if CF_NOTE:
            tail = CF_NOTE
        else:
            movers = sorted((row for row in CF_OPERATING_ROWS +
                             CF_INVESTING_ROWS + CF_FINANCING_ROWS),
                            key=lambda x: abs(x[1]), reverse=True)[:2]
            tail = " and ".join(f"{lab.lower()} ({compact(abs(v))})"
                                for lab, v in movers)
            tail = f"The largest movements were {tail}." if movers else ""
        st += [Spacer(1, 8),
               Paragraph(f"{PERIOD_LABEL}: net cash movement was "
                         f"{compact(NET_CASH)}, against a net profit of "
                         f"{compact(NI)}. {tail}", S["sent"])]

        # ---- 8. Balance sheet snapshot
        st.append(PageBreak())
        st.append(Anchor("Balance sheet snapshot"))
        st += [Paragraph("Balance sheet snapshot", S["h1"]), Spacer(1, 4),
               Rule(CW, 0.7, LINE), Spacer(1, 12)]
        g = Table([[StackBar("Assets", SNAP_A), StackBar("Liabilities and equity", SNAP_L)],
                   [StackBar("Current assets", SNAP_CA),
                    StackBar("Current liabilities", SNAP_CL)]],
                  colWidths=[CW/2, CW/2])
        g.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
                               ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        st.append(g)
        st += [Spacer(1, 2),
               Paragraph(sentence("total assets", PERIOD_LABEL, B_CUR["assets"],
                                  B_PYR["assets"], L["pyr_long"]), S["sent"]),
               Spacer(1, 12)]

        snap_keys = [("Current assets", "current_assets", 1, 1, False),
                     ("Fixed assets", "fixed_assets", 1, 1, False),
                     ("Other assets", "other_assets", 1, 1, False),
                     ("Total assets", "assets", 0, 1, True),
                     ("Current liabilities", "current_liabilities", 1, -1, False),
                     ("Long-term liabilities", "lt_liabilities", 1, -1, False),
                     ("Equity", "equity", 1, 1, False),
                     ("Total liabilities and equity", "liab_equity", 0, 1, True)]
        snap_rows = []
        _fd = True
        for lab, key, lvl, pol, bold in snap_keys:
            snap_rows.append(dict(
                label=lab, level=lvl,
                values=[B_CUR[key], B_PRV[key], variance(B_CUR[key], B_PRV[key]),
                        B_PYR[key], variance(B_CUR[key], B_PYR[key])],
                bold=bold, rule=True if bold else None, polarity=pol, dollar=_fd,
                space_before=(lab == "Current liabilities")))
            _fd = False
        st.append(KeepTogether([
            Paragraph("Composition", S["h2"]),
            statement_table(snap_rows, ["", CUR, PRV, "Variance", PYR, "Variance"],
                            ["", "Actuals", "Actuals", "$", "Actuals", "$"])]))

    # ---- 9. P&L month
    st.append(PageBreak())
    st.append(Anchor("Profit and loss, month"))
    st += [Paragraph("Profit and loss", S["h1"]),
           Paragraph(L["month_ended"], S["note"]), Spacer(1, 2),
           Rule(CW, 0.7, LINE), Spacer(1, 10)]
    gh = ["", CUR, PRV, "Variance", PYR, "Variance"]
    sh = ["", "Actuals", "Actuals", "$", "Actuals", "$"]
    st.append(statement_table(build_pnl_rows(M_CUR, M_PRV, M_PYR), gh, sh))

    # ---- 10. P&L YTD
    st.append(PageBreak())
    st.append(Anchor("Profit and loss, year to date"))
    st += [Paragraph("Profit and loss", S["h1"]),
           Paragraph(L["ytd_ended"], S["note"]), Spacer(1, 2),
           Rule(CW, 0.7, LINE), Spacer(1, 10)]
    gh = ["", L["ytd_cur"], L["ytd_pyr"], "Variance", "Variance"]
    sh = ["", "Actuals", "Actuals", "$", "%"]
    st.append(statement_table(
        to_two_period(build_pnl_rows(YTD_CUR, YTD_PYR, YTD_PYR)), gh, sh,
        col_widths=[CW - 4*1.0*inch] + [1.0*inch] * 4))

    if HAS_BS:
        # ---- 11. Balance sheet
        st.append(PageBreak())
        st.append(Anchor("Balance sheet"))
        st += [Paragraph("Balance sheet", S["h1"]),
               Paragraph(L["as_of"], S["note"]), Spacer(1, 2),
               Rule(CW, 0.7, LINE), Spacer(1, 10)]
        gh = ["", CUR, PRV, "Variance", PYR, "Variance"]
        sh = ["", "Actuals", "Actuals", "$", "Actuals", "$"]
        st.append(statement_table(bs_rows(), gh, sh))

        # ---- 12. Ratio appendix
        st.append(PageBreak())
        st.append(Anchor("Ratio appendix"))
        st += [Paragraph("Ratio appendix", S["h1"]),
               Paragraph("Each ratio shows its inputs so the calculation can be checked.",
                         S["note"]), Spacer(1, 2), Rule(CW, 0.7, LINE), Spacer(1, 12)]

        def ratio_table(title, rows):
            data = [["", CUR, PYR, "Change"]]
            sty = [("FONTNAME", (0, 0), (-1, 0), FONT), ("FONTSIZE", (0, 0), (-1, 0), 6.4),
                   ("TEXTCOLOR", (0, 0), (-1, 0), MUT),
                   ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                   ("LINEBELOW", (0, 0), (-1, 0), 0.5, LINE),
                   ("TOPPADDING", (0, 0), (-1, -1), 2.4),
                   ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4),
                   ("LEFTPADDING", (0, 0), (-1, -1), 3),
                   ("RIGHTPADDING", (0, 0), (-1, -1), 3)]
            r = 1
            for lab, c_, y_, f, bold in rows:
                data.append([lab, f(c_), f(y_), f(c_ - y_) if not bold else f(c_ - y_)])
                sty += [("FONTNAME", (0, r), (-1, r), FONTB if bold else FONT),
                        ("FONTSIZE", (0, r), (-1, r), 7.2),
                        ("TEXTCOLOR", (0, r), (-1, r), INK if bold else INK2)]
                if bold:
                    sty.append(("LINEABOVE", (0, r), (-1, r), 0.5, LINE))
                    if c_ - y_ < 0:
                        sty.append(("TEXTCOLOR", (3, r), (3, r), NEG))
                r += 1
            t = Table(data, colWidths=[2.4*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            t.setStyle(TableStyle(sty))
            return KeepTogether([Paragraph(title, S["h2"]), t, Spacer(1, 12)])

        m2 = lambda v: money(v, False)
        r2 = lambda v: (f"({abs(v):.2f})" if v < 0 else f"{v:.2f}")
        p2 = lambda v: pct(v)

        st.append(ratio_table("Current ratio", [
            ("Current assets", B_CUR["current_assets"], B_PYR["current_assets"], m2, False),
            ("Current liabilities", B_CUR["current_liabilities"],
             B_PYR["current_liabilities"], m2, False),
            ("Current ratio", B_CUR["current_ratio"], B_PYR["current_ratio"], r2, True)]))
        st.append(ratio_table("Working capital", [
            ("Current assets", B_CUR["current_assets"], B_PYR["current_assets"], m2, False),
            ("Current liabilities", B_CUR["current_liabilities"],
             B_PYR["current_liabilities"], m2, False),
            ("Working capital", B_CUR["working_capital"], B_PYR["working_capital"], m2, True)]))
        if B_CUR["equity"] and B_PYR["equity"]:
            st.append(ratio_table("Debt to equity", [
                ("Total liabilities", B_CUR["liabilities"], B_PYR["liabilities"], m2, False),
                ("Total equity", B_CUR["equity"], B_PYR["equity"], m2, False),
                ("Debt to equity", B_CUR["liabilities"]/B_CUR["equity"],
                 B_PYR["liabilities"]/B_PYR["equity"], r2, True)]))
        st.append(ratio_table("Gross profit margin, year to date", [
            ("Gross profit", Y_CUR["gross"], Y_PYR["gross"], m2, False),
            ("Income", Y_CUR["income"], Y_PYR["income"], m2, False),
            ("Gross profit margin", Y_CUR["gm"], Y_PYR["gm"], p2, True)]))

    st.insert(0, NextPageTemplate("body"))
    return st


# ----------------------------------------------------------------------------
# Build. Two passes: the first records section page numbers into a throwaway
# file, the second writes the real contents page.
# ----------------------------------------------------------------------------
_tmp = OUT + ".pass1.tmp"
_d1 = Doc(_tmp)
_d1.build(build_story({}))
_pages = dict(_d1.section_pages)
try:
    os.remove(_tmp)
except OSError:
    pass

doc = Doc(OUT)
doc.build(build_story(_pages))

print("PROOFS PASSED")
if HAS_BS:
    print(f"  closing assets            {B_CUR['assets']:>14,.2f}")
    print(f"  closing liab and equity   {B_CUR['liab_equity']:>14,.2f}")
    print(f"  net cash movement         {NET_CASH:>14,.2f}")
    print(f"  change in bank accounts   {B_CUR['bank']-B_PRV['bank']:>14,.2f}")
print(f"  {CUR} net profit            {P_CUR['net']:>14,.2f}")
print(f"  YTD net profit            {Y_CUR['net']:>14,.2f}")
print(f"wrote {OUT}")
