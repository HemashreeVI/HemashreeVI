#!/usr/bin/env python3
"""Builds the two animated cat cards for the profile README.

    python3 scripts/build_cat_cards.py

assets/cards/cat-hello.svg  under the intro: the cat jumps up into view,
                            lands, waves and says hello.
assets/cards/cat-bye.svg    by the Connect section: the cat waves goodbye.

The cat artwork is assets/cat/cat.png (an original mascot), embedded in the
SVG so it shows wherever the card is shown. Animations are CSS inside the
SVG, which GitHub keeps when the SVG is shown as an image. Standard library
only.
"""
import base64
import random
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
CAT = ROOT / "assets" / "cat" / "cat.png"
OUT = ROOT / "assets" / "cards"

W, H = 1200, 300
CAT_SIZE = 262           # drawn size of the cat image
C = {
    "bg0": "#090B12", "bg1": "#10131F", "line": "#262E47", "royal": "#416AE6",
    "sky": "#839DFB", "ice": "#CEDAFF", "silver": "#E6E9F0", "muted": "#939BB4",
    "gold": "#FFD36E",
}
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"

CARDS = {
    "cat-hello": {
        "side": "left",
        "title": "Hello from the cat",
        "desc": "A small black cat in a royal blue hoodie jumps up into view, lands and waves. "
                "Speech bubble: hi! welcome to my GitHub world.",
        "line1": "hi! welcome to my GitHub world 🌍",
        "line2": "grab a snack, explore the repos, stay a while ✨",
    },
    "cat-bye": {
        "side": "right",
        "title": "Goodbye from the cat",
        "desc": "The same black cat in a royal blue hoodie hops up and waves goodbye. "
                "Speech bubble: thanks for stopping by! see you soon.",
        "line1": "thanks for stopping by! see you soon 👋",
        "line2": "star a repo if something made you smile ⭐",
    },
}

STYLE = """
.jump{animation:jump 1.1s cubic-bezier(.3,.7,.4,1) .25s both}
@keyframes jump{
 0%{transform:translateY(330px)}
 55%{transform:translateY(-46px)}
 75%{transform:translateY(0) scale(1.06,.9)}
 88%{transform:translateY(-8px) scale(.98,1.03)}
 100%{transform:none}}
.idle{animation:hop 4.2s ease-in-out 1.6s infinite}
@keyframes hop{
 0%,70%,100%{transform:none}
 76%{transform:translateY(4px) scale(1.04,.95)}
 84%{transform:translateY(-26px)}
 92%{transform:translateY(0) scale(1.03,.96)}}
.sway{animation:sway 1.6s ease-in-out 1.4s infinite alternate}
@keyframes sway{from{transform:rotate(-4deg)}to{transform:rotate(4deg)}}
.shadow{animation:shadow 1.1s ease-out .25s both}
@keyframes shadow{0%{opacity:0;transform:scaleX(.3)}55%{opacity:.25;transform:scaleX(.6)}75%{opacity:.7;transform:scaleX(1.1)}100%{opacity:.6;transform:none}}
.wave path{opacity:0;animation:wave 1.2s ease-out infinite}
@keyframes wave{0%{opacity:0;transform:scale(.6)}30%{opacity:1}100%{opacity:0;transform:scale(1.15)}}
.bubble{opacity:0;animation:pop .5s cubic-bezier(.3,1.6,.5,1) 1.25s forwards}
@keyframes pop{0%{opacity:0;transform:scale(.2)}100%{opacity:1;transform:none}}
.type{animation:type 1.4s steps(34) 1.7s both}
@keyframes type{from{width:0}}
.sub{opacity:0;animation:fade .6s ease-out 3.1s forwards}
@keyframes fade{to{opacity:1}}
.tw{animation:tw 2.8s ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.15}50%{opacity:.95}}
.heart{opacity:0;animation:heart 3s ease-out infinite}
@keyframes heart{0%{opacity:0;transform:translateY(0) scale(.6)}20%{opacity:1}100%{opacity:0;transform:translateY(-70px) scale(1.1)}}
@media (prefers-reduced-motion:reduce){
 .jump,.idle,.sway,.shadow,.wave path,.bubble,.type,.sub,.tw,.heart{animation:none;opacity:1}
 .heart,.wave path{opacity:0}}
"""


