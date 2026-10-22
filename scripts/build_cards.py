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

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "cards"
PHOTO = ROOT / "assets" / "photo.jpg"

# ---------------------------------------------------------------- palette
C = {
    "bg0": "#0B0912",
    "bg1": "#14101F",
    "bg2": "#1C1630",
    "panel": "#17122A",
    "line": "#2D2647",
    "line2": "#3E3463",
    "violet": "#7B61D9",
    "lav": "#B7A4F2",
    "lilac": "#D9CEFF",
    "silver": "#E8E6F0",
    "mist": "#C9C5D8",
    "muted": "#9A93B4",
    "dim": "#6B6489",
    "rose": "#F0A8D0",
    "mint": "#8FE3C8",
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
        "Co-inventor: smart walker patent (filing in progress)",
        "Backend & DevOps · Kafka · Docker · FastAPI",
        "こんにちは! I speak 4 languages",
        "Let's build something that keeps people safe",
    ],
}

TERMINAL = [
    ("whoami", [("out", "hemashree · software engineer")]),
    ("cat education.txt", [("out", "B.Tech Computer Science Engineering @ VIT Chennai")]),
    ("cat focus.txt", [("out", "vision · reinforcement-learning · embedded · security")]),
    ("ls patents/", [("out", "smart-walker/"), ("note", "  # sensor-fusion fall-risk prediction (filing in progress)")]),
    ("./status --open-to", [("out", "cybersecurity | computer-vision | cyber-physical-systems | backend & devops")]),
    ("echo $LANGUAGES", [("out", "Tamil · English · Hindi · 日本語")]),
]

ABOUT_SIDE = [
    ("BASED IN", "Chennai, India", "open to opportunities"),
    ("SPEAKS", "4 languages", "Tamil · English · Hindi · 日本語"),
    ("BY NIGHT", "Design Lead", "posters, creatives and this README"),
]

RIGHT_NOW = [
    ("RootLens", "AI-assisted root-cause analysis for microservices"),
    ("TriageIQ", "real-time LLM ticket triage with Kafka and RAG"),
    ("Binary search trees in Java", "and solving LeetCode daily"),
    ("Pit Wall", "an F1 race replay built on real GPS data"),
]

QUICK_FACTS = [
    ("Co-inventor", "on a smart walker patent (filing in progress)"),
    ("Singapore", "NUS Industry 4.0 and SuperAI 2025"),
    ("~97% accuracy", "on 13,000+ dental X-rays"),
    ("4 languages", "Tamil · English · Hindi · 日本語"),
    ("Design Lead by night", "posters, creatives and this README"),
]

PIPELINE = [
    ("SENSE", "perceive the world", ["X-rays · IMU + load cells", "pose estimation · sensors"]),
    ("DECIDE", "reason about it", ["YOLOv9 · Q-learning · CNN", "risk scoring · fusion"]),
    ("PROTECT", "make someone safer", ["fall alerts · hazard maps", "automated IDS responses"]),
]

JOURNEY = [
    ("AUG 2023", "VIT Chennai", ["B.Tech CSE", "Cyber Physical"]),
    ("MAY–JUL 2025", "Research intern", ["Pose estimation", "MMPose"]),
    ("JUN 2025", "Singapore", ["NUS Industry 4.0", "SuperAI · IBM Gen AI"]),
    ("JUL–SEP 2025", "97% on X-rays", ["YOLOv9", "13,000+ images"]),
    ("2025–26", "Patent co-inventor", ["Smart walker", "filing in progress"]),
    ("2026", "Backend & DevOps", ["RootLens", "TriageIQ"]),
    ("NOW", "Building 4 more", ["+ grinding LeetCode", "next stop: your team?"]),
]

