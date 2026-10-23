#!/usr/bin/env python3
"""Draws the README's contribution activity graph (last 31 days) as an animated SVG.

Runs in the snake workflow, which publishes dist/ to the `output` branch:

    GITHUB_TOKEN=... python3 scripts/activity_graph.py HemashreeVI dist/activity-graph.svg

Standard library only. Pass --demo instead of a token to render sample data locally.
"""
import datetime as dt
import json
import os
import random
import sys
import urllib.request
from xml.sax.saxutils import escape

DAYS = 31
W, H = 1200, 420
PAD_L, PAD_R, PAD_T, PAD_B = 70, 36, 92, 64
C = {"bg": "#14101F", "line": "#B7A4F2", "area": "#7B61D9", "grid": "#2D2647", "text": "#C9C5D8",
     "muted": "#9A93B4", "title": "#D9CEFF", "point": "#FFFFFF"}

QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
  totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def fetch(login, token):
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
                                 headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [(d["date"], d["contributionCount"]) for w in weeks for d in w["contributionDays"]]
    return days[-DAYS:]


def demo():
    today = dt.date.today()
    random.seed(4)
    return [((today - dt.timedelta(days=DAYS - 1 - i)).isoformat(), max(0, int(random.gauss(4, 4)))) for i in range(DAYS)]


def nice_max(m):
    for step in (1, 2, 5, 10, 20, 25, 50, 100):
        if m <= step * 4:
            return step * 4, step
    return m, max(1, m // 4)


def render(login, days):
    counts = [c for _, c in days]
    top, step = nice_max(max(counts + [1]))
    iw, ih = W - PAD_L - PAD_R, H - PAD_T - PAD_B
    xs = [PAD_L + i * iw / (len(days) - 1) for i in range(len(days))]
    ys = [PAD_T + ih - c / top * ih for c in counts]

    # smooth path (Catmull-Rom → cubic Bézier)
    def path(pts):
        d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
        for i in range(len(pts) - 1):
            p0, p1, p2 = pts[max(0, i - 1)], pts[i], pts[i + 1]
            p3 = pts[min(len(pts) - 1, i + 2)]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            d += f" C{c1[0]:.1f} {min(PAD_T + ih, c1[1]):.1f} {c2[0]:.1f} {min(PAD_T + ih, c2[1]):.1f} {p2[0]:.1f} {p2[1]:.1f}"
        return d

    pts = list(zip(xs, ys))
    line = path(pts)
    area = line + f" L{xs[-1]:.1f} {PAD_T + ih} L{xs[0]:.1f} {PAD_T + ih} Z"
    total = sum(counts)
    active = sum(1 for c in counts if c)
    best_i = max(range(len(counts)), key=lambda i: counts[i])

    grid = []
    for k in range(5):
        v = step * k
        y = PAD_T + ih - v / top * ih
        grid.append(f'<path d="M{PAD_L} {y:.1f}H{W - PAD_R}" stroke="{C["grid"]}" stroke-dasharray="{"0" if k == 0 else "4 6"}"/>'
                    f'<text x="{PAD_L - 14}" y="{y + 5:.1f}" text-anchor="end" class="ax">{v}</text>')
    xl = []
    for i, (d, _) in enumerate(days):
        if i % 5 == 0 or i == len(days) - 1:
            day = dt.date.fromisoformat(d)
            xl.append(f'<text x="{xs[i]:.1f}" y="{H - PAD_B + 30}" text-anchor="middle" class="ax">{day.strftime("%b %-d")}</text>')
    dots = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5 if i == best_i else 3.2}" fill="{C["point"] if c else C["muted"]}" opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" begin="{0.15 + i * 0.045:.2f}s" dur=".3s" fill="freeze"/></circle>'
        for i, ((x, y), c) in enumerate(zip(pts, counts)))
    first, last = dt.date.fromisoformat(days[0][0]), dt.date.fromisoformat(days[-1][0])

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">{escape(login)}'s contribution activity</title>
<desc id="d">{total} contributions on {active} of the last {DAYS} days ({first:%b %-d} to {last:%b %-d}).</desc>
<style>
.ax{{font:12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{C["muted"]}}}
.h{{font:600 20px -apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;fill:{C["title"]}}}
.s{{font:13px -apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;fill:{C["text"]}}}
.k{{font:600 22px -apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;fill:{C["title"]}}}
</style>
<defs><linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["area"]}" stop-opacity=".55"/><stop offset="1" stop-color="{C["area"]}" stop-opacity="0"/></linearGradient>
<clipPath id="reveal"><rect x="0" y="0" width="0" height="{H}"><animate attributeName="width" from="0" to="{W}" dur="1.6s" fill="freeze" calcMode="spline" keySplines=".3 0 .2 1" keyTimes="0;1"/></rect></clipPath></defs>
<rect width="{W}" height="{H}" rx="16" fill="{C["bg"]}"/>
<text x="{PAD_L - 30}" y="44" class="h">Contribution activity</text>
<text x="{PAD_L - 30}" y="68" class="s">Last {DAYS} days · {first:%b %-d} – {last:%b %-d}</text>
<text x="{W - PAD_R}" y="44" text-anchor="end" class="k">{total}</text>
<text x="{W - PAD_R}" y="68" text-anchor="end" class="s">contributions · {active} active days</text>
{"".join(grid)}{"".join(xl)}
<g clip-path="url(#reveal)"><path d="{area}" fill="url(#fill)"/>
<path d="{line}" fill="none" stroke="{C["line"]}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/></g>
{dots}
</svg>
"""


def main():
    login, out = sys.argv[1], sys.argv[2]
    days = demo() if "--demo" in sys.argv else fetch(login, os.environ["GITHUB_TOKEN"])
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(login, days))
    print(f"wrote {out}: {sum(c for _, c in days)} contributions over {len(days)} days")


if __name__ == "__main__":
    main()
