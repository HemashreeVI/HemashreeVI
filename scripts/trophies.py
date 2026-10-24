#!/usr/bin/env python3
"""Draws the README's trophy card (ranked GitHub stats) as an SVG.

Runs in the snake workflow, which publishes dist/ to the `output` branch:

    GITHUB_TOKEN=... python3 scripts/trophies.py HemashreeVI dist/trophies.svg

Seven categories, each ranked C → B → A → AA → AAA → S → SS → SSS by the
thresholds below, with progress towards the next rank. If the API call fails,
the previously published card is kept. --demo renders sample data.
Standard library only.
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_cards import C, e, frame, stars, svg, text  # noqa: E402

RANKS = ["C", "B", "A", "AA", "AAA", "S", "SS", "SSS"]
# (title, key, thresholds for C..SSS, unit)
CATEGORIES = [
    ("Commits", "commits", [1, 10, 100, 200, 500, 1000, 2000, 4000], ""),
    ("Stars", "stars", [1, 10, 30, 50, 100, 200, 700, 2000], ""),
    ("Followers", "followers", [1, 2, 5, 10, 20, 50, 100, 200], ""),
    ("Repositories", "repos", [1, 5, 10, 20, 30, 35, 40, 50], ""),
    ("Pull Requests", "prs", [1, 10, 20, 50, 100, 200, 500, 1000], ""),
    ("Issues", "issues", [1, 10, 20, 50, 100, 200, 500, 1000], ""),
    ("Experience", "months", [1, 6, 12, 24, 36, 60, 120, 180], "months"),
]
RANK_COLORS = {   # cup body, highlight
    "SSS": ("#F6D365", "#FFF3C4"), "SS": ("#F6D365", "#FFF3C4"), "S": ("#F6D365", "#FFF3C4"),
    "AAA": ("#C9CCDA", "#FFFFFF"), "AA": ("#C9CCDA", "#FFFFFF"), "A": ("#C9CCDA", "#FFFFFF"),
    "B": ("#D49A6A", "#F7D2B3"), "C": ("#D49A6A", "#F7D2B3"),
}
PUBLISHED = "https://raw.githubusercontent.com/{user}/{user}/output/trophies.svg"

Q_USER = """query($login:String!){user(login:$login){
  createdAt followers{totalCount}
  pullRequests{totalCount} issues{totalCount}
  repositories(first:100, ownerAffiliations:OWNER, isFork:false, orderBy:{field:STARGAZERS,direction:DESC}){
    totalCount nodes{stargazerCount}}
  contributionsCollection{contributionYears}}}"""
Q_YEAR = """query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){
  contributionsCollection(from:$from,to:$to){totalCommitContributions restrictedContributionsCount}}}"""


def gql(query, variables, token):
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": query, "variables": variables}).encode(),
                                 headers={"Authorization": f"bearer {token}", "User-Agent": "profile-trophies"})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if out.get("errors"):
        raise RuntimeError(out["errors"])
    return out["data"]["user"]


def fetch(login, token):
    u = gql(Q_USER, {"login": login}, token)
    commits = 0
    for year in u["contributionsCollection"]["contributionYears"]:
        y = gql(Q_YEAR, {"login": login, "from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"}, token)
        cc = y["contributionsCollection"]
        commits += cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
    created = dt.datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))
    months = (dt.datetime.now(dt.timezone.utc) - created).days // 30
    return {
        "commits": commits,
        "stars": sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
        "followers": u["followers"]["totalCount"],
        "repos": u["repositories"]["totalCount"],
        "prs": u["pullRequests"]["totalCount"],
        "issues": u["issues"]["totalCount"],
        "months": months,
    }


def rank(value, thresholds):
    """(rank or None, progress 0..1 towards the next rank, next threshold or None)"""
    idx = -1
    for i, t in enumerate(thresholds):
        if value >= t:
            idx = i
    lo = thresholds[idx] if idx >= 0 else 0
    if idx == len(thresholds) - 1:
        return RANKS[idx], 1.0, None
    hi = thresholds[idx + 1]
    return (RANKS[idx] if idx >= 0 else None), (value - lo) / (hi - lo), hi


def fmt(v, unit):
    if unit == "months":
        return f"{v // 12}y {v % 12}m" if v >= 12 else f"{v}m"
    return f"{v / 1000:.1f}k" if v >= 1000 else str(v)


def cup(cx, y, rk, uid):
    """Trophy cup centred at cx with its top at y."""
    if rk is None:
        body, hi = C["line2"], C["dim"]
    else:
        body, hi = RANK_COLORS[rk]
    g = f"{uid}-{(rk or 'none').lower()}"
    plinth = f'<rect x="{cx - 22}" y="{y + 70}" width="44" height="10" rx="3" fill="{C["bg0"]}" stroke="{C["line2"]}"/>'
    return f"""
