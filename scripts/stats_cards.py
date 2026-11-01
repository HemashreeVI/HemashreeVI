#!/usr/bin/env python3
"""Draws the README's GitHub stats, top languages and streak cards as SVGs.

Replaces github-readme-stats.vercel.app and streak-stats.demolab.com, whose
public instances are often rate-limited or down and then show a broken image.
Runs in the profile-cards workflow, which publishes dist/ to the `output` branch:

    GITHUB_TOKEN=... python3 scripts/stats_cards.py HemashreeVI dist/

Writes stats.svg, top-langs.svg and streak.svg. If the API call fails, the
previously published cards are kept. --demo renders sample data.
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

CARDS = ("stats.svg", "top-langs.svg", "streak.svg")
PUBLISHED = "https://raw.githubusercontent.com/{user}/{user}/output/{name}"
TOP_LANGS = 6

Q_USER = """query($login:String!){user(login:$login){
  createdAt
  pullRequests{totalCount} issues{totalCount}
  repositoriesContributedTo(contributionTypes:[COMMIT,PULL_REQUEST,ISSUE,REPOSITORY]){totalCount}
  repositories(first:100, ownerAffiliations:OWNER, isFork:false){
    totalCount nodes{stargazerCount languages(first:10, orderBy:{field:SIZE,direction:DESC}){
      edges{size node{name color}}}}}
  contributionsCollection{contributionYears}}}"""
Q_YEAR = """query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){
  contributionsCollection(from:$from,to:$to){totalCommitContributions restrictedContributionsCount
    contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""


def gql(query, variables, token):
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": query, "variables": variables}).encode(),
                                 headers={"Authorization": f"bearer {token}", "User-Agent": "profile-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if out.get("errors"):
        raise RuntimeError(out["errors"])
    return out["data"]["user"]


def fetch(login, token):
    u = gql(Q_USER, {"login": login}, token)
    today = dt.datetime.now(dt.timezone.utc).date()
    commits_year, commits_all, days = 0, 0, {}
    for year in sorted(u["contributionsCollection"]["contributionYears"]):
        y = gql(Q_YEAR, {"login": login, "from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"}, token)
        cc = y["contributionsCollection"]
        c = cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
        commits_all += c
        if year == today.year:
            commits_year = c
        for w in cc["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
    langs = {}
    for repo in u["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            size, color = langs.get(name, (0, edge["node"]["color"] or C["lav"]))
            langs[name] = (size + edge["size"], color)
    return {
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "commits_year": commits_year,
        "commits_all": commits_all,
        "prs": u["pullRequests"]["totalCount"],
        "issues": u["issues"]["totalCount"],
        "contributed": u["repositoriesContributedTo"]["totalCount"],
        "repos": u["repositories"]["totalCount"],
        "langs": langs,
        "days": sorted(days.items()),
        "today": today.isoformat(),
    }


def demo():
    today = dt.date.today()
    days = [((today - dt.timedelta(days=i)).isoformat(), (i * 7) % 5) for i in range(400)][::-1]
    return {"stars": 12, "commits_year": 640, "commits_all": 742, "prs": 7, "issues": 2, "contributed": 4,
            "repos": 24, "days": days, "today": today.isoformat(),
            "langs": {"Python": (900000, "#3572A5"), "JavaScript": (400000, "#f1e05a"), "Java": (200000, "#b07219"),
                      "HTML": (150000, "#e34c26"), "C++": (80000, "#f34b7d"), "CSS": (60000, "#563d7c"),
                      "Shell": (5000, "#89e051")}}


def fmt(v):
    return f"{v / 1000:.1f}k" if v >= 1000 else str(v)


def streaks(days, today):
    """(total contributions, current streak, its start, longest streak, its start, its end)"""
    total = sum(c for _, c in days)
    longest = run = 0
    l_start = l_end = r_start = None
    for date, c in days:
        if date > today:
            break
        if c > 0:
            if run == 0:
                r_start = date
            run += 1
            if run > longest:
                longest, l_start, l_end = run, r_start, date
        else:
            run = 0
    # The current streak survives a quiet today: count back from yesterday if today is 0.
    past = [(d, c) for d, c in days if d <= today]
    if past and past[-1][1] == 0:
        past = past[:-1]
    current, c_start = 0, None
    for date, c in reversed(past):
        if c == 0:
            break
        current, c_start = current + 1, date
    return total, current, c_start, longest, l_start, l_end


def short(date):
    return dt.date.fromisoformat(date).strftime("%b %-d, %Y") if date else "—"


def render_stats(s, user):
    w, h, u = 600, 300, "sta"
    rows = [
        ("★", "Total stars earned", s["stars"]),
        ("◆", f"Commits ({dt.date.fromisoformat(s['today']).year})", s["commits_year"]),
        ("◇", "Commits (all time)", s["commits_all"]),
        ("⇄", "Pull requests", s["prs"]),
        ("!", "Issues", s["issues"]),
        ("⌂", "Contributed to", s["contributed"]),
    ]
    parts = [frame(w, h, u, glow=(0.8, 0.2)), stars(w, h, 10, seed=31)]
    parts.append('<text x="36" y="50" class="kick">GITHUB STATS</text>')
    for i, (icon, label, v) in enumerate(rows):
        y = 92 + i * 33
        parts.append(f'<g class="float" style="animation-delay:-{i * 0.4:.1f}s">'
                     + text(40, y, icon, 16, C["lav"], "mono", "middle")
                     + text(62, y, label, 15, C["mist"], "sans")
                     + text(w - 40, y, fmt(v), 16, C["silver"], "mono", "end", 'font-weight="700"') + "</g>")
        parts.append(f'<line x1="62" y1="{y + 12}" x2="{w - 40}" y2="{y + 12}" stroke="{C["line"]}"/>')
    desc = "; ".join(f"{label}: {v}" for _, label, v in rows)
    return svg(w, h, u, f"GitHub stats of {user}", desc, "".join(parts))


def render_langs(s, user):
    w, h, u = 600, 300, "lng"
    langs = sorted(s["langs"].items(), key=lambda kv: -kv[1][0])
    total = sum(size for size, _ in s["langs"].values()) or 1
    top = langs[:TOP_LANGS]
    parts = [frame(w, h, u, glow=(0.2, 0.2)), stars(w, h, 10, seed=37)]
    parts.append('<text x="36" y="50" class="kick">MOST USED LANGUAGES</text>')
    # Stacked bar
    x, bw = 40, w - 80
    parts.append(f'<clipPath id="{u}-bar"><rect x="40" y="76" width="{bw}" height="12" rx="6"/></clipPath><g clip-path="url(#{u}-bar)">')
    parts.append(f'<rect x="40" y="76" width="{bw}" height="12" fill="{C["line"]}"/>')
    for name, (size, color) in top:
        seg = bw * size / total
        parts.append(f'<rect x="{x:.1f}" y="76" width="{seg + 0.5:.1f}" height="12" fill="{color}"/>')
        x += seg
    parts.append("</g>")
    for i, (name, (size, color)) in enumerate(top):
        col, row = i % 2, i // 2
        cx, cy = 48 + col * 270, 130 + row * 52
        pct = 100 * size / total
        parts.append(f'<circle cx="{cx}" cy="{cy - 5}" r="6" fill="{color}"/>')
        parts.append(text(cx + 16, cy, name, 15, C["silver"], "sans"))
        parts.append(text(cx + 220, cy, f"{pct:.1f}%", 14, C["muted"], "mono", "end"))
    if not top:
        parts.append(text(w / 2, 160, "no languages yet", 14, C["muted"], "mono", "middle"))
    desc = "; ".join(f"{n}: {100 * sz / total:.1f}%" for n, (sz, _) in top) or "No languages"
    return svg(w, h, u, f"Most used languages of {user}", desc, "".join(parts))


def render_streak(s, user):
    w, h, u = 1200, 240, "stk"
    total, cur, c_start, longest, l_start, l_end = streaks(s["days"], s["today"])
    first = s["days"][0][0] if s["days"] else None
    cols = [
        (fmt(total), "Total contributions", f"{short(first)} – present", C["silver"]),
        (str(cur), "Current streak", f"{short(c_start)} – {short(s['today'])}" if cur else "start one today", C["lilac"]),
        (str(longest), "Longest streak", f"{short(l_start)} – {short(l_end)}" if longest else "—", C["silver"]),
    ]
    parts = [frame(w, h, u, glow=(0.5, 0.3)), stars(w, h, 14, seed=41)]
    parts.append('<text x="48" y="50" class="kick">CONTRIBUTION STREAK</text>')
    slot = (w - 96) / 3
    for i, (num, label, sub, colour) in enumerate(cols):
        cx = round(48 + slot * (i + 0.5))
        if i:
            parts.append(f'<line x1="{48 + slot * i:.0f}" y1="84" x2="{48 + slot * i:.0f}" y2="206" stroke="{C["line2"]}"/>')
        if i == 1:
            parts.append(f'<circle cx="{cx}" cy="128" r="46" fill="none" stroke="{C["lav"]}" stroke-width="5"/>'
                         f'<path d="M{cx} 70c8 8 10 14 6 20 6-2 8-6 8-10 4 6 2 14-6 18-4 2-12 2-16-2-4-6 0-14 8-26z" '
                         f'fill="{C["rose"]}" class="float"/>')
            parts.append(text(cx, 140, num, 34, colour, "serif", "middle", 'font-weight="700"'))
            parts.append(text(cx, 198, label, 15, C["lilac"], "sans", "middle", 'font-weight="700"'))
            parts.append(text(cx, 220, sub, 12, C["muted"], "mono", "middle"))
        else:
            parts.append(text(cx, 140, num, 34, colour, "serif", "middle", 'font-weight="700"'))
            parts.append(text(cx, 176, label, 15, C["mist"], "sans", "middle"))
            parts.append(text(cx, 200, sub, 12, C["muted"], "mono", "middle"))
    desc = "; ".join(f"{label}: {num} ({sub})" for num, label, sub, _ in cols)
    return svg(w, h, u, f"Contribution streak of {user}", desc, "".join(parts))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("user")
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args(argv)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.demo:
        s = demo()
    else:
        try:
            s = fetch(args.user, os.environ["GITHUB_TOKEN"])
        except Exception as ex:
            print(f"could not fetch stats: {ex}")
            for name in CARDS:
                try:
                    data = urllib.request.urlopen(PUBLISHED.format(user=args.user, name=name), timeout=30).read()
                    (args.out_dir / name).write_bytes(data)
                    print(f"kept the previously published {name}")
                except Exception:
                    print(f"no previous {name}; not writing one")
            return 0
    for name, fn in zip(CARDS, (render_stats, render_langs, render_streak)):
        (args.out_dir / name).write_text(fn(s, args.user), encoding="utf-8")
    print("stats:", ", ".join(f"{k}={v}" for k, v in s.items() if k not in ("langs", "days")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
