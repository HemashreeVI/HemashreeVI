#!/usr/bin/env python3
"""Builds every animated SVG card used by the profile README.

All text lives in the PROFILE dict below, so updating the README means
editing data here and re-running:

    python3 scripts/build_cards.py

Output goes to assets/cards/. Standard library only.
"""
import base64
import math
import random
from pathlib import Path
from xml.sax.saxutils import escape

import chess_layer
import phoenix_layer


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "cards"
PHOTO = ROOT / "assets" / "photo.jpg"

# ---------------------------------------------------------------- palette
C = {   # deep navy with a blue glow on one side and a plum glow on the other, like the profile photo
    "bg0": "#0A0C1C",
    "bg1": "#0F1228",
    "bg2": "#171B3A",
    "panel": "#131733",
    "line": "#272C50",
    "line2": "#3A4068",
    "violet": "#6EA8FF",   # photo blue (gradient start)
    "lav": "#A9B8FF",      # periwinkle accents, italic title words
    "lilac": "#E3A6F0",    # photo plum-pink (gradient end)
    "silver": "#EEF0F7",   # main text
    "mist": "#C8CCE0",
    "muted": "#9097B8",
    "dim": "#6A7096",
    "rose": "#E59AC8",
    "mint": "#7EE787",
}

SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,Georgia,'Times New Roman',serif"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

# ---------------------------------------------------------------- content
PROFILE = {
    "name": "HEMASHREE",
    "title": "SOFTWARE ENGINEER",
    "degree": "B.Tech Computer Science Engineering",
    "college": "VIT Chennai",
    "tagline": "Building systems that see, decide and keep people safe.",
    "typing": [
        "Computer Vision · Reinforcement Learning",
        "Embedded Sensing · Intrusion Detection",
        "Co-inventor: 2 patents, smart walker + hazard rover",
        "Backend & DevOps · Kafka · Docker · FastAPI",
        "こんにちは! I speak 4 languages",
        "Let's build something that keeps people safe",
    ],
}

TERMINAL = [
    ("whoami", [("out", "hemashree · software engineer")]),
    ("cat education.txt", [("out", "B.Tech Computer Science Engineering @ VIT Chennai")]),
    ("cat focus.txt", [("out", "vision · reinforcement-learning · embedded · security")]),
    ("ls patents/", [("out", "smart-walker/  hazard-rover/"), ("note", "  # fall-risk prediction · disaster-zone hazard detection (filing in progress)")]),
    ("./status --open-to", [("out", "cybersecurity | computer-vision | cyber-physical-systems | backend & devops")]),
    ("echo $LANGUAGES", [("out", "Tamil · English · Hindi · 日本語")]),
]

ABOUT_SIDE = [
    ("BASED IN", "Chennai, India", "open to opportunities"),
    ("SPEAKS", "4 languages", "Tamil · English · Hindi · 日本語"),
    ("BY NIGHT", "Design Lead", "posters, creatives and this README"),
]

RIGHT_NOW = [
    ("3 deep dives", "SeatLock · RootLens · TriageIQ"),
    ("Backend & DevOps", "concurrency and incident response"),
    ("Binary search trees in Java", "and solving LeetCode daily"),
    ("Pit Wall", "an F1 race replay built on real GPS data"),
]

QUICK_FACTS = [
    ("Co-inventor", "on 2 patents: smart walker + hazard rover"),
    ("Singapore", "NUS Industry 4.0 and SuperAI 2025"),
    ("31 dental conditions", "detected on 13,000+ X-rays"),
    ("4 languages", "Tamil · English · Hindi · 日本語"),
    ("Design Lead by night", "posters, creatives and this README"),
]

PIPELINE = [
    ("SENSE", "perceive the world", ["X-rays · IMU + load cells", "pose estimation · sensors"]),
    ("DECIDE", "reason about it", ["YOLOv9 · Q-learning · CNN", "risk scoring · fusion"]),
    ("PROTECT", "make someone safer", ["fall alerts · hazard maps", "automated IDS responses"]),
]

JOURNEY = [
    ("AUG 2023", "VIT Chennai", ["B.Tech CSE", "Team lead · CodeYGen"]),
    ("MAY–JUL 2025", "Research intern", ["Pose estimation", "MMPose"]),
    ("JUN 2025", "Singapore", ["NUS Industry 4.0", "SuperAI · IBM Gen AI"]),
    ("JUL–SEP 2025", "Dental X-ray AI", ["YOLOv9 · 31 classes", "13,000+ images"]),
    ("2025–26", "2 patents", ["Smart walker · rover", "filing in progress"]),
    ("2026", "Backend & DevOps", ["SeatLock · RootLens", "TriageIQ"]),
    ("OCT 2026", "Open source", ["first PR merged", "14 MIT repos"]),
    ("NOW", "Building 4 more", ["+ grinding LeetCode", "next stop: your team?"]),
]

PROJECTS = [
    {
        "slug": "seatlock",
        "kicker": "01 · BACKEND · CONCURRENCY",
        "name": "SeatLock",
        "pitch": "Thousands of buyers. One seat. Zero double-bookings.",
        "built": "3 locking strategies · @Version fencing · partial unique index · Kafka saga + outbox · Redis waiting room",
        "stats": [("1 / 200", "threads win the same seat"), ("0", "double-bookings under k6"), ("2,171", "req/s with fast reject")],
        "tags": ["Java 21", "Spring Boot", "PostgreSQL", "Redis", "Kafka", "k6", "Testcontainers"],
        "motif": "seats",
    },
    {
        "slug": "rootlens",
        "kicker": "02 · RELIABILITY · INCIDENT RESPONSE",
        "name": "RootLens",
        "pitch": "Finds out why a microservice broke, then fixes it within strict limits.",
        "built": "Detect · investigate · decide · act · verify · rolls back bad releases · audit log of every decision",
        "stats": [("< 2 min", "real incident, open to resolved"), ("118", "unit tests"), ("5 steps", "detect → verify")],
        "tags": ["Python", "FastAPI", "Docker", "Prometheus", "Grafana", "OpenTelemetry", "SQLite", "CI"],
        "motif": "graph",
    },
    {
        "slug": "triageiq",
        "kicker": "03 · LLM · STREAMING",
        "name": "TriageIQ",
        "pitch": "Sorts every support email and drafts a grounded reply, fully on-device.",
        "built": "Kafka pipeline · local LLM classifies with a safe fallback · RAG over solved tickets · human approves every reply",
        "stats": [("3B", "local model, data stays local"), ("Top 3", "similar past tickets"), ("0", "emails sent unapproved")],
        "tags": ["Python", "Kafka", "Ollama", "Qdrant", "FastAPI", "Docker", "SSE"],
        "motif": "stream",
    },
    {
        "slug": "gitloom",
        "kicker": "04 · WEB APP · LIVE",
        "name": "GitLoom",
        "pitch": "Your GitHub, woven into a portfolio website.",
        "built": "Reads repos, languages and activity in the browser · live studio · one index.html to host free",
        "stats": [("10", "templates, same data"), ("1", "HTML file to host"), ("0", "servers or sign-ups")],
        "tags": ["JavaScript", "HTML", "CSS", "GitHub REST API", "GitHub Pages"],
        "motif": "loom",
    },
    {
        "slug": "dental",
        "kicker": "05 · COMPUTER VISION · HEALTHCARE",
        "name": "Dental Malocclusion Detection",
        "pitch": "Reads dental X-rays and explains what it sees.",
        "built": "YOLOv9 pipeline · per-finding HiResCAM · FDI tooth chart · Gradio app · PDF reports",
        "stats": [("31", "dental conditions detected"), ("38.7%", "test mAP@50"), ("13,000+", "X-ray dataset")],
        "tags": ["Python", "PyTorch", "OpenCV", "YOLOv9", "HiResCAM", "Gradio"],
        "motif": "xray",
    },
    {
        "slug": "walker",
        "kicker": "PATENT 01 · IoT · FILING IN PROGRESS",
        "name": "Smart Walker",
        "pitch": "A walker that predicts a fall before it happens.",
        "built": "Dual IMUs + load cells · sensor fusion · fall-risk prediction · standalone on Arduino",
        "stats": [("2× IMU", "+ load cells, fused"), ("< $30", "standalone on Arduino"), ("Patent", "co-inventor")],
        "tags": ["Arduino", "C++", "MPU6050", "HX711", "Sensor fusion"],
        "motif": "wave",
    },
    {
        "slug": "rover",
        "kicker": "PATENT 02 · ROBOTICS · FILING IN PROGRESS",
        "name": "Hazard-Detection Rover",
        "pitch": "A rover that explores a disaster zone and flags hazards for rescuers.",
        "built": "Q-learning navigation + CNN hazard perception · multi-hazard detection · emergency stop · live rescue dashboard",
        "stats": [("Q-learning", "learns to explore"), ("CNN", "hazard perception"), ("Patent", "co-inventor")],
        "tags": ["Python", "PyTorch", "Q-Learning", "CNN", "Node-RED", "MQTT"],
        "motif": "grid",
    },
    {
        "slug": "grocer",
        "kicker": "08 · MULTIMODAL · RETAIL",
        "name": "Smart Grocer",
        "pitch": "Knows which mango will spoil first.",
        "built": "Fresh-produce spoilage detection · item localization · expiry-aware retail inventory",
        "stats": [("Spoilage", "detection"), ("Localize", "items on the shelf"), ("Expiry-aware", "inventory")],
        "tags": ["Python", "OpenCV", "Raspberry Pi", "Multimodal"],
        "motif": "fresh",
    },
]

MORE_PROJECTS = [
    ("Intrusion Detection & Threat Modeling",
     "Behavioral IDS for a simulated bank: risk scoring across login, access and transactions, automated responses, audit logs.",
     ["Python", "IDS", "Threat Modeling"]),
    ("Jarvis",
     "Offline, privacy-friendly voice assistant: opens apps, system controls, battery/status and stock notifications.",
     ["Python", "SpeechRecognition"]),
]

BUILDING = [
    ("Pulse", "A free status page that runs entirely on GitHub Actions + Pages", "STEP 1 OF 5", 0.2),
    ("PortPilot", "Find what's using a port (even Docker containers) and free it with one key", "PLANNED", 0),
    ("BST Playground", "Watch binary search tree operations animate, step by step", "PLANNED", 0),
    ("Pit Wall", "Replay real F1 races with a GPS track map and live leaderboard", "PLANNED", 0),
    ("LeetCode Solutions", "Clean, commented Java solutions, intuition first", "DAILY", -1),
]

TOOLKIT = [
    ("01 LANGUAGES", ["Python · Java", "C++ · JavaScript", "SQL"]),
    ("02 FRONTEND", ["HTML · CSS", "JavaScript", "Three.js · Canvas", "Gradio"]),
    ("03 BACKEND & DEVOPS", ["Spring Boot", "FastAPI · Flask", "Docker · Kafka · Redis", "Prometheus · Grafana", "GitHub Actions · k6"]),
    ("04 MOTION & DESIGN", ["Canva", "CSS keyframes", "SVG animation", "Three.js 3D", "Poster design"]),
    ("05 AI & VISION", ["PyTorch", "TensorFlow · OpenCV", "YOLOv8/v9 · Grad-CAM", "MMPose · Q-learning", "RAG · Ollama · watsonx"]),
    ("06 DATA", ["PostgreSQL", "SQLite · MySQL", "Redis · Qdrant", "Firebase"]),
    ("07 EMBEDDED & IoT", ["Arduino · ESP32", "Raspberry Pi", "Sensor fusion", "LIDAR SLAM"]),
    ("08 SECURITY", ["Threat modeling", "Intrusion detection", "Risk scoring"]),
    ("09 TOOLS", ["Git · GitHub", "VS Code · Linux", "Jupyter · Colab", "Kaggle · Roboflow", "Windows · PowerShell"]),
    ("10 SPOKEN", ["Tamil · English", "Hindi", "日本語"]),
]

MILESTONES = [
    ("PATENT", "Co-inventor · filing in progress",
     "IoT-Enabled Smart Walker with Sensor-Fusion Fall Risk Prediction and Adaptive Mobility Assistance. Inventive disclosure filed with IIPRD."),
    ("PATENT", "Co-inventor · filing in progress",
     "Hazard-Detection Rover: autonomous disaster-zone exploration with learned navigation and multi-hazard detection."),
    ("OSS", "Open source contributor",
     "Merged PR to firstcontributions/first-contributions (Oct 2026) · 14 MIT-licensed repos of my own."),
    ("RESEARCH", "Research Intern, VIT Chennai",
     "Human pose estimation with MMPose, validated against Kinovea ground truth (May–Jul 2025)."),
    ("NUS", "National University of Singapore",
     "Introduction to Industry 4.0 Programme (Jun 2025)."),
    ("SUPERAI", "SuperAI 2025",
     "Marina Bay Sands, Singapore."),
    ("IBM", "Generative AI certification",
     "Gen AI Using IBM watsonx."),
    ("日本語", "Japanese",
     "Studied Japanese as a subject at VIT Chennai."),
    ("LEAD", "Leadership",
     "Team Leader, CodeYGen Club · Design Lead, Fitness Club."),
]

GAMES = [
    ("Keep them standing", "Stop a fall before it happens", "walker"),
    ("Freshness check", "Save a mango from spoiling", "mango"),
    ("Incident hunt", "Find the broken microservice", "hunt"),
    ("Hiragana sprint", "Test your Japanese", "kana"),
]


OPEN_SOURCE_PR = ("firstcontributions/first-contributions", "#126858", "Add Hemashree to Contributors list", "MERGED · OCT 2026")
OPEN_SOURCE_REPOS = [
    ("ReadMeow", "profile READMEs, designed for you"),
    ("gitpulse", "4 free tools for your GitHub"),
    ("PortPilot", "who's using my port? free it"),
    ("typewave", "mechanical keyboard sounds"),
    ("typo-arcade", "a typing test that plays like a game"),
    ("token-meter", "tokens & context, per message"),
    ("Pit Wall", "replay real F1 races"),
    ("ferrodo", "terminal todo manager in Rust"),
]

YOUTUBE = {
    "handle": "@shreejith-l7o",
    "url": "https://www.youtube.com/@shreejith-l7o",
    "name": "Byte Decoded",
    "pitch": "Byte Decoded",
    "line": "Dev builds, AI/ML, project walkthroughs and tech vlogs.",
}

SOCIAL = {
    "mail": "mailto:shreejith2005@gmail.com",
    "linkedin": "https://www.linkedin.com/in/hema-shree272005",
    "youtube": "https://www.youtube.com/@shreejith-l7o",
    "instagram": "https://www.instagram.com/hemashree_2_7/",
    "portfolio": "https://hemashreevi.github.io",
    "leetcode": "https://leetcode.com/u/hemashree_272005/",
    "chess": "https://www.chess.com/member/hemashreevi",
}


EXTENSIONS = [
    {"slug": "job-radar", "name": "Job Radar", "pitch": "Save any job in one click.",
     "points": ["LinkedIn · Naukri · careers pages", "matches jobs to my projects", "5-day follow-up reminders"],
     "tags": ["Manifest V3", "JavaScript", "schema.org"]},
    {"slug": "repo-recap", "name": "Repo Recap", "pitch": "Any GitHub repo, explained in 10 seconds.",
     "points": ["what it does · tech stack", "how to run it, copy-ready", "activity + good first issues"],
     "tags": ["GitHub REST API", "Shadow DOM", "caching"]},
    {"slug": "byte-decoded-clipper", "name": "Byte Decoded Clipper", "pitch": "Articles into 60-second Shorts.",
     "points": ["hook · 3 points · CTA, timed", "on-screen text + hashtags", "Chrome on-device AI or local"],
     "tags": ["Prompt API", "NLP", "YouTube"]},
    {"slug": "contributions-decoded", "name": "Contributions Decoded", "pitch": "GitHub profiles in plain English.",
     "points": ["explains commits, PRs, +/- lines", "streaks, busiest day, monthly chart", "works on any profile"],
     "tags": ["DOM parsing", "no API", "beginner-friendly"]},
    {"slug": "worksync", "name": "WorkSync", "pitch": "My Chrome work, backed up to GitHub.",
     "points": ["Docs, Sheets, Slides, Colab + code", "one commit per thing I do", "a daily journal, private repo"],
     "tags": ["Git Data API", "Manifest V3", "auto-sync"]},
]


