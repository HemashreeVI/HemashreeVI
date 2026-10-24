#!/usr/bin/env python3
"""Draws the README's GitHub achievements card as an SVG.

GitHub has no API for achievements, so this reads the public achievements
page, downloads each badge image and embeds it (images referenced from an
SVG shown in a README are not loaded, so they must be inlined).

Runs in the snake workflow, which publishes dist/ to the `output` branch:

    python3 scripts/achievements.py HemashreeVI dist/achievements.svg

If no achievements can be read (page layout changed, network error), the
previously published card is kept so the README never shows a broken image.
Options: --html FILE parses a saved page; --demo renders sample data.
Standard library only.
"""
import argparse
import base64
import html
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_cards import C, e, frame, stars, svg, text  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (profile-readme achievements card)"}
PUBLISHED = "https://raw.githubusercontent.com/{user}/{user}/output/achievements.svg"

DESCRIPTIONS = {
    "Pull Shark": "Opened pull requests that have been merged",
    "YOLO": "Merged a pull request without code review",
    "Quickdraw": "Closed an issue or pull request within 5 minutes of opening",
    "Pair Extraordinaire": "Coauthored commits on merged pull requests",
    "Starstruck": "Created a repository that has many stars",
    "Galaxy Brain": "Answered discussions",
    "Open Sourcerer": "Had pull requests merged in multiple public repositories",
    "Public Sponsor": "Sponsored open source work via GitHub Sponsors",
    "Heart On Your Sleeve": "Reacted to something on GitHub",
    "Arctic Code Vault Contributor": "Contributed code to the 2020 GitHub Archive Program",
}
TIER_COLORS = {2: "#D49A6A", 3: "#C9CCDA", 4: "#E8C76B"}   # bronze, silver, gold

IMG_RE = re.compile(r'<img\b[^>]*\balt="Achievement:\s*([^"]+)"[^>]*>', re.I)
DATA_SRC_RE = re.compile(r'\bdata-src="([^"]+)"', re.I)   # lazy-loaded images keep the real URL here
SRC_RE = re.compile(r'\bsrc="([^"]+)"', re.I)
TIER_RE = re.compile(r'achievement-tier-label[^>]*>\s*x(\d+)\s*<', re.I)


def get(url, binary=False):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "replace")


def parse(page):
    """Returns [(name, image_url, tier)] in page order, one per achievement."""
    found = {}
    matches = list(IMG_RE.finditer(page))
    for i, m in enumerate(matches):
        name = html.unescape(m.group(1)).strip()
        src = DATA_SRC_RE.search(m.group(0)) or SRC_RE.search(m.group(0))
        end = matches[i + 1].start() if i + 1 < len(matches) else m.end() + 1500
        tier = TIER_RE.search(page, m.end(), min(end, m.end() + 1500))
        tier = int(tier.group(1)) if tier else 1
        if not src:
            continue
        url = html.unescape(src.group(1))
        if url.startswith("/"):
            url = "https://github.com" + url
        if name not in found or tier > found[name][1]:
            found[name] = (url, tier)
    return [(n, u, t) for n, (u, t) in found.items()]


def data_uri(png):
    kind = "image/png" if png[:4] == b"\x89PNG" else "image/svg+xml" if png.lstrip()[:1] == b"<" else "image/png"
    return f"data:{kind};base64,{base64.b64encode(png).decode()}"


def render(items, user):
    """items: [(name, data_uri_or_None, tier)]"""
    per_row = 8
    rows = (len(items) + per_row - 1) // per_row
    w, h = 1200, 110 + rows * 178
    u = "ach"
    parts = [frame(w, h, u, glow=(0.3, 0.2)), stars(w, h, 22, seed=11)]
    parts.append(f'<text x="48" y="54" class="kick">ACHIEVEMENTS</text>')
    parts.append(text(48, 82, f"{len(items)} badges earned on GitHub", 15, C["muted"], "sans"))
    for r in range(rows):
        row = items[r * per_row:(r + 1) * per_row]
        gap = 136
        x0 = w / 2 - (len(row) - 1) * gap / 2
        y = 118 + r * 178
        for i, (name, img, tier) in enumerate(row):
            cx = x0 + i * gap
            delay = (r * per_row + i) * 0.35
            badge = (f'<image href="{img}" x="{cx - 46:.0f}" y="{y}" width="92" height="92"/>' if img else
                     f'<circle cx="{cx:.0f}" cy="{y + 46}" r="40" fill="{C["panel"]}" stroke="{C["line2"]}"/>'
                     f'<text x="{cx:.0f}" y="{y + 56}" text-anchor="middle" class="serif" font-size="30" fill="{C["lav"]}">{e(name[:1])}</text>')
            pill = ""
            if tier > 1:
                col = TIER_COLORS.get(tier, TIER_COLORS[4])
                pill = (f'<rect x="{cx + 18:.0f}" y="{y + 66}" width="34" height="22" rx="11" fill="{C["bg0"]}" stroke="{col}"/>'
                        f'<text x="{cx + 35:.0f}" y="{y + 81}" text-anchor="middle" class="mono" font-size="12" '
                        f'font-weight="700" fill="{col}">x{tier}</text>')
            desc = DESCRIPTIONS.get(name, "GitHub achievement")
            parts.append(
                f'<g class="float" style="animation-delay:-{delay:.2f}s"><title>{e(name)}: {e(desc)}</title>'
                f'<ellipse cx="{cx:.0f}" cy="{y + 98}" rx="34" ry="5" fill="{C["bg0"]}" opacity=".6"/>'
                f'{badge}{pill}</g>'
                + text(round(cx), y + 128, name, 13, C["silver"], "sans", "middle"))
    desc = ", ".join(f"{n}{f' x{t}' if t > 1 else ''}" for n, _, t in items)
    return svg(w, h, u, f"GitHub achievements of {user}", desc, "".join(parts))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("user")
    ap.add_argument("out", type=Path)
    ap.add_argument("--html", type=Path, help="parse a saved achievements page instead of fetching it")
    ap.add_argument("--demo", action="store_true", help="render sample data without network access")
    args = ap.parse_args(argv)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    if args.demo:
        items = [("Pull Shark", None, 2), ("YOLO", None, 1), ("Quickdraw", None, 1), ("Pair Extraordinaire", None, 3)]
        args.out.write_text(render(items, args.user), encoding="utf-8")
        print(f"demo card written to {args.out}")
        return 0

    try:
        page = args.html.read_text(encoding="utf-8") if args.html else get(f"https://github.com/{args.user}?tab=achievements")
        parsed = parse(page)
    except Exception as ex:  # network or parsing problem
        print(f"could not read achievements: {ex}")
        parsed = []

    items = []
    for name, url, tier in parsed:
        try:
            items.append((name, data_uri(get(url, binary=True)), tier))
        except Exception as ex:
            print(f"  {name}: image download failed ({ex}); drawing a placeholder")
            items.append((name, None, tier))

    if items:
        args.out.write_text(render(items, args.user), encoding="utf-8")
        print(f"{len(items)} achievements: " + ", ".join(f"{n} x{t}" for n, _, t in items))
        return 0

    try:   # keep the card that is already published
        args.out.write_bytes(get(PUBLISHED.format(user=args.user), binary=True))
        print("no achievements parsed; kept the previously published card")
    except Exception:
        print("no achievements parsed and no previous card; not writing one")
    return 0


if __name__ == "__main__":
    sys.exit(main())
