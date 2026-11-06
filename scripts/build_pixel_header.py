#!/usr/bin/env python3
"""Builds the animated pixel-art header (assets/cards/pixel-header.svg).

A game-style "player select" screen: the pixel portrait from
assets/pixel/portrait.txt builds in row by row, the name drops in letter by
letter in a 5x7 pixel font, skill bars fill up and the stars twinkle.

    python3 scripts/build_pixel_header.py

Standard library only.
"""
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPRITE = ROOT / "assets" / "pixel" / "portrait.txt"
OUT = ROOT / "assets" / "cards" / "pixel-header.svg"

W, H = 1200, 480
C = {
    "bg0": "#090B14", "bg1": "#10131F", "grid": "#18203A", "line": "#2B3963",
    "royal": "#416AE6", "sky": "#839DFB", "ice": "#CEDAFF", "silver": "#E6E9F0",
    "muted": "#8E9BC0", "mint": "#8FE3C8", "rose": "#F0A8D0", "gold": "#FFD36E",
    "shadow": "#1B2A6B",
}

NAME = "HEMASHREE"
CLASS_LINE = "CLASS: SOFTWARE ENGINEER"
SUB_LINE = "VIT CHENNAI · B.TECH CSE · LVL 2026"
SKILLS = [  # label, fill out of 10, colour
    ("VISION", 9, C["royal"]),
    ("SECURITY", 8, C["sky"]),
    ("BACKEND", 8, C["mint"]),
    ("EMBEDDED", 7, C["rose"]),
]
PERKS = ["PATENT CO-INVENTOR", "4 LANGUAGES", "13K X-RAYS"]

# 5x7 pixel font: each glyph is 7 rows of 5 bits
FONT = {
    "A": "01110 10001 10001 11111 10001 10001 10001",
    "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110",
    "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111",
    "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111",
    "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110",
    "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001",
    "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001",
    "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110",
    "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101",
    "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110",
    "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110",
    "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010",
    "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100",
    "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110",
    "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111",
    "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010",
    "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110",
    "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110",
    "9": "01110 10001 10001 01111 00001 00010 01100",
    ":": "00000 00100 00100 00000 00100 00100 00000",
    ".": "00000 00000 00000 00000 00000 01100 01100",
    "·": "00000 00000 00000 00100 00000 00000 00000",
    "-": "00000 00000 00000 11111 00000 00000 00000",
    "+": "00000 00100 00100 11111 00100 00100 00000",
    "!": "00100 00100 00100 00100 00100 00000 00100",
    "▶": "01000 01100 01110 01111 01110 01100 01000",
    "♥": "00000 01010 11111 11111 01110 00100 00000",
    "★": "00100 00100 11111 01110 01110 11011 00000",
    " ": "00000 00000 00000 00000 00000 00000 00000",
}


def glyph_rects(ch, x, y, s):
    """Rects for one glyph, merging horizontal runs."""
    rows = FONT[ch].split()
    out = []
    for r, bits in enumerate(rows):
        c = 0
        while c < 5:
            if bits[c] == "1":
                start = c
                while c < 5 and bits[c] == "1":
                    c += 1
                out.append(f'<rect x="{x + start * s}" y="{y + r * s}" width="{(c - start) * s}" height="{s}"/>')
            else:
                c += 1
    return "".join(out)


def pixel_text(text, x, y, s, fill, cls="", gap=1):
    adv = (5 + gap) * s
    body = "".join(glyph_rects(ch, x + i * adv, y, s) for i, ch in enumerate(text))
    return f'<g class="{cls}" fill="{fill}">{body}</g>'


def text_width(text, s, gap=1):
    return len(text) * (5 + gap) * s - gap * s


def load_sprite():
    lines = [l.rstrip("\n") for l in SPRITE.read_text().splitlines() if not l.startswith("#")]
    pal = dict(kv.split("=") for kv in lines[0].split())
    return pal, lines[1:]


def portrait(px0, py0, s):
    pal, rows = load_sprite()
    parts = []
    n = len(rows)
    for r, row in enumerate(rows):
        rects = []
        c = 0
        while c < len(row):
            k = row[c]
            start = c
            while c < len(row) and row[c] == k:
                c += 1
            if k != ".":
                op = ' opacity=".85"' if k == "z" else ""
                rects.append(f'<rect x="{px0 + start * s}" y="{py0 + r * s}" width="{(c - start) * s}" height="{s}" fill="#{pal[k]}"{op}/>')
        if rects:
            delay = 0.25 + r * (1.6 / n)
            parts.append(f'<g class="row" style="animation-delay:{delay:.2f}s">{"".join(rects)}</g>')
    return "".join(parts), len(rows[0]) * s, n * s