def build(slug, cfg, cat_b64):
    rnd = random.Random(slug)
    left = cfg["side"] == "left"
    cat_x = 150 if left else W - 150 - CAT_SIZE
    cat_y = H - CAT_SIZE - 14
    foot_x = cat_x + CAT_SIZE / 2
    foot_y = H - 22
    flip = "" if left else f' transform="translate({2 * cat_x + CAT_SIZE} 0) scale(-1 1)"'

    # speech bubble geometry
    bw, bh = 640, 104
    bx = cat_x + CAT_SIZE + 40 if left else cat_x - 40 - bw
    by = 62
    tail = (f"M{bx + 2} {by + 58} L{bx - 30} {by + 84} L{bx + 6} {by + 80} Z" if left
            else f"M{bx + bw - 2} {by + 58} L{bx + bw + 30} {by + 84} L{bx + bw - 6} {by + 80} Z")
    origin = f"{bx - 20}px {by + 80}px" if left else f"{bx + bw + 20}px {by + 80}px"
    # waving paw sits at the cat's raised paw (upper left of the art, mirrored for "right")
    paw_x = cat_x + CAT_SIZE * (0.22 if left else 0.78)
    paw_y = cat_y + CAT_SIZE * 0.52
    d = -1 if left else 1  # waves radiate away from the body

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
         f'viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="{slug}-t {slug}-d">',
         f'<title id="{slug}-t">{escape(cfg["title"])}</title>',
         f'<desc id="{slug}-d">{escape(cfg["desc"])}</desc>',
         f"<style>{STYLE}</style>",
         "<defs>",
         f'<clipPath id="{slug}-card"><rect width="{W}" height="{H}" rx="18"/></clipPath>',
         f'<radialGradient id="{slug}-glow" cx="{foot_x / W:.3f}" cy=".62" r=".34">'
         f'<stop offset="0" stop-color="{C["royal"]}" stop-opacity=".42"/>'
         f'<stop offset="1" stop-color="{C["royal"]}" stop-opacity="0"/></radialGradient>',
         f'<pattern id="{slug}-dots" width="24" height="24" patternUnits="userSpaceOnUse">'
         f'<circle cx="2" cy="2" r="1" fill="{C["line"]}"/></pattern>',
         "</defs>",
         f'<g clip-path="url(#{slug}-card)">',
         f'<rect width="{W}" height="{H}" fill="{C["bg0"]}"/>',
         f'<rect width="{W}" height="{H}" fill="url(#{slug}-dots)" opacity=".7"/>',
         f'<rect width="{W}" height="{H}" fill="url(#{slug}-glow)"/>']
    for _ in range(34):
        x, y = rnd.randrange(20, W - 20), rnd.randrange(16, H - 16)
        if abs(x - foot_x) < 190 or (bx - 20 < x < bx + bw + 20 and by - 10 < y < by + 190):
            continue
        o.append(f'<circle class="tw" cx="{x}" cy="{y}" r="{rnd.choice((1, 1, 1.6))}" fill="{C["ice"]}" '
                 f'style="animation-delay:{rnd.uniform(0, 2.8):.2f}s"/>')
    # ground shadow
    o.append(f'<ellipse class="shadow" style="transform-origin:{foot_x}px {foot_y}px" cx="{foot_x}" cy="{foot_y}" '
             f'rx="92" ry="11" fill="{C["royal"]}" opacity=".6"/>')
    # cat: jump in, then idle hop + sway around the feet
    o.append(f'<g class="jump" style="transform-origin:{foot_x}px {foot_y}px">'
             f'<g class="idle" style="transform-origin:{foot_x}px {foot_y}px">'
             f'<g class="sway" style="transform-origin:{foot_x}px {foot_y}px">'
             f'<image href="data:image/png;base64,{cat_b64}" x="{cat_x}" y="{cat_y}" '
             f'width="{CAT_SIZE}" height="{CAT_SIZE}"{flip}/>'
             f'<g class="wave" fill="none" stroke="{C["sky"]}" stroke-width="4" stroke-linecap="round">')
    for i, r in enumerate((22, 36, 50)):
        o.append(f'<path style="transform-origin:{paw_x}px {paw_y}px;animation-delay:{1.4 + i * .18:.2f}s" '
                 f'd="M{paw_x + d * r * .55:.1f} {paw_y - r * .85:.1f} Q{paw_x + d * r:.1f} {paw_y:.1f} '
                 f'{paw_x + d * r * .55:.1f} {paw_y + r * .85:.1f}"/>')
    o.append("</g></g></g></g>")
    # floating hearts / sparkles near the cat
    for i, (ch, dx) in enumerate((("💙", -165), ("✨", 170), ("💙", 205))):
        hx = foot_x + dx
        o.append(f'<text class="heart" x="{hx}" y="{cat_y + 150}" font-size="22" text-anchor="middle" '
                 f'style="transform-origin:{hx}px {cat_y + 150}px;animation-delay:{2 + i:.1f}s">{ch}</text>')
    # speech bubble
    o.append(f'<g class="bubble" style="transform-origin:{origin}">'
             f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="26" fill="{C["bg1"]}" '
             f'stroke="{C["royal"]}" stroke-width="3"/>'
             f'<path d="{tail}" fill="{C["bg1"]}" stroke="{C["royal"]}" stroke-width="3" stroke-linejoin="round"/>'
             f'<rect x="{bx + 8 if left else bx + bw - 12}" y="{by + 56}" width="6" height="26" fill="{C["bg1"]}"/>'
             f'<clipPath id="{slug}-typed"><rect class="type" x="{bx + 28}" y="{by + 10}" width="{bw - 50}" height="{bh - 20}"/></clipPath>'
             f'<text clip-path="url(#{slug}-typed)" x="{bx + 30}" y="{by + 48}" font-family="{SANS}" font-size="27" '
             f'font-weight="700" fill="{C["silver"]}">{escape(cfg["line1"])}</text>'
             f'<text class="sub" x="{bx + 30}" y="{by + 82}" font-family="{SANS}" font-size="18" '
             f'fill="{C["muted"]}">{escape(cfg["line2"])}</text>'
             "</g>")
    o.append("</g>")
    o.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="17" fill="none" stroke="{C["line"]}" stroke-width="2"/>')
    o.append("</svg>")
    path = OUT / f"{slug}.svg"
    path.write_text("\n".join(o) + "\n")
    print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB)")


def main():
    cat_b64 = base64.b64encode(CAT.read_bytes()).decode()
    for slug, cfg in CARDS.items():
        build(slug, cfg, cat_b64)


if __name__ == "__main__":
    main()
