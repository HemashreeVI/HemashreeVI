#!/usr/bin/env python3
"""Rebuilds the About card (terminal + ID card) with real GitHub numbers:
total stars and public repos, contributions in the last year, achievements,
top languages and the most-starred repos. Run by the profile-cards workflow.

    GITHUB_TOKEN=... python3 scripts/about_live.py HemashreeVI dist/about.svg [dist/achievements.svg]
"""
import datetime as dt
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_cards as bc  # noqa: E402
import os  # noqa: E402

Q = """query($login:String!){user(login:$login){
  repositories(first:100, ownerAffiliations:OWNER, isFork:false, privacy:PUBLIC, orderBy:{field:STARGAZERS,direction:DESC}){
    totalCount nodes{name stargazerCount languages(first:10, orderBy:{field:SIZE,direction:DESC}){edges{size node{name color}}}}}
  contributionsCollection{contributionCalendar{totalContributions}}}}"""


def gql(login, token):
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": Q, "variables": {"login": login}}).encode(),
                                 headers={"Authorization": f"bearer {token}", "User-Agent": "profile-about"})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if out.get("errors"):
        raise RuntimeError(out["errors"])
    return out["data"]["user"]


def live(login, token, achievements_svg=None):
    u = gql(login, token)
    repos = u["repositories"]["nodes"]
    langs = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            size, col = langs.get(n, (0, e["node"]["color"] or "#8B949E"))
            langs[n] = (size + e["size"], col)
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])
    shown = [[n, size, col] for n, (size, col) in top[:4]]
    rest = sum(size for _, (size, _) in top[4:])
    if rest:
        shown.append(["Other", rest, "#8B949E"])
    achievements = bc.LIVE_DEFAULT["achievements"]
    if achievements_svg and Path(achievements_svg).exists():
        n = len(re.findall(r"data:image/png;base64", Path(achievements_svg).read_text()))
        achievements = n or achievements
    return {
        "stars": sum(r["stargazerCount"] for r in repos),
        "repos": u["repositories"]["totalCount"],
        "contributions": u["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "achievements": achievements,
        "langs": shown or bc.LIVE_DEFAULT["langs"],
        "top_repos": [[r["name"], r["stargazerCount"]] for r in repos[:5]],
    }


def main():
    login, out = sys.argv[1], Path(sys.argv[2])
    try:
        data = live(login, os.environ["GITHUB_TOKEN"], sys.argv[3] if len(sys.argv) > 3 else None)
    except Exception as ex:   # keep the card building even if GitHub is unreachable
        print("could not fetch live stats, using the last known ones:", ex)
        data = None
    out.parent.mkdir(parents=True, exist_ok=True)
    bc.OUT = out.parent
    bc.build_about(data)
    produced = out.parent / "about.svg"
    if produced != out:
        produced.rename(out)
    print("about card:", json.dumps({k: v for k, v in (data or {}).items() if k != "langs"}))


if __name__ == "__main__":
    main()
