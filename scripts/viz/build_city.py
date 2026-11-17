#!/usr/bin/env python3
"""Contribution City: the last year of GitHub activity as a neon skyline.

One building per day (per week once there's more than ~4 months of activity).
Taller = more contributions; lit windows = how busy that day was; a quiet day is
a little park; the best day gets a rooftop sign; the newest building has a crane.

    python3 scripts/viz/build_city.py HemashreeVI out.svg     (needs GITHUB_TOKEN)
"""
import datetime as dt
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build_cards as bc          # palette, fonts, svg() wrapper
import cat_layer
from data import load

W, H = 1200, 470
GROUND, LEFT, RIGHT = 372, 40, 1160
MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()
WIN = ["#FDE68A", "#FDE68A", "#FCD34D", "#67E8F9", "#F9A8D4", "#C4B5FD"]


def columns(days):
    """Daily columns from shortly before the first active day; weekly when the span is long."""
    first = next((i for i, (_, c) in enumerate(days) if c), len(days) - 30)
    span = days[max(0, first - 3):]
    if len(span) < 30:
        span = days[-30:]
    if len(span) <= 120:
        return "day", [(d, c) for d, c in span]
    weeks = []
    for i in range(0, len(span), 7):
        chunk = span[i:i + 7]
        weeks.append((chunk[0][0], sum(c for _, c in chunk)))
    return "week", weeks


def streak(days):
    s, i = 0, len(days) - 1
    if days and days[-1][1] == 0:
        i -= 1                       # today isn't over yet
    while i >= 0 and days[i][1] > 0:
        s, i = s + 1, i - 1
    return s


def nice_date(d):
    d = dt.date.fromisoformat(d)
    return f"{MONTHS[d.month - 1].title()} {d.day}"