# Project cards: a real screenshot from each repo (assets/shots/), its headline number and one line.
SHOWCASE = [
    # main projects
    {"slug": "seatlock", "repo": "SeatLock", "tag": "Backend", "num": "0", "label": "double-bookings, 200 threads racing",
     "desc": "A ticket-booking backend where 200 buyers race for one seat and exactly one wins."},
    {"slug": "rootlens", "repo": "rootlens", "tag": "Reliability", "num": "< 2 min", "label": "real incident, open to resolved",
     "desc": "Finds why a microservice broke, rolls back the bad change, then checks it worked."},
    {"slug": "triageiq", "repo": "TriageIQ", "tag": "AI", "num": "0", "label": "emails sent without approval",
     "desc": "Sorts every support email and drafts a grounded reply with a local model."},
    {"slug": "gitloom", "repo": "GitLoom", "tag": "Web app", "num": "10", "label": "templates, one HTML file",
     "desc": "Paste a GitHub username and get a portfolio website you can host anywhere."},
    # research & patents
    {"slug": "walker", "repo": "smart_walker", "tag": "Patent", "num": "< $30", "label": "of hardware, standalone on Arduino",
     "desc": "A walker that predicts a fall before it happens, from tilt and load sensors."},
    {"slug": "rover", "repo": "disaster-response-rover-nodered", "tag": "Patent", "num": "6 / 6", "label": "hazard scenarios handled",
     "desc": "A rover that explores a disaster zone and flags obstacles, heat and toxic gas."},
    {"slug": "dental", "repo": "AI_Malocclusion_Detection", "tag": "Research", "num": "31", "label": "dental conditions detected",
     "desc": "Reads a panoramic X-ray, charts findings per tooth and writes a report. Test mAP@50: 38.7%."},
    # chrome extensions
    {"slug": "job-radar", "repo": "job-radar", "tag": "Extension", "num": "1 click", "label": "to save any job",
     "desc": "Saves jobs from LinkedIn, Naukri or careers pages and matches them to my projects."},
    {"slug": "repo-recap", "repo": "repo-recap", "tag": "Extension", "num": "10 s", "label": "to understand any repo",
     "desc": "A sidebar on GitHub: what a repo does, its tech stack and how to run it."},
    {"slug": "byte-decoded-clipper", "repo": "byte-decoded-clipper", "tag": "Extension", "num": "60 s", "label": "Shorts from any article",
     "desc": "Turns an article into a timed Shorts script with Chrome's on-device AI."},
    {"slug": "contributions-decoded", "repo": "contributions-decoded", "tag": "Extension", "num": "0", "label": "API keys needed",
     "desc": "Explains any GitHub profile's commits, pull requests and streaks in plain English."},
    {"slug": "worksync", "repo": "worksync", "tag": "Extension", "num": "1", "label": "commit per thing I do",
     "desc": "Backs up my Docs, Sheets, Colab notebooks and code to a private repo."},
    {"slug": "nova-launchpad", "repo": "portfolio-extension", "tag": "Extension", "num": "6 in 1", "label": "jobs, mail, LeetCode, GitHub, YouTube, news",
     "desc": "Nova Launchpad, my new tab for the job hunt: resume-matched jobs and daily nudges."},
]

# ---------------------------------------------------------------- helpers
def e(s):
    return escape(str(s), {'"': "&quot;"})


STYLE = f"""
<style>
.serif{{font-family:{SERIF}}}
.sans{{font-family:{SANS}}}
.mono{{font-family:{MONO}}}
.kick{{font-family:{MONO};font-size:12px;letter-spacing:3px;fill:{C['lav']}}}
.twinkle{{animation:tw 4s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.9}}}}
.pulse{{animation:pl 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes pl{{0%,100%{{opacity:.55;transform:scale(1)}}50%{{opacity:1;transform:scale(1.35)}}}}
.spin{{animation:sp 60s linear infinite;transform-box:view-box}}
@keyframes sp{{to{{transform:rotate(360deg)}}}}
.float{{animation:fl 6s ease-in-out infinite}}
@keyframes fl{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}
.fadein{{animation:fi 1.2s ease-out both}}
@keyframes fi{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
</style>"""


def base_defs(uid):
    return f"""
<defs>
  <radialGradient id="{uid}-bg" cx="70%" cy="30%" r="90%">
    <stop offset="0" stop-color="{C['bg2']}"/>
    <stop offset=".55" stop-color="{C['bg1']}"/>
    <stop offset="1" stop-color="{C['bg0']}"/>
  </radialGradient>
  <radialGradient id="{uid}-glowA" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="#2A5AA8" stop-opacity=".55"/>
    <stop offset="1" stop-color="#2A5AA8" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="{uid}-glowB" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="#7A2F7E" stop-opacity=".5"/>
    <stop offset="1" stop-color="#7A2F7E" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="{uid}-silver" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{C['violet']}"/>
    <stop offset=".55" stop-color="{C['lav']}"/>
    <stop offset="1" stop-color="{C['lilac']}"/>
  </linearGradient>
  <linearGradient id="{uid}-rule" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{C['lav']}" stop-opacity="0"/>
    <stop offset=".25" stop-color="{C['lav']}" stop-opacity=".8"/>
    <stop offset="1" stop-color="{C['lav']}" stop-opacity="0"/>
  </linearGradient>
  <pattern id="{uid}-grid" width="28" height="28" patternUnits="userSpaceOnUse">
    <path d="M28 0H0V28" fill="none" stroke="{C['lav']}" stroke-opacity="0"/>
  </pattern>
  <filter id="{uid}-smoke" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.0045 0.011" numOctaves="4" seed="{sum(map(ord, uid)) % 97}"/>
    <feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  2.6 0 0 0 -1.25"/>
    <feGaussianBlur stdDeviation="6"/>
  </filter>
  <linearGradient id="{uid}-sweep" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{C['muted']}"/>
    <stop offset=".45" stop-color="{C['lav']}"/>
    <stop offset=".5" stop-color="#FFFFFF"/>
    <stop offset=".55" stop-color="{C['lav']}"/>
    <stop offset="1" stop-color="{C['muted']}"/>
    <animate attributeName="x1" values="-1;1.2" dur="5s" repeatCount="indefinite"/>
    <animate attributeName="x2" values="0;2.2" dur="5s" repeatCount="indefinite"/>
  </linearGradient>
  <filter id="{uid}-soft" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="3"/>
  </filter>
</defs>"""


def frame(w, h, uid, glow=(0.75, 0.3)):
    gx, gy = glow
    return f"""
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="22" fill="url(#{uid}-bg)" stroke="{C['line']}"/>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="22" fill="url(#{uid}-grid)"/>
<ellipse cx="{w*gx:.0f}" cy="{h*gy:.0f}" rx="{w*0.35:.0f}" ry="{h*0.7:.0f}" fill="url(#{uid}-glowA)"/>
<ellipse cx="{w*(1-gx):.0f}" cy="{h*(1-gy):.0f}" rx="{w*0.25:.0f}" ry="{h*0.5:.0f}" fill="url(#{uid}-glowB)"/>
{atmosphere(w, h, uid)}"""


def atmosphere(w, h, uid):
    """No effects: cards stay flat like GitHub's own panels."""
    return ""


def stars(w, h, n, seed, pad=20):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x, y = rnd.uniform(pad, w - pad), rnd.uniform(pad, h - pad)
        r = rnd.choice([0.8, 1, 1.2, 1.6])
        d = rnd.uniform(0, 4)
        out.append(f'<circle class="twinkle" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{C["lilac"]}" fill-opacity=".35" style="animation-delay:{d:.1f}s"/>')
    return "\n".join(out)


def svg(w, h, uid, title, desc, body):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="{uid}-t {uid}-d">
<title id="{uid}-t">{e(title)}</title>
<desc id="{uid}-d">{e(desc)}</desc>
{STYLE}
{base_defs(uid)}
{body}
</svg>
"""


def text(x, y, s, size, fill, cls="sans", anchor="start", extra=""):
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>{e(s)}</text>'


def wrap(s, n):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def mono_w(s, size):
    # Approximate advance of a monospace glyph; CJK glyphs are double width.
    return sum(size * (1.2 if ord(ch) > 0x2E80 else 0.61) for ch in s)


def chip(x, y, label, size=11, fill=None, stroke=None, color=None):
    w = mono_w(label, size) + 22
    return (
        f'<rect x="{x}" y="{y}" width="{w:.0f}" height="24" rx="12" fill="{fill or C["panel"]}" stroke="{stroke or C["line2"]}"/>'
        + text(x + 11, y + 16, label, size, color or C["mist"], "mono")
    ), w


def chips(x, y, labels, gap=8, maxw=None, **kw):
    out, cx, cy = [], x, y
    for lb in labels:
        w = mono_w(lb, kw.get("size", 11)) + 22
        if maxw and cx + w > x + maxw:
            cx, cy = x, cy + 32
        s, w = chip(cx, cy, lb, **kw)
        out.append(s)
        cx += w + gap
    return "\n".join(out)


def write(name, content):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"  {name:28s} {len(content.encode()) / 1024:6.1f} KB")


# ---------------------------------------------------------------- hero
def build_hero():
    W, H, u = 1200, 500, "hero"
    p = PROFILE
    photo = base64.b64encode(PHOTO.read_bytes()).decode()

    # typing pill: each line types in, holds, then fades; SMIL so it runs inside <img>
    lines = p["typing"]
    per = 4.5
    total = per * len(lines)
    typed = []
    for i, ln in enumerate(lines):
        t0 = i * per / total
        t1 = (i * per + 1.8) / total
        t3 = (i + 1) * per / total
        full = round(mono_w(ln, 13) + 4)
        if i == 0:
            kt_w, v_w = f"0;{t1:.4f};1", f"0;{full};{full}"
            kt_o, v_o = f"0;{t3:.4f}", "1;0"
        else:
            kt_w, v_w = f"0;{t0:.4f};{t1:.4f};1", f"0;0;{full};{full}"
            kt_o, v_o = (f"0;{t0:.4f};{t3:.4f}", "0;1;0") if i < len(lines) - 1 else (f"0;{t0:.4f}", "0;1")
        typed.append(f"""
<clipPath id="hero-type{i}"><rect x="204" y="58" height="24" width="0">
  <animate attributeName="width" dur="{total}s" repeatCount="indefinite" keyTimes="{kt_w}" values="{v_w}"/>
</rect></clipPath>
<g clip-path="url(#hero-type{i})" opacity="{1 if i == 0 else 0}">
  <animate attributeName="opacity" dur="{total}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt_o}" values="{v_o}"/>
  {text(206, 75, ln, 13, C['silver'], 'mono')}
</g>""")
    typed_s = "\n".join(typed)

    # photo arch
    ax, ay, aw, ah = 812, 92, 236, 300
    r = aw / 2
    arch = f"M{ax},{ay+ah} L{ax},{ay+r} A{r},{r} 0 0 1 {ax+aw},{ay+r} L{ax+aw},{ay+ah} Z"
    cx, cy = ax + aw / 2, ay + ah / 2 + 6

    orbit_labels = [("VISION", -128), ("RL", -40), ("IoT", 35), ("SECURITY", 150)]
    olab = []
    for lb, ang in orbit_labels:
        a = math.radians(ang)
        ox, oy = cx + 196 * math.cos(a), cy + 196 * math.sin(a)
        anchor = "start" if math.cos(a) > 0 else "end"
        dx = 10 if anchor == "start" else -10
        olab.append(f'<circle class="pulse" cx="{ox:.0f}" cy="{oy:.0f}" r="3.5" fill="{C["lilac"]}"/>'
                    + text(round(ox + dx), round(oy + 4), lb, 11, C["mist"], "mono", anchor, 'letter-spacing="2"'))

    body = f"""
{frame(W, H, u, (0.78, 0.35))}
<defs>
  <clipPath id="hero-arch"><path d="{arch}"/></clipPath>
  <linearGradient id="hero-fade" x1="0" y1="0" x2="0" y2="1">
    <stop offset=".55" stop-color="{C['bg1']}" stop-opacity="0"/>
    <stop offset="1" stop-color="{C['bg1']}" stop-opacity=".85"/>
  </linearGradient>
  <linearGradient id="hero-tint" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{C['lav']}" stop-opacity=".18"/>
    <stop offset="1" stop-color="{C['violet']}" stop-opacity=".05"/>
  </linearGradient>
  <linearGradient id="hero-sheen" gradientUnits="userSpaceOnUse" x1="-300" y1="0" x2="-60" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset=".5" stop-color="#fff" stop-opacity=".85"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1100 0;1100 0" keyTimes="0;.45;1" dur="7s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="hero-ring" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{C['silver']}" stop-opacity=".7"/>
    <stop offset=".5" stop-color="{C['lav']}" stop-opacity=".15"/>
    <stop offset="1" stop-color="{C['silver']}" stop-opacity=".6"/>
  </linearGradient>
</defs>
{stars(W, H, 46, 7)}

<!-- prompt pill -->
<rect x="60" y="52" width="610" height="36" rx="18" fill="{C['bg0']}" fill-opacity=".7" stroke="{C['line2']}"/>
<circle cx="80" cy="70" r="4" fill="{C['lav']}" class="pulse"/>
{text(94, 75, "~/hemashree", 13, C['muted'], 'mono')}
{text(186, 75, "$", 13, C['lav'], 'mono')}
{typed_s}
<rect x="650" y="61" width="8" height="18" fill="{C['lilac']}" opacity=".9">
  <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
</rect>

<!-- identity -->
<line x1="60" y1="128" x2="92" y2="128" stroke="{C['lav']}"/>
{text(104, 132, "COMPUTER VISION · RL · EMBEDDED · SECURITY · DEVOPS", 12, C['lav'], 'mono', 'start', 'letter-spacing="3"')}
<g class="fadein">
  {text(56, 224, p['name'], 92, f"url(#{u}-silver)", 'serif', 'start', 'letter-spacing="6"')}
  {text(56, 224, p['name'], 92, "url(#hero-sheen)", 'serif', 'start', 'letter-spacing="6" opacity=".55"')}
</g>
<rect x="60" y="246" width="520" height="1.5" fill="url(#{u}-rule)"/>
<circle cx="60" cy="247" r="3" fill="#fff">
  <animate attributeName="cx" values="60;580;60" dur="9s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" dur="9s" repeatCount="indefinite"/>
</circle>
{text(60, 288, p['title'], 17, C['silver'], 'sans', 'start', 'letter-spacing="7" font-weight="600"')}
{text(60, 320, f"{p['degree']} · {p['college']}", 15, C['mist'], 'sans')}
{text(60, 358, p['tagline'], 20, C['lilac'], 'serif', 'start', 'font-style="italic"')}
{chips(60, 384, ["Chennai, India", "● Open to opportunities", "Patent co-inventor"], size=11)}

<line x1="60" y1="440" x2="1140" y2="440" stroke="{C['line']}"/>
{text(60, 466, "B.TECH CSE · VIT CHENNAI · 2023 →", 11, C['muted'], 'mono', 'start', 'letter-spacing="2.5"')}
{text(1140, 466, "SUPERAI SINGAPORE 2025 · NUS INDUSTRY 4.0 · IBM GEN AI", 11, C['silver'], 'mono', 'end', 'letter-spacing="2.5"')}

