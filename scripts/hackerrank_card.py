#!/usr/bin/env python3
"""HackerRank card (badges with their stars, problems solved) from HackerRank's public profile API,
in the README's colours, sized to sit next to the LeetCode card. Run by the profile-cards workflow;
if HackerRank can't be reached it keeps the previously published card.

    python3 scripts/hackerrank_card.py shreejith2005 dist/hackerrank.svg
    python3 scripts/hackerrank_card.py --demo out.svg
"""
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_cards as bc  # noqa: E402

C, text = bc.C, bc.text
PUBLISHED = "https://raw.githubusercontent.com/HemashreeVI/HemashreeVI/output/hackerrank.svg"
HDR = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36", "Accept": "application/json"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=30) as r:
        return json.load(r)


def fetch(user):
    badges = get(f"https://www.hackerrank.com/rest/hackers/{user}/badges")["models"]
    print("badges sample:", json.dumps(badges[:2])[:600])
    try:
        prof = get(f"https://www.hackerrank.com/rest/contests/master/hackers/{user}/profile")["model"]
    except Exception as ex:
        print("profile:", ex); prof = {}
    out = []
    for b in badges:
        name = b.get("badge_name") or b.get("name") or "?"
        stars = int(b.get("stars") or 0)
        solved = int(b.get("solved") or 0)
        if stars or solved:
            out.append({"name": name, "stars": stars, "solved": solved, "total": int(b.get("total_challenges") or 0),
                        "points": float(b.get("current_points") or 0), "next": float(b.get("progress_to_next_star") or 0),
                        "rank": b.get("hacker_rank")})
    out.sort(key=lambda b: (-b["stars"], -b["solved"]))
    return {"user": prof.get("username") or user, "badges": out}


def demo():
    return {"user": "shreejith2005", "badges": [{"name": "Java", "stars": 0, "solved": 2, "total": 64, "points": 8, "next": .32, "rank": 2339568}, {"name": "Problem Solving", "stars": 3, "solved": 25, "total": 560},
            {"name": "Python", "stars": 3, "solved": 20, "total": 115}, {"name": "SQL", "stars": 2, "solved": 18, "total": 58},
            {"name": "C++", "stars": 1, "solved": 5, "total": 40}, {"name": "30 Days of Code", "stars": 1, "solved": 4, "total": 30}]}


def star(x, y, filled):
    pts = "0,-6 1.8,-1.9 6,-1.9 2.6,0.8 3.8,5 0,2.5 -3.8,5 -2.6,0.8 -6,-1.9 -1.8,-1.9"
    return f'<polygon transform="translate({x} {y})" points="{pts}" fill="{"#FFC01E" if filled else C["line"]}"/>'


def render(d):
    W, H, u = 600, 300, "hr"
    bs = d["badges"][:6]
    solved = sum(b["solved"] for b in d["badges"])
    stars = sum(b["stars"] for b in d["badges"])
    rows = []
    n = len(bs)
    rh = 52 if n <= 3 else 40          # fewer badges: taller, fuller rows
    for k, b in enumerate(bs):
        y = 70 + k * (rh + 10)
        frac = min(1, b.get("next", 0))
        rows.append(f'<rect x="30" y="{y}" width="{W - 60}" height="{rh}" rx="10" fill="{C["panel"]}" stroke="{C["line2"]}"/>'
                    + text(46, y + 22, b["name"], 15, C['silver'], 'sans', 'start', 'font-weight="700"')
                    + text(46, y + 40, f'{b["solved"]} / {b["total"]} solved · {b.get("points", 0):g} pts' + (f' · rank #{b["rank"]:,}' if b.get("rank") else ""), 10.5, C['muted'], 'mono')
                    + "".join(star(W - 140 + i * 18, y + 18, i < b["stars"]) for i in range(5))
                    + f'<rect x="{W - 148}" y="{y + 32}" width="98" height="5" rx="2.5" fill="{C["line"]}"/>'
                    + f'<rect x="{W - 148}" y="{y + 32}" width="{max(3, 98 * frac):.0f}" height="5" rx="2.5" fill="#00EA64"/>'
                    + text(W - 46, y + 37, f"{round(frac * 100)}%", 9, C['dim'], 'mono', 'start'))
    if n and n <= 3:
        # what the badges add up to, so the card doesn't look empty
        tot_solved = sum(b["solved"] for b in bs); tot_ch = sum(b["total"] for b in bs) or 1
        y = 70 + n * (rh + 10) + 6
        rows.append(text(30, y + 14, "Progress across my badges", 11, C['lav'], 'mono', 'start', 'letter-spacing="1"')
                    + f'<rect x="30" y="{y + 24}" width="{W - 60}" height="8" rx="4" fill="{C["line"]}"/>'
                    + f'<rect x="30" y="{y + 24}" width="{max(6, (W - 60) * tot_solved / tot_ch):.0f}" height="8" rx="4" fill="#00EA64"/>'
                    + text(W - 30, y + 14, f"{tot_solved} of {tot_ch} challenges", 11, C['mist'], 'mono', 'end'))
    if not bs:
        rows.append(text(W / 2, 160, "No badges yet", 14, C['muted'], 'sans', 'middle'))
    body = f"""{bc.frame(W, H, u, (0.8, 0.2))}
<g transform="translate(30 14)"><path d="M11 0 L22 6.4 V19.2 L11 25.6 L0 19.2 V6.4 Z" fill="#00EA64"/>
<path d="M7 7 V19 M15 7 V19 M7 13 H15" stroke="#0E141E" stroke-width="2.6" stroke-linecap="round"/></g>
{text(64, 36, d["user"], 20, C['silver'], 'sans', 'start', 'font-weight="700"')}
{text(W - 30, 36, f"★ {stars}  ·  {solved} solved", 14, C['mist'], 'mono', 'end', 'font-weight="700"')}
{''.join(rows)}
{text(30, H - 14, "HackerRank · badges", 10, C['dim'], 'mono')}"""
    desc = f"HackerRank {d['user']}: {solved} problems solved, {stars} badge stars. " + "; ".join(f"{b['name']} {b['stars']} stars" for b in bs)
    return bc.svg(W, H, u, f"HackerRank badges of {d['user']}", desc, body)


def main():
    out = Path(sys.argv[2]); out.parent.mkdir(parents=True, exist_ok=True)
    if sys.argv[1] == "--demo":
        out.write_text(render(demo())); return
    try:
        out.write_text(render(fetch(sys.argv[1]))); print("hackerrank card written")
    except Exception as ex:
        print("could not fetch HackerRank badges:", ex)
        try:
            out.write_bytes(urllib.request.urlopen(PUBLISHED, timeout=30).read()); print("kept the previously published card")
        except Exception:
            out.write_text(render({"user": sys.argv[1], "badges": []}))


if __name__ == "__main__":
    main()