PROJECTS = [
    {
        "slug": "dental",
        "kicker": "01 · COMPUTER VISION · HEALTHCARE",
        "name": "Dental Malocclusion Detection",
        "pitch": "Reads dental X-rays and explains what it sees.",
        "built": "YOLOv9 pipeline · Grad-CAM explanations · FDI tooth mapping · Gradio app · PDF reports",
        "stats": [("31", "dental conditions detected"), ("~97%", "accuracy"), ("13,000+", "X-ray dataset")],
        "tags": ["Python", "PyTorch", "OpenCV", "YOLOv9", "Grad-CAM", "Gradio"],
        "motif": "xray",
    },
    {
        "slug": "rootlens",
        "kicker": "02 · RELIABILITY · AIOPS",
        "name": "RootLens",
        "pitch": "When a microservice breaks, it tells you why.",
        "built": "Detects failures across FastAPI services · gathers evidence · ranks root causes · records incidents",
        "stats": [("Detect", "failures across services"), ("Rank", "root causes by evidence"), ("Record", "every incident")],
        "tags": ["Python", "FastAPI", "Docker", "Prometheus", "Grafana", "SQLite", "Chaos tests", "CI"],
        "motif": "graph",
    },
    {
        "slug": "triageiq",
        "kicker": "03 · LLM · STREAMING",
        "name": "TriageIQ",
        "pitch": "Support tickets, triaged the moment they arrive.",
        "built": "Kafka stream · local LLM classifies and prioritises · RAG over past tickets drafts the reply · live dashboard",
        "stats": [("Kafka", "real-time ticket stream"), ("Local LLM", "classify + prioritise"), ("RAG", "drafts replies")],
        "tags": ["Python", "Kafka", "FastAPI", "Docker", "Ollama", "Qdrant"],
        "motif": "stream",
    },
    {
        "slug": "walker",
        "kicker": "04 · IoT · PATENT (FILING IN PROGRESS)",
        "name": "Smart Walker",
        "pitch": "A walker that predicts a fall before it happens.",
        "built": "Dual IMUs + load cells · sensor fusion · fall-risk prediction · standalone on Arduino",
        "stats": [("2× IMU", "+ load cells, fused"), ("< $30", "standalone on Arduino"), ("Patent", "co-inventor")],
        "tags": ["Arduino", "C++", "MPU6050", "HX711", "Sensor fusion"],
        "motif": "wave",
    },
    {
        "slug": "rover",
        "kicker": "05 · REINFORCEMENT LEARNING",
        "name": "RL Rover for Hazard Detection",
        "pitch": "A rover that learns to explore a disaster zone.",
        "built": "Simulated rover discovers hazards through perception · tabular Q-learning + lightweight CNN",
        "stats": [("Q-learning", "tabular agent"), ("CNN", "hazard perception"), ("4-way", "reward ablation")],
        "tags": ["Python", "PyTorch", "Q-Learning", "CNN"],
        "motif": "grid",
    },
    {
        "slug": "grocer",
        "kicker": "06 · MULTIMODAL · RETAIL",
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
    ("01 LANGUAGES", ["Python · Java", "C++ · JavaScript", "HTML · CSS"]),
    ("02 AI & VISION", ["PyTorch · TensorFlow", "OpenCV · YOLOv8/v9", "Grad-CAM · MMPose", "Q-learning · RAG · Ollama", "IBM watsonx"]),
    ("03 EMBEDDED & IoT", ["Arduino · Raspberry Pi", "ESP32", "Sensor fusion", "LIDAR SLAM"]),
    ("04 BACKEND & DEVOPS", ["FastAPI · Flask", "Docker · Kafka", "Prometheus · Grafana", "GitHub Actions"]),
    ("05 DATA", ["SQLite · MySQL", "Firebase", "Qdrant"]),
    ("06 SECURITY", ["Intrusion detection", "Threat modeling", "Risk scoring"]),
    ("07 TOOLS", ["Git · GitHub · VS Code", "Linux · Windows · PowerShell", "Jupyter · Colab · Kaggle", "Roboflow · Gradio"]),
    ("08 SPOKEN", ["Tamil · English", "Hindi", "日本語"]),
]

MILESTONES = [
    ("PATENT", "Co-inventor · filing in progress",
     "IoT-Enabled Smart Walker with Sensor-Fusion Fall Risk Prediction and Adaptive Mobility Assistance. Inventive disclosure filed with IIPRD."),
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
    <stop offset="0" stop-color="{C['violet']}" stop-opacity=".45"/>
    <stop offset="1" stop-color="{C['violet']}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="{uid}-glowB" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="{C['silver']}" stop-opacity=".12"/>
    <stop offset="1" stop-color="{C['silver']}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="{uid}-silver" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#FFFFFF"/>
    <stop offset=".5" stop-color="{C['mist']}"/>
    <stop offset="1" stop-color="{C['lav']}"/>
  </linearGradient>
  <linearGradient id="{uid}-rule" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{C['lav']}" stop-opacity="0"/>
    <stop offset=".25" stop-color="{C['lav']}" stop-opacity=".8"/>
    <stop offset="1" stop-color="{C['lav']}" stop-opacity="0"/>
  </linearGradient>
  <pattern id="{uid}-grid" width="28" height="28" patternUnits="userSpaceOnUse">
    <path d="M28 0H0V28" fill="none" stroke="{C['lav']}" stroke-opacity=".05"/>
  </pattern>
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
<ellipse cx="{w*(1-gx):.0f}" cy="{h*(1-gy):.0f}" rx="{w*0.25:.0f}" ry="{h*0.5:.0f}" fill="url(#{uid}-glowB)"/>"""


def stars(w, h, n, seed, pad=20):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x, y = rnd.uniform(pad, w - pad), rnd.uniform(pad, h - pad)
        r = rnd.choice([0.8, 1, 1.2, 1.6])
        d = rnd.uniform(0, 4)
        out.append(f'<circle class="twinkle" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{C["silver"]}" style="animation-delay:{d:.1f}s"/>')
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
def build_title(num, kicker, plain, italic, right, slug):
    W, H, u = 1200, 104, f"t{num}"
    width_plain = len(plain) * 19
    body = f"""
{text(30, 32, num, 12, C['silver'], 'mono', 'start', 'letter-spacing="3"')}
{text(58, 32, kicker, 12, C['lav'], 'mono', 'start', 'letter-spacing="3"')}
{text(1170, 32, right, 11, C['muted'], 'mono', 'end', 'letter-spacing="3"')}
<text x="30" y="80" class="serif" font-size="40" fill="{C['silver']}">{e(plain)} <tspan fill="{C['lav']}" font-style="italic">{e(italic)}</tspan></text>
<rect x="30" y="96" width="1140" height="1.2" fill="url(#{u}-rule)"/>
<circle cy="96.6" r="2.6" fill="#fff">
  <animate attributeName="cx" values="30;1170" dur="6s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.8;1" dur="6s" repeatCount="indefinite"/>
</circle>
"""
    write(f"title-{slug}.svg", svg(W, H, u, f"{num} {kicker.title()}: {plain} {italic}", right, body))


# ---------------------------------------------------------------- about
def build_about():
    W, H, u = 1200, 486, "about"
    tx, ty, tw, th = 32, 34, 760, 418
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
        t = (0.4 + i * 0.9) / cycle
        rows.append(f"""<g opacity="0"><animate attributeName="opacity" dur="{cycle}s" repeatCount="indefinite" keyTimes="0;{t:.3f};{t + 0.02:.3f};.94;.97;1" values="0;0;1;1;0;0"/>{''.join(group)}</g>""")
        i += 1
    cursor_y = y - step + 4

    side = []
    sx, sy = 822, 40
    for k, (lab, big, small) in enumerate(ABOUT_SIDE):
        yy = sy + k * 140
        side.append(f"""
<g class="fadein" style="animation-delay:{0.3 + k * 0.25}s">
  <rect x="{sx}" y="{yy}" width="346" height="124" rx="16" fill="{C['panel']}" stroke="{C['line2']}"/>
  <rect x="{sx}" y="{yy + 16}" width="3" height="92" rx="1.5" fill="{C['lav']}"/>
  {text(sx + 24, yy + 36, lab, 11, C['lav'], 'mono', 'start', 'letter-spacing="3"')}
  {text(sx + 24, yy + 74, big, 30, C['silver'], 'serif')}
  {text(sx + 24, yy + 101, small, 13, C['muted'], 'sans')}
</g>""")

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
{text(x + 84, y + 28, "malocclusion 0.97", 10, C['rose'], 'mono')}
<rect x="{x + 186}" y="{y + 104}" width="40" height="66" fill="none" stroke="{C['mint']}" stroke-width="1.5"/>
{text(x + 160, y + 186, "FDI 36 · caries 0.91", 10, C['mint'], 'mono')}
<rect x="{x}" y="{y}" width="310" height="3" fill="{L}" opacity=".8">
  <animate attributeName="y" values="{y + 8};{y + 190};{y + 8}" dur="4s" repeatCount="indefinite"/>
</rect>"""
    if kind == "graph":
        nodes = [(60, 50, "gateway"), (180, 40, "auth"), (110, 120, "orders"), (240, 110, "payments"), (180, 160, "db")]
        edges = [(0, 1), (0, 2), (2, 3), (1, 3), (3, 4), (2, 4)]
        s = [f'<rect x="{x}" y="{y}" width="310" height="200" rx="16" fill="{C["bg0"]}" stroke="{C["line2"]}"/>']
        for a, b in edges:
            s.append(f'<path d="M{x + nodes[a][0]} {y + nodes[a][1]}L{x + nodes[b][0]} {y + nodes[b][1]}" stroke="{L}" stroke-opacity=".35"/>')
        for i, (nx, ny, lb) in enumerate(nodes):
            bad = lb == "payments"
            col = C['rose'] if bad else L
            s.append(f'<circle cx="{x + nx}" cy="{y + ny}" r="{12 if bad else 9}" fill="{C["panel"]}" stroke="{col}" stroke-width="1.5"/>')
            if bad:
                s.append(f'<circle cx="{x + nx}" cy="{y + ny}" r="12" fill="none" stroke="{col}"><animate attributeName="r" values="12;28" dur="1.8s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;0" dur="1.8s" repeatCount="indefinite"/></circle>')
            s.append(text(x + nx, y + ny + 26, lb, 10, col if bad else C['muted'], 'mono', 'middle'))
        s.append(text(x + 16, y + 22, "root cause #1 → payments (p=0.82)", 10, C['rose'], 'mono'))
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
        s.append(text(x + 18, y + 186, "draft reply ready · 0.4s", 10, C['mint'], 'mono'))
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


def build_more():
    W, H, u = 1200, 220, "more"
    parts = [frame(W, H, u, (0.5, 0.3))]
    for k, (name, what, tags) in enumerate(MORE_PROJECTS):
        x = 32 + k * 576
        parts.append(f"""
<rect x="{x}" y="26" width="560" height="168" rx="18" fill="{C['panel']}" stroke="{C['line2']}"/>
{text(x + 24, 54, f"0{7 + k} · MORE", 11, C['lav'], 'mono', 'start', 'letter-spacing="3"')}
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
    cw, ch = 271, 232
    for k, (lab, items) in enumerate(TOOLKIT):
        col, row = k % 4, k // 4
        x, y = 32 + col * (cw + 13), 32 + row * (ch + 16)
        parts.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="16" fill="{C["panel"]}" stroke="{C["line2"]}"/>')
        parts.append(text(x + 20, y + 32, lab, 11, C['lav'], 'mono', 'start', 'letter-spacing="2.5"'))
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
"""
    write("footer.svg", svg(W, H, u, "Let's build something that keeps people safe",
                            "Open to roles in cybersecurity, computer vision, cyber-physical systems, backend and DevOps. よろしくお願いします", body))


def main():
    print("building cards →", OUT.relative_to(ROOT))
    build_hero()
    titles = [
        ("01", "ABOUT", "Hello, I'm", "Hemashree.", "WHO I AM", "about"),
        ("02", "PHILOSOPHY", "How I think about", "problems.", "SENSE · DECIDE · PROTECT", "think"),
        ("03", "JOURNEY", "The road", "so far.", "2023 → NOW", "journey"),
        ("04", "SELECTED WORK", "Things I've", "built.", "FEATURED PROJECTS", "work"),
        ("05", "IN PROGRESS", "Currently", "building.", "ON THE BENCH", "building"),
        ("06", "TOOLKIT", "The tools I", "reach for.", "TECH & TOOLS", "toolkit"),
        ("07", "MILESTONES", "Proof,", "on the record.", "RECOGNITION", "milestones"),
        ("08", "PLAY", "Play on my", "portfolio.", "4 MINI-GAMES", "play"),
        ("09", "COMMIT LOG", "A year of", "building.", "CONTRIBUTIONS", "commits"),
        ("10", "CONNECT", "Let's", "talk.", "SAY HI", "connect"),
    ]
    for t in titles:
        build_title(*t)
    build_about()
    build_now()
    build_pipeline()
    build_journey()
    for i, p in enumerate(PROJECTS):
        build_project(p, i)
    build_more()
    build_building()
    build_toolkit()
    build_milestones()
    build_games()
    build_footer()


if __name__ == "__main__":
    main()
