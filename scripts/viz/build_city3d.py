#!/usr/bin/env python3
"""Contribution City 3D: the contribution calendar as an isometric city.

Every day is a city lot (weeks run one way, weekdays the other, roads between).
No contributions: a park. A few: a low-rise. More: an office block. A lot: a glass
skyscraper. The best day is a landmark tower with a spire; today has a crane.

    python3 scripts/viz/build_city3d.py HemashreeVI out.svg     (needs GITHUB_TOKEN)
"""
import datetime as dt
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build_cards as bc
from data import load

W = 1200
COS, SIN = math.cos(math.radians(30)), math.sin(math.radians(30))
MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()
DAYS = "SUN MON TUE WED THU FRI SAT".split()


def shade(hex_, k):
    """k > 1 lightens, k < 1 darkens."""
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    f = (lambda v: min(255, int(v + (255 - v) * (k - 1)))) if k > 1 else (lambda v: int(v * k))
    return f"#{f(r):02x}{f(g):02x}{f(b):02x}"


def calendar_grid(days):
    """Weeks (Sunday first, like GitHub) from shortly before the first active day, at least 8 weeks."""
    first = next((i for i, (_, c) in enumerate(days) if c), len(days) - 1)
    start = dt.date.fromisoformat(days[max(0, first - 7)][0])
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)            # back to Sunday
    end = dt.date.fromisoformat(days[-1][0])
    count = dict(days)
    nweeks = max(8, (end - start).days // 7 + 1)
    start = min(start, end - dt.timedelta(days=(end.weekday() + 1) % 7) - dt.timedelta(weeks=nweeks - 1))
    grid = []
    for w in range(nweeks):
        for d in range(7):
            day = start + dt.timedelta(weeks=w, days=d)
            if day <= end:
                grid.append((w, d, day.isoformat(), count.get(day.isoformat(), 0)))
    return nweeks, grid


def build(user, out):
    data = load(user)
    days = data["days"]
    nweeks, grid = calendar_grid(days)
    peak = max(c for *_, c in grid) or 1
    best = max(grid, key=lambda g: g[3])
    today = grid[-1]
    rnd = random.Random(11)

    s = min(64, 1080 / ((nweeks + 7) * COS))                 # lot size
    a, b = s * COS, s * SIN
    HMAX = min(300, s * 4.6)
    ox = 60 + 7 * a                                           # screen origin of lot (0,0)

    def height(c):
        return 0 if c == 0 else 10 + math.pow(c / peak, .75) * HMAX

    # fit the picture to the tallest thing: buildings, the best-day sign (+80) and the crane (+60)
    reach = min((w + d) * b - height(c) - (80 if (w, d) == best[:2] else 60 if (w, d) == today[:2] else 0) for w, d, _, c in grid)
    oy = 132 - min(reach, 0)
    H = int(oy + (nweeks + 7) * b + 70)

    def P(i, j, h=0.0):
        return ox + (i - j) * a, oy + (i + j) * b - h

    def poly(pts, fill, extra=""):
        return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}" {extra}/>'

    defs = ["""<linearGradient id="c3sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#070B1A"/><stop offset=".6" stop-color="#121A3A"/><stop offset="1" stop-color="#2B1B4A"/></linearGradient>
<linearGradient id="glassL" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2E5C8A"/><stop offset="1" stop-color="#14304F"/></linearGradient>
<linearGradient id="glassR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5B8DBE"/><stop offset="1" stop-color="#244A72"/></linearGradient>
<linearGradient id="landL" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5B3FA0"/><stop offset="1" stop-color="#2A1A55"/></linearGradient>
<linearGradient id="landR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8B6FD8"/><stop offset="1" stop-color="#43308A"/></linearGradient>
<filter id="c3blur"><feGaussianBlur stdDeviation="2.2"/></filter>"""]
    # window patterns in face coordinates (u along the wall, v down), so they skew with each face
    lit_cols = ["#FFE7A3", "#FFD27A", "#FFF3C4", "#9BE7FF"]
    for tier, density in (("lo", .3), ("md", .55), ("hi", .8)):
        for v in range(3):
            cells = []
            for fy in range(6):
                for fx in range(4):
                    on = rnd.random() < density
                    cells.append(f'<rect x="{fx * 7 + 1.5}" y="{fy * 10 + 2.5}" width="4" height="6" fill="{rnd.choice(lit_cols) if on else "#0E1A2E"}" opacity="{.95 if on else .9}"/>')
            defs.append(f'<pattern id="win{tier}{v}" width="28" height="60" patternUnits="userSpaceOnUse">{"".join(cells)}</pattern>')
            # glass curtain wall: mullions + a few lit floors
            g = [f'<rect width="28" height="60" fill="none"/>', '<path d="M7 0V60M14 0V60M21 0V60" stroke="#0B1626" stroke-opacity=".55" stroke-width=".8"/>']
            for fy in range(6):
                g.append(f'<path d="M0 {fy * 10}H28" stroke="#0B1626" stroke-opacity=".5" stroke-width=".8"/>')
                if rnd.random() < density * .6:
                    x0 = rnd.choice([0, 7, 14])
                    g.append(f'<rect x="{x0 + 1}" y="{fy * 10 + 2}" width="{rnd.choice([5, 12, 19])}" height="6" fill="{rnd.choice(lit_cols)}" opacity=".7"/>')
            defs.append(f'<pattern id="gls{tier}{v}" width="28" height="60" patternUnits="userSpaceOnUse">{"".join(g)}</pattern>')

    p = [f'<rect width="{W}" height="{H}" rx="22" fill="url(#c3sky)"/>']
    for _ in range(80):
        p.append(f'<circle class="twinkle" cx="{rnd.uniform(20, W - 20):.0f}" cy="{rnd.uniform(112, max(160, oy * .7)):.0f}" r="{rnd.choice([.6, .9, 1.2])}" fill="#fff" style="animation-delay:{rnd.uniform(0, 4):.1f}s"/>')

    # ground: asphalt slab, then sidewalks per lot, lane markings
    g0, g1, g2, g3 = P(-.15, -.15), P(nweeks + .15, -.15), P(nweeks + .15, 7.15), P(-.15, 7.15)
    p.append(poly([P(-.15, 7.15), P(nweeks + .15, 7.15), (P(nweeks + .15, 7.15)[0], P(nweeks + .15, 7.15)[1] + 14), (g3[0], g3[1] + 14)], "#0A0D18"))
    p.append(poly([P(nweeks + .15, -.15), P(nweeks + .15, 7.15), (g2[0], g2[1] + 14), (g1[0], g1[1] + 14)], "#141A2C"))
    p.append(poly([g0, g1, g2, g3], "#1E2436"))
    for w in range(nweeks + 1):
        p.append(f'<path d="M{P(w - .04, 0)[0]:.1f} {P(w - .04, 0)[1]:.1f}L{P(w - .04, 7)[0]:.1f} {P(w - .04, 7)[1]:.1f}" stroke="#FDE68A" stroke-opacity=".18" stroke-dasharray="4 6"/>')
    lots = {}
    for w, d, date, c in grid:
        f0, f1 = .08, .92
        p.append(poly([P(w + f0, d + f0), P(w + f1, d + f0), P(w + f1, d + f1), P(w + f0, d + f1)], "#2C3448" if c else "#1F4D2E"))
        lots[(w, d)] = (date, c)

    # buildings, back to front
    for w, d, date, c in sorted(grid, key=lambda g: (g[0] + g[1], g[0])):
        h = height(c)
        if c == 0:                                   # park: a couple of trees
            for tx, ty in ((.3, .35), (.68, .62), (.62, .25))[: 1 + (w * 7 + d) % 3]:
                x, y = P(w + tx, d + ty)
                r = s * .13
                p.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * 1.1:.1f}" ry="{r * .5:.1f}" fill="#000" opacity=".25"/>'
                         f'<rect x="{x - 1:.1f}" y="{y - r * 1.4:.1f}" width="2" height="{r * 1.4:.1f}" fill="#4A3424"/>'
                         f'<circle cx="{x:.1f}" cy="{y - r * 1.7:.1f}" r="{r:.1f}" fill="#2F7D3A"/><circle cx="{x - r * .3:.1f}" cy="{y - r * 1.95:.1f}" r="{r * .55:.1f}" fill="#4CAF50" opacity=".8"/>')
            continue
        is_best, is_today = (w, d) == (best[0], best[1]), (w, d) == (today[0], today[1])
        f0, f1 = (.12, .88) if h > HMAX * .45 or is_best else (.16, .84)
        tier = "hi" if c / peak > .55 else "md" if c / peak > .2 else "lo"
        v = (w * 7 + d) % 3
        kind = "landmark" if is_best else "glass" if c / peak > .45 else "office" if c / peak > .12 else "house"
        base = rnd.choice(["#6B5B4E", "#7A6A5C", "#5E6878", "#6E7A8C", "#8A6F5A"])     # brick / concrete
        # shadow on the ground (light from the upper right)
        sh = [P(w + f0, d + f1), P(w + f1, d + f1), (P(w + f1, d + f1)[0] - h * .55, P(w + f1, d + f1)[1] + h * .08), (P(w + f0, d + f1)[0] - h * .55, P(w + f0, d + f1)[1] + h * .08)]
        p.append(poly(sh, "#000", 'opacity=".28" filter="url(#c3blur)"'))
        # left face (facing +weekday) and right face (facing +week), drawn as skewed rects so windows follow
        L, R = P(w + f0, d + f1, h), P(w + f1, d + f1, h)
        wl = (f1 - f0) * s
        if kind in ("glass", "landmark"):
            lf, rf, pat = ("url(#landL)", "url(#landR)", f"gls{tier}{v}") if kind == "landmark" else ("url(#glassL)", "url(#glassR)", f"gls{tier}{v}")
        else:
            lf, rf, pat = shade(base, .62), shade(base, 1.0), f"win{tier}{v}"
        p.append(f'<g transform="matrix({COS:.4f},{SIN:.4f},0,1,{L[0]:.1f},{L[1]:.1f})"><rect width="{wl:.1f}" height="{h:.1f}" fill="{lf}"/><rect y="4" width="{wl:.1f}" height="{max(0, h - 8):.1f}" fill="url(#{pat})"/></g>')
        p.append(f'<g transform="matrix({COS:.4f},{-SIN:.4f},0,1,{R[0]:.1f},{R[1]:.1f})"><rect width="{wl:.1f}" height="{h:.1f}" fill="{rf}"/><rect y="4" width="{wl:.1f}" height="{max(0, h - 8):.1f}" fill="url(#{pat})" opacity=".9"/></g>')
        top = [P(w + f0, d + f0, h), P(w + f1, d + f0, h), P(w + f1, d + f1, h), P(w + f0, d + f1, h)]
        p.append(poly(top, shade(base, 1.25) if kind in ("house", "office") else "#3E5F86" if kind == "glass" else "#7C5CFF"))
        p.append(f'<path d="M{top[3][0]:.1f} {top[3][1]:.1f}L{top[2][0]:.1f} {top[2][1]:.1f}L{top[1][0]:.1f} {top[1][1]:.1f}" stroke="#fff" stroke-opacity=".18" fill="none"/>')
        cx, cy = P(w + .5, d + .5, h)
        if kind == "house" and h < s * .9:            # pitched-roof hint: a little roof cap
            p.append(poly([P(w + f0, d + f1, h), P(w + f1, d + f1, h), (cx + 0, cy - s * .18), ], shade(base, .45), 'opacity=".9"'))
        elif kind == "office":                         # water tank + AC unit
            p.append(f'<rect x="{cx - 4:.1f}" y="{cy - 11:.1f}" width="8" height="9" fill="#5B4636"/><ellipse cx="{cx:.1f}" cy="{cy - 11:.1f}" rx="4" ry="1.8" fill="#7A5E48"/>'
                     f'<path d="M{cx - 3:.1f} {cy - 2:.1f}l-1.5 3M{cx + 3:.1f} {cy - 2:.1f}l1.5 3" stroke="#3A2C22"/>'
                     f'<rect x="{cx + 6:.1f}" y="{cy - 3:.1f}" width="6" height="4" fill="#9AA3B2"/>')
        elif kind == "glass":                          # antenna with a red light
            p.append(f'<path d="M{cx:.1f} {cy:.1f}V{cy - 16:.1f}" stroke="#C9D2E3" stroke-width="1.2"/><circle cx="{cx:.1f}" cy="{cy - 17:.1f}" r="2" fill="#FF3355"><animate attributeName="opacity" values="1;.2;1" dur="1.4s" repeatCount="indefinite"/></circle>')
        else:                                          # landmark: crown, spire, beacon, sign
            p.append(poly([P(w + .3, d + .3, h), P(w + .7, d + .3, h), P(w + .7, d + .7, h), P(w + .3, d + .7, h)], "#A78BFA"))
            p.append(f'<path d="M{cx:.1f} {cy:.1f}V{cy - 40:.1f}" stroke="#E9D5FF" stroke-width="2"/>'
                     f'<circle cx="{cx:.1f}" cy="{cy - 42:.1f}" r="3.5" fill="#F472B6"><animate attributeName="r" values="3;6;3" dur="1.8s" repeatCount="indefinite"/></circle>'
                     f'<circle cx="{cx:.1f}" cy="{cy - 42:.1f}" r="14" fill="#F472B6" opacity=".18"><animate attributeName="opacity" values=".08;.3;.08" dur="1.8s" repeatCount="indefinite"/></circle>')
            label = f"★ BEST DAY · {c}"
            lw = len(label) * 7.4 + 18
            p.append(f'<rect x="{cx - lw / 2:.1f}" y="{cy - 74:.1f}" width="{lw:.1f}" height="22" rx="6" fill="#12061F" stroke="#F472B6" stroke-width="1.5"/>'
                     + bc.text(cx, cy - 59, label, 11.5, "#FFE4F1", 'mono', 'middle', 'font-weight="700"'))
        if is_today:                                   # crane over today's building
            bx, by = P(w + .9, d + .1, 0)
            tt = max(h + 50, s * 1.6)
            p.append(f'<g stroke="#FCD34D" fill="none"><path d="M{bx:.1f} {by:.1f}V{by - tt:.1f}" stroke-width="2.4"/>'
                     f'<path d="M{bx - 54:.1f} {by - tt + 4:.1f}L{bx + 20:.1f} {by - tt - 6:.1f}" stroke-width="2.4"/>'
                     f'<path d="M{bx - 34:.1f} {by - tt + 1:.1f}V{by - tt + 30:.1f}" stroke-width="1"><animate attributeName="d" values="M{bx - 34:.1f} {by - tt + 1:.1f}V{by - tt + 30:.1f};M{bx - 34:.1f} {by - tt + 1:.1f}V{by - tt + 58:.1f};M{bx - 34:.1f} {by - tt + 1:.1f}V{by - tt + 30:.1f}" dur="4s" repeatCount="indefinite"/></path></g>'
                     f'<circle cx="{bx:.1f}" cy="{by - tt - 4:.1f}" r="3" fill="#FF3355"><animate attributeName="opacity" values="1;.15;1" dur="1.2s" repeatCount="indefinite"/></circle>')

    # edge labels: months along the front, weekdays along the side
    seen = set()
    for w, d, date, c in grid:
        if d == 0 and date[:7] not in seen:
            seen.add(date[:7])
            x, y = P(w + .5, 7.6)
            p.append(bc.text(x, y + 6, MONTHS[int(date[5:7]) - 1], 11, bc.C['muted'], 'mono', 'middle', 'letter-spacing="2"'))
    for d in (1, 3, 5):
        x, y = P(nweeks + .5, d + .5)
        p.append(bc.text(x + 8, y + 8, DAYS[d], 10, bc.C['muted'], 'mono', 'start', 'letter-spacing="1.5"'))
    tx, ty = P(today[0] + .5, today[1] + .5)

    # header
    C = bc.C
    total, active = data["total"], sum(1 for _, c in days if c)
    def streak():
        k, i = 0, len(days) - 1
        if days[i][1] == 0:
            i -= 1
        while i >= 0 and days[i][1] > 0:
            k, i = k + 1, i - 1
        return k
    p.append(bc.text(36, 44, "CONTRIBUTION CITY", 11, C['lav'], 'mono', 'start', 'letter-spacing="3"'))
    p.append(f'<text x="36" y="74" class="serif" font-size="24" fill="{C["silver"]}">{total:,} contributions</text>')
    p.append(f'<text x="36" y="98" class="sans" font-size="13" fill="{C["muted"]}">Each lot is one day · taller building = more contributions · 🌳 park = a day off · 🏗 crane = today</text>')
    bd = dt.date.fromisoformat(best[2])
    stats = [("BEST DAY", f"{best[3]} · {MONTHS[bd.month - 1].title()} {bd.day}"), ("STREAK", f"{streak()} days"), ("ACTIVE DAYS", str(active))]
    x = W - 36
    for lab, val in reversed(stats):
        wdt = max(len(val) * 8.6, len(lab) * 7.2) + 26
        x -= wdt
        p.append(f'<rect x="{x:.0f}" y="34" width="{wdt:.0f}" height="42" rx="10" fill="#0E1428" stroke="#2A3A66"/>'
                 + bc.text(x + 13, 51, lab, 9, C['muted'], 'mono', 'start', 'letter-spacing="1.5"')
                 + bc.text(x + 13, 68, val, 14, "#fff", 'sans', 'start', 'font-weight="700"'))
        x -= 10

    desc = (f"Contribution City in 3D: {total} contributions, one city lot per day. Busier days are taller buildings, from low-rises to glass skyscrapers; "
            f"days off are parks. The best day, {best[3]} contributions on {best[2]}, is a landmark tower; today has a crane. "
            f"Streak {streak()} days, {active} active days.")
    svg = bc.svg(W, H, "city3d", "Contribution City", desc, f'<defs>{"".join(defs)}</defs>' + "".join(p))
    Path(out).write_text(svg, encoding="utf-8")
    print(f"{out}: {nweeks} weeks, lot {s:.0f}px, {H}px tall, {len(svg) // 1024} KB")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
