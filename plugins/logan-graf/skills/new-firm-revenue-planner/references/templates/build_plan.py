#!/usr/bin/env python3
"""Revenue plan engine. Feed it a payload, never edit this file.

Usage:    python3 <skill folder>/references/templates/build_plan.py <plan>.json [<plan>.pdf]
          Run from the user's working folder. Without a PDF name, the PDF takes
          the payload's name, for example osher-road-to-100k.pdf. Writing
          inside the skill folder is refused.
Requires: pip install reportlab

The payload carries the owner's inputs. The engine derives clients needed per
tier, the mix, the price floor, the proposal verdict, and three sensitivity
tables (client mix, margin, hiring). A check that misses the goal fails the
build and no file is written.

This PDF never passes through theme.py. The Kick brand tokens live here. Bars
are soft fills; red is reserved for a miss. Inter sits beside this script. A
Helvetica fallback is off-brand and must not be handed over.

Payload:
  title         str, optional. Default "<owner>'s Road to <goal>" or "Road to <goal>"
  owner         str, optional, the owner's first name for the default title
  entity        str, optional, the firm's name for the page header
  period        str, the goal year
  goal          number, annual
  goal_basis    "profit" or "revenue"
  overhead      number, annual fixed overhead, default 0
  capacity      number of clients, or null
  delivery      {kind: "percent"|"dollars", value, per: "month"|"year"}
                percent is a fraction (0.40). dollars is cost per client; per
                defaults to "month"
  tiers         [{name, billing: "monthly"|"annual", price}], one bar each, when the
                owner gave two or more prices. Leave out for the Bronze, Silver,
                Gold ladder
  current_price optional {billing, price}, the owner's one price, anchors the ladder
  mix           optional {tier name: client count}, the owner's mix. Left out with
                two or more tiers, the engine starts from 60/40, 40/40/20, or an
                even split of capacity. A mix that misses the goal at capacity
                is replaced by the nearest one that reaches it, tagged Placeholder
  services      optional [{name, billing, price}], two or more, for the client mix table.
                Left out, the engine uses placeholder Tax, Books, and Both. [] omits it
  service_mix   optional {service name: percent}, the owner's expected split
  cost_cuts     optional [percent], default [5, 10, 15, 20]
  hires         optional [{label, salary, adds}], adds is clients of capacity.
                Left out on a profit goal with capacity, the engine uses placeholder
                part-time, full-time, and two full-time hires. [] omits it
  proposal      optional {monthly, one_time, one_time_label, delivery?}
                delivery, when present, replaces the plan delivery for the check only
  parameters    [{name, value, source}], source Owner, Books, File, Default, or Placeholder.
                Ladder tiers and a default mix are appended by the engine, tagged Placeholder
                unless they are the owner's current price
  notes         [str], printed under Parameters and Sources
"""

import itertools
import json
import math
import os
import sys
from fractions import Fraction as F

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, KeepTogether,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

INK = colors.HexColor("#0f1826")
INK2 = colors.HexColor("#515d71")
MUT = colors.HexColor("#949ba7")
LINE = colors.HexColor("#e9ecf0")
HEAD = colors.HexColor("#eef0f3")
BASE = colors.HexColor("#f6f8fa")
MISS = colors.HexColor("#9f4237")

NAMED_FILLS = {
    "bronze": "#ecc9a8",
    "silver": "#d6dbe2",
    "gold": "#f1dc9c",
    "platinum": "#dfe3ea",
}
SOFT_FILLS = ["#a8deff", "#bfe6d4", "#d9cff2", "#f6cdb8", "#f3e3a6"]

FONT = "Helvetica"
FONTB = "Helvetica-Bold"


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def register_inter():
    global FONT, FONTB
    here = os.path.dirname(os.path.abspath(__file__))
    regular = os.path.join(here, "inter-latin-400.ttf")
    bold = os.path.join(here, "inter-latin-640.ttf")
    if not (os.path.isfile(regular) and os.path.isfile(bold)):
        print("warning: inter-latin-400.ttf / inter-latin-640.ttf not found beside "
              "this script, falling back to Helvetica. A fallback build is off-brand "
              "and must not be handed over.")
        return
    pdfmetrics.registerFont(TTFont("Inter", regular))
    pdfmetrics.registerFont(TTFont("Inter-Semibold", bold))
    FONT, FONTB = "Inter", "Inter-Semibold"


def num(x, what):
    try:
        return F(str(x))
    except (TypeError, ValueError):
        fail(f"{what} must be a number")


