#!/usr/bin/env python3
"""Two playful contribution cards for the profile README.

  commit-run.svg       an arcade take on the contribution grid: a ship flies the
                       last year of contributions and lights up every busy day,
                       with level, streak, stars, followers and language power-ups.
  commit-exchange.svg  contributions as a stock: weekly candlesticks of a
                       30-day rolling "price", volume bars, repo "holdings" by
                       stars and a "sector allocation" by language.

In the profile-cards workflow (GITHUB_TOKEN set):

    python3 scripts/viz/arcade.py HemashreeVI dist --theme midnight

For a local preview, pass --data file.json with the same shape fetch() returns.
Themes live in themes.py. Standard library only.
"""
import argparse
import datetime as dt
import json
import math
import os
import sys
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import themes  # noqa: E402

QUERY = """query($login:String!){ user(login:$login){
  followers { totalCount }
  repositories(first:100, ownerAffiliations:OWNER, isFork:false, privacy:PUBLIC,
               orderBy:{field:STARGAZERS, direction:DESC}) {
    nodes { name stargazerCount primaryLanguage { name color } }
  }
  contributionsCollection {
    contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
  } } }"""

FONT = "font-family=\"'JetBrains Mono','SFMono-Regular',Menlo,Consolas,monospace\""
SANS = "font-family=\"'Inter','Segoe UI',Helvetica,Arial,sans-serif\""


def fetch(login, token):
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
                                 headers={"Authorization": f"bearer {token}", "User-Agent": "profile-arcade"})
    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.load(r)
    if out.get("errors"):
        raise RuntimeError(out["errors"])
    u = out["data"]["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    return {
        "login": login,
        "followers": u["followers"]["totalCount"],
        "total": cal["totalContributions"],
        "days": [[d["date"], d["contributionCount"]] for w in cal["weeks"] for d in w["contributionDays"]],
        "repos": [{"name": r["name"], "stars": r["stargazerCount"],
                   "language": (r["primaryLanguage"] or {}).get("name") or "",
                   "color": (r["primaryLanguage"] or {}).get("color") or "#8b949e"} for r in u["repositories"]["nodes"]],
    }


# ---------------------------------------------------------------- helpers

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def t(x, y, s, size, fill, font=FONT, anchor="start", extra=""):
    return f'<text x="{x}" y="{y}" {font} font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


def short(n):
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def level_of(n, top):
    if n <= 0:
        return 0
    return min(4, max(1, math.ceil(4 * n / max(top, 1))))


def streaks(days):
    cur = 0
    for i, (_, n) in enumerate(reversed(days)):
        if n > 0:
            cur += 1
        elif i == 0:
            continue          # today can still be empty without breaking the streak
        else:
            break
    return cur


def languages(repos, k=5):
    c = Counter(r["language"] for r in repos if r["language"])
    colors = {r["language"]: r["color"] for r in repos if r["language"]}
    total = sum(c.values()) or 1
    return [(name, n / total, colors[name]) for name, n in c.most_common(k)]


