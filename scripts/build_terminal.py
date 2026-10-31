"""Builds assets/cards/terminal.svg: an animated neofetch-style terminal header.

Run: python scripts/build_terminal.py
"""
import math, random
from pathlib import Path

W, H = 1200, 800
OUT = Path(__file__).resolve().parent.parent / "assets" / "cards" / "terminal.svg"

FONT = {
 "H": ["10001","10001","10001","11111","10001","10001","10001"],
 "E": ["11111","10000","10000","11110","10000","10000","11111"],
 "M": ["10001","11011","10101","10101","10001","10001","10001"],
 "A": ["01110","10001","10001","11111","10001","10001","10001"],
 "S": ["01111","10000","10000","01110","00001","00001","11110"],
 "R": ["11110","10001","10001","11110","10100","10010","10001"],
}
WORD, CELL = "HEMASHREE", 12

def pixel_path(x0, y0):
    d = []
    cols = len(WORD) * 6 - 1
    for li, ch in enumerate(WORD):
        for r, row in enumerate(FONT[ch]):
            for c, bit in enumerate(row):
                if bit == "1":
                    x = x0 + (li * 6 + c) * CELL
                    y = y0 + r * CELL
                    d.append(f"M{x} {y}h{CELL-1}v{CELL-1}h-{CELL-1}z")
    return "".join(d), cols * CELL

PROMPT = '<tspan class="u">hemashree@vit-chennai</tspan><tspan class="p">:~$</tspan>'
FACTS = [
    ("user",   "Hemashree"),
    ("role",   "Software Engineer"),
    ("edu",    "B.Tech CSE · VIT Chennai"),
    ("focus",  "Vision · RL · Embedded · Security"),
    ("langs",  "Python · Java · C++ · JavaScript"),
    ("stack",  "PyTorch · FastAPI · Docker · Kafka"),
    ("patent", "smart walker (filing in progress)"),
    ("motto",  "build things that keep people safe"),
]

def network():
    random.seed(7)
    cols = [(150, [0, 1, 2], "#7FE0E8"), (285, [0, 1, 2, 3, 4], "#B7A4F2"),
            (420, [0, 1, 2, 3, 4], "#B7A4F2"), (545, [1, 3], "#F0A8D0")]
    top, step = 384, 62
    pts = []
    for x, idx, col in cols:
        n = len(idx)
        span = (4 * step)
        ys = [top + span / 2 + (i - (n - 1) / 2) * (span / max(n - 1, 1) if n < 5 else step) for i in range(n)]
        if n == 2: ys = [top + step, top + 3 * step]
        if n == 3: ys = [top + 0.4 * step, top + 2 * step, top + 3.6 * step]
        pts.append([(x, y, col) for y in ys])
    out = ['<g class="net">']
    edges = []
    for a, b in zip(pts, pts[1:]):
        for (x1, y1, _) in a:
            for (x2, y2, _) in b:
                edges.append((x1, y1, x2, y2))
                out.append(f'<line x1="{x1}" y1="{y1:.0f}" x2="{x2}" y2="{y2:.0f}"/>')
    out.append("</g>")
    # travelling pulses
    for i, (x1, y1, x2, y2) in enumerate(random.sample(edges, 9)):
        col = ["#7FE0E8", "#F0A8D0", "#B7A4F2"][i % 3]
        dur = 2.4 + (i % 4) * 0.5
        out.append(f'<circle r="3" fill="{col}"><animateMotion dur="{dur}s" begin="{i*0.35:.2f}s" repeatCount="indefinite" path="M{x1} {y1:.0f}L{x2} {y2:.0f}"/></circle>')
    for layer in pts:
        for (x, y, col) in layer:
            out.append(f'<circle cx="{x}" cy="{y:.0f}" r="11" fill="#14101F" stroke="{col}" stroke-width="2.4"/>'
                       f'<circle cx="{x}" cy="{y:.0f}" r="4.5" fill="{col}" opacity=".85"/>')
    labels = [(150, "sense"), (352, "decide"), (545, "protect")]
    for x, t in labels:
        out.append(f'<text x="{x}" y="{top + 4*step + 42}" class="lab" text-anchor="middle">{t}</text>')
    return "\n".join(out)

def build():
    path, pw = pixel_path(0, 0)
    px = (W - pw) / 2
    s = []
    s.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="term-t term-d">
<title id="term-t">hemashree@vit-chennai</title>
<desc id="term-d">Animated terminal. ./boot --profile prints HEMASHREE in pixel letters: Software Engineer, Computer Vision, Cyber-Physical Systems. neofetch lists: {"; ".join(f"{k}: {v}" for k, v in FACTS)}; status: open to opportunities.</desc>
<defs>
 <linearGradient id="g" x1="{px}" y1="0" x2="{px+pw}" y2="0" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#8FB8FF"/><stop offset=".35" stop-color="#B7A4F2"/><stop offset=".6" stop-color="#F0A8D0"/><stop offset="1" stop-color="#7FE0E8"/>
 </linearGradient>
 <linearGradient id="frame" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#B7A4F2"/><stop offset=".5" stop-color="#F0A8D0"/><stop offset="1" stop-color="#7FE0E8"/></linearGradient>
 <filter id="glow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#ffffff" opacity=".018"/></pattern>
