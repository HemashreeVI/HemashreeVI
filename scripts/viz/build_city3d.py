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
import phoenix_layer
import scenery
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


def tree(x, y, r, kind, rnd):
    """An isometric tree at ground point (x, y), radius r. Light comes from the upper right."""
    out = [f'<ellipse cx="{x - r * .5:.1f}" cy="{y + 1:.1f}" rx="{r * 1.3:.1f}" ry="{r * .5:.1f}" fill="#000" opacity=".3"/>']
    if kind == "pine":
        out.append(f'<rect x="{x - 1.2:.1f}" y="{y - r * .8:.1f}" width="2.4" height="{r * .8:.1f}" fill="#4A3020"/>')
        for k, (wid, top) in enumerate(((1.15, 1.1), (.9, 1.9), (.62, 2.6))):
            yb, yt = y - r * (.5 + k * .75), y - r * (top + .9)
            out.append(f'<path d="M{x:.1f} {yt:.1f}L{x - r * wid:.1f} {yb:.1f}L{x:.1f} {yb + r * .18:.1f}Z" fill="#1E4D2B"/>'
                       f'<path d="M{x:.1f} {yt:.1f}L{x + r * wid:.1f} {yb:.1f}L{x:.1f} {yb + r * .18:.1f}Z" fill="#3E8A4A"/>')
        return "".join(out)
    if kind == "bush":
        for k in range(3):
            out.append(f'<circle cx="{x + (k - 1) * r * .55:.1f}" cy="{y - r * .4 - (k % 2) * r * .15:.1f}" r="{r * .55:.1f}" fill="url(#leafC)"/>')
        return "".join(out)
    grad = "sakura" if kind == "sakura" else rnd.choice(["leafA", "leafB", "leafC"])
    trunk = "#5A3A26" if kind != "sakura" else "#4A2E2A"
    h = r * 1.15
    out.append(f'<path d="M{x - 1.6:.1f} {y:.1f}L{x - 1:.1f} {y - h:.1f}L{x + 1:.1f} {y - h:.1f}L{x + 1.6:.1f} {y:.1f}Z" fill="{trunk}"/>'
               f'<path d="M{x:.1f} {y - h * .6:.1f}L{x + r * .45:.1f} {y - h * 1.05:.1f}M{x:.1f} {y - h * .7:.1f}L{x - r * .4:.1f} {y - h * 1.1:.1f}" stroke="{trunk}" stroke-width="1.2"/>')
    # canopy: overlapping leaf clusters, back ones darker
    cy = y - h - r * .55
    blobs = [(rnd.uniform(-.55, .55) * r, rnd.uniform(-.45, .35) * r, rnd.uniform(.42, .62) * r) for _ in range(7)]
    blobs.sort(key=lambda b: b[1])
    for bx, by, br in blobs:
        out.append(f'<circle cx="{x + bx:.1f}" cy="{cy + by:.1f}" r="{br:.1f}" fill="url(#{grad})"/>')
    if kind == "sakura":
        for _ in range(6):
            out.append(f'<circle cx="{x + rnd.uniform(-.6, .6) * r:.1f}" cy="{cy + rnd.uniform(-.5, .4) * r:.1f}" r="{r * .07:.1f}" fill="#fff" opacity=".8"/>')
    return "".join(out)