def ceil(x):
    x = F(x)
    return -(-x.numerator // x.denominator)


def rnd(x):
    x = F(x)
    return int((x * 2 + 1) // 2)


def money(n):
    n = rnd(n)
    return f"-${abs(n):,}" if n < 0 else f"${n:,}"


def short(n):
    n = rnd(n)
    if n >= 1_000_000:
        s = f"{n / 1_000_000:.2f}".rstrip("0").rstrip(".")
        return f"{s}M"
    if n >= 1_000:
        s = f"{n / 1_000:.1f}".rstrip("0").rstrip(".")
        return f"{s}K"
    return str(n)


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Model:
    """Plan arithmetic. Every figure on the page comes from here."""

    def __init__(self, data):
        self.goal = num(data.get("goal"), "goal")
        if self.goal <= 0:
            fail("goal must be a positive number")
        self.basis = data.get("goal_basis")
        if self.basis not in ("profit", "revenue"):
            fail('goal_basis must be "profit" or "revenue"')
        self.overhead = num(data.get("overhead") or 0, "overhead")
        cap = data.get("capacity")
        self.capacity = None if cap is None else int(cap)
        if self.capacity is not None and self.capacity < 1:
            fail("capacity must be at least 1")
        self.delivery = self.parse_delivery(data.get("delivery") or {})

    @staticmethod
    def parse_delivery(d):
        kind = d.get("kind")
        if kind not in ("percent", "dollars"):
            fail('delivery.kind must be "percent" or "dollars"')
        value = num(d.get("value"), "delivery.value")
        if kind == "percent":
            if value <= 0 or value >= 1:
                fail("delivery percent must be greater than 0 and less than 1")
            return {"kind": kind, "rate": value}
        if value < 0:
            fail("delivery dollars cannot be negative")
        per = d.get("per") or "month"
        if per not in ("month", "year"):
            fail('delivery.per must be "month" or "year"')
        return {"kind": kind, "year": value * (12 if per == "month" else 1)}

    @staticmethod
    def annual(price, billing):
        if billing not in ("monthly", "annual"):
            fail('billing must be "monthly" or "annual"')
        p = num(price, "price")
        if p <= 0:
            fail("a price must be positive")
        return p * (12 if billing == "monthly" else 1)

    def contrib(self, annual, delivery=None):
        """What one client adds toward the goal in a year."""
        d = delivery or self.delivery
        if self.basis == "revenue":
            return annual
        if d["kind"] == "percent":
            return annual * (1 - d["rate"])
        return annual - d["year"]

    def fixed(self, extra=0):
        return (self.overhead if self.basis == "profit" else 0) + extra

    def need(self, contrib, extra=0):
        if contrib <= 0:
            fail("a price does not cover its delivery cost")
        n = ceil((self.goal + self.fixed(extra)) / contrib)
        if n * contrib - self.fixed(extra) < self.goal:
            fail("client check misses the goal")
        return n

    def result(self, n, contrib, extra=0):
        return n * contrib - self.fixed(extra)

    def floor(self, capacity=None, extra=0, delivery=None):
        cap = capacity or self.capacity
        if cap is None:
            return None
        d = delivery or self.delivery
        target = self.goal + self.fixed(extra)
        if self.basis == "revenue":
            return ceil(target / cap / 12)
        if d["kind"] == "percent":
            return ceil(target / (1 - d["rate"]) / cap / 12)
        return ceil(target / cap / 12 + d["year"] / 12)


def fill_for(name, i):
    return NAMED_FILLS.get(name.strip().lower(), SOFT_FILLS[i % len(SOFT_FILLS)])


def even_split(n, lead=None):
    """Integer percents summing to 100. lead gets 60 when set."""
    if lead is None:
        base = [100 // n] * n
        for i in range(100 - sum(base)):
            base[i] += 1
        return base
    rest = 40
    others = [rest // (n - 1)] * (n - 1)
    for i in range(rest - sum(others)):
        others[i] += 1
    out = []
    it = iter(others)
    for i in range(n):
        out.append(60 if i == lead else next(it))
    return out


def build_ladder(m, current):
    """Bronze, Silver, Gold when the owner gave one price or none.

    Silver is the floor rounded up to the next $100, the cheapest round price
    that reaches the goal at capacity. Bronze is the owner's current price, or
    60% of Silver when the current price already clears Silver. Gold is the
    premium tier at twice Silver.
    """
    floor = m.floor()
    cur_m = None
    if current:
        cur_m = m.annual(current.get("price"), current.get("billing")) / 12
    if floor is None and cur_m is None:
        fail("tiers, or a current_price with a capacity, are required")
    silver_m = None if floor is None else ceil(F(floor, 100)) * 100
    rows = {}
    if cur_m is not None and (silver_m is None or cur_m >= silver_m):
        rows["Silver"] = (current, "Owner, current price")
        silver_m = cur_m
        bronze_m = max(50, int(silver_m * F(6, 10)) // 50 * 50)
        rows["Bronze"] = ({"billing": "monthly", "price": bronze_m}, "Placeholder, 60% of Silver")
    else:
        rows["Silver"] = ({"billing": "monthly", "price": silver_m},
                          "Placeholder, floor rounded up to the next $100")
        if cur_m is not None:
            rows["Bronze"] = (current, "Owner, current price")
        else:
            bronze_m = max(50, int(silver_m * F(6, 10)) // 50 * 50)
            rows["Bronze"] = ({"billing": "monthly", "price": bronze_m}, "Placeholder, 60% of Silver")
    gold_m = ceil(F(silver_m * 2, 100)) * 100
    rows["Gold"] = ({"billing": "monthly", "price": gold_m}, "Placeholder, premium at twice Silver")
    tiers, params = [], []
    for name in ("Bronze", "Silver", "Gold"):
        spec, source = rows[name]
        tiers.append({"name": name, "billing": spec["billing"], "price": spec["price"]})
        unit = "mo" if spec["billing"] == "monthly" else "yr"
        params.append({"name": f"{name} tier", "value": f"{money(num(spec['price'], 'price'))} / {unit}",
                       "source": source})
    base = 0 if cur_m is not None and rows["Bronze"][1].startswith("Owner") else 1
    return tiers, params, base


def default_mix(tiers, cap):
    """A starting mix when the owner gave none: 60/40 for two tiers, 40/40/20 for
    three, an even split past that, applied to capacity (10 clients without one)."""
    n = len(tiers)
    if n == 2:
        weights = [F(60, 100), F(40, 100)]
    elif n == 3:
        weights = [F(40, 100), F(40, 100), F(20, 100)]
    else:
        weights = [F(1, n)] * n
    total = cap or 10
    counts = [rnd(total * w) for w in weights[:-1]]
    counts.append(total - sum(counts))
    mix = {t["name"]: c for t, c in zip(tiers, counts) if c > 0}
    return mix, "/".join(str(rnd(w * 100)) for w in weights)


def fit_mix(m, tiers, start, cap):
    """The mix nearest the starting one that reaches the goal with capacity full.

    Nearest is the smallest sum of squared client changes, so the mix tilts up
    across every tier instead of emptying one. Ties go to the smallest
    overshoot. None when a full book in the best tier still misses.
    """
    contrib = [t["contrib"] for t in tiers]
    target = m.goal + m.fixed()
    if cap * max(contrib) < target:
        return None
    total = sum(start.values())
    want = [float(F(start.get(t["name"], 0) * cap, total)) for t in tiers]
    n = len(tiers)
    step = 1
    while math.comb(cap // step + n - 1, n - 1) > 200_000:
        step += 1
    units = cap // step
    best = None
    for cuts in itertools.combinations(range(units + n - 1), n - 1):
        edges = (-1,) + cuts + (units + n - 1,)
        counts = [(edges[k + 1] - edges[k] - 1) * step for k in range(n)]
        counts[0] += cap - units * step
        made = sum(c * v for c, v in zip(counts, contrib))
        if made < target:
            continue
        dist = sum((c - w) ** 2 for c, w in zip(counts, want))
        key = (round(dist, 6), made - target)
        if best is None or key < best[0]:
            best = (key, counts)
    return {t["name"]: c for t, c in zip(tiers, best[1]) if c > 0}


def mix_stats(m, tiers, counts_by_name, cap):
    by_name = {t["name"]: t for t in tiers}
    counts = [(by_name[k], int(v)) for k, v in counts_by_name.items() if int(v) > 0]
    counts.sort(key=lambda tv: tiers.index(tv[0]))
    total = sum(v for _, v in counts)
    if total < 1:
        fail("mix needs at least one client")
    annual = F(sum(t["annual"] * v for t, v in counts), total)
    c = F(sum(t["contrib"] * v for t, v in counts), total)
    n = m.need(c)
    initials = [t["name"][0].upper() for t, _ in counts]
    use_initials = len(set(initials)) == len(initials)
    label = " / ".join(f"{v} {t['name'][0].upper() if use_initials else t['name']}" for t, v in counts)
    return {
        "name": "Mix", "annual": annual, "contrib": c, "clients": n,
        "check": m.result(n, c), "count": total, "label": label,
        "long_label": " / ".join(f"{v} {t['name']}" for t, v in counts),
        "full_book": m.result(total, c),
        "shares": [(t["fill"], F(v, total)) for t, v in counts],
        "over": cap is not None and n > cap,
        "at_cap": None if cap is None else m.result(cap, c),
    }


def default_services(m, current, tiers):
    """Books at the owner's monthly price, Tax at $2,000 a year, Both as the two
    together. Empty when a service would not cover its delivery cost."""
    if current:
        books = m.annual(current.get("price"), current.get("billing")) / 12
    else:
        monthly = [t for t in tiers if t["billing"] == "monthly"]
        books = monthly[0]["price"] if monthly else tiers[0]["annual"] / 12
    books = rnd(books)
    tax = 2_000
    both = rnd(books + F(tax, 12))
    services = [
        {"name": "Tax", "billing": "annual", "price": tax},
        {"name": "Books", "billing": "monthly", "price": books},
        {"name": "Both", "billing": "monthly", "price": both},
    ]
    for s in services:
        if m.contrib(m.annual(s["price"], s["billing"])) <= 0:
            return []
    return services


def derive(data):
    m = Model(data)
    cap = m.capacity

    raw_tiers = data.get("tiers") or data.get("scenarios") or []
    ladder_params, base_index = [], 0
    if not raw_tiers:
        raw_tiers, ladder_params, base_index = build_ladder(m, data.get("current_price"))
    tiers = []
    for i, t in enumerate(raw_tiers):
        name = t.get("name") or t.get("label") or f"Tier {i + 1}"
        billing = t.get("billing")
        annual = m.annual(t.get("price"), billing)
        c = m.contrib(annual)
        n = m.need(c)
        tiers.append({
            "name": name, "billing": billing, "price": num(t["price"], "price"),
            "annual": annual, "contrib": c, "clients": n,
            "check": m.result(n, c), "fill": fill_for(name, i),
            "over": cap is not None and n > cap,
            "at_cap": None if cap is None else m.result(cap, c),
        })

    mix, own_mix = None, None
    raw_mix = data.get("mix")
    if raw_mix:
        names = {t["name"] for t in tiers}
        for k in raw_mix:
            if k not in names:
                fail(f"mix names a tier that is not in tiers: {k}")
        mix = mix_stats(m, tiers, raw_mix, cap)
        if cap is not None and mix["count"] > cap:
            fail("mix has more clients than capacity")
        start_text = f"your {mix['long_label']}"
    elif len(tiers) >= 2:
        start, split = default_mix(tiers, cap)
        mix = mix_stats(m, tiers, start, cap)
        start_text = f"a {split} split"
        source = f"Placeholder, {split} split {'of capacity' if cap else 'of 10 clients'}"
    if mix and mix["over"] and len(tiers) >= 2:
        fitted = fit_mix(m, tiers, raw_mix or start, cap)
        if fitted:
            if raw_mix:
                own_mix = mix
            mix = mix_stats(m, tiers, fitted, cap)
            source = f"Placeholder, the mix closest to {start_text} that reaches the goal at {cap} clients"
    if mix and (own_mix or not raw_mix):
        ladder_params.append({"name": "Tier mix", "value": mix["long_label"], "source": source})

    base = mix or tiers[base_index]
    base_name = f"the {mix['label']} mix" if mix else tiers[base_index]["name"]
    floor = m.floor()

    proposal = None
    raw_p = data.get("proposal")
    if raw_p:
        use = raw_p.get("delivery")
        use = m.parse_delivery(use) if use and use.get("kind") else m.delivery
        monthly = num(raw_p["monthly"], "proposal.monthly")
        c = m.contrib(monthly * 12, use)
        n = m.need(c)
        pfloor = m.floor(delivery=use)
        fits = pfloor is not None and monthly >= pfloor
        proposal = {
            "monthly": rnd(monthly), "floor": pfloor, "fits": fits,
            "gap": None if pfloor is None else pfloor - rnd(monthly),
            "clients": n, "over": cap is not None and n > cap,
            "at_cap": None if cap is None else rnd(m.result(cap, c)),
            "one_time": raw_p.get("one_time"),
            "one_time_label": (lambda s: s[:1].upper() + s[1:])(raw_p.get("one_time_label") or "One-time fee"),
        }

    notes = list(data.get("notes") or data.get("open_inputs") or [])

    services = data.get("services")
    if services is None:
        services = default_services(m, data.get("current_price"), tiers)
        if services:
            ladder_params.append({
                "name": "Services",
                "value": ", ".join(f"{s['name']} {money(s['price'])} / "
                                   f"{'mo' if s['billing'] == 'monthly' else 'yr'}" for s in services),
                "source": "Placeholder, Books at your price, Tax at $2,000 a year, Both is the two together",
            })
    svc_rows = []
    if services:
        notes.append("Every client counts the same against capacity, annual tax clients included.")
        if len(services) < 2:
            fail("services needs two or more entries")
        names = [s["name"] for s in services]
        svc = {s["name"]: {"annual": m.annual(s["price"], s["billing"]), "billing": s["billing"]}
               for s in services}
        scenarios = []
        own = data.get("service_mix")
        if own:
            if set(own) - set(names):
                fail("service_mix names a service that is not in services")
            scenarios.append(("Your mix", [int(own.get(n, 0)) for n in names]))
        for i, n in enumerate(names):
            scenarios.append((f"Mostly {n.lower()}", even_split(len(names), i)))
        scenarios.append(("Even split", even_split(len(names))))
        for label, shares in scenarios:
            if sum(shares) != 100:
                fail(f"{label} shares must add to 100")
            c = sum(F(p, 100) * m.contrib(svc[n]["annual"]) for n, p in zip(names, shares))
            monthly = sum(p for n, p in zip(names, shares) if svc[n]["billing"] == "monthly")
            n_need = m.need(c)
            svc_rows.append({
                "label": label, "monthly": monthly, "shares": shares, "contrib": c,
                "clients": n_need, "over": cap is not None and n_need > cap,
                "at_cap": None if cap is None else m.result(cap, c),
            })

    margin_rows = []
    if m.basis == "profit":
        cuts = [0] + [int(x) for x in (data.get("cost_cuts") or [5, 10, 15, 20]) if int(x) > 0]
        for cut in cuts:
            d = dict(m.delivery)
            if d["kind"] == "percent":
                d["rate"] = d["rate"] * (100 - cut) / 100
            else:
                d["year"] = d["year"] * (100 - cut) / 100
            c = F(base["contrib"]) if cut == 0 else m.contrib(base["annual"], d)
            n_need = m.need(c)
            margin_rows.append({
                "cut": cut, "delivery": d, "clients": n_need,
                "floor": m.floor(delivery=d),
                "over": cap is not None and n_need > cap,
                "at_cap": None if cap is None else m.result(cap, c),
            })

    hire_rows = []
    hires = data.get("hires")
    if hires is None:
        hires = []
        if cap is not None and m.basis == "profit":
            half = max(1, rnd(F(cap, 2)))
            hires = [
                {"label": "Part-time hire", "salary": 30_000, "adds": half},
                {"label": "Full-time hire", "salary": 60_000, "adds": cap},
                {"label": "Two full-time hires", "salary": 120_000, "adds": cap * 2},
            ]
            ladder_params.append({
                "name": "Hires",
                "value": f"Part-time $30,000 adds {half}, full-time $60,000 adds {cap}",
                "source": "Placeholder, a full-time hire adds your own capacity",
            })
    if hires:
        notes.append("Salaries leave out payroll taxes and benefits, and hires serve clients at the same "
                     "delivery cost.")
        if cap is None:
            fail("hires need a capacity to add to")
        if m.basis != "profit":
            fail("hires need a profit goal")
        for label, salary, adds in [("Solo", 0, 0)] + [
                (h["label"], num(h["salary"], "hire salary"), int(h["adds"])) for h in hires]:
            hc = cap + adds
            n_need = m.need(base["contrib"], salary)
            hire_rows.append({
                "label": label, "salary": salary, "capacity": hc, "clients": n_need,
                "floor": m.floor(capacity=hc, extra=salary),
                "over": n_need > hc,
                "at_cap": m.result(hc, base["contrib"], salary),
            })

    owner = (data.get("owner") or "").strip()
    default_title = f"Road to {short(m.goal)}"
    title = (data.get("title") or "").strip() or (f"{owner}'s {default_title}" if owner else default_title)

    return {
        "model": m, "title": title,
        "entity": (data.get("entity") or "").strip(),
        "period": data.get("period") or "This year",
        "tiers": tiers, "mix": mix, "own_mix": own_mix, "base_name": base_name, "floor": floor,
        "proposal": proposal, "services": services, "svc_rows": svc_rows,
        "margin_rows": margin_rows, "hire_rows": hire_rows, "base": base,
        "parameters": (data.get("parameters") or data.get("inputs") or []) + ladder_params,
        "notes": list(dict.fromkeys(notes)),
    }


def price_text(r):
    if r["billing"] == "monthly":
        return f"{money(r['price'])} / mo"
    return f"{money(r['price'])} / yr"


class TierBars(Flowable):
    """Horizontal clients-needed bars, soft fills, mix as the last bar, dotted capacity line."""

    def __init__(self, rows, capacity, width):
        Flowable.__init__(self)
        self.rows, self.capacity, self.width = rows, capacity, width
        self.row_h = 30
        self.height = 22 + len(rows) * self.row_h + 6

    def wrap(self, aw, ah):
        return self.width, self.height

    def draw(self):
        c = self.canv
        cap = self.capacity
        labw = 1.55 * inch
        avail = self.width - labw - 0.85 * inch
        peak = max([r["clients"] for r in self.rows] + ([cap] if cap else []))
        scale = avail / peak
        bar_h = 15
        top = self.height - 22
        ends = []
        for i, r in enumerate(self.rows):
            y = top - (i + 1) * self.row_h + (self.row_h - bar_h) / 2
            c.setFillColor(INK)
            c.setFont(FONTB, 8.5)
            if r.get("shares"):
                c.drawString(0, y + 11, r["name"][:24])
                c.setFillColor(MUT)
                split = r["long_label"]
                if c.stringWidth(split, FONT, 6.8) > labw - 8:
                    split = r["label"]
                size = 6.8
                while size > 5.4 and c.stringWidth(split, FONT, size) > labw - 8:
                    size -= 0.2
                c.setFont(FONT, size)
                c.drawString(0, y + 2.5, split)
                c.setFont(FONT, 6.8)
                c.drawString(0, y - 5.5, f"avg {money(r['annual'] / 12)} / mo")
            else:
                c.drawString(0, y + 8, r["name"][:24])
                c.setFillColor(MUT)
                c.setFont(FONT, 6.8)
                c.drawString(0, y - 1, price_text(r))
            w = r["clients"] * scale
            if r.get("shares"):
                c.saveState()
                clip = c.beginPath()
                clip.roundRect(labw, y, w, bar_h, 3)
                c.clipPath(clip, stroke=0, fill=0)
                x = labw
                for fill, share in r["shares"]:
                    seg = float(share) * w
                    c.setFillColor(colors.HexColor(fill))
                    c.rect(x, y, seg, bar_h, stroke=0, fill=1)
                    x += seg
                c.setStrokeColor(colors.white)
                c.setLineWidth(1.4)
                x = labw
                for _, share in r["shares"][:-1]:
                    x += float(share) * w
                    c.line(x, y, x, y + bar_h)
                c.restoreState()
            else:
                c.setFillColor(colors.HexColor(r["fill"]))
                c.roundRect(labw, y, w, bar_h, 3, stroke=0, fill=1)
            ends.append((r, labw + w, y))

        c.setFillColor(MUT)
        c.setFont(FONT, 6.5)
        c.drawString(labw, top + 9, "Clients needed")
        cx = None
        if cap:
            cx = labw + cap * scale
            c.setStrokeColor(INK2)
            c.setLineWidth(0.9)
            c.setDash(2.5, 2.5)
            c.line(cx, top - len(self.rows) * self.row_h + 2, cx, top + 4)
            c.setDash()
            c.setFillColor(INK2)
            c.setFont(FONTB, 7)
            c.drawCentredString(cx, top + 9, f"Capacity {cap}")

        for r, end, y in ends:
            text = str(r["clients"])
            tw = c.stringWidth(text, FONTB, 9)
            tx = end + 6
            if cx is not None and tx - 3 < cx < tx + tw + 3:
                tx = cx + 5
            c.setFillColor(MISS if r["over"] else INK)
            c.setFont(FONTB, 9)
            c.drawString(tx, y + 4, text)
            if r["over"]:
                c.setFont(FONT, 6.8)
                c.drawString(tx + tw + 4, y + 4.5, f"{r['clients'] - cap} over")


def table(data, widths, width, flags=None, flag_cols=(), base_row=None, left_cols=1):
    scale = width / sum(widths)
    t = Table(data, colWidths=[w * scale for w in widths], hAlign="LEFT", repeatRows=1)
    style = [
        ("FONTNAME", (0, 0), (-1, -1), FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 7.8),
        ("TEXTCOLOR", (0, 0), (-1, 0), INK2),
        ("BACKGROUND", (0, 0), (-1, 0), HEAD),
        ("TEXTCOLOR", (0, 1), (0, -1), INK),
        ("TEXTCOLOR", (1, 1), (-1, -1), INK2),
        ("ALIGN", (left_cols, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 3.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    if base_row is not None:
        style.append(("BACKGROUND", (0, base_row), (-1, base_row), BASE))
    for i, bad in enumerate(flags or [], start=1):
        if bad:
            for col in flag_cols:
                style.append(("TEXTCOLOR", (col, i), (col, i), MISS))
    t.setStyle(TableStyle(style))
    return t


def styles():
    return {
        "h1": ParagraphStyle("h1", fontName=FONTB, fontSize=22, leading=26, textColor=INK),
        "sub": ParagraphStyle("sub", fontName=FONT, fontSize=9, leading=13, textColor=INK2, spaceBefore=3),
        "h2": ParagraphStyle("h2", fontName=FONTB, fontSize=11.5, leading=14, textColor=INK,
                             spaceBefore=12, spaceAfter=3),
        "lede": ParagraphStyle("lede", fontName=FONT, fontSize=7.8, leading=11, textColor=MUT, spaceAfter=5),
        "body": ParagraphStyle("body", fontName=FONT, fontSize=8.2, leading=11.8, textColor=INK2,
                               spaceBefore=5, spaceAfter=2),
        "bad": ParagraphStyle("bad", fontName=FONTB, fontSize=8.6, leading=12, textColor=MISS,
                              spaceBefore=5, spaceAfter=2),
        "ok": ParagraphStyle("ok", fontName=FONTB, fontSize=8.6, leading=12, textColor=INK,
                             spaceBefore=5, spaceAfter=2),
        "note": ParagraphStyle("note", fontName=FONT, fontSize=7, leading=10, textColor=MUT),
    }


def join_names(names):
    if len(names) <= 1:
        return "".join(names)
    return f"{', '.join(names[:-1])} and {names[-1]}"


def subtitle(plan):
    m = plan["model"]
    if m.basis == "profit":
        parts = [f"{money(m.goal)} take-home profit a year."]
    else:
        parts = [f"{money(m.goal)} revenue a year."]
    if m.capacity:
        parts.append(f"Up to {m.capacity} clients.")
    d = m.delivery
    if d["kind"] == "percent":
        parts.append(f"Delivery runs {rnd(d['rate'] * 100)}% of revenue.")
    else:
        parts.append(f"{money(d['year'])} a year to serve each client.")
    if m.overhead:
        parts.append(f"Fixed overhead {money(m.overhead)} a year.")
    return " ".join(parts)


def delivery_text(d):
    if d["kind"] == "percent":
        return f"{float(d['rate'] * 100):.1f}".rstrip("0").rstrip(".") + "% of revenue"
    return money(d["year"])


def story(plan, S, width):
    m = plan["model"]
    cap = m.capacity
    cap_head = f"Profit at {cap}" if m.basis == "profit" else f"Revenue at {cap}"
    rows = plan["tiers"] + ([plan["mix"]] if plan["mix"] else [])

    st = [Paragraph(_esc(plan["title"]), S["h1"]), Paragraph(_esc(subtitle(plan)), S["sub"]),
          Paragraph("Clients needed by tier", S["h2"]), Spacer(1, 4), TierBars(rows, cap, width)]

    over = [r["name"] for r in rows if r["over"]]
    fits = [r["name"] for r in rows if not r["over"]]
    line = ""
    if plan["floor"] is not None:
        line += f"Your floor at {cap} clients is {money(plan['floor'])} a month. "
        if over:
            line += f"{join_names(over)} cannot reach {money(m.goal)} with the clients you can serve. "
        if fits:
            verb = "clears" if len(fits) == 1 else "clear"
            line += f"{join_names(fits)} {verb} it. "
    else:
        line += "Capacity is still open, so there is no floor yet. "
    mix = plan["mix"]
    own = plan["own_mix"]
    if own:
        line += (f"Your {own['long_label']} mix needs {own['clients']} clients, "
                 f"{own['clients'] - cap} over. ")
    if mix:
        line += f"The {mix['label']} mix needs {mix['clients']} clients"
        if cap:
            verb = "makes" if m.basis == "profit" else "brings in"
            line += f" and {verb} {money(mix['at_cap'])} with all {cap}."
        else:
            line += "."
    st.append(Paragraph(_esc(line.strip()), S["body"]))

    prop = plan["proposal"]
    if prop and prop["floor"] is not None:
        if prop["fits"]:
            st.append(Paragraph(f"Proposal at {money(prop['monthly'])} a month fits the plan.", S["ok"]))
        else:
            gap = abs(prop["gap"])
            st.append(Paragraph(
                f"Proposal at {money(prop['monthly'])} a month is below the plan by {money(gap)} a month, "
                f"{money(gap * 12)} a year.", S["bad"]))
            detail = f"If every client paid {money(prop['monthly'])}, the goal needs {prop['clients']} clients"
            detail += f" ({prop['clients'] - cap} over capacity)." if prop["over"] else "."
            if prop["at_cap"] is not None:
                detail += f" {cap} clients at that price make {money(prop['at_cap'])}."
            st.append(Paragraph(detail, S["body"]))
        if prop.get("one_time"):
            st.append(Paragraph(
                f"{_esc(prop['one_time_label'])} {money(prop['one_time'])} is separate and does not change "
                f"the floor.", S["note"]))

    if plan["svc_rows"]:
        names = [s["name"] for s in plan["services"]]
        hstyle = ParagraphStyle("head", fontName=FONT, fontSize=7.8, leading=9.5, textColor=INK2, alignment=2)
        head = ["", Paragraph("Monthly vs annual", hstyle), Paragraph(_esc(" vs ".join(names)), hstyle),
                "Profit per client" if m.basis == "profit"
                else "Revenue per client", "Clients needed"] + ([cap_head] if cap else [])
        data = [head]
        for r in plan["svc_rows"]:
            row = [r["label"], f"{r['monthly']} / {100 - r['monthly']}",
                   " / ".join(str(p) for p in r["shares"]), money(r["contrib"]),
                   f"{r['clients']} ({r['clients'] - cap} over)" if r["over"] else str(r["clients"])]
            if cap:
                row.append(money(r["at_cap"]))
            data.append(row)
        prices = ". ".join(f"{_esc(s['name'])} is {money(s['price'])} "
                           f"{'a month' if s['billing'] == 'monthly' else 'a year'}"
                           for s in plan["services"])
        widths = [1.15, 1.1, 1.3, 1.05, 1.0] + ([1.0] if cap else [])
        base_row = 1 if data[1][0] == "Your mix" else None
        st.append(KeepTogether([
            Paragraph("Client mix", S["h2"]),
            Paragraph(f"Share of clients, in percent. {prices}.", S["lede"]),
            table(data, widths, width, [r["over"] for r in plan["svc_rows"]], (4, 5), base_row),
        ]))

    if plan["margin_rows"]:
        d0 = m.delivery
        head = ["Delivery cost", "Per client / yr" if d0["kind"] == "dollars" else "Cost share"]
        head += (["Price floor"] if cap else []) + ["Clients needed"] + ([cap_head] if cap else [])
        data = [head]
        for r in plan["margin_rows"]:
            row = ["Today" if r["cut"] == 0 else f"{r['cut']}% lower", delivery_text(r["delivery"])]
            if cap:
                row.append(f"{money(r['floor'])} / mo")
            row.append(f"{r['clients']} ({r['clients'] - cap} over)" if r["over"] else str(r["clients"]))
            if cap:
                row.append(money(r["at_cap"]))
            data.append(row)
        widths = [1.3, 1.1] + ([1.1] if cap else []) + [1.1] + ([1.1] if cap else [])
        need_col = 3 if cap else 2
        first, last = plan["margin_rows"][0], plan["margin_rows"][-1]
        base = plan["base"]
        if d0["kind"] == "dollars":
            share = rnd(d0["year"] / base["annual"] * 100)
        else:
            share = rnd(d0["rate"] * 100)
        note = f"Delivery cost is about {share}% of what a client pays. "
        joiner = " and" if cap else ""
        if cap:
            note += (f"A {last['cut']}% cut adds {money(last['at_cap'] - first['at_cap'])} a year at {cap} "
                     f"clients")
        else:
            note += f"A {last['cut']}% cut"
        if last["clients"] == first["clients"]:
            note += f"{joiner} does not change the client count."
        else:
            note += f"{joiner} moves the client count from {first['clients']} to {last['clients']}."
        st.append(KeepTogether([
            Paragraph("Margin", S["h2"]),
            Paragraph(f"Lowering what each client costs you to serve, on {_esc(plan['base_name'])}.", S["lede"]),
            table(data, widths, width, [r["over"] for r in plan["margin_rows"]],
                  (need_col, need_col + 1), base_row=1),
            Paragraph(_esc(note), S["body"]),
        ]))

    if plan["hire_rows"]:
        data = [["", "Salary", "Capacity", "Clients needed", "Price floor", "Profit at capacity"]]
        for r in plan["hire_rows"]:
            data.append([r["label"], money(r["salary"]), str(r["capacity"]),
                         f"{r['clients']} ({r['clients'] - r['capacity']} over)" if r["over"] else str(r["clients"]),
                         f"{money(r['floor'])} / mo", money(r["at_cap"])])
        st.append(KeepTogether([
            Paragraph("Hiring", S["h2"]),
            Paragraph(f"Salary is a fixed cost. Each hire adds clients you can serve, on "
                      f"{_esc(plan['base_name'])}.", S["lede"]),
            table(data, [1.45, 0.95, 0.8, 1.05, 1.0, 1.25], width,
                  [r["over"] for r in plan["hire_rows"]], (3, 5), base_row=1),
        ]))

    if not plan["parameters"]:
        fail("parameters needs at least one row")
    block = [Paragraph("Parameters and Sources", S["h2"])]
    cell = ParagraphStyle("cell", fontName=FONT, fontSize=7.8, leading=10, textColor=INK2)
    pdata = [["Parameter", "Value", "Source"]]
    for row in plan["parameters"]:
        pdata.append([_esc(row.get("name", "")), Paragraph(_esc(row.get("value", "")), cell),
                      Paragraph(_esc(row.get("source", "")), cell)])
    block.append(table(pdata, [1.3, 3.0, 2.2], width, left_cols=99))
    if plan["notes"]:
        block += [Spacer(1, 6), Paragraph(_esc(" ".join(plan["notes"])), S["note"])]
    st.append(KeepTogether(block))
    return st


DISCLAIMER = "Read only. Nothing in the books was changed. The goal is before income tax."
PW, PH = letter
LM = RM = 0.75 * inch
CW = PW - LM - RM


class Doc(BaseDocTemplate):
    def __init__(self, path, plan):
        BaseDocTemplate.__init__(
            self, path, pagesize=letter, leftMargin=LM, rightMargin=RM,
            topMargin=0.75 * inch, bottomMargin=0.6 * inch,
            title=", ".join(p for p in (plan["title"], plan["period"], plan["entity"]) if p),
            author="Kick")
        self.plan = plan
        frame = Frame(LM, 0.6 * inch, CW, PH - 0.75 * inch - 0.6 * inch, id="n",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id="body", frames=[frame], onPage=self.body_page)])

    def body_page(self, c, d):
        plan = self.plan
        c.saveState()
        c.setFont(FONT, 7)
        c.setFillColor(MUT)
        c.drawRightString(PW - RM, PH - 0.48 * inch, "  |  ".join(
            p for p in (plan["title"], plan["entity"], plan["period"]) if p))
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.line(LM, PH - 0.6 * inch, PW - RM, PH - 0.6 * inch)
        c.setFont(FONT, 5.6)
        c.drawString(LM, 0.38 * inch, DISCLAIMER)
        c.setFont(FONT, 7)
        c.drawRightString(PW - RM, 0.38 * inch, str(c.getPageNumber()))
        c.restoreState()


def main():
    if len(sys.argv) not in (2, 3):
        fail("usage: python3 build_plan.py <plan>.json [<plan>.pdf]")
    register_inter()
    try:
        data = json.loads(open(sys.argv[1], encoding="utf-8").read())
    except (OSError, json.JSONDecodeError) as e:
        fail(f"cannot read payload: {e}")
    plan = derive(data)
    out = sys.argv[2] if len(sys.argv) == 3 else os.path.splitext(sys.argv[1])[0] + ".pdf"
    here = os.path.dirname(os.path.abspath(__file__))
    skill_root = os.path.dirname(os.path.dirname(here))
    if os.path.realpath(os.path.abspath(out)).startswith(os.path.realpath(skill_root) + os.sep):
        fail("write the plan to the user's working folder, not inside the skill folder")
    Doc(out, plan).build(story(plan, styles(), CW))
    print(f"wrote {os.path.abspath(out)}")
    print(f"floor={plan['floor']}")
    prop = plan["proposal"]
    if prop and prop["floor"] is not None:
        print(f"verdict={'Fits the plan' if prop['fits'] else 'Below the plan'}")
        print(f"gap_monthly={prop['gap']}")
    for r in plan["tiers"] + ([plan["mix"]] if plan["mix"] else []):
        print(f"bar={r['name']}|{r['clients']}|{'over' if r['over'] else 'fits'}")
    for r in plan["svc_rows"]:
        print(f"client_mix={r['label']}|{r['clients']}")
    for r in plan["margin_rows"]:
        print(f"margin={r['cut']}|{r['clients']}|{r['floor']}")
    for r in plan["hire_rows"]:
        print(f"hire={r['label']}|{r['capacity']}|{r['clients']}|{r['floor']}")


if __name__ == "__main__":
    main()
