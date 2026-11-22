#!/usr/bin/env python3
"""LeetCode card (solved by difficulty, ranking, 52-week heatmap) drawn from LeetCode's public
GraphQL API, in the README's colours. Run by the profile-cards workflow; if LeetCode can't be
reached it keeps the previously published card.

    python3 scripts/leetcode_card.py hemashree_272005 dist/leetcode.svg
    python3 scripts/leetcode_card.py --demo out.svg
"""
import datetime as dt
import json
import random
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_cards as bc  # noqa: E402

C, text = bc.C, bc.text
PUBLISHED = "https://raw.githubusercontent.com/HemashreeVI/HemashreeVI/output/leetcode.svg"
Q = """query($u:String!){
  allQuestionsCount{difficulty count}
  matchedUser(username:$u){username profile{ranking}
    submitStatsGlobal{acSubmissionNum{difficulty count}}
    userCalendar{submissionCalendar}}}"""


def fetch(user):
    req = urllib.request.Request("https://leetcode.com/graphql", data=json.dumps({"query": Q, "variables": {"u": user}}).encode(),
                                 headers={"Content-Type": "application/json", "Referer": f"https://leetcode.com/u/{user}/",
                                          "User-Agent": "Mozilla/5.0 (profile-readme)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)["data"]
    m = d["matchedUser"]
    total = {x["difficulty"]: x["count"] for x in d["allQuestionsCount"]}
    solved = {x["difficulty"]: x["count"] for x in m["submitStatsGlobal"]["acSubmissionNum"]}
    cal = {dt.datetime.fromtimestamp(int(k), dt.timezone.utc).date().isoformat(): v
           for k, v in json.loads(m["userCalendar"]["submissionCalendar"] or "{}").items()}
    return {"user": m["username"], "rank": m["profile"]["ranking"], "solved": solved, "total": total, "cal": cal}


def demo():
    rnd = random.Random(3); today = dt.date.today()
    return {"user": "hemashree_272005", "rank": 812345, "solved": {"All": 120, "Easy": 64, "Medium": 50, "Hard": 6},
            "total": {"All": 3500, "Easy": 900, "Medium": 1900, "Hard": 800},
            "cal": {(today - dt.timedelta(days=i)).isoformat(): rnd.choice([0, 0, 1, 2, 4]) for i in range(365)}}


def render(d):
    W, H, u = 600, 300, "lc"
    s, t = d["solved"], d["total"]
    allc = s.get("All", 0)
    pct = allc / max(t.get("All", 1), 1)
    R, cx, cy = 52, 92, 140
    import math
    a = 2 * math.pi * pct
    arc = f'<path d="M{cx} {cy - R} A{R} {R} 0 {1 if pct > .5 else 0} 1 {cx + R * math.sin(a):.1f} {cy - R * math.cos(a):.1f}" stroke="#FFA116" stroke-width="7" fill="none" stroke-linecap="round"/>' if allc else ""
    bars = []
    for k, (name, col) in enumerate([("Easy", "#00B8A3"), ("Medium", "#FFC01E"), ("Hard", "#FF375F")]):
        y = 86 + k * 46; frac = s.get(name, 0) / max(t.get(name, 1), 1)
        bars.append(text(178, y, name, 15, C['silver'], 'sans', 'start', 'font-weight="700"')
                    + text(W - 30, y, f"{s.get(name, 0)} / {t.get(name, 0)}", 13, C['mist'], 'mono', 'end')
                    + f'<rect x="178" y="{y + 9}" width="{W - 208}" height="6" rx="3" fill="{C["line"]}"/>'
                    + f'<rect x="178" y="{y + 9}" width="{max(4, (W - 208) * frac):.0f}" height="6" rx="3" fill="{col}"/>')
    today = dt.date.today()
    start = today - dt.timedelta(days=today.weekday() + 1 + 51 * 7)
    cells = []
    for i in range(52 * 7 + today.weekday() + 2):
        day = start + dt.timedelta(days=i)
        if day > today: break
        n = d["cal"].get(day.isoformat(), 0)
        col = C['line'] if n == 0 else "#0E4429" if n < 2 else "#006D32" if n < 4 else "#26A641" if n < 7 else "#39D353"
        cells.append(f'<rect x="{30 + (i // 7) * 10.4:.1f}" y="{214 + (i % 7) * 9}" width="8" height="7" rx="1.5" fill="{col}"/>')
    body = f"""{bc.frame(W, H, u, (0.2, 0.2))}
<path d="M24 21 l10 -10 M24 21 l10 10" stroke="#FFA116" stroke-width="3.5" stroke-linecap="round" fill="none" transform="translate(4 8)"/>
<path d="M38 29 h12" stroke="{C['mist']}" stroke-width="3.5" stroke-linecap="round"/>
{text(64, 36, d["user"], 20, C['silver'], 'sans', 'start', 'font-weight="700"')}
{text(W - 30, 36, f"#{d['rank']:,}" if d.get("rank") else "", 16, C['mist'], 'mono', 'end', 'font-weight="700"')}
<circle cx="{cx}" cy="{cy}" r="{R}" stroke="{C['line']}" stroke-width="7" fill="none"/>{arc}
<text x="{cx}" y="{cy + 10}" text-anchor="middle" class="sans" font-size="30" font-weight="800" fill="{C['silver']}">{allc}</text>
{text(cx, cy + 28, "solved", 11, C['muted'], 'sans', 'middle')}
{''.join(bars)}
<path d="M24 200 H{W - 24}" stroke="{C['line']}"/>
{''.join(cells)}
{text(30, H - 14, "LeetCode · last 52 weeks", 10, C['dim'], 'mono')}"""
    desc = f"LeetCode {d['user']}: {allc} solved (Easy {s.get('Easy', 0)}, Medium {s.get('Medium', 0)}, Hard {s.get('Hard', 0)}), ranking {d.get('rank')}, with a 52-week heatmap."
    return bc.svg(W, H, u, f"LeetCode stats of {d['user']}", desc, body)


def main():
    out = Path(sys.argv[2]); out.parent.mkdir(parents=True, exist_ok=True)
    if sys.argv[1] == "--demo":
        out.write_text(render(demo())); return
    try:
        out.write_text(render(fetch(sys.argv[1]))); print("leetcode card written")
    except Exception as ex:
        print("could not fetch LeetCode stats:", ex)
        try:
            out.write_bytes(urllib.request.urlopen(PUBLISHED, timeout=30).read()); print("kept the previously published card")
        except Exception:
            out.write_text(render({"user": sys.argv[1], "rank": None, "solved": {}, "total": {}, "cal": {}}))


if __name__ == "__main__":
    main()
