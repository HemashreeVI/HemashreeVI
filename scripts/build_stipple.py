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
INK = "#ECE8DC"          # warm off-white dots, like paper under a lamp
N_DOTS = 24000
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
    im = Image.open(SRC).convert("RGBA")
    im = im.crop((60, 0, im.width - 40, round(im.height * 0.66)))   # head and shoulders
    ph = 480                                   # portrait height on the card
    pw = round(im.width * ph / im.height)
    im = im.resize((pw, ph), Image.LANCZOS)
    alpha = np.asarray(im.getchannel("A"), dtype=np.float32) / 255
    grey = ImageOps.grayscale(im.convert("RGB")).filter(ImageFilter.UnsharpMask(4, 160, 2))
    a = np.asarray(grey, dtype=np.float32)
    m = alpha > .5
    lo, hi = np.percentile(a[m], 2), np.percentile(a[m], 99)
    lum = np.clip((a - lo) / (hi - lo), 0, 1)
    edges = np.asarray(grey.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(1)), dtype=np.float32) / 255
    edges = np.clip(edges * 3, 0, 1)
    # light areas get dense dots, edges get extra, and the whole figure keeps a faint base so the dark suit still reads
    dens = (0.05 + lum ** 1.8 + 0.35 * edges) * alpha
    dens = dens / dens.sum()
    idx = np.random.default_rng(SEED).choice(dens.size, size=N_DOTS, replace=True, p=dens.ravel())
    ys, xs = np.divmod(idx, pw)
    ox, oy = (W - pw) / 2, 14
    pts = [(ox + x + rnd.random(), oy + y + rnd.random()) for x, y in zip(xs, ys)]
    return pts


def dot_paths(pts, groups=4):
    """All dots as zero-length round-capped strokes: far smaller than one <circle> per dot."""
    buckets = [[] for _ in range(groups)]
    for i, (x, y) in enumerate(pts):
        buckets[i % groups].append(f"M{x:.1f} {y:.1f}h0")
    out = []
    for g, b in enumerate(buckets):
        out.append(f'<path class="tw tw{g}" d="{"".join(b)}" stroke="{INK}" stroke-width="1.35" stroke-linecap="round" fill="none"/>')
    return "\n".join(out)


def ring(cx, cy, rx, ry, rot, dur, rev=False):
    """A thin elliptical orbit with a dotted track sliding along it."""
    return (f'<g transform="rotate({rot} {cx} {cy})">'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{INK}" stroke-opacity=".22" stroke-width="1"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{INK}" stroke-opacity=".55" stroke-width="2.2" '
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
    return (f'<g class="name" fill="{INK}" stroke="#000" stroke-width="1.2">'
            + "".join(out) + "</g>")


def main():
    rnd = random.Random(SEED)
    pts = portrait_dots(rnd)
    cx, cy = W / 2, 250
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
<rect width="{W}" height="{H}" rx="18" fill="#000"/>
{stars(rnd)}
{ring(cx, cy, 440, 120, -8, 90)}
{ring(cx, cy + 40, 360, 92, 14, 70, rev=True)}
<g>{dot_paths(pts)}</g>
{block_name("HEMASHREE", 470)}
</svg>
"""
    OUT.write_text(svg, encoding="utf-8")
    print(f"stipple.svg  {len(svg.encode()) / 1024:.0f} KB, {len(pts)} dots")


if __name__ == "__main__":
    main()
