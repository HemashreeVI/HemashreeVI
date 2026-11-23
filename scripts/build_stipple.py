#!/usr/bin/env python3
"""Stippled portrait footer: the photo redrawn as thousands of light dots on black, two dotted
orbit rings around it and HEMASHREE in block pixel letters.
Input:  assets/portrait-cut.webp (the photo with its background removed)
Output: assets/cards/stipple.svg
Run:    python3 scripts/build_stipple.py
"""
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "portrait-cut.webp"
OUT = ROOT / "assets" / "cards" / "stipple.svg"

W, H = 1200, 600
INK = "#ECE8DC"          # stars
GRID = 3.4          # dot spacing in px; smaller = more dots, sharper face
SEED = 7

# 5 x 7 block font: only the letters the name needs
FONT = {
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
}


def portrait_dots(rnd):
    """Halftone stipple: a dense jittered grid where each dot's size and brightness follow the photo,
    coloured from the photo. The face is contrast-stretched on its own so eyes, brows and glasses read."""
    im = Image.open(SRC).convert("RGBA")
    im = im.crop((110, 0, im.width - 90, round(im.height * 0.47)))   # head and shoulders, face large
    ph = 510
    pw = round(im.width * ph / im.height)
    im = im.resize((pw, ph), Image.LANCZOS)
    alpha = np.asarray(im.getchannel("A"), dtype=np.float32) / 255
    rgb = np.asarray(im.convert("RGB"), dtype=np.float32) / 255
    grey = ImageOps.grayscale(im.convert("RGB")).filter(ImageFilter.UnsharpMask(3, 120, 1))
    a = np.asarray(grey, dtype=np.float32)
    m = alpha > .5
    r, g, bl = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    skin = ((r - bl > .08) & (r > g) & (r > .25)).astype(np.float32) * alpha
    skin = np.asarray(Image.fromarray((skin * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5)), dtype=np.float32) / 255
    sm = skin > .5
    stretch = lambda lo, hi: np.clip((a - lo) / (hi - lo), 0, 1)
    body = stretch(np.percentile(a[m], 3), np.percentile(a[m], 98)) ** .7
    face = stretch(np.percentile(a[sm], 4), np.percentile(a[sm], 94)) ** .55
    edges = np.clip(np.asarray(grey.filter(ImageFilter.FIND_EDGES), dtype=np.float32) / 255 * 2.5, 0, 1)
    # hair: dark, not very colourful, not skin, in the upper part of the picture (the suit below is navy)
    mx = rgb.max(axis=2); sat = (mx - rgb.min(axis=2)) / np.maximum(mx, 1e-3)
    yy = np.arange(ph)[:, None] / ph
    hair = (alpha > .5) & (skin < .3) & (mx < .32) & ((sat < .5) | (yy < .35)) & (yy < .78)
    hair = np.asarray(Image.fromarray((hair * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5)), dtype=np.float32) / 255 > .5
    val = (1 - skin) * np.clip(.18 + .82 * body + .3 * edges, 0, 1) + skin * face
    ox, oy = (W - pw) / 2, 8
    pts = []
    step = GRID
    row = 0
    y = 0.0
    while y < ph - 1:
        x = step / 2 if row % 2 else 0.0
        while x < pw - 1:
            jx, jy = x + rnd.uniform(-.2, .2) * step, y + rnd.uniform(-.2, .2) * step
            xi, yi = min(pw - 1, max(0, int(jx))), min(ph - 1, max(0, int(jy)))
            v = val[yi, xi] * alpha[yi, xi]
            if v > .08 and rnd.random() < .45 + v:
                size = (1.3, 1.9, 2.5, 3.0)[min(3, int(v * 4))]
                kind = 'hair' if hair[yi, xi] else 'skin' if skin[yi, xi] > .5 else ''
                pts.append((ox + jx, oy + jy, vivid(rgb[yi, xi], v, kind), size))
            x += step
        y += step * .87
        row += 1
    return pts


def vivid(c, v=1.0, kind=""):
    """Photo colour made bright and saturated enough to glow on black, snapped to a small palette.
    Hair stays near-black (a dark blue-violet sheen so it still shows on black); skin is lifted lighter."""
    import colorsys
    h, s_, _ = colorsys.rgb_to_hsv(*c)
    if kind == "hair":
        h, s_, v = .7, .45, .22 + .3 * v
    elif kind == "skin":
        s_ = min(.6, s_ * .9 + .08)
        v = .86 + .14 * v
    else:
        s_ = min(1, s_ * 1.35 + .12)
        v = .62 + .38 * v
    r, g, b = colorsys.hsv_to_rgb(h, s_, v)
    q = lambda t: min(255, round(t * 255 / 24) * 24)
    return f"#{q(r):02X}{q(g):02X}{q(b):02X}"