<!-- portrait -->
<ellipse cx="{cx}" cy="{cy}" rx="260" ry="220" fill="url(#{u}-glowA)"/>
<circle cx="{cx}" cy="{cy}" r="196" fill="none" stroke="{C['lav']}" stroke-opacity=".22"/>
<g style="transform-origin:{cx}px {cy}px" class="spin">
  <circle cx="{cx}" cy="{cy}" r="172" fill="none" stroke="url(#hero-ring)" stroke-width="1.2" stroke-dasharray="2 10"/>
  <circle cx="{cx + 172}" cy="{cy}" r="3" fill="{C['silver']}"/>
</g>
{''.join(olab)}
<g class="float">
  <path d="{arch}" transform="translate(10 10)" fill="none" stroke="{C['lav']}" stroke-opacity=".45"/>
  <g clip-path="url(#hero-arch)">
    <image href="data:image/jpeg;base64,{photo}" x="{ax}" y="{ay}" width="{aw}" height="{ah}" preserveAspectRatio="xMidYMid slice"/>
    <rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" fill="url(#hero-tint)"/>
    <rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" fill="url(#hero-fade)"/>
  </g>
  <path d="{arch}" fill="none" stroke="url(#hero-ring)" stroke-width="1.5"/>
  <path d="M{ax-14},{ay+ah-40} v40 h40" fill="none" stroke="{C['silver']}" stroke-opacity=".7"/>
  <path d="M{ax+aw+14},{ay+ah-40} v40 h-40" fill="none" stroke="{C['silver']}" stroke-opacity=".7"/>
</g>
"""
    write("hero.svg", svg(W, H, u, f"{p['name']}, {p['title'].title()}",
                          f"{p['degree']} at {p['college']}. {p['tagline']}", body))


# ---------------------------------------------------------------- section titles
def build_title(num, kicker, plain, italic, right, slug, extra=""):
    W, H, u = 1200, 104, f"t{num}"
    width_plain = len(plain) * 19
    body = f"""
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{C['bg1']}" stroke="{C['line']}"/>
{text(30, 32, num, 12, C['silver'], 'mono', 'start', 'letter-spacing="3"')}
{text(58, 32, kicker, 12, C['lav'], 'mono', 'start', 'letter-spacing="3"')}
{text(1170, 32, right, 11, C['muted'], 'mono', 'end', 'letter-spacing="3"')}
<text x="30" y="80" class="serif" font-size="40" fill="{C['silver']}">{e(plain)} <tspan fill="url(#{u}-sweep)" font-style="italic">{e(italic)}</tspan></text>
<rect x="30" y="96" width="1140" height="1.2" fill="url(#{u}-rule)"/>
<circle cy="96.6" r="2.6" fill="{C['lav']}">
  <animate attributeName="cx" values="30;1170" dur="6s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.8;1" dur="6s" repeatCount="indefinite"/>
</circle>
{extra}
"""
    write(f"title-{slug}.svg", svg(W, H, u, f"{num} {kicker.title()}: {plain} {italic}", right, body))


# ---------------------------------------------------------------- about
def build_about():
    W, H, u = 1200, 630, "about"
    tx, ty, tw, th = 32, 34, 740, 562
    rows, y, step, i = [], ty + 66, 22, 0
    cycle = 16
    for cmd, outs in TERMINAL:
        group = [text(tx + 28, y, "$", 13, C['lav'], 'mono'), text(tx + 46, y, cmd, 13, C['silver'], 'mono')]
        y += step
        for kind, s in outs:
            col = C['muted'] if kind == "note" else C['mist']
            if kind == "out":
                group.append(text(tx + 28, y, "→", 13, C['violet'], 'mono'))
            group.append(text(tx + 46, y, s, 13, col, 'mono'))
            y += step
        y += 6
        if i < 2:   # the first two commands are always there, so the terminal never looks empty
            rows.append(f"<g>{''.join(group)}</g>")
        else:
            t = (0.2 + (i - 2) * 0.6) / cycle
            rows.append(f"""<g opacity="0"><animate attributeName="opacity" dur="{cycle}s" repeatCount="indefinite" keyTimes="0;{t:.3f};{t + 0.02:.3f};.95;.98;1" values="0;0;1;1;0;0"/>{''.join(group)}</g>""")
        i += 1
    cursor_y = y - step + 4

    side = [f'<g transform="translate(796 14) scale(1.12)">{id_card(u + "id")}</g>']
    body = f"""
{frame(W, H, u, (0.85, 0.2))}
<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="14" fill="{C['bg0']}" fill-opacity=".85" stroke="{C['line2']}"/>
<path d="M{tx} {ty + 36}H{tx + tw}" stroke="{C['line']}"/>
<circle cx="{tx + 20}" cy="{ty + 18}" r="5" fill="{C['rose']}" fill-opacity=".7"/>
<circle cx="{tx + 38}" cy="{ty + 18}" r="5" fill="{C['lav']}" fill-opacity=".7"/>
<circle cx="{tx + 56}" cy="{ty + 18}" r="5" fill="{C['mint']}" fill-opacity=".7"/>
{text(tx + tw / 2, ty + 23, "hemashree@vit-chennai: ~/about", 12, C['muted'], 'mono', 'middle')}
{''.join(rows)}
{text(tx + 28, cursor_y + 18, "$", 13, C['lav'], 'mono')}
<rect x="{tx + 46}" y="{cursor_y + 6}" width="8" height="15" fill="{C['lilac']}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>
{''.join(side)}
"""
    desc = " ".join(f"$ {c}: " + "; ".join(s for _, s in o) for c, o in TERMINAL)
    write("about.svg", svg(W, H, u, "About Hemashree", desc, body))


# ---------------------------------------------------------------- now + facts
def build_now():
    W, H, u = 1200, 330, "now"
    cols = [("RIGHT NOW", "What I'm building", RIGHT_NOW, 32), ("QUICK FACTS", "Things worth knowing", QUICK_FACTS, 612)]
    parts = []
    for lab, head, items, x in cols:
        parts.append(f"""
<rect x="{x}" y="28" width="556" height="274" rx="18" fill="{C['panel']}" fill-opacity=".8" stroke="{C['line2']}"/>
{text(x + 28, 60, lab, 11, C['lav'], 'mono', 'start', 'letter-spacing="3"')}
{text(x + 28, 94, head, 26, C['silver'], 'serif')}""")
        gap = 190 / len(items)
        for k, (big, small) in enumerate(items):
            yy = 130 + k * gap
            dot = f'<circle class="pulse" cx="{x + 34}" cy="{yy - 5}" r="4" fill="{C["mint"] if lab == "RIGHT NOW" else C["lav"]}" style="animation-delay:{k * 0.4}s"/>'
            parts.append(dot + f'<text x="{x + 52}" y="{yy}" class="sans" font-size="15" fill="{C["silver"]}" font-weight="600">{e(big)} <tspan fill="{C["muted"]}" font-weight="400">{e(small)}</tspan></text>')
    body = frame(W, H, u, (0.5, 0.2)) + "".join(parts)
    desc = "Right now: " + "; ".join(f"{a} {b}" for a, b in RIGHT_NOW) + ". Quick facts: " + "; ".join(f"{a} {b}" for a, b in QUICK_FACTS)
    write("now.svg", svg(W, H, u, "Right now and quick facts", desc, body))


# ---------------------------------------------------------------- pipeline
def build_pipeline():
    W, H, u = 1200, 330, "pipe"
    xs = [70, 450, 830]
    parts = [frame(W, H, u, (0.5, 0.5))]
    for k, (name, sub, lines) in enumerate(PIPELINE):
        x = xs[k]
        parts.append(f"""
<g>
<rect x="{x}" y="60" width="300" height="180" rx="18" fill="{C['panel']}" stroke="{C['line2']}"/>
<circle cx="{x + 40}" cy="100" r="16" fill="none" stroke="{C['lav']}"/>
<circle cx="{x + 40}" cy="100" r="5" fill="{C['lilac']}" class="pulse" style="animation-delay:{k * 0.8}s"/>
{text(x + 68, 98, f"0{k + 1}", 11, C['muted'], 'mono', 'start', 'letter-spacing="2"')}
{text(x + 68, 115, sub.upper(), 10, C['lav'], 'mono', 'start', 'letter-spacing="2"')}
{text(x + 24, 168, name, 34, C['silver'], 'serif', 'start', 'letter-spacing="4"')}
{text(x + 24, 198, lines[0], 13, C['mist'], 'mono')}
{text(x + 24, 220, lines[1], 13, C['muted'], 'mono')}
</g>""")
        if k < 2:
            a, b = x + 300, xs[k + 1]
            parts.append(f"""<path d="M{a + 6} 150H{b - 6}" stroke="{C['lav']}" stroke-dasharray="3 5"/>
<path d="M{b - 14} 144l8 6-8 6" fill="none" stroke="{C['lav']}"/>
<circle r="3.5" fill="#fff"><animateMotion dur="1.8s" repeatCount="indefinite" path="M{a + 6} 150H{b - 10}" begin="{k * 0.9}s"/></circle>""")
    loop = f"M{xs[2] + 150} 240 V282 H{xs[0] + 150} V244"
    parts.append(f"""<path d="{loop}" fill="none" stroke="{C['lav']}" stroke-opacity=".5" stroke-dasharray="3 6"/>
<path d="M{xs[0] + 144} 252l6-8 6 8" fill="none" stroke="{C['lav']}" stroke-opacity=".7"/>
<circle r="3" fill="{C['lilac']}"><animateMotion dur="5s" repeatCount="indefinite" path="{loop}"/></circle>
{text(600, 300, "CLOSED FEEDBACK LOOP", 11, C['lav'], 'mono', 'middle', 'letter-spacing="4"')}
{text(600, 38, "Every project follows the same loop: perceive the world, decide, and make someone safer.", 14, C['muted'], 'serif', 'middle', 'font-style="italic"')}""")
    desc = " → ".join(f"{n}: {', '.join(l)}" for n, _, l in PIPELINE)
    write("pipeline.svg", svg(W, H, u, "Sense, Decide, Protect", desc, "".join(parts)))


# ---------------------------------------------------------------- journey
def build_journey():
    W, H, u = 1200, 400, "jour"
    n = len(JOURNEY)
    x0, x1, ly = 90, 1110, 200
    parts = [frame(W, H, u, (0.3, 0.5))]
    parts.append(f"""<path d="M{x0} {ly}H{x1}" stroke="{C['line2']}" stroke-width="2"/>
<path d="M{x0} {ly}H{x1}" stroke="url(#{u}-silver)" stroke-width="2" stroke-dasharray="1020" stroke-dashoffset="1020">
  <animate attributeName="stroke-dashoffset" values="1020;0;0" keyTimes="0;.6;1" dur="8s" repeatCount="indefinite"/>
</path>""")
    for k, (date, head, sub) in enumerate(JOURNEY):
        x = x0 + k * (x1 - x0) / (n - 1)
        up = k % 2 == 0
        t = 0.6 * k / (n - 1)
        last = k == n - 1
        card_y = 52 if up else 226
        stem = f'<path d="M{x:.0f} {ly - 8 if up else ly + 8}V{card_y + 122 if up else card_y}" stroke="{C["line2"]}"/>'
        parts.append(f"""
{stem}
<circle cx="{x:.0f}" cy="{ly}" r="{9 if last else 7}" fill="{C['bg0']}" stroke="{C['lilac'] if last else C['lav']}" stroke-width="2"/>
<circle cx="{x:.0f}" cy="{ly}" r="3" fill="{C['silver']}" opacity="0">
  <animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{t:.3f};{t + 0.02:.3f};1" dur="8s" repeatCount="indefinite"/>
</circle>
<rect x="{x - 74:.0f}" y="{card_y}" width="148" height="122" rx="14" fill="{C['panel']}" stroke="{C['lilac'] if last else C['line2']}" {'stroke-dasharray="4 4"' if last else ''}/>
{text(round(x), card_y + 26, date, 10, C['lav'], 'mono', 'middle', 'letter-spacing="1.5"')}
{text(round(x), card_y + 56, head, 16, C['silver'], 'serif', 'middle')}
{text(round(x), card_y + 84, sub[0], 12, C['mist'], 'sans', 'middle')}
{text(round(x), card_y + 104, sub[1], 12, C['muted'], 'sans', 'middle')}""")
    desc = "; ".join(f"{d}: {h} ({', '.join(s)})" for d, h, s in JOURNEY)
    write("journey.svg", svg(W, H, u, "My journey, 2023 to now", desc, "".join(parts)))


# ---------------------------------------------------------------- project motifs
def motif(kind, x, y):
    L, V, S = C['lav'], C['violet'], C['silver']
    if kind == "xray":
        teeth = []
        for i in range(8):
            tx = x + 20 + i * 34
            teeth.append(f'<rect x="{tx}" y="{y + 40}" width="26" height="54" rx="10" fill="{S}" fill-opacity=".14" stroke="{S}" stroke-opacity=".35"/>')
            teeth.append(f'<rect x="{tx}" y="{y + 110}" width="26" height="54" rx="10" fill="{S}" fill-opacity=".12" stroke="{S}" stroke-opacity=".3"/>')
        return f"""
<rect x="{x}" y="{y}" width="310" height="200" rx="16" fill="{C['bg0']}" stroke="{C['line2']}"/>
{''.join(teeth)}
<rect x="{x + 84}" y="{y + 34}" width="68" height="66" fill="none" stroke="{C['rose']}" stroke-width="1.5"/>
{text(x + 84, y + 28, "impacted 0.88", 10, C['rose'], 'mono')}
<rect x="{x + 186}" y="{y + 104}" width="40" height="66" fill="none" stroke="{C['mint']}" stroke-width="1.5"/>
{text(x + 160, y + 186, "FDI 36 · caries 0.91", 10, C['mint'], 'mono')}
<rect x="{x}" y="{y}" width="310" height="3" fill="{L}" opacity=".8">
  <animate attributeName="y" values="{y + 8};{y + 190};{y + 8}" dur="4s" repeatCount="indefinite"/>
</rect>"""
    if kind == "graph":
        nodes = [(60, 60, "customer"), (180, 50, "user"), (110, 130, "order"), (240, 120, "payment"), (180, 170, "sqlite")]
        edges = [(0, 1), (0, 2), (2, 3), (1, 3), (3, 4), (2, 4)]
        s = [f'<rect x="{x}" y="{y}" width="310" height="200" rx="16" fill="{C["bg0"]}" stroke="{C["line2"]}"/>']
        for a, b in edges:
            s.append(f'<path d="M{x + nodes[a][0]} {y + nodes[a][1]}L{x + nodes[b][0]} {y + nodes[b][1]}" stroke="{L}" stroke-opacity=".35"/>')
        for i, (nx, ny, lb) in enumerate(nodes):
            bad = lb == "payment"
            col = C['rose'] if bad else L
            s.append(f'<circle cx="{x + nx}" cy="{y + ny}" r="{12 if bad else 9}" fill="{C["panel"]}" stroke="{col}" stroke-width="1.5"/>')
            if bad:
                s.append(f'<circle cx="{x + nx}" cy="{y + ny}" r="12" fill="none" stroke="{col}"><animate attributeName="r" values="12;28" dur="1.8s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;0" dur="1.8s" repeatCount="indefinite"/></circle>')
            s.append(text(x + nx, y + ny + 26, lb, 10, col if bad else C['muted'], 'mono', 'middle'))
        s.append(text(x + 16, y + 22, "payment v2 · errors · score 1.00 → rollback", 10, C['rose'], 'mono'))
        return "".join(s)
    if kind == "stream":
        s = [f'<rect x="{x}" y="{y}" width="310" height="200" rx="16" fill="{C["bg0"]}" stroke="{C["line2"]}"/>',
             text(x + 18, y + 26, "kafka://tickets", 10, C['muted'], 'mono'),
             f'<rect x="{x + 120}" y="{y + 70}" width="70" height="60" rx="12" fill="{C["panel"]}" stroke="{L}"/>',
             text(x + 155, y + 98, "LLM", 13, S, 'mono', 'middle'), text(x + 155, y + 116, "+ RAG", 10, L, 'mono', 'middle')]
        for i in range(3):
            s.append(f'<rect width="40" height="22" rx="5" fill="{C["panel"]}" stroke="{S}" stroke-opacity=".5"><animateMotion dur="3s" begin="{i}s" repeatCount="indefinite" path="M{x + 10} {y + 89}H{x + 110}"/></rect>')
        for i, (lb, col) in enumerate([("P1 · billing", C['rose']), ("P2 · login", L), ("P3 · feature", C['mint'])]):
            s.append(f'<path d="M{x + 190} {y + 100}L{x + 214} {y + 52 + i * 48}" stroke="{col}" stroke-opacity=".5"/>')
            s.append(f'<rect x="{x + 214}" y="{y + 40 + i * 48}" width="84" height="24" rx="12" fill="none" stroke="{col}"/>')
            s.append(text(x + 256, y + 56 + i * 48, lb, 10, col, 'mono', 'middle'))
        s.append(text(x + 18, y + 186, "draft ready · waiting for approval", 10, C['mint'], 'mono'))
        return "".join(s)
    if kind == "seats":
        s = [f'<rect x="{x}" y="{y}" width="310" height="200" rx="16" fill="{C["bg0"]}" stroke="{C["line2"]}"/>',
             text(x + 18, y + 26, "200 buyers → seat C5", 10, C['muted'], 'mono')]
        for r in range(4):
            for c in range(8):
                sx, sy = x + 30 + c * 32, y + 44 + r * 28
                tgt = (r, c) == (2, 4)
                booked = (r * 8 + c) % 5 == 1
                col = C['mint'] if tgt else (C['rose'] if booked else L)
                op = ".9" if tgt else (".35" if booked else ".1")
                s.append(f'<rect x="{sx}" y="{sy}" width="24" height="20" rx="5" fill="{col}" fill-opacity="{op}" stroke="{col}" stroke-opacity=".6"/>')
        tx, ty = x + 30 + 4 * 32 + 12, y + 44 + 2 * 28 + 10
        for i, (dx, dy) in enumerate([(-130, -30), (130, -30), (130, 26)]):
            s.append(f'<circle r="5" fill="{S}"><animateMotion dur="2s" begin="{i * 0.15}s" repeatCount="indefinite" path="M{tx + dx} {ty + dy}L{tx} {ty}"/><animate attributeName="opacity" values="1;1;0" keyTimes="0;.8;1" dur="2s" begin="{i * 0.15}s" repeatCount="indefinite"/></circle>')
        s.append(text(x + 18, y + 186, "1 × 201 Created · 199 × 409", 10, C['mint'], 'mono'))
        return "".join(s)
    if kind == "loom":
        s = [f'<rect x="{x}" y="{y}" width="310" height="200" rx="16" fill="{C["bg0"]}" stroke="{C["line2"]}"/>',
             text(x + 18, y + 26, "github.com/you", 10, C['muted'], 'mono')]
        cols = [L, C['rose'], C['mint'], V, S]
        for r in range(6):
            for k in range(9):
                over = (r + k) % 2 == 0
                s.append(f'<rect x="{x + 22 + k * 30}" y="{y + 42 + r * 20}" width="{24 if over else 10}" height="12" rx="3" fill="{cols[(r + k) % len(cols)]}" fill-opacity="{.85 if over else .25}"/>')
        s.append(f'<rect x="{x + 22}" y="{y + 166}" width="0" height="12" rx="3" fill="{C["lav"]}"><animate attributeName="width" values="0;266;266" keyTimes="0;.7;1" dur="2.6s" repeatCount="indefinite"/></rect>')
        s.append(text(x + 18, y + 192, "→ yourname.github.io", 10, C['mint'], 'mono'))
        return "".join(s)
    if kind == "wave":
        pts = " ".join(f"{x + 20 + i * 2.7:.1f},{y + 90 + 22 * math.sin(i / 6) * (1 + (i > 70) * 0.9):.1f}" for i in range(100))
        return f"""
<rect x="{x}" y="{y}" width="310" height="200" rx="16" fill="{C['bg0']}" stroke="{C['line2']}"/>
{text(x + 18, y + 26, "IMU-1 · IMU-2 · load cells", 10, C['muted'], 'mono')}
<polyline points="{pts}" fill="none" stroke="{L}" stroke-width="1.6" stroke-dasharray="600" stroke-dashoffset="600">
  <animate attributeName="stroke-dashoffset" values="600;0;0" keyTimes="0;.7;1" dur="4s" repeatCount="indefinite"/>
</polyline>
<rect x="{x + 210}" y="{y + 40}" width="80" height="100" fill="{C['rose']}" fill-opacity=".08" stroke="{C['rose']}" stroke-dasharray="3 3"/>
{text(x + 250, y + 156, "FALL RISK ↑", 10, C['rose'], 'mono', 'middle')}
<rect x="{x + 18}" y="{y + 168}" width="274" height="8" rx="4" fill="{C['panel']}"/>
<rect x="{x + 18}" y="{y + 168}" width="40" height="8" rx="4" fill="url(#proj-risk)">
  <animate attributeName="width" values="40;40;250;250" keyTimes="0;.5;.75;1" dur="4s" repeatCount="indefinite"/>
</rect>"""
    if kind == "grid":
        s = [f'<rect x="{x}" y="{y}" width="310" height="200" rx="16" fill="{C["bg0"]}" stroke="{C["line2"]}"/>']
        hz = {(2, 1), (5, 3), (7, 0), (3, 4)}
        for gx in range(9):
            for gy in range(5):
                cx, cy = x + 20 + gx * 31, y + 20 + gy * 32
                h = (gx, gy) in hz
                s.append(f'<rect x="{cx}" y="{cy}" width="27" height="28" rx="5" fill="{C["rose"] if h else L}" fill-opacity="{.35 if h else .06}"/>')
        path = "M{0} {1}H{2}V{3}H{4}V{5}H{6}".format(x + 33, y + 34, x + 126, y + 162, x + 250, y + 98, x + 282)
        s.append(f'<path d="{path}" fill="none" stroke="{S}" stroke-opacity=".5" stroke-dasharray="3 4"/>')
        s.append(f'<circle r="7" fill="{C["lilac"]}"><animateMotion dur="6s" repeatCount="indefinite" path="{path}"/></circle>')
        s.append(text(x + 18, y + 192, "ε-greedy · hazards found: 4/4", 10, C['mint'], 'mono'))
        return "".join(s)
    if kind == "fresh":
        s = [f'<rect x="{x}" y="{y}" width="310" height="200" rx="16" fill="{C["bg0"]}" stroke="{C["line2"]}"/>']
        items = [("mango", 0.85, C['mint'], "4d"), ("tomato", 0.55, L, "2d"), ("banana", 0.2, C['rose'], "today")]
        for i, (lb, v, col, d) in enumerate(items):
            yy = y + 36 + i * 54
            s.append(f'<circle cx="{x + 36}" cy="{yy + 8}" r="16" fill="{col}" fill-opacity=".2" stroke="{col}"/>')
            s.append(text(x + 64, yy + 4, lb, 12, S, 'mono'))
            s.append(text(x + 292, yy + 4, f"expires {d}", 10, col, 'mono', 'end'))
            s.append(f'<rect x="{x + 64}" y="{yy + 12}" width="228" height="6" rx="3" fill="{C["panel"]}"/>')
            s.append(f'<rect x="{x + 64}" y="{yy + 12}" width="0" height="6" rx="3" fill="{col}"><animate attributeName="width" values="0;{228 * v:.0f};{228 * v:.0f}" keyTimes="0;.4;1" dur="4s" repeatCount="indefinite"/></rect>')
        return "".join(s)
    return ""


def build_project(p, idx):
    W, H, u = 1200, 318, "proj"
    x = 40
    built = wrap(p["built"], 84)
    stats = []
    for k, (big, small) in enumerate(p["stats"]):
        sx = x + k * 225
        stats.append(text(sx, 222, big, 30, C['silver'], 'serif') + text(sx, 245, small, 13, C['muted'], 'sans'))
    body = f"""
{frame(W, H, u, (0.8, 0.4))}
<defs><linearGradient id="proj-risk" x1="0" x2="1"><stop offset="0" stop-color="{C['mint']}"/><stop offset="1" stop-color="{C['rose']}"/></linearGradient></defs>
{text(x, 44, p['kicker'], 11, C['lav'], 'mono', 'start', 'letter-spacing="3"')}
{text(x - 2, 96, p['name'], 44, f"url(#{u}-silver)", 'serif')}
{text(x, 128, p['pitch'], 17, C['mist'], 'serif', 'start', 'font-style="italic"')}
{''.join(text(x, 154 + i * 18, ('BUILT › ' if i == 0 else '         ') + ln, 12, C['muted'], 'mono') for i, ln in enumerate(built[:2]))}
<rect x="{x}" y="186" width="680" height="1" fill="{C['line2']}"/>
{''.join(stats)}
{chips(x, 264, p['tags'], size=10.5, maxw=700)}
<g class="float">{motif(p['motif'], 850, 54)}</g>
"""
    desc = f"{p['name']}: {p['pitch']} {p['built']}. " + "; ".join(f"{a} {b}" for a, b in p["stats"]) + ". Tech: " + ", ".join(p["tags"])
    write(f"project-{p['slug']}.svg", svg(W, H, u, p["name"], desc, body))


# ---------------------------------------------------------------- compact project tiles (two per row)
def build_project_tile(p, idx):
    W, H, u = 580, 312, f"pt{idx}"
    x = 28
    pitch = wrap(p["pitch"], 40)
    parts = [frame(W, H, u, (0.85, 0.2)),
             f'<defs><linearGradient id="proj-risk" x1="0" x2="1"><stop offset="0" stop-color="{C["mint"]}"/><stop offset="1" stop-color="{C["rose"]}"/></linearGradient></defs>',
             f'<g class="float"><g transform="translate(384 22) scale(.58)">{motif(p["motif"], 0, 0)}</g></g>',
             text(x, 44, p["kicker"].split(" · ", 1)[-1] if p["kicker"][:2].isdigit() else p["kicker"], 10, C['lav'], 'mono', 'start', 'letter-spacing="2"'),
             text(x - 1, 80, p["name"], 28 if len(p["name"]) < 16 else 23, f"url(#{u}-silver)", 'serif')]
    for i, ln in enumerate(pitch[:3]):
        parts.append(text(x, 108 + i * 20, ln, 14.5, C['mist'], 'serif', 'start', 'font-style="italic"'))
    parts.append(f'<rect x="{x}" y="170" width="{W - 2 * x}" height="1" fill="{C["line2"]}"/>')
    for k, (big, small) in enumerate(p["stats"]):
        sx = x + k * 178
        parts.append(text(sx, 202, big, 22, C['silver'], 'serif'))
        for j, ln in enumerate(wrap(small, 24)[:2]):
            parts.append(text(sx, 222 + j * 14, ln, 11, C['muted'], 'sans'))
    parts.append(chips(x, 254, p["tags"][:5], size=10, maxw=W - 2 * x - 70))
    parts.append(text(W - 22, H - 20, "open ↗", 11, C['muted'], 'mono', 'end'))
    desc = f"{p['name']}: {p['pitch']} " + "; ".join(f"{a} {b}" for a, b in p["stats"]) + ". Tech: " + ", ".join(p["tags"])
    write(f"tile-{p['slug']}.svg", svg(W, H, u, p["name"], desc, "".join(parts)))


def build_more():
    W, H, u = 1200, 220, "more"
    parts = [frame(W, H, u, (0.5, 0.3))]
    for k, (name, what, tags) in enumerate(MORE_PROJECTS):
        x = 32 + k * 576
        parts.append(f"""
<rect x="{x}" y="26" width="560" height="168" rx="18" fill="{C['panel']}" stroke="{C['line2']}"/>
{text(x + 24, 54, f"{9 + k:02d} · MORE", 11, C['lav'], 'mono', 'start', 'letter-spacing="3"')}
{text(x + 24, 88, name, 24, C['silver'], 'serif')}
{''.join(text(x + 24, 116 + i * 19, ln, 13, C['muted'], 'sans') for i, ln in enumerate(wrap(what, 72)[:2]))}
{chips(x + 24, 152, tags, size=10.5)}""")
    desc = "; ".join(f"{n}: {w}" for n, w, _ in MORE_PROJECTS)
    write("project-more.svg", svg(W, H, u, "More projects", desc, "".join(parts)))


# ---------------------------------------------------------------- currently building
def build_building():
    W, H = 1200, 70 + 66 * len(BUILDING)
    u = "bld"
    parts = [frame(W, H, u, (0.2, 0.4))]
    for k, (name, what, status, prog) in enumerate(BUILDING):
        y = 32 + k * 66
        parts.append(f'<rect x="32" y="{y}" width="1136" height="54" rx="14" fill="{C["panel"]}" stroke="{C["line2"]}"/>')
        parts.append(text(56, y + 34, f"0{k + 1}", 12, C['dim'], 'mono'))
        parts.append(text(96, y + 35, name, 20, C['silver'], 'serif'))
        parts.append(text(300, y + 33, what, 14, C['muted'], 'sans'))
        bx = 900
        if prog > 0:
            parts.append(f'<rect x="{bx}" y="{y + 24}" width="120" height="6" rx="3" fill="{C["bg0"]}"/>')
            parts.append(f'<rect x="{bx}" y="{y + 24}" width="{120 * prog:.0f}" height="6" rx="3" fill="{C["mint"]}"><animate attributeName="opacity" values=".5;1;.5" dur="2s" repeatCount="indefinite"/></rect>')
            col = C['mint']
        elif prog < 0:
            col = C['rose']
            parts.append(f'<circle class="pulse" cx="{bx + 8}" cy="{y + 27}" r="4" fill="{col}"/>')
        else:
            col = C['lav']
            parts.append(f'<path d="M{bx} {y + 27}H{bx + 120}" stroke="{col}" stroke-opacity=".5" stroke-dasharray="2 5"/>')
        parts.append(text(1150, y + 32, status, 10.5, col, 'mono', 'end', 'letter-spacing="2"'))
    desc = "; ".join(f"{n} ({s.lower()}): {w}" for n, w, s, _ in BUILDING)
    write("building.svg", svg(W, H, u, "Currently building", desc, "".join(parts)))


# ---------------------------------------------------------------- toolkit
def build_toolkit():
    W, H, u = 1200, 544, "tool"
    parts = [frame(W, H, u, (0.5, 0.5))]
    cols = 5
    cw, ch = (W - 64 - (cols - 1) * 12) // cols, 232
    for k, (lab, items) in enumerate(TOOLKIT):
        col, row = k % cols, k // cols
        x, y = 32 + col * (cw + 12), 32 + row * (ch + 16)
        parts.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="16" fill="{C["panel"]}" stroke="{C["line2"]}"/>')
        parts.append(text(x + 20, y + 32, lab, 11, C['lav'], 'mono', 'start', 'letter-spacing="1.5"'))
        sizes = [24, 19, 17, 15, 14]
        yy = y + 74
        for i, it in enumerate(items):
            sz = sizes[min(i, 4)]
            fill = C['silver'] if i < 2 else C['mist'] if i < 3 else C['muted']
            parts.append(text(x + 20, yy, it, sz, fill, 'serif'))
            yy += sz + 12
        parts.append(f'<rect x="{x + 20}" y="{y + ch - 12}" width="40" height="2" rx="1" fill="{C["lav"]}"><animate attributeName="width" values="40;{cw - 40};40" dur="{6 + k}s" repeatCount="indefinite"/></rect>')
    desc = "; ".join(f"{l[3:].title()}: {', '.join(i)}" for l, i in TOOLKIT)
    write("toolkit.svg", svg(W, H, u, "Tech and tools", desc, "".join(parts)))


# ---------------------------------------------------------------- milestones
def build_milestones():
    rowh = 66
    W, H, u = 1200, 50 + rowh * len(MILESTONES), "mile"
    parts = [frame(W, H, u, (0.8, 0.3))]
    parts.append(f'<path d="M110 40V{H - 40}" stroke="{C["line2"]}"/>')
    for k, (badge, head, detail) in enumerate(MILESTONES):
        y = 34 + k * rowh
        bw = max(mono_w(badge, 10.5) + 22, 64)
        parts.append(f'<rect x="{110 - bw / 2:.0f}" y="{y + 10}" width="{bw:.0f}" height="24" rx="12" fill="{C["bg0"]}" stroke="{C["lav"]}"/>')
        parts.append(text(110, y + 26, badge, 10.5, C['lilac'], 'mono', 'middle', 'letter-spacing="1.5"'))
        parts.append(text(190, y + 24, head, 20, C['silver'], 'serif'))
        lines = wrap(detail, 120)
        parts.append(text(190, y + 46, lines[0], 13, C['muted'], 'sans'))
        if len(lines) > 1:
            parts[-1] = text(190, y + 46, " ".join(lines), 12.5, C['muted'], 'sans')
    desc = "; ".join(f"{h}: {d}" for _, h, d in MILESTONES)
    write("milestones.svg", svg(W, H, u, "Milestones", desc, "".join(parts)))


# ---------------------------------------------------------------- portfolio games
def game_icon(kind, x, y):
    L, R, M, S = C['lav'], C['rose'], C['mint'], C['silver']
    if kind == "walker":
        return f'<g stroke="{S}" stroke-width="2" fill="none"><path d="M{x - 18} {y + 26}V{y - 18}H{x + 18}V{y + 26}"/><path d="M{x - 18} {y}H{x + 18}"/></g><circle cx="{x}" cy="{y - 30}" r="5" fill="{R}"><animate attributeName="cy" values="{y - 30};{y - 24};{y - 30}" dur="1.2s" repeatCount="indefinite"/></circle>'
    if kind == "mango":
        return f'<ellipse cx="{x}" cy="{y}" rx="20" ry="26" fill="{M}" fill-opacity=".3" stroke="{M}"><animate attributeName="fill" values="{M};#E9C46A;{R};{M}" dur="5s" repeatCount="indefinite"/></ellipse><path d="M{x} {y - 26}q6 -10 14 -8" stroke="{M}" fill="none"/>'
    if kind == "hunt":
        dots = "".join(f'<circle cx="{x + dx}" cy="{y + dy}" r="6" fill="{R if (dx, dy) == (14, 12) else L}" fill-opacity=".7"/>' for dx, dy in [(-18, -14), (14, -16), (-12, 14), (14, 12)])
        return dots + f'<circle cx="{x}" cy="{y}" r="16" fill="none" stroke="{S}" stroke-width="2"><animateMotion dur="4s" repeatCount="indefinite" path="M0 0L-14 -12L12 -14L-10 12L12 12Z"/></circle>'
    return text(x, y + 14, "あ", 40, S, 'serif', 'middle') + f'<circle cx="{x}" cy="{y}" r="30" fill="none" stroke="{L}" stroke-dasharray="4 6" class="spin" style="transform-origin:{x}px {y}px"/>'


def build_games():
    W, H, u = 1200, 360, "game"
    parts = [frame(W, H, u, (0.5, 0.2))]
    parts.append(text(600, 50, "My portfolio isn't just a page to read. It has 4 mini-games built from my projects.", 17, C['mist'], 'serif', 'middle', 'font-style="italic"'))
    for k, (name, what, icon) in enumerate(GAMES):
        x = 32 + k * 287
        parts.append(f"""
<g>
<rect x="{x}" y="76" width="273" height="190" rx="18" fill="{C['panel']}" stroke="{C['line2']}"/>
{text(x + 20, 102, f"GAME 0{k + 1}", 10.5, C['lav'], 'mono', 'start', 'letter-spacing="2.5"')}
{game_icon(icon, x + 136, 150)}
{text(x + 136, 224, name, 19, C['silver'], 'serif', 'middle')}
{text(x + 136, 248, what, 12.5, C['muted'], 'sans', 'middle')}
</g>""")
    parts.append(f'<text x="600" y="310" class="sans" font-size="14" fill="{C["muted"]}" text-anchor="middle">Plus a <tspan fill="{C["silver"]}">3D LIDAR hero</tspan>, a <tspan fill="{C["silver"]}">"Hiring for…" switch</tspan> that reshapes the page for your role, and <tspan fill="{C["silver"]}">Detection mode</tspan> (press <tspan class="mono" fill="{C["lilac"]}">D</tspan>).</text>')
    parts.append(text(600, 338, "hemashreevi.github.io", 12, C['lav'], 'mono', 'middle', 'letter-spacing="3"'))
    desc = "Portfolio mini-games: " + "; ".join(f"{n}: {w}" for n, w, _ in GAMES) + ". Plus a 3D LIDAR hero, a Hiring-for switch and Detection mode (press D)."
    write("games.svg", svg(W, H, u, "Play on my portfolio", desc, "".join(parts)))


# ---------------------------------------------------------------- open source
def build_opensource():
    W, H, u = 1200, 330, "oss"
    repo, num, title, status = OPEN_SOURCE_PR
    parts = [frame(W, H, u, (0.25, 0.35))]
    # left: the merged pull request, drawn as a branch merging back into main
    parts.append(f'<rect x="32" y="28" width="440" height="274" rx="18" fill="{C["panel"]}" stroke="{C["line2"]}"/>')
    parts.append(text(56, 60, "CONTRIBUTION", 11, C['lav'], 'mono', 'start', 'letter-spacing="3"'))
    parts.append(f'<rect x="324" y="44" width="124" height="24" rx="12" fill="#8957E5" fill-opacity=".22" stroke="#A371F7"/>')
    parts.append(text(386, 60, status.split(" ·")[0], 10.5, "#D2A8FF", 'mono', 'middle', 'letter-spacing="2"'))
    parts.append(text(56, 102, "first-contributions", 26, C['silver'], 'serif'))
    parts.append(text(56, 126, f"{repo} {num}", 12, C['muted'], 'mono'))
    parts.append(text(56, 152, f"“{title}”", 15, C['mist'], 'serif', 'start', 'font-style="italic"'))
    y0, y1 = 236, 204
    parts.append(f'<path d="M56 {y0}H424" stroke="{C["muted"]}" stroke-width="3" stroke-linecap="round"/>')
    parts.append(f'<path d="M110 {y0}C140 {y0} 140 {y1} 170 {y1}H300C330 {y1} 330 {y0} 360 {y0}" fill="none" stroke="#A371F7" stroke-width="3"/>')
    for cx in (80, 110, 360, 400):
        parts.append(f'<circle cx="{cx}" cy="{y0}" r="7" fill="{C["bg0"]}" stroke="{C["muted"]}" stroke-width="3"/>')
    for cx in (200, 250):
        parts.append(f'<circle cx="{cx}" cy="{y1}" r="7" fill="{C["bg0"]}" stroke="#A371F7" stroke-width="3"/>')
    parts.append(f'<circle r="5" fill="#fff"><animateMotion dur="3.2s" repeatCount="indefinite" path="M110 {y0}C140 {y0} 140 {y1} 170 {y1}H300C330 {y1} 330 {y0} 360 {y0}"/></circle>')
    parts.append(f'<circle class="pulse" cx="360" cy="{y0}" r="10" fill="none" stroke="#A371F7" stroke-width="2"/>')
    parts.append(text(56, 278, "main", 11, C['muted'], 'mono') + text(200, 186, "my branch", 11, "#D2A8FF", 'mono'))
    parts.append(text(424, 278, status.split("· ")[1], 11, C['muted'], 'mono', 'end', 'letter-spacing="2"'))
    # right: my own open-source tools
    parts.append(text(504, 60, "MY OPEN-SOURCE TOOLS · MIT LICENSED", 11, C['lav'], 'mono', 'start', 'letter-spacing="3"'))
    parts.append(text(1168, 60, "14 MIT REPOS · FREE TO USE &amp; FORK".replace("&amp;", "&"), 11, C['mint'], 'mono', 'end', 'letter-spacing="2"'))
    for k, (name, what) in enumerate(OPEN_SOURCE_REPOS):
        col, row = k % 2, k // 2
        x, y = 504 + col * 336, 80 + row * 56
        parts.append(f'<rect x="{x}" y="{y}" width="324" height="46" rx="12" fill="{C["panel"]}" stroke="{C["line2"]}"/>')
        parts.append(f'<circle class="pulse" cx="{x + 20}" cy="{y + 23}" r="4" fill="{[C["mint"], C["lav"], C["rose"]][k % 3]}" style="animation-delay:{k * .3:.1f}s"/>')
        parts.append(text(x + 36, y + 21, name, 15, C['silver'], 'serif'))
        parts.append(text(x + 36, y + 37, what, 11.5, C['muted'], 'sans'))
    desc = (f"Open source. Merged pull request {num} to {repo}: {title}. "
            "My own MIT-licensed tools: " + "; ".join(f"{n}: {w}" for n, w in OPEN_SOURCE_REPOS) + ".")
    write("opensource.svg", svg(W, H, u, "Open source", desc, "".join(parts)))


# ---------------------------------------------------------------- youtube
def build_youtube():
    W, H, u = 1200, 330, "yt"
    y = YOUTUBE
    RED = "#FF0033"
    parts = [frame(W, H, u, (0.75, 0.4))]
    parts.append(f'<radialGradient id="yt-red" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{RED}" stop-opacity=".35"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>')
    parts.append(f'<ellipse cx="860" cy="165" rx="360" ry="200" fill="url(#yt-red)"/>')
    # left: channel identity
    parts.append(f'<g transform="translate(40 40)"><rect width="68" height="48" rx="14" fill="{RED}"/><path d="M27 14L45 24L27 34Z" fill="#fff"/></g>')
    parts.append(text(124, 60, "YOUTUBE CHANNEL", 11, "#FF8FA3", 'mono', 'start', 'letter-spacing="3"'))
    parts.append(text(124, 84, y["handle"] + " · 60+ videos", 16, C['mist'], 'mono'))
    parts.append(text(38, 152, y["pitch"], 44, f"url(#{u}-silver)", 'serif'))
    parts.append(text(40, 186, y["line"], 15, C['muted'], 'sans'))
    # subscribe button with a ringing bell
    parts.append(f'<g transform="translate(40 216)"><rect width="190" height="50" rx="25" fill="{RED}"><animate attributeName="opacity" values="1;.82;1" dur="2s" repeatCount="indefinite"/></rect>'
                 f'<text x="78" y="31" class="sans" font-size="16" font-weight="700" fill="#fff" letter-spacing="1.5">SUBSCRIBE</text>'
                 f'<g transform="translate(40 25)"><g><path d="M-9 6V-1a9 9 0 0 1 18 0V6l3 3H-12Z M-3 11a3 3 0 0 0 6 0" fill="#fff"/>'
                 f'<animateTransform attributeName="transform" type="rotate" values="0;18;-18;12;-12;0;0" keyTimes="0;.06;.12;.18;.24;.3;1" dur="3s" repeatCount="indefinite"/></g></g></g>')
    parts.append(text(250, 248, "▸ click anywhere on this card", 12, C['dim'], 'mono'))
    # right: a video player mock with a pulsing play button and a progress bar
    vx, vy, vw, vh = 640, 34, 520, 262
    parts.append(f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="16" fill="{C["bg0"]}" stroke="{C["line2"]}"/>')
    parts.append(f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="16" fill="url(#{u}-grid)"/>')
    for k in range(5):
        bx = vx + 40 + k * 92
        hgt = 40 + (k * 37) % 70
        parts.append(f'<rect x="{bx}" y="{vy + 190 - hgt}" width="56" height="{hgt}" rx="6" fill="{[C["lav"], C["rose"], C["mint"]][k % 3]}" fill-opacity=".18">'
                     f'<animate attributeName="height" values="{hgt};{hgt + 30};{hgt}" dur="{2 + k * .4:.1f}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="y" values="{vy + 190 - hgt};{vy + 160 - hgt};{vy + 190 - hgt}" dur="{2 + k * .4:.1f}s" repeatCount="indefinite"/></rect>')
    cx, cy = vx + vw / 2, vy + 112
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="44" fill="{RED}" fill-opacity=".25"><animate attributeName="r" values="40;58;40" dur="2.4s" repeatCount="indefinite"/><animate attributeName="fill-opacity" values=".35;0;.35" dur="2.4s" repeatCount="indefinite"/></circle>')
    parts.append(f'<rect x="{cx - 42}" y="{cy - 30}" width="84" height="60" rx="18" fill="{RED}"/><path d="M{cx - 11} {cy - 15}L{cx + 15} {cy}L{cx - 11} {cy + 15}Z" fill="#fff"/>')
    py = vy + vh - 34
    parts.append(f'<rect x="{vx + 24}" y="{py}" width="{vw - 48}" height="5" rx="2.5" fill="{C["line2"]}"/>')
    parts.append(f'<rect x="{vx + 24}" y="{py}" width="0" height="5" rx="2.5" fill="{RED}"><animate attributeName="width" values="0;{vw - 48}" dur="8s" repeatCount="indefinite"/></rect>')
    parts.append(f'<circle cy="{py + 2.5}" r="7" fill="{RED}"><animate attributeName="cx" values="{vx + 24};{vx + vw - 24}" dur="8s" repeatCount="indefinite"/></circle>')
    parts.append(text(vx + 24, py - 12, "▶ NEW VIDEOS", 11, C['mist'], 'mono', 'start', 'letter-spacing="2"'))
    parts.append(text(vx + vw - 24, py - 12, y["handle"], 11, C['muted'], 'mono', 'end'))
    desc = f"My YouTube channel Byte Decoded ({y['handle']}): {y['line']} Click to subscribe."
    write("youtube.svg", svg(W, H, u, f"Byte Decoded on YouTube", desc, "".join(parts)))


# ---------------------------------------------------------------- social icons
SOCIAL_ICONS = {
    "gmail": ("Gmail", '<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#EEF1F6"/></linearGradient>',
             '<g fill="none" stroke-width="7.5">'
             '<path d="M14.5 47V25" stroke="#4285F4" stroke-linecap="butt"/>'
             '<path d="M49.5 47V25" stroke="#34A853" stroke-linecap="butt"/>'
             '<path d="M14.5 24L32 37.5L49.5 24" stroke="#EA4335" stroke-linecap="round" stroke-linejoin="round"/>'
             '<path d="M14.5 31V24L19.5 27.8" stroke="#C5221F" stroke-linecap="round" stroke-linejoin="round"/>'
             '<path d="M49.5 31V24L44.5 27.8" stroke="#FBBC04" stroke-linecap="round" stroke-linejoin="round"/>'
             '</g>'),
    "linkedin": ("LinkedIn", '<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2D8CFF"/><stop offset="1" stop-color="#0A66C2"/></linearGradient>',
                 '<circle cx="21" cy="19.5" r="4.6" fill="#fff"/><rect x="16.6" y="27" width="8.8" height="22" rx="1.5" fill="#fff"/>'
                 '<path d="M30 27h8.4v3.2c1.4-2.3 3.9-3.8 7-3.8 5.2 0 7.6 3.3 7.6 9V49h-8.8V37.2c0-2.8-1-4.4-3.4-4.4-2.6 0-4 1.8-4 4.6V49H30Z" fill="#fff"/>'),
    "youtube": ("YouTube", '<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FF4D5E"/><stop offset="1" stop-color="#E00022"/></linearGradient>',
                '<rect x="12" y="18" width="40" height="28" rx="9" fill="#fff"/><path d="M28 24.5L39 32L28 39.5Z" fill="#E00022"/>'),
    "portfolio": ("Portfolio", '<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#22D3EE"/><stop offset=".5" stop-color="#8B5CF6"/><stop offset="1" stop-color="#F472B6"/></linearGradient>',
                  '<rect x="12" y="16" width="40" height="32" rx="6" fill="none" stroke="#fff" stroke-width="3.4"/>'
                  '<path d="M12 25H52" stroke="#fff" stroke-width="3"/>'
                  '<circle cx="17.5" cy="20.6" r="1.6" fill="#fff"/><circle cx="22.5" cy="20.6" r="1.6" fill="#fff"/><circle cx="27.5" cy="20.6" r="1.6" fill="#fff"/>'
                  '<path d="M27 31.5L22 36.5L27 41.5M37 31.5L42 36.5L37 41.5" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
                  '<path d="M48 6.5l1.6 3.9 3.9 1.6-3.9 1.6L48 17.5l-1.6-3.9-3.9-1.6 3.9-1.6Z" fill="#FDE68A" stroke="#fff" stroke-width=".8"/>'),
    "leetcode": ("LeetCode", '<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2B2B2B"/><stop offset="1" stop-color="#121212"/></linearGradient>',
                 '<g fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-width="5">'
                 '<path d="M37 13L21.5 29.5a4 4 0 0 0 0 5.5L33 47a4 4 0 0 0 5.6 0.2L42 44" stroke="#FFFFFF"/>'
                 '<path d="M23 27L35 14" stroke="#FFA116"/>'
                 '<path d="M29 32.5H46" stroke="#B3B3B3"/>'
                 '</g>'),
    "chesscom": ("Chess.com",
              '<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3D3A36"/><stop offset="1" stop-color="#211F1C"/></linearGradient>'
              '<linearGradient id="pw" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#B5E26E"/><stop offset=".55" stop-color="#81B64C"/><stop offset="1" stop-color="#5A8A2A"/></linearGradient>'
              '<radialGradient id="glow" cx="50%" cy="60%" r="50%"><stop offset="0" stop-color="#81B64C" stop-opacity=".45"/><stop offset="1" stop-color="#81B64C" stop-opacity="0"/></radialGradient>'
              '<clipPath id="tile"><rect width="64" height="64" rx="16"/></clipPath>',
              '<g clip-path="url(#tile)"><g fill="#fff" fill-opacity=".05"><rect x="0" y="36" width="8" height="8"/><rect x="16" y="36" width="8" height="8"/><rect x="32" y="36" width="8" height="8"/><rect x="48" y="36" width="8" height="8"/><rect x="8" y="44" width="8" height="8"/><rect x="24" y="44" width="8" height="8"/><rect x="40" y="44" width="8" height="8"/><rect x="56" y="44" width="8" height="8"/><rect x="0" y="52" width="8" height="8"/><rect x="16" y="52" width="8" height="8"/><rect x="32" y="52" width="8" height="8"/><rect x="48" y="52" width="8" height="8"/><rect x="8" y="60" width="8" height="8"/><rect x="24" y="60" width="8" height="8"/><rect x="40" y="60" width="8" height="8"/><rect x="56" y="60" width="8" height="8"/></g></g>'
              '<circle cx="32" cy="34" r="24" fill="url(#glow)"/>'
              '<ellipse cx="32" cy="54" rx="15" ry="2.6" fill="#000" fill-opacity=".45"/>'
              '<g fill="url(#pw)" stroke="#3F6B17" stroke-width="1.2" stroke-linejoin="round">'
              '<path d="M27.5 30.5C27.5 37.5 24.5 42.5 20.5 46.5H43.5C39.5 42.5 36.5 37.5 36.5 30.5Z"/>'
              '<rect x="22.5" y="26.5" width="19" height="5" rx="2.5"/>'
              '<circle cx="32" cy="17.5" r="8"/>'
              '<rect x="15.5" y="46" width="33" height="7" rx="3.5"/>'
              '</g>'
              '<ellipse cx="29" cy="14.5" rx="3.2" ry="2.2" fill="#fff" fill-opacity=".55" transform="rotate(-30 29 14.5)"/>'
              '<path d="M29.5 32.5C29.5 37.5 27.8 41.5 25 44.5" stroke="#fff" stroke-opacity=".4" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
              '<rect x="18.5" y="47.6" width="14" height="1.6" rx=".8" fill="#fff" fill-opacity=".4"/>'),
    "instagram": ("Instagram", '<radialGradient id="g" cx="30%" cy="107%" r="150%"><stop offset="0" stop-color="#FDF497"/><stop offset=".05" stop-color="#FDF497"/><stop offset=".45" stop-color="#FD5949"/><stop offset=".6" stop-color="#D6249F"/><stop offset=".9" stop-color="#285AEB"/></radialGradient>',
                  '<rect x="15" y="15" width="34" height="34" rx="10" fill="none" stroke="#fff" stroke-width="3.6"/><circle cx="32" cy="32" r="8" fill="none" stroke="#fff" stroke-width="3.6"/><circle cx="41.6" cy="22.4" r="2.5" fill="#fff"/>'),
}


def build_social_icons():
    out = ROOT / "assets" / "icons"
    for slug, (name, grad, glyph) in SOCIAL_ICONS.items():
        content = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" role="img" aria-label="{name}">'
                   f'<title>{name}</title><defs>{grad}</defs><rect width="64" height="64" rx="16" fill="url(#g)"/>{glyph}</svg>\n')
        (out / f"social-{slug}.svg").write_text(content, encoding="utf-8")
        print(f"  icons/social-{slug}.svg")


# ---------------------------------------------------------------- chrome extensions
def build_extensions():
    import re as _re
    W, H = 580, 236
    for k, x in enumerate(EXTENSIONS):
        u = f"ext{k}"
        icon = (ROOT / "assets" / "icons" / f"ext-{x['slug']}.svg").read_text()
        icon = _re.sub(r'id="(\w+)"', lambda m: f'id="{u}{m.group(1)}"', icon)
        icon = _re.sub(r'url\(#(\w+)\)', lambda m: f'url(#{u}{m.group(1)})', icon)
        icon = icon.replace('<svg ', '<svg x="28" y="30" width="72" height="72" ', 1)
        parts = [frame(W, H, u, (0.85, 0.25)),
                 f'<g class="float">{icon}</g>',
                 text(120, 54, f"0{k + 1} · CHROME EXTENSION", 10.5, C['lav'], 'mono', 'start', 'letter-spacing="2.5"'),
                 text(119, 86, x['name'], 27, f"url(#{u}-silver)", 'serif'),
                 text(120, 110, x['pitch'], 14.5, C['mist'], 'serif', 'start', 'font-style="italic"')]
        for i, pt in enumerate(x['points']):
            y = 140 + i * 21
            parts.append(f'<circle cx="34" cy="{y - 4}" r="3" fill="{[C["mint"], C["lav"], C["rose"]][i]}"/>')
            parts.append(text(46, y, pt, 12.5, C['silver'], 'sans'))
        parts.append(chips(28, 196, x['tags'], size=10))
        parts.append(text(W - 24, H - 22, "open repo ↗", 11, C['muted'], 'mono', 'end'))
        desc = f"{x['name']}: {x['pitch']} " + "; ".join(x['points']) + ". Built with " + ", ".join(x['tags']) + "."
        write(f"ext-{x['slug']}.svg", svg(W, H, u, x['name'], desc, "".join(parts)))


# ---------------------------------------------------------------- project cards (screenshot + headline number)
def build_showcase():
    W, H = 600, 492
    for k, p in enumerate(SHOWCASE):
        u = f"sc{k}"
        shot = base64.b64encode((ROOT / "assets" / "shots" / f"{p['slug']}.webp").read_bytes()).decode()
        ix, iy, iw, ih = 16, 46, 568, 325
        tag_w = len(p['tag']) * 7.4 + 26
        num_size = 40
        num_w = len(p['num']) * num_size * 0.6
        lines = wrap(p['desc'], 66)
        dots = "".join(f'<circle cx="{24 + i * 16}" cy="23" r="5" fill="{c}"/>' for i, c in enumerate(["#D97B7B", "#D9B96B", "#7FBF8F"]))
        body = f"""
{frame(W, H, u, (0.8, 0.15))}
{dots}
<text x="76" y="28" class="mono" font-size="13"><tspan fill="{C['muted']}">HemashreeVI /</tspan> <tspan fill="{C['silver']}" font-weight="600">{e(p['repo'])}</tspan></text>
<rect x="{W - 18 - tag_w:.0f}" y="12" width="{tag_w:.0f}" height="22" rx="11" fill="{C['panel']}" stroke="{C['line2']}"/>
<circle cx="{W - 18 - tag_w + 12:.0f}" cy="23" r="3" fill="{C['lav']}"/>
{text(W - 18 - tag_w / 2 + 5, 27.5, p['tag'], 11.5, C['mist'], 'sans', 'middle')}
<clipPath id="{u}-shot"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="10"/></clipPath>
<image x="{ix}" y="{iy}" width="{iw}" height="{ih}" preserveAspectRatio="xMidYMin slice" clip-path="url(#{u}-shot)" href="data:image/webp;base64,{shot}"/>
<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="10" fill="none" stroke="{C['line2']}"/>
<defs><linearGradient id="{u}-green" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7EE787"/><stop offset="1" stop-color="#3FB950"/></linearGradient></defs>
<text x="24" y="{iy + ih + 54}" class="mono" font-size="{num_size}" font-weight="700" fill="url(#{u}-green)">{e(p['num'])}</text>
{text(24 + num_w + 14, iy + ih + 52, p['label'], 15, C['muted'], 'sans')}
{"".join(text(24, iy + ih + 86 + i * 22, ln, 15, C['mist'], 'sans') for i, ln in enumerate(lines[:2]))}
"""
        desc = f"{p['repo']} ({p['tag']}): {p['num']} {p['label']}. {p['desc']} Screenshot from the project."
        write(f"show-{p['slug']}.svg", svg(W, H, u, p['repo'], desc, body))


# ---------------------------------------------------------------- ID card on a lanyard (About section)
GITHUB_PATH = ("M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04"
    "-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 "
    "1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303"
    "-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23"
    ".645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896"
    "-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12")


TECH_ICONS = [  # Simple Icons (simpleicons.org, CC0): name, brand colour, 24x24 path
    ('Java', '#F89820', 'M11.915 0 11.7.215C9.515 2.4 7.47 6.39 6.046 10.483c-1.064 1.024-3.633 2.81-3.711 3.551-.093.87 1.746 2.611 1.55 3.235-.198.625-1.304 1.408-1.014 1.939.1.188.823.011 1.277-.491a13.389 13.389 0 0 0-.017 2.14c.076.906.27 1.668.643 2.232.372.563.956.911 1.667.911.397 0 .727-.114 1.024-.264.298-.149.571-.33.91-.5.68-.34 1.634-.666 3.53-.604 1.903.062 2.872.39 3.559.704.687.314 1.15.664 1.925.664.767 0 1.395-.336 1.807-.9.412-.563.631-1.33.72-2.24.06-.623.055-1.32 0-2.066.454.45 1.117.604 1.213.424.29-.53-.816-1.314-1.013-1.937-.198-.624 1.642-2.366 1.549-3.236-.08-.748-2.707-2.568-3.748-3.586C16.428 6.374 14.308 2.394 12.13.215zm.175 6.038a2.95 2.95 0 0 1 2.943 2.942 2.95 2.95 0 0 1-2.943 2.943A2.95 2.95 0 0 1 9.148 8.98a2.95 2.95 0 0 1 2.942-2.942zM8.685 7.983a3.515 3.515 0 0 0-.145.997c0 1.951 1.6 3.55 3.55 3.55 1.95 0 3.55-1.598 3.55-3.55 0-.329-.046-.648-.132-.951.334.095.64.208.915.336a42.699 42.699 0 0 1 2.042 5.829c.678 2.545 1.01 4.92.846 6.607-.082.844-.29 1.51-.606 1.94-.315.431-.713.651-1.315.651-.593 0-.932-.27-1.673-.61-.741-.338-1.825-.694-3.792-.758-1.974-.064-3.073.293-3.821.669-.375.188-.659.373-.911.5s-.466.2-.752.2c-.53 0-.876-.209-1.16-.64-.285-.43-.474-1.101-.545-1.948-.141-1.693.176-4.069.823-6.614a43.155 43.155 0 0 1 1.934-5.783c.348-.167.749-.31 1.192-.425zm-3.382 4.362a.216.216 0 0 1 .13.031c-.166.56-.323 1.116-.463 1.665a33.849 33.849 0 0 0-.547 2.555 3.9 3.9 0 0 0-.2-.39c-.58-1.012-.914-1.642-1.16-2.08.315-.24 1.679-1.755 2.24-1.781zm13.394.01c.562.027 1.926 1.543 2.24 1.783-.246.438-.58 1.068-1.16 2.08a4.428 4.428 0 0 0-.163.309 32.354 32.354 0 0 0-.562-2.49 40.579 40.579 0 0 0-.482-1.652.216.216 0 0 1 .127-.03z'),
    ('Python', '#3776AB', 'M11.858 0c-.978.005-1.913.088-2.736.234C6.7.662 6.26 1.558 6.26 3.21v2.182h5.725v.727H4.111c-1.664 0-3.121 1-3.577 2.903-.526 2.181-.549 3.542 0 5.82.407 1.694 1.379 2.902 3.043 2.902h1.969v-2.616c0-1.89 1.635-3.557 3.576-3.557h5.72c1.591 0 2.862-1.31 2.862-2.91v-5.45c0-1.553-1.309-2.718-2.863-2.977A18 18 0 0 0 11.858 0M8.762 1.755c.591 0 1.074.491 1.074 1.095 0 .601-.483 1.087-1.074 1.087A1.08 1.08 0 0 1 7.688 2.85c0-.604.48-1.095 1.074-1.095m9.656 4.364v2.543c0 1.971-1.671 3.63-3.577 3.63H9.122c-1.566 0-2.862 1.34-2.862 2.91v5.452c0 1.551 1.349 2.464 2.862 2.91 1.813.532 3.55.628 5.72 0 1.44-.418 2.862-1.258 2.862-2.91V18.47h-5.719v-.727h8.582c1.664 0 2.284-1.16 2.862-2.903.598-1.793.573-3.518 0-5.819-.41-1.656-1.196-2.903-2.862-2.903zm-3.216 13.807a1.08 1.08 0 0 1 1.074 1.088c0 .604-.48 1.094-1.074 1.094-.592 0-1.075-.49-1.075-1.094 0-.601.483-1.088 1.075-1.088'),
    ('Spring Boot', '#6DB33F', 'm23.693 10.7058-4.73-8.1844c-.4094-.7106-1.4166-1.2942-2.2402-1.2942H7.2725c-.819 0-1.8308.5836-2.2402 1.2942L.307 10.7058c-.4095.7106-.4095 1.873 0 2.5837l4.7252 8.189c.4094.7107 1.4166 1.2943 2.2402 1.2943h9.455c.819 0 1.826-.5836 2.2402-1.2942l4.7252-8.189c.4095-.7107.4095-1.8732 0-2.5838zM10.9763 5.7547c0-.5365.4377-.9742.9742-.9742s.9742.4377.9742.9742v5.8217c0 .5366-.4377.9742-.9742.9742s-.9742-.4376-.9742-.9742zm.9742 12.4294c-3.6427 0-6.6077-2.965-6.6077-6.6077.0047-2.0896.993-4.0521 2.6685-5.304a.8657.8657 0 0 1 1.2142.1788.8657.8657 0 0 1-.1788 1.2143c-2.1602 1.6048-2.612 4.6592-1.0072 6.8194 1.6049 2.1603 4.6593 2.612 6.8195 1.0072 1.2378-.9177 1.9673-2.372 1.9673-3.9157a4.8972 4.8972 0 0 0-1.9861-3.925c-.386-.2824-.466-.8284-.1836-1.2143.2824-.386.8283-.466 1.2143-.1835 1.6895 1.2471 2.6826 3.2238 2.6873 5.3228 0 3.6474-2.965 6.6077-6.6077 6.6077z'),
    ('Docker', '#2496ED', 'M13.983 11.078h2.119a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.119a.185.185 0 00-.185.185v1.888c0 .102.083.185.185.185m-2.954-5.43h2.118a.186.186 0 00.186-.186V3.574a.186.186 0 00-.186-.185h-2.118a.185.185 0 00-.185.185v1.888c0 .102.082.185.185.185m0 2.716h2.118a.187.187 0 00.186-.186V6.29a.186.186 0 00-.186-.185h-2.118a.185.185 0 00-.185.185v1.887c0 .102.082.185.185.186m-2.93 0h2.12a.186.186 0 00.184-.186V6.29a.185.185 0 00-.185-.185H8.1a.185.185 0 00-.185.185v1.887c0 .102.083.185.185.186m-2.964 0h2.119a.186.186 0 00.185-.186V6.29a.185.185 0 00-.185-.185H5.136a.186.186 0 00-.186.185v1.887c0 .102.084.185.186.186m5.893 2.715h2.118a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.118a.185.185 0 00-.185.185v1.888c0 .102.082.185.185.185m-2.93 0h2.12a.185.185 0 00.184-.185V9.006a.185.185 0 00-.184-.186h-2.12a.185.185 0 00-.184.185v1.888c0 .102.083.185.185.185m-2.964 0h2.119a.185.185 0 00.185-.185V9.006a.185.185 0 00-.184-.186h-2.12a.186.186 0 00-.186.186v1.887c0 .102.084.185.186.185m-2.92 0h2.12a.185.185 0 00.184-.185V9.006a.185.185 0 00-.184-.186h-2.12a.185.185 0 00-.184.185v1.888c0 .102.082.185.185.185M23.763 9.89c-.065-.051-.672-.51-1.954-.51-.338.001-.676.03-1.01.087-.248-1.7-1.653-2.53-1.716-2.566l-.344-.199-.226.327c-.284.438-.49.922-.612 1.43-.23.97-.09 1.882.403 2.661-.595.332-1.55.413-1.744.42H.751a.751.751 0 00-.75.748 11.376 11.376 0 00.692 4.062c.545 1.428 1.355 2.48 2.41 3.124 1.18.723 3.1 1.137 5.275 1.137.983.003 1.963-.086 2.93-.266a12.248 12.248 0 003.823-1.389c.98-.567 1.86-1.288 2.61-2.136 1.252-1.418 1.998-2.997 2.553-4.4h.221c1.372 0 2.215-.549 2.68-1.009.309-.293.55-.65.707-1.046l.098-.288Z'),
    ('Kafka', '#E6EDF3', 'M9.71 2.136a1.43 1.43 0 0 0-2.047 0h-.007a1.48 1.48 0 0 0-.421 1.042c0 .41.161.777.422 1.039l.007.007c.257.264.616.426 1.019.426.404 0 .766-.162 1.027-.426l.003-.007c.261-.262.421-.629.421-1.039 0-.408-.159-.777-.421-1.042H9.71zM8.683 22.295c.404 0 .766-.167 1.027-.429l.003-.008c.261-.261.421-.631.421-1.036 0-.41-.159-.778-.421-1.044H9.71a1.42 1.42 0 0 0-1.027-.432 1.4 1.4 0 0 0-1.02.432h-.007c-.26.266-.422.634-.422 1.044 0 .406.161.775.422 1.036l.007.008c.258.262.617.429 1.02.429zm7.89-4.462c.359-.096.683-.33.882-.684l.027-.052a1.47 1.47 0 0 0 .114-1.067 1.454 1.454 0 0 0-.675-.896l-.021-.014a1.425 1.425 0 0 0-1.078-.132c-.36.091-.684.335-.881.686-.2.349-.241.75-.146 1.119.099.363.33.691.675.896h.002c.346.203.737.239 1.101.144zm-6.405-7.342a2.083 2.083 0 0 0-1.485-.627c-.58 0-1.103.242-1.482.627-.378.385-.612.916-.612 1.507s.233 1.124.612 1.514a2.08 2.08 0 0 0 2.967 0c.379-.39.612-.923.612-1.514s-.233-1.122-.612-1.507zm-.835-2.51c.843.141 1.6.552 2.178 1.144h.004c.092.093.182.196.265.299l1.446-.851a3.176 3.176 0 0 1-.047-1.808 3.149 3.149 0 0 1 1.456-1.926l.025-.016a3.062 3.062 0 0 1 2.345-.306c.77.21 1.465.721 1.898 1.482v.002c.431.757.518 1.626.313 2.408a3.145 3.145 0 0 1-1.456 1.928l-.198.118h-.02a3.095 3.095 0 0 1-2.154.201 3.127 3.127 0 0 1-1.514-.944l-1.444.848a4.162 4.162 0 0 1 0 2.879l1.444.846c.413-.47.939-.789 1.514-.944a3.041 3.041 0 0 1 2.371.319l.048.023v.002a3.17 3.17 0 0 1 1.408 1.906 3.215 3.215 0 0 1-.313 2.405l-.026.053-.003-.005a3.147 3.147 0 0 1-1.867 1.436 3.096 3.096 0 0 1-2.371-.318v-.006a3.156 3.156 0 0 1-1.456-1.927 3.175 3.175 0 0 1 .047-1.805l-1.446-.848a3.905 3.905 0 0 1-.265.294l-.004.005a3.938 3.938 0 0 1-2.178 1.138v1.699a3.09 3.09 0 0 1 1.56.862l.002.004c.565.572.914 1.368.914 2.243 0 .873-.35 1.664-.914 2.239l-.002.009a3.1 3.1 0 0 1-2.21.931 3.1 3.1 0 0 1-2.206-.93h-.002v-.009a3.186 3.186 0 0 1-.916-2.239c0-.875.35-1.672.916-2.243v-.004h.002a3.1 3.1 0 0 1 1.558-.862v-1.699a3.926 3.926 0 0 1-2.176-1.138l-.006-.005a4.098 4.098 0 0 1-1.173-2.874c0-1.122.452-2.136 1.173-2.872h.006a3.947 3.947 0 0 1 2.176-1.144V6.289a3.137 3.137 0 0 1-1.558-.864h-.002v-.004a3.192 3.192 0 0 1-.916-2.243c0-.871.35-1.669.916-2.243l.002-.002A3.084 3.084 0 0 1 8.683 0c.861 0 1.641.355 2.21.932v.002h.002c.565.574.914 1.372.914 2.243 0 .876-.35 1.667-.914 2.243l-.002.005a3.142 3.142 0 0 1-1.56.864v1.692zm8.121-1.129l-.012-.019a1.452 1.452 0 0 0-.87-.668 1.43 1.43 0 0 0-1.103.146h.002c-.347.2-.58.529-.677.896-.095.365-.054.768.146 1.119l.007.009c.2.347.519.579.874.673.357.103.755.059 1.098-.144l.019-.009a1.47 1.47 0 0 0 .657-.885 1.493 1.493 0 0 0-.141-1.118'),
    ('Redis', '#FF4438', 'M22.71 13.145c-1.66 2.092-3.452 4.483-7.038 4.483-3.203 0-4.397-2.825-4.48-5.12.701 1.484 2.073 2.685 4.214 2.63 4.117-.133 6.94-3.852 6.94-7.239 0-4.05-3.022-6.972-8.268-6.972-3.752 0-8.4 1.428-11.455 3.685C2.59 6.937 3.885 9.958 4.35 9.626c2.648-1.904 4.748-3.13 6.784-3.744C8.12 9.244.886 17.05 0 18.425c.1 1.261 1.66 4.648 2.424 4.648.232 0 .431-.133.664-.365a100.49 100.49 0 0 0 5.54-6.765c.222 3.104 1.748 6.898 6.014 6.898 3.819 0 7.604-2.756 9.33-8.965.2-.764-.73-1.361-1.261-.73zm-4.349-5.013c0 1.959-1.926 2.922-3.685 2.922-.941 0-1.664-.247-2.235-.568 1.051-1.592 2.092-3.225 3.21-4.973 1.972.334 2.71 1.43 2.71 2.619z'),
    ('React', '#61DAFB', 'M14.23 12.004a2.236 2.236 0 0 1-2.235 2.236 2.236 2.236 0 0 1-2.236-2.236 2.236 2.236 0 0 1 2.235-2.236 2.236 2.236 0 0 1 2.236 2.236zm2.648-10.69c-1.346 0-3.107.96-4.888 2.622-1.78-1.653-3.542-2.602-4.887-2.602-.41 0-.783.093-1.106.278-1.375.793-1.683 3.264-.973 6.365C1.98 8.917 0 10.42 0 12.004c0 1.59 1.99 3.097 5.043 4.03-.704 3.113-.39 5.588.988 6.38.32.187.69.275 1.102.275 1.345 0 3.107-.96 4.888-2.624 1.78 1.654 3.542 2.603 4.887 2.603.41 0 .783-.09 1.106-.275 1.374-.792 1.683-3.263.973-6.365C22.02 15.096 24 13.59 24 12.004c0-1.59-1.99-3.097-5.043-4.032.704-3.11.39-5.587-.988-6.38-.318-.184-.688-.277-1.092-.278zm-.005 1.09v.006c.225 0 .406.044.558.127.666.382.955 1.835.73 3.704-.054.46-.142.945-.25 1.44-.96-.236-2.006-.417-3.107-.534-.66-.905-1.345-1.727-2.035-2.447 1.592-1.48 3.087-2.292 4.105-2.295zm-9.77.02c1.012 0 2.514.808 4.11 2.28-.686.72-1.37 1.537-2.02 2.442-1.107.117-2.154.298-3.113.538-.112-.49-.195-.964-.254-1.42-.23-1.868.054-3.32.714-3.707.19-.09.4-.127.563-.132zm4.882 3.05c.455.468.91.992 1.36 1.564-.44-.02-.89-.034-1.345-.034-.46 0-.915.01-1.36.034.44-.572.895-1.096 1.345-1.565zM12 8.1c.74 0 1.477.034 2.202.093.406.582.802 1.203 1.183 1.86.372.64.71 1.29 1.018 1.946-.308.655-.646 1.31-1.013 1.95-.38.66-.773 1.288-1.18 1.87-.728.063-1.466.098-2.21.098-.74 0-1.477-.035-2.202-.093-.406-.582-.802-1.204-1.183-1.86-.372-.64-.71-1.29-1.018-1.946.303-.657.646-1.313 1.013-1.954.38-.66.773-1.286 1.18-1.868.728-.064 1.466-.098 2.21-.098zm-3.635.254c-.24.377-.48.763-.704 1.16-.225.39-.435.782-.635 1.174-.265-.656-.49-1.31-.676-1.947.64-.15 1.315-.283 2.015-.386zm7.26 0c.695.103 1.365.23 2.006.387-.18.632-.405 1.282-.66 1.933-.2-.39-.41-.783-.64-1.174-.225-.392-.465-.774-.705-1.146zm3.063.675c.484.15.944.317 1.375.498 1.732.74 2.852 1.708 2.852 2.476-.005.768-1.125 1.74-2.857 2.475-.42.18-.88.342-1.355.493-.28-.958-.646-1.956-1.1-2.98.45-1.017.81-2.01 1.085-2.964zm-13.395.004c.278.96.645 1.957 1.1 2.98-.45 1.017-.812 2.01-1.086 2.964-.484-.15-.944-.318-1.37-.5-1.732-.737-2.852-1.706-2.852-2.474 0-.768 1.12-1.742 2.852-2.476.42-.18.88-.342 1.356-.494zm11.678 4.28c.265.657.49 1.312.676 1.948-.64.157-1.316.29-2.016.39.24-.375.48-.762.705-1.158.225-.39.435-.788.636-1.18zm-9.945.02c.2.392.41.783.64 1.175.23.39.465.772.705 1.143-.695-.102-1.365-.23-2.006-.386.18-.63.406-1.282.66-1.933zM17.92 16.32c.112.493.2.968.254 1.423.23 1.868-.054 3.32-.714 3.708-.147.09-.338.128-.563.128-1.012 0-2.514-.807-4.11-2.28.686-.72 1.37-1.536 2.02-2.44 1.107-.118 2.154-.3 3.113-.54zm-11.83.01c.96.234 2.006.415 3.107.532.66.905 1.345 1.727 2.035 2.446-1.595 1.483-3.092 2.295-4.11 2.295-.22-.005-.406-.05-.553-.132-.666-.38-.955-1.834-.73-3.703.054-.46.142-.944.25-1.438zm4.56.64c.44.02.89.034 1.345.034.46 0 .915-.01 1.36-.034-.44.572-.895 1.095-1.345 1.565-.455-.47-.91-.993-1.36-1.565z'),
    ('YOLO', '#7B61FF', 'm12.736 7.341-.002 2.897c.012 3.953-3.188 7.177-7.098 7.171-1.553-.003-2.967-.48-4.112-1.313 2.056 3.725 5.999 6.24 10.48 6.245 6.511-.003 11.891-5.343 11.992-11.91l-.002-.027c.006-.151 0-2.951.006-3.075-.01-3.116-2.538-5.677-5.63-5.67-3.105-.006-5.645 2.54-5.634 5.683zM5.629 4.573C2.525 4.573 0 7.118 0 10.246s2.525 5.673 5.63 5.673c3.103 0 5.629-2.545 5.629-5.673s-2.526-5.673-5.63-5.673'),
]


def id_card(u, ox=0, oy=0):
    """A swinging ID card on a black, glowing GitHub lanyard, laid out like a GitHub profile sidebar. 346 x 486."""
    photo = base64.b64encode((ROOT / "assets" / "id-photo.webp").read_bytes()).decode()
    badges = [(n, base64.b64encode((ROOT / "assets" / "badges" / f"{n}.png").read_bytes()).decode())
              for n in ("pull-shark", "pair-extraordinaire", "yolo", "quickdraw")]
    cx = 173
    x0, y0, w, h = 13, 122, 320, 398
    per = 2 * (w + h)
    gh = lambda x, y, sc, fill="#F0F6FC", rot=0: f'<g transform="translate({x} {y}) rotate({rot}) scale({sc}) translate(-12 -12)"><path d="{GITHUB_PATH}" fill="{fill}"/></g>'
    # lanyard straps: black with a neon glow and GitHub logos along them
    straps = []
    for side in (-1, 1):
        x1, y1, x2, y2 = cx + side * 92, -6, cx + side * 10, 86
        straps.append(f'<path d="M{x1} {y1} L{x2} {y2}" stroke="url(#{u}-neon)" stroke-width="26" stroke-linecap="round" opacity=".55" filter="url(#{u}-glow)"/>')
        straps.append(f'<path d="M{x1} {y1} L{x2} {y2}" stroke="#05060A" stroke-width="22" stroke-linecap="round"/>')
        straps.append(f'<path d="M{x1} {y1} L{x2} {y2}" stroke="url(#{u}-neon)" stroke-width="22" stroke-linecap="round" fill="none" opacity=".9" stroke-dasharray="0" style="mix-blend-mode:normal" mask="url(#{u}-edge)"/>')
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
        for t in (.22, .5, .78):
            straps.append(gh(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, .42, "#E6EDF3", ang - 90 if side < 0 else ang + 90))
    icon = {
        "uni": '<path d="M-6 -2 L0 -6 L6 -2 Z M-5 -1 V4 M-1.7 -1 V4 M1.7 -1 V4 M5 -1 V4 M-6.5 5 H6.5" stroke="#A9B8FF" stroke-width="1.3" fill="none"/>',
        "link": '<path d="M-1.5 2.5 l-1.8 1.8 a2.4 2.4 0 0 1 -3.4 -3.4 l2.6 -2.6 a2.4 2.4 0 0 1 3.4 0 M1.5 -2.5 l1.8 -1.8 a2.4 2.4 0 0 1 3.4 3.4 l-2.6 2.6 a2.4 2.4 0 0 1 -3.4 0" stroke="#A9B8FF" stroke-width="1.3" fill="none" transform="translate(0.3 0)"/>',
        "pin": '<path d="M0 6 C-4 1 -5 -1 -5 -2.5 A5 5 0 0 1 5 -2.5 C5 -1 4 1 0 6 Z" stroke="#A9B8FF" stroke-width="1.3" fill="none"/><circle cx="0" cy="-2.6" r="1.6" fill="#A9B8FF"/>',
        "play": '<rect x="-6" y="-4.5" width="12" height="9" rx="2.5" fill="#FF3355"/><path d="M-1.5 -2 L2.5 0 L-1.5 2 Z" fill="#fff"/>',
    }
    P = "#0D1117"     # panels
    B = "#30363D"     # panel borders
    def panel(x, y, pw, ph, title, emoji):
        return (f'<rect x="{x}" y="{y}" width="{pw}" height="{ph}" rx="9" fill="{P}" stroke="{B}"/>'
                f'<text x="{x + 9}" y="{y + 17}" class="sans" font-size="10.5" font-weight="800" fill="#F0F6FC">{emoji} {e(title)}</text>')
    L, T = x0 + 12, y0 + 12            # inner left / top
    IW = w - 24
    # tech stack tiles
    tiles = TECH_ICONS
    tx0, ty0 = L + 140, T + 118
    tile_svg = "".join(f'<rect x="{tx0 + 8 + (k % 4) * 33}" y="{ty0 + 24 + (k // 4) * 27}" width="30" height="23" rx="5" fill="#161B22" stroke="{c}" stroke-opacity=".55">'
                       f'<title>{name}</title></rect>'
                       f'<g transform="translate({tx0 + 15.5 + (k % 4) * 33} {ty0 + 28 + (k // 4) * 27}) scale(.62)"><path d="{d}" fill="{c}"/></g>'
                       for k, (name, c, d) in enumerate(tiles))
    # github stats + language donut
    stats = [("★", "Total stars", "75"), ("⧉", "Public repos", "44"), ("◆", "Contributions", "640+"), ("🏅", "Achievements", "4")]
    sx0, sy0 = L, T + 212
    stat_svg = "".join(text(sx0 + 10, sy0 + 50 + k * 16, f"{ic}  {lab}", 8.5, "#C9D1D9", 'sans')
                       + text(sx0 + 112, sy0 + 50 + k * 16, val, 8.5, "#F0F6FC", 'mono', 'end', 'font-weight="700"') for k, (ic, lab, val) in enumerate(stats))
    langs = [("JavaScript", 12, "#F1E05A"), ("Python", 8, "#3572A5"), ("HTML", 6, "#E34C26"), ("Java", 3, "#B07219"), ("Other", 15, "#8B949E")]
    tot = sum(n for _, n, _ in langs); a0 = -math.pi / 2; dcx, dcy, R = sx0 + 145, sy0 + 52, 16
    arcs = []
    for name, n, col in langs:
        a1 = a0 + 2 * math.pi * n / tot
        large = 1 if a1 - a0 > math.pi else 0
        arcs.append(f'<path d="M{dcx + R * math.cos(a0):.1f} {dcy + R * math.sin(a0):.1f} A{R} {R} 0 {large} 1 {dcx + R * math.cos(a1):.1f} {dcy + R * math.sin(a1):.1f}" stroke="{col}" stroke-width="7" fill="none"/>')
        a0 = a1
    legend = "".join(f'<circle cx="{sx0 + 128}" cy="{sy0 + 82 + k * 9}" r="2.2" fill="{col}"/>' + text(sx0 + 133, sy0 + 84.5 + k * 9, name, 6.5, "#8B949E", 'sans')
                     for k, (name, _, col) in enumerate(langs[:3]))
    # top repositories
    repos = [("rootlens", 4), ("TriageIQ", 4), ("Nova", 4), ("Leetcode-Solutions", 3), ("smart-day", 3)]
    rx0, ry0 = L + 182, T + 212
    repo_svg = "".join(text(rx0 + 9, ry0 + 36 + k * 15, f"• {n if len(n) < 12 else n[:10] + '…'}", 8.5, "#C9D1D9", 'sans')
                       + text(rx0 + IW - 182 - 8, ry0 + 36 + k * 15, f"★ {st}", 8, "#E3B341", 'mono', 'end') for k, (n, st) in enumerate(repos))
    li = '<rect x="-8" y="-8" width="16" height="16" rx="3.5" fill="#0A66C2"/><text x="0" y="4.2" text-anchor="middle" font-family="Arial" font-weight="900" font-size="10.5" fill="#fff">in</text>'
    mail = '<rect x="-8" y="-6" width="16" height="12" rx="2" fill="none" stroke="#E6EDF3" stroke-width="1.5"/><path d="M-7 -5 L0 1 L7 -5" stroke="#E6EDF3" stroke-width="1.5" fill="none"/>'
    yt = '<rect x="-8.5" y="-6" width="17" height="12" rx="3.5" fill="#FF0033"/><path d="M-2.5 -3 L3.5 0 L-2.5 3 Z" fill="#fff"/>'
    cy0 = T + 336
    return f"""
<defs>
  <linearGradient id="{u}-neon" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#3B82F6"/><stop offset=".5" stop-color="#A855F7"/><stop offset="1" stop-color="#EC4899"/>
  </linearGradient>
  <linearGradient id="{u}-name" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#60A5FA"/><stop offset=".55" stop-color="#A78BFA"/><stop offset="1" stop-color="#F472B6"/>
  </linearGradient>
  <linearGradient id="{u}-face" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#0F1533"/><stop offset=".6" stop-color="#141136"/><stop offset="1" stop-color="#2A1236"/>
  </linearGradient>
  <radialGradient id="{u}-blue" cx="15%" cy="15%" r="70%"><stop offset="0" stop-color="#2563EB" stop-opacity=".35"/><stop offset="1" stop-color="#2563EB" stop-opacity="0"/></radialGradient>
  <radialGradient id="{u}-pink" cx="90%" cy="90%" r="60%"><stop offset="0" stop-color="#DB2777" stop-opacity=".3"/><stop offset="1" stop-color="#DB2777" stop-opacity="0"/></radialGradient>
  <filter id="{u}-glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="{u}-glow2" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <clipPath id="{u}-ph"><circle cx="{x0 + w - 52}" cy="{y0 + 68}" r="36"/></clipPath>
  <linearGradient id="{u}-endglow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7C3AED" stop-opacity="0"/><stop offset="1" stop-color="#7C3AED" stop-opacity=".28"/></linearGradient>
</defs>
<g transform="translate({ox} {oy})"><g>
  <animateTransform attributeName="transform" type="rotate" values="-1.6 {cx} 0;1.6 {cx} 0;-1.6 {cx} 0" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>
  {''.join(s for s in straps if 'mask=' not in s)}
  <rect x="{cx - 16}" y="80" width="32" height="22" rx="5" fill="#2B2F3A" stroke="#9CA3AF" stroke-width="1.2"/>
  {gh(cx, 91, .55, "#E6EDF3")}
  <rect x="{cx - 7}" y="100" width="14" height="28" rx="4" fill="none" stroke="#C9CED6" stroke-width="2.5"/>

  <!-- card: full black, with a soft theme glow at the bottom -->
  <ellipse cx="{cx}" cy="{y0 + h - 4}" rx="{w * .46:.0f}" ry="22" fill="url(#{u}-neon)" opacity=".55" filter="url(#{u}-glow2)"/>
  <rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="20" fill="none" stroke="url(#{u}-neon)" stroke-width="6" opacity=".7" filter="url(#{u}-glow2)"/>
  <rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="20" fill="#000000"/>
  <rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="20" fill="none" stroke="url(#{u}-neon)" stroke-width="2" filter="url(#{u}-glow)"/>
  <rect x="{x0}" y="{y0 + h - 60}" width="{w}" height="60" rx="20" fill="url(#{u}-endglow)"/>
  <rect x="{x0 + 22}" y="{y0 + h - 1.5}" width="{w - 44}" height="2" rx="1" fill="url(#{u}-neon)" opacity=".9"/>
  <rect x="{cx - 22}" y="{y0 + 10}" width="44" height="7" rx="3.5" fill="#0D1117" stroke="#30363D"/>
  {text(L, T + 14, "▣ README.md", 8.5, "#8B949E", 'mono')}
  <text x="{L}" y="{T + 44}" class="sans" font-size="21" font-weight="900" fill="#F0F6FC">Hi there! 👋</text>
  <text x="{L}" y="{T + 70}" class="sans" font-size="21" font-weight="900" fill="#F0F6FC">I'm <tspan fill="url(#{u}-name)">Hemashree</tspan></text>
  {text(L, T + 88, "Software Engineer | Open Source Enthusiast |", 8.5, "#C9D1D9", 'sans')}
  {text(L, T + 100, "Patent co-inventor", 8.5, "#C9D1D9", 'sans')}
  <circle cx="{x0 + w - 52}" cy="{T + 56}" r="40" fill="none" stroke="url(#{u}-neon)" stroke-width="3" filter="url(#{u}-glow)"/>
  <image x="{x0 + w - 88}" y="{T + 20}" width="72" height="72" clip-path="url(#{u}-ph)" href="data:image/webp;base64,{photo}"/>
  {panel(L, T + 118, 132, 84, "About Me", "🚀")}
  {text(L + 9, T + 148, "I build safe systems: vision", 7.8, "#C9D1D9", 'sans')}
  {text(L + 9, T + 161, "models, backends and IoT,", 7.8, "#C9D1D9", 'sans')}
  {text(L + 9, T + 174, "from idea to production.", 7.8, "#C9D1D9", 'sans')}
  {panel(tx0, ty0, IW - 140, 84, "Tech Stack", "🛠")}
  {tile_svg}
  {panel(sx0, sy0, 174, 112, "GitHub Stats", "📊")}
  {text(sx0 + 10, sy0 + 31, "@HemashreeVI", 8, "#F0F6FC", 'sans', 'start', 'font-weight="700"')}
  {stat_svg}
  {''.join(arcs)}{legend}
  {panel(rx0, ry0, IW - 182, 112, "Top Repositories", "🔥")}
  {repo_svg}
  <rect x="{L}" y="{cy0}" width="{IW}" height="34" rx="9" fill="{P}" stroke="{B}"/>
  <text x="{L + 9}" y="{cy0 + 21}" class="sans" font-size="10.5" font-weight="800" fill="#F0F6FC">🔗 Let's connect!</text>
  <g transform="translate({L + 112} {cy0 + 17})">{li}</g><g transform="translate({L + 134} {cy0 + 17})">{mail}</g><g transform="translate({L + 156} {cy0 + 17})">{yt}</g>
  {text(L + IW - 9, cy0 + 15, "Always open to collaborate", 7, "#8B949E", 'sans', 'end')}
  {text(L + IW - 9, cy0 + 25, "on great projects ✨", 7, "#8B949E", 'sans', 'end')}
  <!-- the GitHub tag hanging from the strap -->
  <g><animateTransform attributeName="transform" type="rotate" values="9 {cx + 52} 40;-7 {cx + 52} 40;9 {cx + 52} 40" dur="3.4s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>
    <path d="M{cx + 52} 40 L{cx + 62} 66" stroke="#C9CED6" stroke-width="2" stroke-dasharray="3 2.2"/>
    <circle cx="{cx + 62}" cy="69" r="4" fill="none" stroke="#C9CED6" stroke-width="1.8"/>
    <rect x="{cx + 43}" y="72" width="38" height="44" rx="10" fill="#05060A" stroke="url(#{u}-neon)" stroke-width="2" filter="url(#{u}-glow2)"/>
    <rect x="{cx + 43}" y="72" width="38" height="44" rx="10" fill="#05060A" stroke="url(#{u}-neon)" stroke-width="1.6"/>
    {gh(cx + 62, 90, .8)}
    {text(cx + 62, 110, "GitHub", 6.2, C['mist'], 'mono', 'middle', 'font-weight="600"')}
  </g>
</g></g>"""


def build_id_card():
    W, H, u = 346, 528, "idc"
    write("id-card.svg", svg(W, H, u, "ID card: Hemashree, Software Engineer",
          "An ID card swinging on a lanyard with a GitHub tag hanging from its clip: photo, HEMASHREE, Software Engineer, B.Tech CSE at VIT Chennai, open to work. "
          "Based in Chennai, India; speaks Tamil, English, Hindi and Japanese; Design Lead by night. ID HVI-2027.", id_card(u)))

# ---------------------------------------------------------------- footer
def build_footer():
    W, H, u = 1200, 330, "foot"
    body = f"""
{frame(W, H, u, (0.5, 0.75))}
{stars(W, H, 30, 3)}
{text(600, 64, "LET'S BUILD SOMETHING THAT KEEPS PEOPLE SAFE", 12, C['lav'], 'mono', 'middle', 'letter-spacing="4"')}
<text x="600" y="168" class="serif" font-size="96" font-style="italic" text-anchor="middle" fill="url(#{u}-silver)" letter-spacing="2">Hemashree</text>
<text x="600" y="168" class="serif" font-size="96" font-style="italic" text-anchor="middle" fill="none" stroke="#fff" stroke-width="1.4" stroke-dasharray="120 900" letter-spacing="2" opacity=".8">Hemashree<animate attributeName="stroke-dashoffset" values="1020;0" dur="6s" repeatCount="indefinite"/></text>
<rect x="380" y="196" width="440" height="1.2" fill="url(#{u}-rule)"/>
{text(600, 236, "Open to roles in cybersecurity · computer vision · cyber-physical systems · backend & devops", 15, C['mist'], 'sans', 'middle')}
{text(600, 280, "よろしくお願いします", 20, C['lilac'], 'serif', 'middle')}
{phoenix_layer.warmth("phx", 1128, 270, 90, 30, sparks=7, seed=5)}
{chess_layer.checkmate("pcK")}
{phoenix_layer.rises("phx", (1128, 268), (980, -150), .2, .62, 10, .44, .78)}
"""
    write("footer.svg", svg(W, H, u, "Let's build something that keeps people safe",
                            "Open to roles in cybersecurity, computer vision, cyber-physical systems, backend and DevOps. よろしくお願いします", body))


def main():
    print("building cards →", OUT.relative_to(ROOT))
    build_hero()
    titles = [
        ("01", "ABOUT", "Hello, I'm", "Hemashree.", "WHO I AM", "about"),
        ("02", "JOURNEY", "The road", "so far.", "2023 → NOW", "journey"),
        ("03", "MAIN PROJECTS", "Things I've", "built.", "SEATLOCK · ROOTLENS · TRIAGEIQ · GITLOOM", "work"),
        ("04", "RESEARCH & PATENTS", "Ideas,", "on file.", "2 PATENTS · 1 RESEARCH", "patents"),
        ("05", "OPEN SOURCE", "Built in", "the open.", "MERGED PRS · MIT REPOS", "opensource"),
        ("06", "CHROME EXTENSIONS", "Tools I built", "for the browser.", "6 EXTENSIONS · FREE", "extensions"),
        ("07", "YOUTUBE", "Byte", "Decoded.", "TECH · PROJECTS · AI · CODING", "youtube"),
        ("08", "PLAY", "Play on my", "portfolio.", "4 MINI-GAMES", "play"),
        ("09", "COMMIT LOG", "A year of", "building.", "CONTRIBUTIONS", "commits"),
        ("10", "CONNECT", "Let's", "talk.", "SAY HI", "connect"),
    ]
    # a silver chess piece turns up in some of the section titles
    piece = {
        "about": chess_layer.queen_rises("pcQ"),
        "work": chess_layer.knight_hops("pcN"),
        "play": chess_layer.rook_slides("pcR"),
        "commits": chess_layer.pawn_marches("pcP"),
    }
    for t in titles:
        build_title(*t, extra=piece.get(t[-1], ""))
    build_about()
    build_now()
    build_pipeline()
    build_journey()
    for i, p in enumerate(PROJECTS):
        build_project(p, i)
        if p['slug'] in ('seatlock', 'rootlens', 'triageiq', 'gitloom', 'walker', 'rover'):
            build_project_tile(p, i)
    build_more()
    build_building()
    build_toolkit()
    build_games()
    build_opensource()
    build_extensions()
    build_showcase()
    build_id_card()
    build_youtube()
    build_social_icons()
    build_footer()


if __name__ == "__main__":
    main()