def build():
    rnd = random.Random(7)
    fy0 = (H - 70 * 4) // 2
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="ph-t ph-d" shape-rendering="crispEdges">')
    o.append('<title id="ph-t">HEMASHREE: player select</title>')
    o.append('<desc id="ph-d">Pixel-art portrait of Hemashree in a navy suit beside her name in a pixel font. '
             'Class: Software Engineer. Skill bars for vision, security, backend and embedded fill up. '
             'Perks: patent co-inventor, 4 languages, 13K X-rays. Press start.</desc>')
    o.append(f"""<style>
.row{{opacity:0;animation:row .35s steps(3) forwards}}
@keyframes row{{0%{{opacity:0;transform:translateX(-12px)}}100%{{opacity:1;transform:none}}}}
.scan{{animation:scan 1.9s linear .2s forwards;opacity:0}}
@keyframes scan{{0%{{opacity:.9;transform:translateY(0)}}95%{{opacity:.9}}100%{{opacity:0;transform:translateY(276px)}}}}
.bob{{animation:bob 2.4s steps(2) 2.2s infinite}}
@keyframes bob{{0%,100%{{transform:none}}50%{{transform:translateY(-4px)}}}}
.ltr{{opacity:0;animation:drop .5s cubic-bezier(.3,1.6,.5,1) forwards}}
@keyframes drop{{0%{{opacity:0;transform:translateY(-60px)}}60%{{opacity:1}}100%{{opacity:1;transform:none}}}}
.fade{{opacity:0;animation:fade .4s steps(4) forwards}}
@keyframes fade{{to{{opacity:1}}}}
.bar{{transform:scaleX(0);animation:fill 1s steps(10) forwards}}
@keyframes fill{{to{{transform:scaleX(1)}}}}
.tw{{animation:tw 2.6s steps(2) infinite}}
@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:1}}}}
.blink{{animation:blink 1s steps(1) 4.4s infinite;opacity:0}}
@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}}}
.heart{{animation:beat 1.2s steps(2) infinite}}
@keyframes beat{{0%,100%{{opacity:1}}50%{{opacity:.45}}}}
@media (prefers-reduced-motion:reduce){{.row,.ltr,.fade,.blink{{animation:none;opacity:1}}.bar{{animation:none;transform:none}}.scan,.tw,.bob,.heart{{animation:none}}}}
</style>""")
    # background, pixel grid, stars
    o.append(f'<defs><pattern id="pg" width="12" height="12" patternUnits="userSpaceOnUse"><path d="M12 0H0V12" fill="none" stroke="{C["grid"]}" stroke-width="1"/></pattern>'
             f'<radialGradient id="glow" cx=".15" cy=".5" r=".5"><stop offset="0" stop-color="{C["royal"]}" stop-opacity=".28"/><stop offset="1" stop-color="{C["royal"]}" stop-opacity="0"/></radialGradient>'
             f'<pattern id="scanl" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity=".18"/></pattern></defs>')
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="{C["bg0"]}"/>')
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#pg)" opacity=".55"/>')
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#glow)"/>')
    for _ in range(120):
        x, y = rnd.randrange(20, W - 20), rnd.randrange(20, H - 20)
        if (44 < x < 340 and fy0 - 20 < y < fy0 + 300) or (346 < x < 1080 and 30 < y < 455):
            continue  # keep stars off the portrait and the text
        sz = rnd.choice((3, 3, 3, 6))
        col = rnd.choice((C["ice"], C["sky"], C["silver"], C["gold"]))
        o.append(f'<rect class="tw" x="{x}" y="{y}" width="{sz}" height="{sz}" fill="{col}" style="animation-delay:{rnd.uniform(0, 2.6):.2f}s"/>')

    # portrait inside a chunky pixel frame
    s = 4  # portrait pixel size
    fw, fh = 50 * s + 24, 70 * s
    fx, fy = 64, (H - fh) // 2
    o.append(f'<rect x="{fx - 6}" y="{fy - 6}" width="{fw + 12}" height="{fh + 12}" fill="{C["shadow"]}"/>')
    o.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" fill="{C["bg1"]}" stroke="{C["royal"]}" stroke-width="6"/>')
    for cx, cy in ((fx - 6, fy - 6), (fx + fw, fy - 6), (fx - 6, fy + fh), (fx + fw, fy + fh)):
        o.append(f'<rect x="{cx}" y="{cy}" width="6" height="6" fill="{C["bg0"]}"/>')
    o.append(f'<rect x="{fx + 6}" y="{fy + fh - 40}" width="{fw - 12}" height="34" fill="{C["royal"]}" opacity=".12"/>')
    body, pw, ph = portrait(fx + 12, fy + 4, s)
    o.append(f'<g class="bob">{body}</g>')
    o.append(f'<rect class="scan" x="{fx + 6}" y="{fy + 4}" width="{fw - 12}" height="6" fill="{C["ice"]}"/>')
    o.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" fill="url(#scanl)"/>')
    # P1 tag
    o.append(f'<rect x="{fx + 10}" y="{fy + 10}" width="38" height="22" fill="{C["royal"]}"/>')
    o.append(pixel_text("P1", fx + 17, fy + 16, 2, C["silver"], gap=1))

    # right column
    rx = 380
    o.append(pixel_text("▶ PLAYER SELECT", rx, 46, 3, C["sky"], "fade", gap=1).replace('class="fade"', 'class="fade" style="animation-delay:.2s"'))
    o.append(f'<rect class="fade" style="animation-delay:.3s" x="{rx}" y="78" width="{W - rx - 60}" height="3" fill="{C["line"]}"/>')
    ls = 11  # name pixel size
    adv = 6 * ls
    for i, ch in enumerate(NAME):
        x = rx + i * adv
        d = 0.6 + i * 0.12
        o.append(f'<g class="ltr" style="animation-delay:{d:.2f}s">'
                 f'<g fill="{C["shadow"]}">{glyph_rects(ch, x + 5, 108 + 5, ls)}</g>'
                 f'<g fill="{C["royal"]}">{glyph_rects(ch, x, 108, ls)}</g>'
                 f'</g>')
    y = 108 + 7 * ls + 30
    o.append(pixel_text(CLASS_LINE, rx, y, 3, C["silver"], "fade", gap=1).replace('class="fade"', 'class="fade" style="animation-delay:1.9s"'))
    o.append(pixel_text(SUB_LINE, rx, y + 34, 2, C["muted"], "fade", gap=1).replace('class="fade"', 'class="fade" style="animation-delay:2.1s"'))

    # HP hearts
    hy = y + 66
    hx = rx
    o.append(pixel_text("HP", hx, hy + 2, 2, C["muted"], "fade").replace('class="fade"', 'class="fade" style="animation-delay:2.2s"'))
    for i in range(5):
        o.append(f'<g class="fade" style="animation-delay:{2.25 + i * .08:.2f}s"><g class="heart" style="animation-delay:{i * .15:.2f}s">'
                 f'{pixel_text("♥", hx + 36 + i * 22, hy, 3, C["rose"])}</g></g>')
    o.append(pixel_text("XP", hx + 170, hy + 2, 2, C["muted"], "fade").replace('class="fade"', 'class="fade" style="animation-delay:2.3s"'))
    o.append(f'<rect class="fade" style="animation-delay:2.3s" x="{hx + 200}" y="{hy}" width="206" height="18" fill="none" stroke="{C["line"]}" stroke-width="3"/>')
    o.append(f'<rect class="bar" style="animation-delay:2.4s;transform-origin:{hx + 203}px 0" x="{hx + 203}" y="{hy + 3}" width="180" height="12" fill="{C["gold"]}"/>')

    # skill bars, two columns
    by = hy + 44
    for i, (label, val, col) in enumerate(SKILLS):
        cx = rx + (i % 2) * 340
        cy = by + (i // 2) * 34
        d = 2.6 + i * 0.2
        o.append(pixel_text(label, cx, cy + 3, 2, C["silver"], "fade").replace('class="fade"', f'class="fade" style="animation-delay:{d:.2f}s"'))
        bx = cx + 112
        for k in range(10):
            o.append(f'<rect class="fade" style="animation-delay:{d:.2f}s" x="{bx + k * 18}" y="{cy}" width="14" height="18" fill="{C["grid"]}"/>')
        for k in range(val):
            o.append(f'<rect class="fade" style="animation-delay:{d + .1 + k * .07:.2f}s" x="{bx + k * 18}" y="{cy}" width="14" height="18" fill="{col}"/>')

    # perks
    py = by + 84
    px = rx
    for i, perk in enumerate(PERKS):
        label = "★ " + perk
        w = text_width(label, 2) + 24
        d = 3.6 + i * 0.18
        o.append(f'<g class="fade" style="animation-delay:{d:.2f}s"><rect x="{px}" y="{py}" width="{w}" height="30" fill="{C["bg1"]}" stroke="{C["line"]}" stroke-width="3"/>'
                 f'{pixel_text(label, px + 12, py + 8, 2, C["gold"] if i == 0 else C["ice"])}</g>')
        px += w + 12

    # press start
    o.append(f'<g class="blink">{pixel_text("PRESS START", W - 60 - text_width("PRESS START", 3), H - 50, 3, C["mint"])}</g>')
    o.append(f'<rect x="3" y="3" width="{W - 6}" height="{H - 6}" rx="16" fill="none" stroke="{C["line"]}" stroke-width="2"/>')
    o.append("</svg>")
    OUT.write_text("\n".join(o) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build()