def dot_paths(pts, groups=4):
    """All dots as zero-length round-capped strokes, one path per colour: far smaller than one <circle> per dot."""
    from collections import defaultdict
    by = defaultdict(list)
    for i, (x, y, col, w) in enumerate(pts):
        by[(col, w, i % groups)].append(f"M{x:.1f} {y:.1f}h0")
    return "\n".join(f'<path class="tw tw{g}" d="{"".join(d)}" stroke="{col}" stroke-width="{w}" stroke-linecap="round" fill="none"/>'
                     for (col, w, g), d in sorted(by.items()))


def ring(cx, cy, rx, ry, rot, dur, rev=False, col=INK):
    """A thin elliptical orbit with a dotted track sliding along it."""
    return (f'<g transform="rotate({rot} {cx} {cy})">'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{col}" stroke-opacity=".22" stroke-width="1"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{col}" stroke-opacity=".55" stroke-width="2.2" '
            f'stroke-linecap="round" stroke-dasharray="0 14" pathLength="1400">'
            f'<animate attributeName="stroke-dashoffset" from="0" to="{"" if rev else "-"}1400" dur="{dur}s" repeatCount="indefinite"/></ellipse>'
            f'</g>')


def stars(rnd, n=90):
    out = []
    for _ in range(n):
        x, y = rnd.uniform(10, W - 10), rnd.uniform(10, H - 10)
        r = rnd.choice([0.6, 0.8, 1, 1.3])
        out.append(f'<circle class="st" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{INK}" style="animation-delay:{rnd.uniform(0, 5):.1f}s"/>')
    return "".join(out)


def block_name(name, y0, cell=13, gap=2, letter_gap=13):
    step = cell + gap
    lw = 5 * step - gap
    total = len(name) * lw + (len(name) - 1) * letter_gap
    x0 = (W - total) / 2
    out = []
    for k, ch in enumerate(name):
        lx = x0 + k * (lw + letter_gap)
        for r, row in enumerate(FONT[ch]):
            for c, bit in enumerate(row):
                if bit == "1":
                    out.append(f'<rect x="{lx + c * step:.1f}" y="{y0 + r * step}" width="{cell}" height="{cell}" rx="1.5"/>')
    return (f'<g class="name" fill="url(#neon)" stroke="#000" stroke-width="1.2">'
            + "".join(out) + "</g>")


def main():
    rnd = random.Random(SEED)
    pts = portrait_dots(rnd)
    cx, cy = W / 2, 330
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">HEMASHREE</title>
<desc id="d">A stippled portrait of Hemashree drawn in thousands of light dots on black, with two orbit rings around her and her name in block pixel letters.</desc>
<style>
.st{{animation:st 5s ease-in-out infinite;opacity:.2}}
@keyframes st{{0%,100%{{opacity:.15}}50%{{opacity:.85}}}}
.tw{{animation:tw 6s ease-in-out infinite}}
.tw1{{animation-delay:-1.5s}}.tw2{{animation-delay:-3s}}.tw3{{animation-delay:-4.5s}}
@keyframes tw{{0%,100%{{opacity:1}}50%{{opacity:.55}}}}
.name rect{{animation:nm 4s ease-in-out infinite}}
@keyframes nm{{0%,100%{{opacity:.96}}50%{{opacity:.8}}}}
</style>
<defs>
  <linearGradient id="neon" gradientUnits="userSpaceOnUse" x1="200" y1="0" x2="1000" y2="0">
    <stop offset="0" stop-color="#60A5FA"/><stop offset=".5" stop-color="#A78BFA"/><stop offset="1" stop-color="#F472B6"/>
  </linearGradient>
  <filter id="glow" x="-5%" y="-20%" width="110%" height="140%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="#000"/>
{stars(rnd)}
{ring(cx, cy, 440, 120, -8, 90, col="#60A5FA")}
{ring(cx, cy + 40, 360, 92, 14, 70, rev=True, col="#F472B6")}
<g>{dot_paths(pts)}</g>
<g filter="url(#glow)">{block_name("HEMASHREE", 478)}</g>
</svg>
"""
    OUT.write_text(svg, encoding="utf-8")
    print(f"stipple.svg  {len(svg.encode()) / 1024:.0f} KB, {len(pts)} dots")


if __name__ == "__main__":
    main()
