#!/usr/bin/env python3
"""Metro Map: a year of GitHub work drawn like a subway map.

Each project is a coloured line, each station is a week I committed to it (bigger
station = more commits), and an interchange marks a week I juggled 4+ projects.
Little trains run along every line.

    python3 scripts/viz/build_metro.py HemashreeVI out.svg     (needs GITHUB_TOKEN)
"""
import datetime as dt
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build_cards as bc
from data import load

LINES = ["#E4002B", "#0098D4", "#00A651", "#FFC72C", "#9B59D0", "#F7941D", "#EC4899", "#00B2A9"]
NICE = {"HemashreeVI": "Profile README", "HemashreeVI.github.io": "Portfolio", "Leetcode-Solutions": "LeetCode Solutions",
        "Pit-Wall-an-animated-race-replay": "Pit Wall", "AI_Malocclusion_Detection": "Dental AI", "FRONTEND_FOOD_ORDERING_SYSTEM": "Food Ordering"}
MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()
MAX_LINES = 8


def monday(d):
    d = dt.date.fromisoformat(d)
    return d - dt.timedelta(days=d.weekday())


def build(user, out):
    data = load(user)
    repos = [r for r in data["repos"] if sum(r["days"].values())]
    repos.sort(key=lambda r: -sum(r["days"].values()))
    shown, rest = repos[:MAX_LINES], repos[MAX_LINES:]
    weeks_all = sorted({monday(d) for r in shown for d in r["days"]})
    if not weeks_all:
        return
    w0, w1 = weeks_all[0], monday(dt.date.today().isoformat())
    weeks = [w0 + dt.timedelta(weeks=i) for i in range((w1 - w0).days // 7 + 1)]
    nW = len(weeks)

    W = 1200
    TOP, ROW, X0, X1 = 128, 50, 300, 1150
    H = TOP + ROW * len(shown) + 70
    step = (X1 - X0) / max(1, nW - 1)
    xw = {wk: X0 + i * step for i, wk in enumerate(weeks)}
    C = bc.C
    p = [f"""<defs><linearGradient id="mbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0D1024"/><stop offset="1" stop-color="#090B18"/></linearGradient>
<pattern id="mgrid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#fff" stroke-opacity=".035"/></pattern></defs>
<rect width="{W}" height="{H}" rx="22" fill="url(#mbg)"/><rect width="{W}" height="{H}" rx="22" fill="url(#mgrid)"/>"""]

    # month "zones" and a river, for that printed-map feel
    month_starts = [(i, wk) for i, wk in enumerate(weeks) if i == 0 or wk.month != weeks[i - 1].month]
    for k, (i, wk) in enumerate(month_starts):
        xa = xw[wk] - step / 2
        xb = (xw[month_starts[k + 1][1]] - step / 2) if k + 1 < len(month_starts) else X1 + step / 2
        if k % 2 == 0:
            p.append(f'<rect x="{xa:.0f}" y="{TOP - 30}" width="{xb - xa:.0f}" height="{ROW * len(shown) + 20}" fill="#fff" opacity=".025"/>')
        p.append(bc.text(xa + 8, H - 22, f"ZONE {MONTHS[wk.month - 1]} {wk.year}", 10.5, C['muted'], 'mono', 'start', 'letter-spacing="2"'))
    river = f"M0 {TOP + ROW * len(shown) * .62:.0f} C 300 {TOP + 40} 520 {TOP + ROW * len(shown):.0f} 760 {TOP + ROW * 2.2:.0f} S 1080 {TOP + ROW * len(shown) * .8:.0f} 1200 {TOP + ROW:.0f}"
    p.append(f'<path d="{river}" stroke="#1D4ED8" stroke-opacity=".16" stroke-width="26" fill="none" stroke-linecap="round"/>')

    # lines, stations, trains
    stations_by_week = {}
    for li, r in enumerate(shown):
        col, y = LINES[li % len(LINES)], TOP + li * ROW
        per_week = {}
        for d, c in r["days"].items():
            per_week[monday(d)] = per_week.get(monday(d), 0) + c
        act = sorted(per_week)
        xa, xb = xw[act[0]] - 18, xw[act[-1]] + 18
        name = NICE.get(r["name"], r["name"])
        total = sum(per_week.values())
        # terminus label on the left, the line runs from it
        p.append(f'<path d="M{X0 - 70} {y}H{xa:.0f}" stroke="{col}" stroke-width="3" stroke-dasharray="2 6" opacity=".35"/>')
        p.append(f'<rect x="24" y="{y - 15}" width="200" height="30" rx="15" fill="{col}"/>'
                 + bc.text(40, y + 5, name[:20], 13.5, "#0B0B12" if col in ("#FFC72C",) else "#fff", 'sans', 'start', 'font-weight="700"')
                 + bc.text(214, y + 5, f"{total}", 12, "#0B0B12" if col in ("#FFC72C",) else "#fff", 'mono', 'end', 'opacity=".85"'))
        path = f"M{xa:.1f} {y}H{xb:.1f}"
        p.append(f'<path d="{path}" stroke="{col}" stroke-width="9" stroke-linecap="round"/>')
        peak = max(per_week.values())
        for wk, c in per_week.items():
            rad = min(11, 5 + 6 * math.sqrt(c / 40))
            stations_by_week.setdefault(wk, []).append((xw[wk], y, rad))
            p.append(f'<circle cx="{xw[wk]:.1f}" cy="{y}" r="{rad:.1f}" fill="#fff" stroke="#0B0B12" stroke-width="2.5"/>')
            if c == peak and c >= 5:
                p.append(bc.text(xw[wk], y - rad - 6, f"{c}", 10.5, "#fff", 'mono', 'middle', 'font-weight="700"'))
        # a train shuttling along the line
        dur = max(5, (xb - xa) / 60)
        p.append(f'<g><rect x="-11" y="{y - 5}" width="22" height="10" rx="5" fill="#fff" stroke="{col}" stroke-width="2"/>'
                 f'<animateMotion dur="{dur:.1f}s" begin="-{li * 1.3:.1f}s" repeatCount="indefinite" keyPoints="0;1;0" keyTimes="0;.5;1" calcMode="linear" path="M{xa + 12:.1f} 0H{xb - 12:.1f}"/></g>')

    # interchanges: weeks with 3+ projects
    for wk, st in stations_by_week.items():
        if len(st) < 4:
            continue
        ys = sorted(s[1] for s in st)
        x = st[0][0]
        p.append(f'<rect x="{x - 9:.1f}" y="{ys[0] - 9}" width="18" height="{ys[-1] - ys[0] + 18}" rx="9" fill="#fff" fill-opacity=".07" stroke="#fff" stroke-width="1.6" stroke-opacity=".45"/>')

    # "you are here"
    tx = xw[weeks[-1]]
    p.append(f'<path d="M{tx:.1f} {TOP - 34}V{TOP + ROW * (len(shown) - 1) + 20}" stroke="#FCD34D" stroke-dasharray="3 5" opacity=".6"/>'
             f'<circle cx="{tx:.1f}" cy="{TOP - 38}" r="5" fill="#FCD34D"><animate attributeName="r" values="4;7;4" dur="1.6s" repeatCount="indefinite"/></circle>'
             + bc.text(tx - 10, TOP - 34, "YOU ARE HERE", 10, "#FCD34D", 'mono', 'end', 'letter-spacing="2"'))

    # header and legend
    commits = sum(sum(r["days"].values()) for r in repos)
    p.append(bc.text(32, 42, "METRO MAP · A YEAR OF PROJECTS", 11, C['lav'], 'mono', 'start', 'letter-spacing="3"'))
    p.append(f'<text x="32" y="72" class="serif" font-size="22" fill="{C["silver"]}">{commits:,} commits on {len(repos)} lines'
             f'<tspan fill="{C["muted"]}" font-size="14" font-style="italic"> · each line = a project · each station = a week I worked on it · bigger = more commits · white capsule = a week on 4+ projects</tspan></text>')
    if rest:
        p.append(bc.text(W - 32, 42, f"+{len(rest)} smaller lines not shown", 11, C['muted'], 'mono', 'end'))

    desc = ("Metro map of my GitHub year: " + "; ".join(f"{NICE.get(r['name'], r['name'])} line, {sum(r['days'].values())} commits" for r in shown)
            + ". Stations are weeks; interchanges are weeks with four or more projects.")
    Path(out).write_text(bc.svg(W, H, "metro", "Metro map of my projects", desc, "".join(p)), encoding="utf-8")
    print(f"{out}: {len(shown)} lines over {nW} weeks, {H}px tall")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