<defs><linearGradient id="{g}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{body}"/><stop offset=".45" stop-color="{hi}"/><stop offset="1" stop-color="{body}"/>
</linearGradient></defs>
<path d="M{cx - 26} {y + 6}h52v8c0 18-10 30-26 32-16-2-26-14-26-32z" fill="url(#{g})"/>
<path d="M{cx - 26} {y + 10}h-10c0 14 8 20 14 20M{cx + 26} {y + 10}h10c0 14-8 20-14 20" fill="none" stroke="{body}" stroke-width="4" stroke-linecap="round"/>
<rect x="{cx - 4}" y="{y + 46}" width="8" height="12" fill="{body}"/>
<rect x="{cx - 16}" y="{y + 58}" width="32" height="10" rx="3" fill="url(#{g})"/>
{plinth}
<rect x="{cx - 26}" y="{y + 2}" width="52" height="6" rx="3" fill="{hi}" opacity=".9"/>"""


def render(stats, user):
    w, h = 1200, 300
    u = "tro"
    n = len(CATEGORIES)
    slot = (w - 80) / n
    parts = [frame(w, h, u, glow=(0.65, 0.25)), stars(w, h, 20, seed=23)]
    parts.append('<text x="48" y="54" class="kick">TROPHIES</text>')
    earned = 0
    for i, (title, key, th, unit) in enumerate(CATEGORIES):
        v = stats[key]
        rk, prog, nxt = rank(v, th)
        earned += rk is not None
        cx = round(40 + slot * (i + 0.5))
        y = 92
        colour = RANK_COLORS[rk][0] if rk else C["dim"]
        parts.append(f'<g class="float" style="animation-delay:-{i * 0.6:.1f}s"><title>{e(title)}: {e(fmt(v, unit))}'
                     f'{f", next rank at {fmt(nxt, unit)}" if nxt else ", max rank"}</title>{cup(cx, y, rk, u)}</g>')
        parts.append(f'<text x="{cx}" y="{y + 36}" text-anchor="middle" class="serif" font-size="{14 if rk and len(rk) > 2 else 17 if rk and len(rk) > 1 else 20}" '
                     f'font-weight="700" fill="{C["bg0"]}">{e(rk or "?")}</text>')
        parts.append(text(cx, y + 108, title, 14, C["silver"], "sans", "middle"))
        parts.append(text(cx, y + 130, fmt(v, unit), 13, colour, "mono", "middle"))
        bw = 96
        parts.append(f'<rect x="{cx - bw / 2:.0f}" y="{y + 144}" width="{bw}" height="5" rx="2.5" fill="{C["line"]}"/>'
                     f'<rect x="{cx - bw / 2:.0f}" y="{y + 144}" width="{max(3, bw * prog):.0f}" height="5" rx="2.5" fill="{colour}"/>')
        nxt_label = f"next: {fmt(nxt, unit)}" if nxt else "max rank"
        parts.append(text(cx, y + 166, nxt_label, 11, C["muted"], "mono", "middle"))
    parts.append(text(w - 48, 54, f"{earned}/{n} unlocked", 13, C["muted"], "mono", "end"))
    desc = "; ".join(f"{t}: {fmt(stats[k], un)} ({rank(stats[k], th)[0] or 'locked'})" for t, k, th, un in CATEGORIES)
    return svg(w, h, u, f"GitHub trophies of {user}", desc, "".join(parts))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("user")
    ap.add_argument("out", type=Path)
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args(argv)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    if args.demo:
        stats = {"commits": 742, "stars": 12, "followers": 9, "repos": 24, "prs": 7, "issues": 0, "months": 30}
    else:
        try:
            stats = fetch(args.user, os.environ["GITHUB_TOKEN"])
        except Exception as ex:
            print(f"could not fetch stats: {ex}")
            try:
                args.out.write_bytes(urllib.request.urlopen(PUBLISHED.format(user=args.user), timeout=30).read())
                print("kept the previously published card")
            except Exception:
                print("no previous card; not writing one")
            return 0
    args.out.write_text(render(stats, args.user), encoding="utf-8")
    print("trophies:", ", ".join(f"{k}={v}" for k, v in stats.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