</defs>
<style>
text{{font-family:ui-monospace,SFMono-Regular,'JetBrains Mono',Menlo,Consolas,'Liberation Mono',monospace;font-size:19px;fill:#E8E6F0}}
.u{{fill:#8FE3C8}} .p{{fill:#9A93B4}} .k{{fill:#B7A4F2;font-weight:700}} .ar{{fill:#6E6690}} .dim{{fill:#9A93B4}} .ok{{fill:#8FE3C8}}
.lab{{font-size:12px;letter-spacing:3px;fill:#6E6690}}
.net line{{stroke:#B7A4F2;stroke-opacity:.16;stroke-width:1}}
.in{{opacity:0;animation:in .45s ease-out forwards}}
@keyframes in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
.type{{animation:type 1s steps(18) forwards}}
@keyframes type{{from{{width:0}}to{{width:360px}}}}
.cur{{animation:blink 1s steps(1) infinite}} @keyframes blink{{50%{{opacity:0}}}}
.dot{{animation:pulse 2s ease-in-out infinite}} @keyframes pulse{{50%{{opacity:.35}}}}
.flick{{animation:flick 6s linear infinite}} @keyframes flick{{0%,96%,100%{{opacity:1}}97%{{opacity:.7}}98%{{opacity:1}}99%{{opacity:.8}}}}
</style>
<rect x="6" y="6" width="{W-12}" height="{H-12}" rx="22" fill="#0E0B17" stroke="url(#frame)" stroke-width="2"/>
<rect x="7" y="7" width="{W-14}" height="54" rx="21" fill="#17122A"/>
<rect x="7" y="40" width="{W-14}" height="21" fill="#17122A"/>
<line x1="7" y1="61" x2="{W-7}" y2="61" stroke="#2A2340"/>
<circle cx="42" cy="34" r="8" fill="#FF6B6B"/><circle cx="70" cy="34" r="8" fill="#FFC048"/><circle cx="98" cy="34" r="8" fill="#4ED98B"/>
<text x="{W/2}" y="40" text-anchor="middle" class="dim" style="font-size:16px">hemashree@vit-chennai: ~</text>
<rect x="7" y="61" width="{W-14}" height="{H-68}" fill="url(#scan)"/>

<g class="in" style="animation-delay:.2s"><text x="44" y="110">{PROMPT}  ./boot --profile</text></g>
<g class="in flick" style="animation-delay:.8s" transform="translate({px:.0f},134)">
 <path d="{path}" transform="translate(6,6)" fill="none" stroke="#B7A4F2" stroke-opacity=".45" stroke-width="1.2"/>
 <path d="{path}" fill="url(#g)" filter="url(#glow)"/>
</g>
<g class="in" style="animation-delay:1.3s"><text x="{W/2}" y="262" text-anchor="middle" class="dim">[ Software Engineer  ·  Computer Vision  ·  CPS ]</text></g>

<g class="in" style="animation-delay:1.8s"><text x="44" y="324">{PROMPT}  neofetch</text></g>
<g class="in" style="animation-delay:2.2s">
{network()}
</g>
''')
    y0, dy, x0 = 384, 36, 628
    for i, (k, v) in enumerate(FACTS):
        y = y0 + i * dy
        s.append(f'<g class="in" style="animation-delay:{2.4 + i*0.18:.2f}s"><text x="{x0}" y="{y}"><tspan class="k">{k}</tspan></text>'
                 f'<text x="{x0+110}" y="{y}" class="ar">▸</text><text x="{x0+140}" y="{y}">{v}</text></g>')
    y = y0 + len(FACTS) * dy
    s.append(f'<g class="in" style="animation-delay:{2.4 + len(FACTS)*0.18:.2f}s"><text x="{x0}" y="{y}"><tspan class="k">status</tspan></text>'
             f'<text x="{x0+110}" y="{y}" class="ar">▸</text><text x="{x0+140}" y="{y}" class="ok">open to opportunities</text>'
             f'<circle class="dot" cx="{x0+404}" cy="{y-6}" r="7" fill="#4ED98B"/></g>')
    cols = ["#FF6B6B", "#FFC048", "#4ED98B", "#7FE0E8", "#B7A4F2", "#F0A8D0", "#E8E6F0", "#2A2340"]
    sw = "".join(f'<rect x="{x0 + i*50}" y="{y+24}" width="44" height="22" rx="4" fill="{c}"/>' for i, c in enumerate(cols))
    s.append(f'<g class="in" style="animation-delay:{2.6 + len(FACTS)*0.18:.2f}s">{sw}</g>')
    t = 4.4
    s.append(f'''<g class="in" style="animation-delay:{t}s"><text x="44" y="{H-42}">{PROMPT}  echo "let's build something"</text>
<rect class="cur" x="666" y="{H-60}" width="12" height="24" fill="#B7A4F2"/></g>
</svg>''')
    OUT.write_text("\n".join(s), encoding="utf-8")
    print("wrote", OUT)

if __name__ == "__main__":
    build()