def build(user, out):
    data = load(user)
    days = data["days"]
    unit, cols = columns(days)
    n = len(cols)
    slot = (RIGHT - LEFT) / n
    bw = max(4.0, slot * .8)
    peak = max(c for _, c in cols) or 1
    best = max(range(n), key=lambda i: cols[i][1])
    rnd = random.Random(7)
    total = data["total"]
    active = sum(1 for _, c in days if c)
    C = bc.C
    p = []

    # sky, stars, moon, distant skyline
    p.append(f"""<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#070316"/><stop offset=".55" stop-color="#17093A"/><stop offset="1" stop-color="#4A1259"/></linearGradient>
<linearGradient id="bld" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A1A55"/><stop offset="1" stop-color="#140B2C"/></linearGradient>
<linearGradient id="bestb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4C1D95"/><stop offset="1" stop-color="#1E1048"/></linearGradient>
<linearGradient id="road" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1A1030"/><stop offset="1" stop-color="#07040F"/></linearGradient>
<radialGradient id="moon" cx="40%" cy="35%" r="65%"><stop offset="0" stop-color="#FFF7D6"/><stop offset="1" stop-color="#F9A8D4"/></radialGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
</defs>
<rect width="{W}" height="{H}" rx="22" fill="url(#sky)"/>""")
    for _ in range(90):
        x, y, r = rnd.uniform(20, W - 20), rnd.uniform(12, 230), rnd.choice([.7, .9, 1.2])
        p.append(f'<circle class="twinkle" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff" style="animation-delay:{rnd.uniform(0, 4):.1f}s"/>')
    p.append(f'<circle cx="1080" cy="150" r="30" fill="url(#moon)" opacity=".9"/><circle cx="1080" cy="150" r="46" fill="#F9A8D4" opacity=".08"/>')
    x = 0
    while x < W:                                   # far skyline silhouette
        w, h = rnd.uniform(26, 60), rnd.uniform(40, 120)
        p.append(f'<rect x="{x:.0f}" y="{GROUND - h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="#1B0F3A" opacity=".55"/>')
        x += w + 2

    # buildings
    for i, (d, c) in enumerate(cols):
        x = LEFT + i * slot + (slot - bw) / 2
        if c == 0:                                  # a day off: a little park
            tx = x + bw / 2
            col = rnd.choice(["#14532D", "#166534", "#15803D"])
            p.append(f'<rect x="{tx - 1:.1f}" y="{GROUND - 9}" width="2" height="9" fill="#3F2A1D"/>'
                     f'<circle cx="{tx:.1f}" cy="{GROUND - 12}" r="{min(6, bw / 1.6):.1f}" fill="{col}"/>')
            continue
        h = 22 + math.pow(c / peak, .8) * 222
        top = GROUND - h
        fill = "url(#bestb)" if i == best else "url(#bld)"
        p.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{fill}" stroke="#3B2A70" stroke-width=".6"/>')
        p.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{bw:.1f}" height="1.6" fill="#7C5CFF" opacity=".55"/>')
        # windows: busier day, more lights on
        cw, ch = 4.2, 6.5
        ncols = max(1, int((bw - 3) // (cw + 2.4)))
        ox = x + (bw - ncols * (cw + 2.4) + 2.4) / 2
        lit_share = min(.95, .2 + .8 * c / peak)
        wy = top + 6
        while wy < GROUND - 9:
            for k in range(ncols):
                if rnd.random() < lit_share:
                    colr = rnd.choice(WIN)
                    flick = ' class="twinkle"' if rnd.random() < .06 else ''
                    p.append(f'<rect{flick} x="{ox + k * (cw + 2.4):.1f}" y="{wy:.1f}" width="{cw}" height="{ch}" fill="{colr}" opacity=".85"/>')
            wy += ch + 4.5
        if i == best:                               # rooftop neon sign + beacon
            label = f"★ {c}"
            sw = 14 + len(label) * 8
            sx = min(max(x + bw / 2 - sw / 2, 8), W - sw - 8)
            p.append(f'<g><rect x="{sx:.0f}" y="{top - 30:.0f}" width="{sw}" height="22" rx="6" fill="#12061F" stroke="{C["rose"]}" stroke-width="1.6"/>'
                     f'<rect x="{sx:.0f}" y="{top - 30:.0f}" width="{sw}" height="22" rx="6" fill="none" stroke="{C["rose"]}" stroke-width="3" opacity=".5" filter="url(#glow)">'
                     f'<animate attributeName="opacity" values=".2;.7;.2" dur="2.4s" repeatCount="indefinite"/></rect>'
                     + bc.text(sx + sw / 2, top - 14, label, 13, "#FFE4F1", 'mono', 'middle', 'font-weight="700"') +
                     f'<path d="M{x + bw / 2:.1f} {top - 8:.0f}V{top:.0f}" stroke="{C["rose"]}" stroke-width="1.2"/></g>')
    # the newest building: a crane, still under construction
    lx = LEFT + (n - 1) * slot + slot / 2
    lc = cols[-1][1]
    ltop = GROUND - (22 + math.pow(lc / peak, .8) * 222 if lc else 10)
    cx = lx - 6
    p.append(f'<g opacity=".95"><path d="M{cx} {GROUND}V{ltop - 40:.0f}" stroke="{C["gold"] if "gold" in C else "#FCD34D"}" stroke-width="2.4"/>'
             f'<path d="M{cx - 46} {ltop - 40:.0f}H{cx + 18}" stroke="#FCD34D" stroke-width="2.4"/>'
             f'<path d="M{cx - 30} {ltop - 40:.0f}V{ltop - 20:.0f}" stroke="#FCD34D" stroke-width="1"><animate attributeName="d" values="M{cx - 30} {ltop - 40:.0f}V{ltop - 20:.0f};M{cx - 30} {ltop - 40:.0f}V{ltop - 4:.0f};M{cx - 30} {ltop - 40:.0f}V{ltop - 20:.0f}" dur="4s" repeatCount="indefinite"/></path>'
             f'<circle cx="{cx}" cy="{ltop - 44:.0f}" r="3" fill="#FF3355"><animate attributeName="opacity" values="1;.15;1" dur="1.2s" repeatCount="indefinite"/></circle></g>')

    # street, lane markings, cars
    p.append(f'<rect x="0" y="{GROUND}" width="{W}" height="{H - GROUND}" fill="url(#road)"/>'
             f'<rect x="0" y="{GROUND}" width="{W}" height="2" fill="#7C5CFF" opacity=".6"/>'
             f'<path d="M0 {GROUND + 30}H{W}" stroke="#FDE68A" stroke-width="2" stroke-dasharray="18 16" opacity=".35"/>')
    for k, (y, dur, col, rev) in enumerate([(GROUND + 20, 11, "#22D3EE", False), (GROUND + 40, 15, "#F472B6", True), (GROUND + 20, 19, "#A78BFA", False)]):
        a, b = (W + 60, -80) if rev else (-80, W + 60)
        head = -6 if rev else 34
        p.append(f'<g><animateTransform attributeName="transform" type="translate" values="{a} 0;{b} 0" dur="{dur}s" begin="-{k * 4}s" repeatCount="indefinite"/>'
                 f'<rect x="0" y="{y - 8}" width="30" height="10" rx="4" fill="{col}" opacity=".85"/><rect x="6" y="{y - 13}" width="16" height="6" rx="2" fill="{col}" opacity=".6"/>'
                 f'<circle cx="{head + (0 if rev else -4)}" cy="{y - 3}" r="2.2" fill="#FFF7D6"/></g>')
    # month labels and "today"
    seen = set()
    for i, (d, _) in enumerate(cols):
        m = d[:7]
        if m not in seen and (unit == "week" or d[8:] <= "07" or i == 0):
            seen.add(m)
            x = LEFT + i * slot
            p.append(f'<path d="M{x:.1f} {GROUND + 2}v6" stroke="{C["muted"]}"/>' + bc.text(x + 3, GROUND + 60, MONTHS[int(d[5:7]) - 1], 11, C['muted'], 'mono', 'start', 'letter-spacing="2"'))
    p.append(bc.text(RIGHT, GROUND + 60, "TODAY ▸", 11, "#FCD34D", 'mono', 'end', 'letter-spacing="2"'))
    p.append(cat_layer.walker("citycat", card_w=W, ground=GROUND + 4, height=34, duration=26))

    # header: what you're looking at, and the key numbers
    p.append(f'<rect x="24" y="20" width="{W - 48}" height="62" rx="14" fill="#0B0620" opacity=".72" stroke="#3B2A70"/>')
    p.append(bc.text(44, 44, "CONTRIBUTION CITY", 11, C['lav'], 'mono', 'start', 'letter-spacing="3"'))
    p.append(f'<text x="44" y="70" class="serif" font-size="22" fill="{C["silver"]}">{total:,} contributions <tspan fill="{C["muted"]}" font-size="14" font-style="italic">· 1 building = 1 {unit} · taller = busier · lit windows = activity · 🌳 = a day off</tspan></text>')
    stats = [("BEST DAY" if unit == "day" else "BEST WEEK", f"{cols[best][1]} · {nice_date(cols[best][0])}"), ("STREAK", f"{streak(days)} days"), ("ACTIVE DAYS", f"{active}")]
    x = W - 44
    for lab, val in reversed(stats):
        w = max(len(val) * 8.6, len(lab) * 7.2) + 26
        x -= w
        p.append(f'<rect x="{x:.0f}" y="32" width="{w:.0f}" height="40" rx="10" fill="#140B2C" stroke="#3B2A70"/>'
                 + bc.text(x + 13, 48, lab, 9, C['muted'], 'mono', 'start', 'letter-spacing="1.5"')
                 + bc.text(x + 13, 65, val, 13.5, "#fff", 'sans', 'start', 'font-weight="700"'))
        x -= 10

    desc = (f"Contribution City: {total} contributions in the last year drawn as a skyline, one building per {unit}. "
            f"The tallest building, {cols[best][1]} on {nice_date(cols[best][0])}, has a neon sign; quiet {unit}s are parks; "
            f"the newest building has a crane. Current streak {streak(days)} days, {active} active days.")
    Path(out).write_text(bc.svg(W, H, "city", "Contribution City", desc, "".join(p)), encoding="utf-8")
    print(f"{out}: {n} {unit}s, peak {peak}, {len(''.join(p)) // 1024} KB")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
