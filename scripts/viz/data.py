"""Activity data for the Contribution City and Metro Map cards.

In GitHub Actions it reads the official contribution calendar and per-repository
commits from the GraphQL API (GITHUB_TOKEN). For a local preview it can read a
TSV of "repo<TAB>YYYY-MM-DD" lines instead.
"""
import datetime as dt
import json
import os
import urllib.request
from collections import Counter, defaultdict

QUERY = """query($login:String!){ user(login:$login){
  contributionsCollection {
    contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    commitContributionsByRepository(maxRepositories: 25) {
      repository { name isFork primaryLanguage { name color } }
      contributions(first: 100) { nodes { occurredAt commitCount } }
    }
  } } }"""

# a few linguist colours, for the TSV preview only (the API gives the real ones)
LANG = {"Python": "#3572A5", "Java": "#b07219", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "HTML": "#e34c26", "CSS": "#563d7c",
        "Shell": "#89e051", "Rust": "#dea584", "Jupyter Notebook": "#DA5B0B", "PowerShell": "#012456", "C++": "#f34b7d", "Go": "#00ADD8"}


def from_api(user, token):
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
                                 headers={"Authorization": f"bearer {token}", "User-Agent": "profile-viz"})
    with urllib.request.urlopen(req, timeout=60) as r:
        c = json.load(r)["data"]["user"]["contributionsCollection"]
    days = [(d["date"], d["contributionCount"]) for w in c["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    repos = []
    for item in c["commitContributionsByRepository"]:
        repo = item["repository"]
        if repo["isFork"]:
            continue
        per_day = Counter()
        for n in item["contributions"]["nodes"]:
            per_day[n["occurredAt"][:10]] += n["commitCount"]
        repos.append({"name": repo["name"], "color": (repo["primaryLanguage"] or {}).get("color") or "#8b949e",
                      "language": (repo["primaryLanguage"] or {}).get("name") or "", "days": dict(per_day)})
    return {"total": c["contributionCalendar"]["totalContributions"], "days": days, "repos": repos}


def from_tsv(path, languages=None):
    rows = [l.rstrip("\n").split("\t") for l in open(path) if "\t" in l]
    by_day = Counter(d for _, d in rows)
    today = dt.date.today()
    days = [((today - dt.timedelta(days=i)).isoformat(), 0) for i in range(370, -1, -1)]
    days = [(d, by_day.get(d, 0)) for d, _ in days]
    per = defaultdict(Counter)
    for repo, d in rows:
        per[repo][d] += 1
    languages = languages or {}
    repos = [{"name": r, "language": languages.get(r, ""), "color": LANG.get(languages.get(r, ""), "#8b949e"), "days": dict(c)} for r, c in per.items()]
    return {"total": len(rows), "days": days, "repos": repos}


def load(user):
    tsv = os.environ.get("VIZ_TSV")
    if tsv:
        langs = json.loads(open(os.environ["VIZ_LANGS"]).read()) if os.environ.get("VIZ_LANGS") else {}
        return from_tsv(tsv, langs)
    return from_api(user, os.environ["GITHUB_TOKEN"])