def car(u, v, s, body, forward=True):
    """A little isometric car at the origin. u = unit screen vector along the road, v = across it."""
    L, Wd, Hc = s * .38, s * .19, s * .09
    def pt(a, b, z=0):
        return (u[0] * a + v[0] * b, u[1] * a + v[1] * b - z)
    def pg(pts, fill, op=1):
        return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}" opacity="{op}"/>'
    hl, hw = L / 2, Wd / 2
    out = [pg([pt(-hl, -hw), pt(hl, -hw), pt(hl, hw), pt(-hl, hw)], "#000", .35)]                       # shadow
    out.append(pg([pt(-hl, hw), pt(hl, hw), pt(hl, hw, Hc), pt(-hl, hw, Hc)], body))                     # side
    out.append(pg([pt(hl, -hw), pt(hl, hw), pt(hl, hw, Hc), pt(hl, -hw, Hc)], body, .8))                 # end
    out.append(pg([pt(-hl, -hw, Hc), pt(hl, -hw, Hc), pt(hl, hw, Hc), pt(-hl, hw, Hc)], body))           # bonnet/boot
    r0, r1 = (-hl * .45, hl * .25) if forward else (-hl * .25, hl * .45)
    out.append(pg([pt(r0, -hw * .8, Hc * 1.8), pt(r1, -hw * .8, Hc * 1.8), pt(r1, hw * .8, Hc * 1.8), pt(r0, hw * .8, Hc * 1.8)], "#C9D6EA"))   # roof
    out.append(pg([pt(r0, hw * .8, Hc), pt(r1, hw * .8, Hc), pt(r1, hw * .8, Hc * 1.8), pt(r0, hw * .8, Hc * 1.8)], "#1B2B44"))              # window
    front, back = (hl, -hl) if forward else (-hl, hl)
    for side in (-hw * .6, hw * .6):
        fx, fy = pt(front, side, Hc * .6)
        bx, by = pt(back, side, Hc * .6)
        out.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="1.6" fill="#FFF7D6"/><circle cx="{bx:.1f}" cy="{by:.1f}" r="1.3" fill="#FF3355"/>')
    gx, gy = pt(front + (s * .35 if forward else -s * .35), 0)
    fx, fy = pt(front, 0)
    out.insert(0, f'<polygon points="{fx:.1f},{fy:.1f} {gx + v[0] * s * .12:.1f},{gy + v[1] * s * .12:.1f} {gx - v[0] * s * .12:.1f},{gy - v[1] * s * .12:.1f}" fill="#FFF3C4" opacity=".16"/>')   # headlight beam
    return "".join(out)


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
    H = int(oy + (nweeks + 7) * b + 110)
    ZW = -12                                                  # water level, below the quay
    yH = oy + 1.0 * b                                         # horizon line

    def P(i, j, h=0.0):
        return ox + (i - j) * a, oy + (i + j) * b - h

    def poly(pts, fill, extra=""):
        return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}" {extra}/>'

    brng = random.Random(23)
    bases = {(w, d): brng.choice(["#6B5B4E", "#7A6A5C", "#5E6878", "#6E7A8C", "#8A6F5A"]) for w, d, _, _ in grid}
    defs = ["""<linearGradient id="c3sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#070B1A"/><stop offset=".6" stop-color="#121A3A"/><stop offset="1" stop-color="#2B1B4A"/></linearGradient>
<linearGradient id="glassL" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2E5C8A"/><stop offset="1" stop-color="#14304F"/></linearGradient>
<linearGradient id="glassR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5B8DBE"/><stop offset="1" stop-color="#244A72"/></linearGradient>
<linearGradient id="landL" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5B3FA0"/><stop offset="1" stop-color="#2A1A55"/></linearGradient>
<linearGradient id="landR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8B6FD8"/><stop offset="1" stop-color="#43308A"/></linearGradient>
<filter id="c3blur"><feGaussianBlur stdDeviation="2.2"/></filter>
<linearGradient id="gL" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2B5A86"/><stop offset=".35" stop-color="#173A5E"/><stop offset="1" stop-color="#0B1E35"/></linearGradient>
<linearGradient id="gR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8EC5F0"/><stop offset=".3" stop-color="#4E86BC"/><stop offset="1" stop-color="#1B3D66"/></linearGradient>
<linearGradient id="pL" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6D4FC2"/><stop offset=".4" stop-color="#3F2A86"/><stop offset="1" stop-color="#1E1048"/></linearGradient>
<linearGradient id="pR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C4B5FD"/><stop offset=".35" stop-color="#8B6FD8"/><stop offset="1" stop-color="#3B2A86"/></linearGradient>
<linearGradient id="sheen" x1="0" y1="0" x2="1" y2="1"><stop offset=".38" stop-color="#fff" stop-opacity="0"/><stop offset=".47" stop-color="#fff" stop-opacity=".32"/><stop offset=".5" stop-color="#fff" stop-opacity=".08"/><stop offset=".55" stop-color="#fff" stop-opacity=".22"/><stop offset=".62" stop-color="#fff" stop-opacity="0"/>
<animateTransform attributeName="gradientTransform" type="translate" values="-1.2 -1.2;1.2 1.2;1.2 1.2" keyTimes="0;.55;1" dur="7s" repeatCount="indefinite"/></linearGradient>
<linearGradient id="skyref" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset=".18" stop-color="#fff" stop-opacity="0"/><stop offset=".8" stop-color="#F472B6" stop-opacity="0"/><stop offset="1" stop-color="#F59E0B" stop-opacity=".22"/></linearGradient>
<pattern id="grass" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><rect width="14" height="14" fill="#2E6B34"/><rect width="7" height="14" fill="#357A3B"/></pattern>
<radialGradient id="leafA" cx="68%" cy="28%" r="75%"><stop offset="0" stop-color="#9BD77A"/><stop offset=".45" stop-color="#4E9A42"/><stop offset="1" stop-color="#1F4F25"/></radialGradient>
<radialGradient id="leafB" cx="68%" cy="28%" r="75%"><stop offset="0" stop-color="#C5E07A"/><stop offset=".45" stop-color="#6E9F3A"/><stop offset="1" stop-color="#2F5220"/></radialGradient>
<radialGradient id="leafC" cx="68%" cy="28%" r="75%"><stop offset="0" stop-color="#7CCB8E"/><stop offset=".5" stop-color="#2F7D4A"/><stop offset="1" stop-color="#123A22"/></radialGradient>
""" + scenery.defs() + """<radialGradient id="sakura" cx="68%" cy="28%" r="75%"><stop offset="0" stop-color="#FFE4EF"/><stop offset=".45" stop-color="#F7A8C8"/><stop offset="1" stop-color="#B85C86"/></radialGradient>"""]
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

    p = [f'<clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath><g clip-path="url(#card)">',
         f'<rect width="{W}" height="{H}" fill="url(#c3sky)"/>']
    for _ in range(110):
        p.append(f'<circle class="twinkle" cx="{rnd.uniform(20, W - 20):.0f}" cy="{rnd.uniform(112, max(130, yH - 150)):.0f}" r="{rnd.choice([.5, .7, .9, 1.1])}" fill="#fff" style="animation-delay:{rnd.uniform(0, 4):.1f}s"/>')
    moon = (W - 140, 168, 24)
    p.append(scenery.backdrop(W, H, yH, 110, random.Random(41), moon))

    def ground(x, y, z=0.0):
        """Screen point -> lot coordinates (i, j) on the plane at height z."""
        u, v = (x - ox) / a, (y + z - oy) / b
        return (u + v) / 2, (v - u) / 2
    FAR = nweeks + 3.3                                          # the far bank across the river
    def is_water(x, y):
        i, j = ground(x, y, ZW)
        return y >= yH and (j >= 7.55 or i >= nweeks + .55) and i < FAR
    def is_land(x, y):
        i, j = ground(x, y)
        on_slab = -.2 <= i <= nweeks + .2 and -.2 <= j <= 7.2
        return y >= yH and not on_slab and not is_water(x, y)
    p.append(scenery.far_lights(W, yH, is_land, random.Random(8)))

    # water: the bay in front and the river on the right, clipped below the horizon
    L0, C0, R0 = P(-40, 7.55, ZW), P(nweeks + .55, 7.55, ZW), P(nweeks + .55, -40, ZW)
    wpoly = [L0, C0, R0, (R0[0], H + 50), (L0[0], H + 50)]
    bank = [P(FAR, -40, ZW), P(FAR, 40, ZW), (P(FAR, 40, ZW)[0] + 4000, P(FAR, 40, ZW)[1]), (P(FAR, -40, ZW)[0] + 4000, P(FAR, -40, ZW)[1])]
    p.append(f'<clipPath id="wclip"><polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in wpoly)}"/></clipPath>'
             f'<clipPath id="below"><rect x="0" y="{yH:.0f}" width="{W}" height="{H}"/></clipPath>')
    p.append(f'<g clip-path="url(#below)"><g clip-path="url(#wclip)"><rect x="0" y="{yH:.0f}" width="{W}" height="{H - yH:.0f}" fill="url(#water)"/>')
    # reflections of the waterfront buildings, warped by ripples
    refl = []
    for w, d, date, c in grid:
        if c == 0 or not (d >= 4 or w >= nweeks - 4):
            continue
        h = height(c)
        f0, f1 = (.12, .88) if h > HMAX * .45 or (w, d) == best[:2] else (.16, .84)
        kind = "landmark" if (w, d) == best[:2] else "glass" if c / peak > .45 else "office" if c / peak > .12 else "house"
        col = {"landmark": "#4C1D95", "glass": "#1D3F66"}.get(kind, shade(bases[(w, d)], .55))
        tier = "hi" if c / peak > .55 else "md" if c / peak > .2 else "lo"
        pat = f"gls{tier}{(w * 7 + d) % 3}" if kind in ("glass", "landmark") else f"win{tier}{(w * 7 + d) % 3}"
        wl = (f1 - f0) * s
        A, B = P(w + f0, d + f1, 2 * ZW), P(w + f1, d + f1, 2 * ZW)
        for (X, Y), k in ((A, SIN), (B, -SIN)):
            refl.append(f'<g transform="matrix({COS:.4f},{k:.4f},0,1,{X:.1f},{Y:.1f})"><rect width="{wl:.1f}" height="{h:.1f}" fill="{col}"/><rect width="{wl:.1f}" height="{h:.1f}" fill="url(#{pat})" opacity=".8"/></g>')
    # lamp reflections along the quays
    lamps = [(i0 + .25, 7.1) for i0 in [x * .5 for x in range(2 * nweeks)]] + [(nweeks + .1, j0 + .25) for j0 in [x * .5 for x in range(14)]]
    for li, lj in lamps:
        x, y = P(li, lj, ZW)
        refl.append(f'<rect x="{x - 1.6:.1f}" y="{y + 6:.1f}" width="3.2" height="{s * .55:.1f}" fill="url(#streak)"/>')
    p.append(f'<g filter="url(#warp)" opacity=".42">{"".join(refl)}</g>')
    # moonlight glitter on the river
    gx = moon[0]
    gy = next((y for y in range(int(yH), H) if is_water(gx, y)), H)
    p.append(f'<ellipse cx="{gx}" cy="{(gy + H) / 2:.0f}" rx="34" ry="{(H - gy) / 2:.0f}" fill="#FFF3D6" opacity=".05" filter="url(#soft)"/>')
    for k in range(150):
        t = rnd.random() ** .8
        y = gy + t * (H - gy)
        spread = 6 + t * 46
        x = gx + rnd.gauss(0, spread / 2)
        wdt = rnd.uniform(1.5, 6) * (1 + t * 1.5)
        p.append(f'<rect class="twinkle" x="{x - wdt / 2:.1f}" y="{y:.1f}" width="{wdt:.1f}" height="{.7 + t * .6:.1f}" fill="#FFF7E0" opacity="{.75 - .45 * t:.2f}" style="animation-delay:{rnd.uniform(0, 4):.1f}s"/>')
    # surface ripples drifting
    p.append(f'<g opacity=".5"><rect x="-100" y="{yH:.0f}" width="{W + 200}" height="{H - yH:.0f}" filter="url(#ripple)">'
             f'<animateTransform attributeName="transform" type="translate" values="0 0;-60 6;0 0" dur="24s" repeatCount="indefinite"/></rect></g>')
    # boats: a ferry on the river, a launch and a sailboat in the bay
    ju_, iu_ = (-COS, SIN), (COS, SIN)
    f0p, f1p = P(nweeks + 1.15, -4, ZW), P(nweeks + 1.15, 10, ZW)
    ferry = scenery.boat_box(ju_, iu_, s * .9, s * .3, s * .1, "#B91C1C", "#3F3F46", (s * .55, s * .24, s * .13, "#F3F4F6", "#FFE7A3"))
    p.append(f'<g>{ferry}<animateMotion dur="34s" repeatCount="indefinite" path="M{f0p[0]:.1f} {f0p[1]:.1f}L{f1p[0]:.1f} {f1p[1]:.1f}"/></g>')
    l0, l1 = P(-6, 9.3, ZW), P(nweeks + 2, 9.3, ZW)
    launch = scenery.boat_box(iu_, ju_, s * .5, s * .18, s * .07, "#F8FAFC", "#94A3B8", (s * .2, s * .13, s * .08, "#E2E8F0", "#BFE3FF"))
    p.append(f'<g>{launch}<animateMotion dur="28s" begin="-9s" repeatCount="indefinite" path="M{l0[0]:.1f} {l0[1]:.1f}L{l1[0]:.1f} {l1[1]:.1f}"/></g>')
    sx, sy = P(2.2, 9.9, ZW)
    p.append(f'<g><g transform="translate({sx:.1f} {sy:.1f})">{scenery.boat_box(iu_, ju_, s * .32, s * .12, s * .05, "#E5E7EB", "#9CA3AF")}'
             f'<path d="M0 {-s * .05:.1f}V{-s * .62:.1f}" stroke="#D1D5DB" stroke-width="1.2"/><path d="M1 {-s * .6:.1f}L{s * .2:.1f} {-s * .1:.1f}L1 {-s * .1:.1f}Z" fill="#F1F5F9" opacity=".9"/></g>'
             f'<animateTransform attributeName="transform" type="translate" values="0 0;0 1.5;0 0" dur="3.2s" repeatCount="indefinite"/></g>')
    p.append('</g></g>')
    # the far bank across the river: embankment, a dense tree line, houses' lights behind it
    tr = random.Random(17)
    p.append(f'<g clip-path="url(#below)"><polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in bank)}" fill="url(#land)"/>')
    e0, e1 = P(FAR, -40, ZW), P(FAR, 40, ZW)
    p.append(f'<path d="M{e0[0]:.1f} {e0[1]:.1f}L{e1[0]:.1f} {e1[1]:.1f}" stroke="#8FA3C8" stroke-opacity=".35" stroke-width="1.4"/>')
    for k in range(260):
        jj = tr.uniform(-12, 14)
        x, y = P(FAR + tr.uniform(1.2, 4), jj, ZW)
        if 0 < x < W and yH < y < H:
            p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{tr.choice([.7, .9, 1.2])}" fill="{tr.choice(["#FFE3A1", "#FFD27A", "#FFF3D6"])}" opacity="{tr.uniform(.4, .9):.2f}"/>')
    for row in (2, 1, 0):
        for k in range(130):
            jj = tr.uniform(-14, 14)
            x, y = P(FAR + .25 + row * .28 + tr.uniform(0, .2), jj, ZW)
            if -20 < x < W + 20 and yH < y < H + 20:
                r = s * tr.uniform(.09, .15) * (1 - row * .1)
                p.append(f'<ellipse cx="{x:.1f}" cy="{y - r * .85:.1f}" rx="{r * .85:.1f}" ry="{r:.1f}" fill="url(#nightTree)" opacity="{.8 if row else 1}"/>')
    p.append('</g>')
    # the waterfront continues beyond the island: stone edges and lamps on the far shores
    for (sa, sb) in ((P(-40, 7.55, ZW), P(-.15, 7.55, ZW)), (P(nweeks + .55, -40, ZW), P(nweeks + .55, -.15, ZW))):
        p.append(f'<g clip-path="url(#below)"><path d="M{sa[0]:.1f} {sa[1]:.1f}L{sb[0]:.1f} {sb[1]:.1f}" stroke="#8FA3C8" stroke-opacity=".4" stroke-width="1.6"/>'
                 f'<path d="M{sa[0]:.1f} {sa[1] + 3:.1f}L{sb[0]:.1f} {sb[1] + 3:.1f}" stroke="#0B0F1C" stroke-width="3"/></g>')
    for k in range(1, 40):
        for (x, y) in (P(-.15 - k * .5, 7.5, 0), P(nweeks + .5, -.15 - k * .5, 0)):
            if 0 < x < W and y > yH + 4:
                p.append(f'<circle cx="{x:.1f}" cy="{y - 6:.1f}" r="5" fill="url(#lampG)" opacity=".7"/><circle cx="{x:.1f}" cy="{y - 6:.1f}" r="1.2" fill="#FFF3C4"/>'
                         f'<rect x="{x - 1:.1f}" y="{y + 12:.1f}" width="2" height="16" fill="url(#streak)" opacity=".5"/>')

    # ground: asphalt slab, then sidewalks per lot, lane markings
    g0, g1, g2, g3 = P(-.15, -.15), P(nweeks + .15, -.15), P(nweeks + .15, 7.15), P(-.15, 7.15)
    qd = -ZW + 2                                     # quay wall height, down to the water
    p.append(poly([P(-.15, 7.15), P(nweeks + .15, 7.15), (g2[0], g2[1] + qd), (g3[0], g3[1] + qd)], "url(#stone)"))
    p.append(poly([P(-.15, 7.15), P(nweeks + .15, 7.15), (g2[0], g2[1] + qd), (g3[0], g3[1] + qd)], "#000", 'opacity=".35"'))
    p.append(poly([P(nweeks + .15, -.15), P(nweeks + .15, 7.15), (g2[0], g2[1] + qd), (g1[0], g1[1] + qd)], "url(#stone)"))
    p.append(f'<path d="M{g3[0]:.1f} {g3[1] + qd:.1f}L{g2[0]:.1f} {g2[1] + qd:.1f}L{g1[0]:.1f} {g1[1] + qd:.1f}" stroke="#AFC3E8" stroke-opacity=".25" stroke-width="1.2" fill="none"/>')
    p.append(poly([g0, g1, g2, g3], "#1E2436"))
    for w in range(nweeks + 1):
        p.append(f'<path d="M{P(w - .04, 0)[0]:.1f} {P(w - .04, 0)[1]:.1f}L{P(w - .04, 7)[0]:.1f} {P(w - .04, 7)[1]:.1f}" stroke="#FDE68A" stroke-opacity=".18" stroke-dasharray="4 6"/>')
    lots = {}
    for w, d, date, c in grid:
        f0, f1 = .08, .92
        p.append(poly([P(w + f0, d + f0), P(w + f1, d + f0), P(w + f1, d + f1), P(w + f0, d + f1)], "#2C3448" if c else "url(#grass)"))
        lots[(w, d)] = (date, c)

    # traffic: cars drive along the avenues between weeks and on the front boulevard
    crng = random.Random(5)
    ju, iu = (-COS, SIN), (COS, SIN)                # screen directions of +weekday and +week
    bodies = ["#E4002B", "#F7F7F2", "#2563EB", "#FBBF24", "#10B981", "#9CA3AF", "#F97316", "#7C3AED"]
    avenues = sorted(crng.sample(range(1, nweeks), min(nweeks - 1, max(3, nweeks // 2))))
    for k, wv in enumerate(avenues):
        down = k % 2 == 0
        a0, a1 = (P(wv - .04, -.6), P(wv - .04, 7.6)) if down else (P(wv - .04, 7.6), P(wv - .04, -.6))
        dur = crng.uniform(7, 12)
        body = car(ju, iu, s, crng.choice(bodies), forward=down)
        for n in range(1 + (k % 2)):
            t0 = ((n * .5 + crng.random()) % 1) * dur      # same start for the move and the fade
            p.append(f'<g opacity="0">{body}<animateMotion dur="{dur:.1f}s" begin="-{t0:.1f}s" repeatCount="indefinite" path="M{a0[0]:.1f} {a0[1]:.1f}L{a1[0]:.1f} {a1[1]:.1f}"/>'
                     f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.06;.94;1" dur="{dur:.1f}s" begin="-{t0:.1f}s" repeatCount="indefinite"/></g>')
    for k in range(3):                               # the boulevard along the front edge
        right = k % 2 == 0
        a0, a1 = (P(-.6, 7.08), P(nweeks + .6, 7.08)) if right else (P(nweeks + .6, 7.08), P(-.6, 7.08))
        dur = crng.uniform(10, 15)
        t0 = crng.random() * dur
        p.append(f'<g opacity="0">{car(iu, ju, s, crng.choice(bodies), forward=right)}<animateMotion dur="{dur:.1f}s" begin="-{t0:.1f}s" repeatCount="indefinite" path="M{a0[0]:.1f} {a0[1]:.1f}L{a1[0]:.1f} {a1[1]:.1f}"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.05;.95;1" dur="{dur:.1f}s" begin="-{t0:.1f}s" repeatCount="indefinite"/></g>')

    # buildings, back to front
    for w, d, date, c in sorted(grid, key=lambda g: (g[0] + g[1], g[0])):
        h = height(c)
        if c == 0:                                   # park: footpath, bushes and a few real-looking trees
            trng = random.Random(w * 31 + d)
            if trng.random() < .5:                     # a curved path across the lawn
                p0, p1, p2 = P(w + .1, d + .55), P(w + .5, d + .35), P(w + .9, d + .6)
                p.append(f'<path d="M{p0[0]:.1f} {p0[1]:.1f}Q{p1[0]:.1f} {p1[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}" stroke="#C9B48A" stroke-opacity=".55" stroke-width="{s * .05:.1f}" fill="none" stroke-linecap="round"/>')
            spots = [(.28, .3), (.7, .68), (.66, .26), (.3, .72)]
            trng.shuffle(spots)
            for tx, ty in sorted(spots[: 2 + trng.randrange(2)], key=lambda t: t[0] + t[1]):
                x, y = P(w + tx, d + ty)
                p.append(tree(x, y, s * trng.uniform(.13, .17), trng.choices(["oak", "oak", "pine", "sakura", "bush"], [4, 3, 2, 1.4, 1])[0], trng))
            continue
        is_best, is_today = (w, d) == (best[0], best[1]), (w, d) == (today[0], today[1])
        f0, f1 = (.12, .88) if h > HMAX * .45 or is_best else (.16, .84)
        tier = "hi" if c / peak > .55 else "md" if c / peak > .2 else "lo"
        v = (w * 7 + d) % 3
        kind = "landmark" if is_best else "glass" if c / peak > .45 else "office" if c / peak > .12 else "house"
        base = bases[(w, d)]                       # brick / concrete
        # shadow on the ground (light from the upper right)
        sh = [P(w + f0, d + f1), P(w + f1, d + f1), (P(w + f1, d + f1)[0] - h * .55, P(w + f1, d + f1)[1] + h * .08), (P(w + f0, d + f1)[0] - h * .55, P(w + f0, d + f1)[1] + h * .08)]
        p.append(poly(sh, "#000", 'opacity=".28" filter="url(#c3blur)"'))
        # left face (facing +weekday) and right face (facing +week), drawn as skewed rects so windows follow
        L, R = P(w + f0, d + f1, h), P(w + f1, d + f1, h)
        wl = (f1 - f0) * s
        glass = kind in ("glass", "landmark")
        if glass:
            lf, rf, pat = ("url(#pL)", "url(#pR)", f"gls{tier}{v}") if kind == "landmark" else ("url(#gL)", "url(#gR)", f"gls{tier}{v}")
        else:
            lf, rf, pat = shade(base, .62), shade(base, 1.0), f"win{tier}{v}"
        over = (f'<rect width="{wl:.1f}" height="{h:.1f}" fill="url(#skyref)"/><rect width="{wl:.1f}" height="{h:.1f}" fill="url(#sheen)"/>') if glass else ""
        p.append(f'<g transform="matrix({COS:.4f},{SIN:.4f},0,1,{L[0]:.1f},{L[1]:.1f})"><rect width="{wl:.1f}" height="{h:.1f}" fill="{lf}"/><rect y="4" width="{wl:.1f}" height="{max(0, h - 8):.1f}" fill="url(#{pat})"/>{over}</g>')
        p.append(f'<g transform="matrix({COS:.4f},{-SIN:.4f},0,1,{R[0]:.1f},{R[1]:.1f})"><rect width="{wl:.1f}" height="{h:.1f}" fill="{rf}"/><rect y="4" width="{wl:.1f}" height="{max(0, h - 8):.1f}" fill="url(#{pat})" opacity=".9"/>{over}</g>')
        if glass:                                      # bright vertical corner where the two glass walls meet
            p.append(f'<path d="M{R[0]:.1f} {R[1]:.1f}V{R[1] + h:.1f}" stroke="#E0F2FF" stroke-opacity=".55" stroke-width="1.2"/>')
        top = [P(w + f0, d + f0, h), P(w + f1, d + f0, h), P(w + f1, d + f1, h), P(w + f0, d + f1, h)]
        p.append(poly(top, shade(base, 1.25) if kind in ("house", "office") else "#22476E" if kind == "glass" else "#5B3FA0"))
        p.append(f'<path d="M{top[3][0]:.1f} {top[3][1]:.1f}L{top[2][0]:.1f} {top[2][1]:.1f}L{top[1][0]:.1f} {top[1][1]:.1f}" stroke="#fff" stroke-opacity="{.6 if kind in ("glass", "landmark") else .18}" fill="none"/>')
        cx, cy = P(w + .5, d + .5, h)
        if kind == "house" and h < s * .9:            # pitched-roof hint: a little roof cap
            p.append(poly([P(w + f0, d + f1, h), P(w + f1, d + f1, h), (cx + 0, cy - s * .18), ], shade(base, .45), 'opacity=".9"'))
        elif kind == "office":                         # water tank + AC unit
            p.append(f'<rect x="{cx - 4:.1f}" y="{cy - 11:.1f}" width="8" height="9" fill="#5B4636"/><ellipse cx="{cx:.1f}" cy="{cy - 11:.1f}" rx="4" ry="1.8" fill="#7A5E48"/>'
                     f'<path d="M{cx - 3:.1f} {cy - 2:.1f}l-1.5 3M{cx + 3:.1f} {cy - 2:.1f}l1.5 3" stroke="#3A2C22"/>'
                     f'<rect x="{cx + 6:.1f}" y="{cy - 3:.1f}" width="6" height="4" fill="#9AA3B2"/>')
        elif kind == "glass":                          # rooftop penthouse + antenna with a red light
            p.append(poly([P(w + .38, d + .38, h + 7), P(w + .62, d + .38, h + 7), P(w + .62, d + .62, h + 7), P(w + .38, d + .62, h + 7)], "#2F4F73")
                     + poly([P(w + .38, d + .62, h), P(w + .62, d + .62, h), P(w + .62, d + .62, h + 7), P(w + .38, d + .62, h + 7)], "#173350")
                     + poly([P(w + .62, d + .62, h), P(w + .62, d + .38, h), P(w + .62, d + .38, h + 7), P(w + .62, d + .62, h + 7)], "#27476B"))
            cy -= 7
            p.append(f'<path d="M{cx:.1f} {cy:.1f}V{cy - 16:.1f}" stroke="#C9D2E3" stroke-width="1.2"/><circle cx="{cx:.1f}" cy="{cy - 17:.1f}" r="2" fill="#FF3355"><animate attributeName="opacity" values="1;.2;1" dur="1.4s" repeatCount="indefinite"/></circle>')
        elif kind == "landmark":                     # landmark: crown, spire, beacon, sign
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

    # street lamps along the quays, with pools of light on the promenade
    for li, lj in lamps:
        x, y = P(li, lj)
        ph = s * .34
        p.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{s * .2:.1f}" ry="{s * .09:.1f}" fill="url(#lampG)" opacity=".5"/>'
                 f'<path d="M{x:.1f} {y:.1f}V{y - ph:.1f}" stroke="#4B5563" stroke-width="1.3"/>'
                 f'<circle cx="{x:.1f}" cy="{y - ph:.1f}" r="7" fill="url(#lampG)"/><circle cx="{x:.1f}" cy="{y - ph:.1f}" r="1.7" fill="#FFF3C4"/>')
    p.append(f'<path d="M{P(-.15, 7.13, 2.5)[0]:.1f} {P(-.15, 7.13, 2.5)[1]:.1f}L{P(nweeks + .13, 7.13, 2.5)[0]:.1f} {P(nweeks + .13, 7.13, 2.5)[1]:.1f}L{P(nweeks + .13, -.15, 2.5)[0]:.1f} {P(nweeks + .13, -.15, 2.5)[1]:.1f}" stroke="#9CA3AF" stroke-opacity=".5" fill="none"/>')

    # cable-stayed bridge across the river to the far bank
    jb, i0b, i1b, ip = 3.5, nweeks + .15, FAR + .6, nweeks + 1.85
    deck_t = [P(i0b, jb - .22), P(i1b, jb - .22), P(i1b, jb + .22), P(i0b, jb + .22)]
    p.append(poly([P(i0b, jb + .22), P(i1b, jb + .22), P(i1b, jb + .22, -5), P(i0b, jb + .22, -5)], "#3A4058"))
    for pi in (nweeks + 1.0, nweeks + 2.7):           # piers into the water
        p.append(poly([P(pi - .06, jb + .12, -5), P(pi + .06, jb + .12, -5), P(pi + .06, jb + .12, ZW), P(pi - .06, jb + .12, ZW)], "#2B3044"))
    p.append(poly(deck_t, "#272C3D"))
    for e in (-.2, .2):
        q0, q1 = P(i0b, jb + e, 3), P(i1b, jb + e, 3)
        p.append(f'<path d="M{q0[0]:.1f} {q0[1]:.1f}L{q1[0]:.1f} {q1[1]:.1f}" stroke="#CBD5E1" stroke-opacity=".55" stroke-width="1"/>')
    m0, m1 = P(i0b, jb), P(i1b, jb)
    p.append(f'<path d="M{m0[0]:.1f} {m0[1]:.1f}L{m1[0]:.1f} {m1[1]:.1f}" stroke="#FDE68A" stroke-opacity=".35" stroke-dasharray="5 6"/>')
    # cars crossing
    for k, (fw, dur) in enumerate(((True, 9), (False, 11))):
        e = -.1 if fw else .1
        q0, q1 = (P(i0b - .3, jb + e), P(i1b + .5, jb + e)) if fw else (P(i1b + .5, jb + e), P(i0b - .3, jb + e))
        p.append(f'<g>{car((COS, SIN), (-COS, SIN), s * .85, ["#F8FAFC", "#DC2626"][k], forward=fw)}<animateMotion dur="{dur}s" begin="-{k * 4}s" repeatCount="indefinite" path="M{q0[0]:.1f} {q0[1]:.1f}L{q1[0]:.1f} {q1[1]:.1f}"/></g>')
    # pylon (A-frame) and stay cables
    Hp = s * 2.5
    top = P(ip, jb, Hp)
    for e in (-.3, .3):
        b0 = P(ip, jb + e, ZW)
        p.append(f'<path d="M{b0[0]:.1f} {b0[1]:.1f}L{top[0]:.1f} {top[1]:.1f}" stroke="{"#C7CEDB" if e > 0 else "#8B95A8"}" stroke-width="{s * .07:.1f}" stroke-linecap="round"/>')
    for k in range(1, 7):
        for side in (-1, 1):
            dq = P(ip + side * k * .27, jb + .2 if side > 0 else jb - .2, 2)
            p.append(f'<path d="M{top[0]:.1f} {top[1] + 4:.1f}L{dq[0]:.1f} {dq[1]:.1f}" stroke="#E2E8F0" stroke-opacity=".45" stroke-width=".7"/>')
    p.append(f'<circle cx="{top[0]:.1f}" cy="{top[1] - 2:.1f}" r="2.6" fill="#FF3355"><animate attributeName="opacity" values="1;.2;1" dur="1.5s" repeatCount="indefinite"/></circle>')

    # light pollution over the city, a helicopter on the landmark and a plane on approach
    cxm, cym = P(nweeks / 2, 3.5, HMAX * .6)
    p.append(f'<ellipse cx="{cxm:.0f}" cy="{cym:.0f}" rx="{(nweeks + 7) * a * .55:.0f}" ry="{HMAX * .9:.0f}" fill="url(#cityglow)"/>')
    bx_, by_ = P(best[0] + .5, best[1] + .5, height(best[3]) + 95)
    p.append(scenery.helicopter(bx_, by_))
    p.append(scenery.plane(W, max(150, yH - 120)))

    # edge labels: months along the front, weekdays along the side
    seen = set()
    for w, d, date, c in grid:
        if d == 0 and date[:7] not in seen:
            seen.add(date[:7])
            x, y = P(w + .5, 7.6)
            p.append(bc.text(x, y + 6, MONTHS[int(date[5:7]) - 1], 11, bc.C['muted'], 'mono', 'middle', 'letter-spacing="2"'))
    tx, ty = P(today[0] + .5, today[1] + .5)

    p.append('</g>')
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
    # the fire phoenix crosses the night sky now and then, in front of the moon
    p.append(phoenix_layer.flies("cityphx", W, moon[1] + 8))
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
            f"Streak {streak()} days, {active} active days. The city is an island in a harbour at night: mountains and moon behind, "
            f"a river with a ferry, a cable-stayed bridge with traffic, reflections in the water, a helicopter and a plane.")
    svg = bc.svg(W, H, "city3d", "Contribution City", desc, f'<defs>{"".join(defs)}</defs>' + "".join(p))
    Path(out).write_text(svg, encoding="utf-8")
    print(f"{out}: {nweeks} weeks, lot {s:.0f}px, {H}px tall, {len(svg) // 1024} KB")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