def card(w, h, th, uid, title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-labelledby="{uid}-t"><title id="{uid}-t">{esc(title)}</title>'
            f'<defs><linearGradient id="{uid}-bg" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{th["panel"]}"/><stop offset="1" stop-color="{th["bg"]}"/></linearGradient>'
            f'<filter id="{uid}-glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/>'
            f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18" fill="url(#{uid}-bg)" stroke="{th["line"]}" stroke-width="2"/>'
            f'{body}</svg>')


def window_bar(th, w, label):
    dots = "".join(f'<circle cx="{34 + i * 18}" cy="30" r="6" fill="{c}"/>' for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")))
    return (dots + t(100, 35, label, 13, th["muted"]) + t(w - 32, 35, "LIVE", 12, th["accent"], anchor="end",
                                                           extra='letter-spacing="2"')
            + f'<circle cx="{w - 80}" cy="30" r="4" fill="{th["accent"]}"><animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></circle>'
            + f'<line x1="20" y1="54" x2="{w - 20}" y2="54" stroke="{th["line"]}"/>')


# ---------------------------------------------------------------- Commit Run

def commit_run(d, th):
    w, h, uid = 1200, 430, "run"
    days = d["days"][-371:]
    top = max((n for _, n in days), default=1)
    first = dt.date.fromisoformat(days[0][0])
    offset = (first.weekday() + 1) % 7            # row of the first day (Sunday = 0)
    cells = [(offset + i) // 7 for i in range(len(days))]
    cols = cells[-1] + 1
    size, gap = 15, 4
    step = size + gap
    gx = (w - cols * step) // 2
    gy = 118
    lane = 3                                      # the ship flies along Wednesday
    dur = 14.0
    parts = [window_bar(th, w, f"{d['login']} / README.md")]
    parts.append(t(40, 92, f"COMMIT RUN · @{d['login'].upper()}", 15, th["accent"], extra='letter-spacing="2" font-weight="700"'))
    parts.append(t(w - 40, 92, f"HI-SCORE {d['total']:,}", 15, "#FFD166", anchor="end", extra='letter-spacing="2" font-weight="700"'))
    for i, (date, n) in enumerate(days):
        col, row = cells[i], (offset + i) % 7
        x, y = gx + col * step, gy + row * step
        lv = level_of(n, top)
        fill = th["levels"][lv]
        anim = ""
        if lv >= 2:                               # busy days flash as the ship passes their column
            when = round(dur * col / cols, 2)
            anim = (f'<animate attributeName="opacity" values="1;0.35;1" keyTimes="0;0.5;1" dur="0.6s" '
                    f'begin="{when}s;run_loop.begin+{when}s"/>')
        parts.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="3" fill="{fill}"><title>{n} on {date}</title>{anim}</rect>')
    # the ship: a small pixel fighter with a flickering flame and a fading trail
    ly = gy + lane * step + size / 2
    ship = (f'<g filter="url(#{uid}-glow)">'
            f'<rect x="-46" y="-1.5" width="40" height="3" rx="1.5" fill="{th["accent2"]}" opacity=".55"/>'
            f'<polygon points="-10,-4 -18,0 -10,4" fill="#FFB86B"><animate attributeName="points" '
            f'values="-10,-4 -18,0 -10,4;-10,-4 -24,0 -10,4;-10,-4 -18,0 -10,4" dur=".25s" repeatCount="indefinite"/></polygon>'
            f'<polygon points="-10,-9 14,0 -10,9 -5,0" fill="{th["text"]}"/>'
            f'<rect x="-3" y="-2" width="6" height="4" rx="1" fill="{th["accent"]}"/></g>')
    parts.append(f'<g transform="translate(0 {ly})">'
                 f'<animate id="run_loop" attributeName="opacity" from="1" to="1" dur="{dur}s" begin="0s;run_loop.end"/>'
                 f'<g>{ship}<animateTransform attributeName="transform" type="translate" from="{gx - 30} 0" '
                 f'to="{gx + cols * step + 30} 0" dur="{dur}s" repeatCount="indefinite"/></g></g>')
    # stat tiles
    stars = sum(r["stars"] for r in d["repos"])
    lvl = max(1, int(math.sqrt(d["total"] / 5)))
    tiles = [("LEVEL", str(lvl)), ("STREAK", f"{streaks(days)} DAY" + ("" if streaks(days) == 1 else "S")), ("STARS", short(stars)), ("FOLLOWERS", short(d["followers"]))]
    ty, tw = 278, 262
    for i, (k, v) in enumerate(tiles):
        x = 40 + i * (tw + 20)
        parts.append(f'<rect x="{x}" y="{ty}" width="{tw}" height="70" rx="12" fill="{th["bg"]}" stroke="{th["line"]}"/>')
        parts.append(t(x + 18, ty + 26, k, 11, th["muted"], extra='letter-spacing="2"'))
        parts.append(t(x + 18, ty + 54, v, 24, th["text"], extra='font-weight="700"'))
    # power-ups: top languages
    parts.append(t(40, 384, "POWER-UPS", 11, th["muted"], extra='letter-spacing="2"'))
    x = 140
    for name, _, color in languages(d["repos"], 5):
        wpx = 34 + len(name) * 8
        parts.append(f'<rect x="{x}" y="368" width="{wpx}" height="26" rx="13" fill="none" stroke="{color}"/>'
                     f'<circle cx="{x + 14}" cy="381" r="5" fill="{color}"/>' + t(x + 26, 386, name, 12, th["text"]))
        x += wpx + 10
    parts.append(t(w - 40, 386, "the ship flies my real contribution grid and lights up every busy day", 11, th["muted"], anchor="end"))
    return card(w, h, th, uid, f"Commit Run: {d['total']} contributions in the last year", "".join(parts))


# ---------------------------------------------------------------- Commit Exchange

def commit_exchange(d, th):
    w, h, uid = 1200, 560, "exc"
    days = d["days"]
    counts = [n for _, n in days]
    price = [sum(counts[max(0, i - 29):i + 1]) for i in range(len(counts))]     # 30-day rolling contributions
    now, before = price[-1], price[-29] if len(price) > 29 else price[0]
    change = (now - before) / before * 100 if before else 0.0
    up = change >= 0
    weeks = 24
    tail = list(zip(days, price))[-weeks * 7:]
    candles = []
    for k in range(0, len(tail), 7):
        chunk = tail[k:k + 7]
        ps = [p for _, p in chunk]
        candles.append((ps[0], ps[-1], max(ps), min(ps), sum(n for (_, n), _ in chunk)))
    parts = [window_bar(th, w, f"{d['login']} / README.md")]
    # header
    langs = languages(d["repos"], 5)
    sector = (langs[0][0] if langs else "CODE").upper()
    parts.append(f'<rect x="40" y="74" width="54" height="54" rx="14" fill="{th["accent"]}" opacity=".15" stroke="{th["accent"]}"/>'
                 + t(67, 110, d["login"][:1].upper(), 26, th["accent"], anchor="middle", extra='font-weight="700"'))
    parts.append(t(110, 98, f"${d['login'].upper()}", 24, th["text"], extra='font-weight="700"'))
    label = f"SECTOR · {sector}"
    chip_w = 28 + len(label) * 8
    parts.append(f'<rect x="110" y="108" width="{chip_w}" height="22" rx="11" fill="none" stroke="{th["accent2"]}"/>'
                 + t(124, 123, label, 11, th["accent2"],
                     extra=f'textLength="{chip_w - 28}" lengthAdjust="spacingAndGlyphs"'))
    parts.append(t(110 + chip_w + 14, 124, "price = contributions in the last 30 days · candles = weeks", 12, th["muted"], SANS))
    color = th["up"] if up else th["down"]
    parts.append(t(w - 40, 104, f"${now:,.2f}", 30, th["text"], anchor="end", extra='font-weight="700"'))
    parts.append(t(w - 40, 126, f"{'▲' if up else '▼'} {abs(change):.1f}%  4 weeks", 13, color, anchor="end"))
    # chart
    cx0, cy0, cw, ch = 40, 162, w - 80, 182
    hi = max((c[2] for c in candles), default=1) or 1
    lo = min((c[3] for c in candles), default=0)
    span = max(hi - lo, 1)
    for g in range(5):
        y = cy0 + ch * g / 4
        val = hi - span * g / 4
        parts.append(f'<line x1="{cx0}" y1="{y:.1f}" x2="{cx0 + cw - 50}" y2="{y:.1f}" stroke="{th["line"]}" stroke-dasharray="3 5"/>'
                     + t(cx0 + cw, y + 4, f"{val:.0f}", 11, th["muted"], anchor="end"))
    slot = (cw - 60) / max(len(candles), 1)
    vmax = max((c[4] for c in candles), default=1) or 1

    def py(v):
        return cy0 + ch * (hi - v) / span

    for i, (o, c, hgh, low, vol) in enumerate(candles):
        x = cx0 + slot * i + slot / 2
        col = th["up"] if c >= o else th["down"]
        top_, bot = py(max(o, c)), py(min(o, c))
        delay = round(0.06 * i, 2)
        parts.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{delay}s" dur=".4s" fill="freeze"/>'
                     f'<line x1="{x:.1f}" y1="{py(hgh):.1f}" x2="{x:.1f}" y2="{py(low):.1f}" stroke="{col}" stroke-width="2"/>'
                     f'<rect x="{x - slot * 0.3:.1f}" y="{top_:.1f}" width="{slot * 0.6:.1f}" height="{max(bot - top_, 2):.1f}" rx="2" fill="{col}">'
                     f'<title>week {i + 1}: open {o} close {c} · {vol} contributions</title></rect>'
                     f'<rect x="{x - slot * 0.3:.1f}" y="{cy0 + ch + 44 - 36 * vol / vmax:.1f}" width="{slot * 0.6:.1f}" '
                     f'height="{max(36 * vol / vmax, 1):.1f}" fill="{th["muted"]}" opacity=".45"/></g>')
    parts.append(t(cx0, cy0 + ch + 62, f"volume = contributions per week · last {weeks} weeks", 11, th["muted"]))
    # holdings
    py0 = 430
    parts.append(f'<rect x="40" y="{py0 - 16}" width="540" height="136" rx="12" fill="{th["bg"]}" stroke="{th["line"]}"/>'
                 + t(58, py0 + 8, "▲ HOLDINGS", 12, th["accent"], extra='letter-spacing="2"'))
    holdings = sorted(d["repos"], key=lambda r: -r["stars"])[:4]
    for i, r in enumerate(holdings):
        y = py0 + 34 + i * 22
        tick = "".join(ch for ch in r["name"].upper() if ch.isalnum())[:8]
        parts.append(t(58, y, tick, 13, th["text"], extra='font-weight="700"')
                     + f'<circle cx="168" cy="{y - 4}" r="5" fill="{r["color"]}"/>'
                     + t(182, y, r["name"], 13, th["muted"])
                     + t(560, y, f"+{r['stars']}★", 13, th["up"], anchor="end"))
    # sector allocation
    sx = 620
    parts.append(f'<rect x="{sx}" y="{py0 - 16}" width="540" height="136" rx="12" fill="{th["bg"]}" stroke="{th["line"]}"/>'
                 + t(sx + 18, py0 + 8, "▲ SECTOR ALLOCATION", 12, th["accent"], extra='letter-spacing="2"'))
    for i, (name, share, colr) in enumerate(langs[:4]):
        y = py0 + 34 + i * 22
        bw = 260 * share / (langs[0][1] or 1)
        parts.append(f'<circle cx="{sx + 24}" cy="{y - 4}" r="5" fill="{colr}"/>' + t(sx + 36, y, name, 13, th["text"])
                     + f'<rect x="{sx + 200}" y="{y - 11}" width="260" height="9" rx="4.5" fill="{th["line"]}"/>'
                     + f'<rect x="{sx + 200}" y="{y - 11}" width="0" height="9" rx="4.5" fill="{colr}">'
                     f'<animate attributeName="width" from="0" to="{bw:.1f}" dur="1.2s" begin="{0.3 + i * 0.15}s" fill="freeze"/></rect>'
                     + t(sx + 520, y, f"{share * 100:.0f}%", 13, th["muted"], anchor="end"))
    return card(w, h, th, uid, f"Commit Exchange: {now} contributions in the last 30 days", "".join(parts))


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("login")
    ap.add_argument("out_dir")
    ap.add_argument("--theme", default=os.environ.get("CARD_THEME", themes.DEFAULT))
    ap.add_argument("--data", help="JSON file with the shape fetch() returns (local preview)")
    a = ap.parse_args()
    d = json.load(open(a.data)) if a.data else fetch(a.login, os.environ["GITHUB_TOKEN"])
    th = themes.get(a.theme)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "commit-run.svg").write_text(commit_run(d, th))
    (out / "commit-exchange.svg").write_text(commit_exchange(d, th))
    print("wrote", out / "commit-run.svg", out / "commit-exchange.svg")


if __name__ == "__main__":
    main()
