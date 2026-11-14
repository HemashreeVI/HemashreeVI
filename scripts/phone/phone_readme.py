#!/usr/bin/env python3
"""Prints the README HTML for the phone from assets/phone/manifest.json.

Every slice is an <img align="top"> (no gap under it) inside its own link,
written with no whitespace in between so the slices join seamlessly.

Next to it floats a second phone (build_video_phone.py) playing a screen
recording of the portfolio and GitLoom.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
M = json.loads((ROOT / "assets/phone/manifest.json").read_text())
TOTAL = 320   # phone width in the README: fits a phone-width GitHub page (~340px)
SCALE = TOTAL / M["top"]["w"]

GH = "https://github.com/HemashreeVI/"
LINKS = {
    "seatlock": (GH + "SeatLock", "SeatLock: zero double-bookings"),
    "rootlens": (GH + "rootlens", "RootLens: incident response"),
    "triageiq": (GH + "TriageIQ", "TriageIQ: on-device AI inbox"),
    "gitloom": ("https://hemashreevi.github.io/GitLoom/", "GitLoom: GitHub to portfolio"),
    "walker": (GH + "smart_walker", "Smart Walker (patent)"),
    "rover": (GH + "disaster-response-rover-nodered", "Hazard-Detection Rover (patent)"),
    "dental": (GH + "AI_Malocclusion_Detection", "Dental X-ray AI"),
    "bytedecoded": ("https://www.youtube.com/@shreejith-l7o", "Byte Decoded on YouTube"),
    "leetcode": ("https://leetcode.com/u/hemashree_272005/", "LeetCode"),
    "chesscom": ("https://www.chess.com/member/hemashreevi", "Play me on Chess.com"),
    "portfolio": ("https://hemashreevi.github.io", "My portfolio"),
    "games": ("https://hemashreevi.github.io", "Mini-games on my portfolio"),
    "gmail": ("mailto:shreejith2005@gmail.com", "Email me"),
    "linkedin": ("https://www.linkedin.com/in/hema-shree272005", "LinkedIn"),
    "instagram": ("https://www.instagram.com/hemashree_2_7/", "Instagram"),
    "github": ("https://github.com/HemashreeVI?tab=repositories", "All my repositories"),
}


def widths(items):
    ws = [round(i["w"] * SCALE) for i in items]
    ws[-1] += TOTAL - sum(ws)          # absorb rounding so every row is exactly TOTAL wide
    return ws


def img(s, w, alt):
    # explicit integer height: slices in a row share it exactly, so no hairline seams
    h = round(s["h"] * SCALE)
    return f'<img src="./assets/phone/{s["file"]}" width="{w}" height="{h}" align="top" alt="{alt}">'


def full(s, alt, link=None):
    tag = img(s, TOTAL, alt)
    return f'<a href="{link}">{tag}</a>' if link else tag


def row(items):
    out = []
    for s, w in zip(items, widths(items)):
        href, title = LINKS[s["id"]]
        out.append(f'<a href="{href}" title="{title}">{img(s, w, title)}</a>')
    return "".join(out)


V = json.loads((ROOT / "assets/phone/video.json").read_text())
import os
# srcset needs absolute URLs; PHONE_BRANCH=phone-demo previews from a branch
RAW = f"https://raw.githubusercontent.com/HemashreeVI/HemashreeVI/{os.environ.get('PHONE_BRANCH', 'main')}/assets/phone/"
WIDE = "(min-width: 1200px)"
H_PHONE = round(M["top"]["h"] * SCALE) + sum(round(r[0]["h"] * SCALE) for r in M["rows"]) \
    + round(M["dots"]["h"] * SCALE) + round(M["dock"][0]["h"] * SCALE) + round(M["bottom"]["h"] * SCALE)

# the second phone, playing a screen recording; it floats right of the clickable phone.
# Only a height is given, so each source keeps its own width: on wide screens the copy
# with a transparent right margin centres the pair, elsewhere the plain one is used.
SIDES = (f'<a href="https://hemashreevi.github.io" title="Open my portfolio"><picture>'
         f'<source media="{WIDE}" srcset="{RAW}{V["playing_wide"]}">'
         f'<img src="./assets/phone/{V["playing"]}" height="{H_PHONE}" align="right" '
         f'alt="A second phone playing a screen recording: my portfolio opens with F1 start lights, picks the Recruiter profile and scrolls through '
         f'projects, skills, certifications and Singapore, then slides over to GitLoom"></picture></a>')

lines = [full(M["top"], "Hemashree's phone: lock-screen clock, profile widget (Software Engineer, VIT '27, open to work) and a notification: hey, welcome in! tap any app to open it", "https://hemashreevi.github.io")]
lines += [row(r) for r in M["rows"]]
lines += [full(M["dots"], ""), row(M["dock"]), full(M["bottom"], "")]
print('<p align="center">\n' + SIDES + "<br>\n".join(lines) + "\n</p>")
