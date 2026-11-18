#!/usr/bin/env python3
"""Cuts the marble chess pieces out of the green-screen images (generated with ChatGPT)
and writes assets/chess/<piece>.webp, which build_cards.py embeds in the section titles
and the footer. Needs numpy and Pillow.

    python3 scripts/chess_pieces/cut_pieces.py
"""
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / "assets" / "chess"
SCALE = 0.26          # pixels kept per pixel of the green-screen photo of the set (the king ends up ~190 px tall)
NAMES = ["queen", "king", "knight", "rook", "bishop", "pawn"]   # left to right in set-green.webp


def key(path):
    """Green screen → transparency: the greener a pixel is than its red/blue, the more transparent."""
    a = np.asarray(Image.open(path).convert("RGB")).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = np.maximum(r, b)
    alpha = np.clip(1 - (g - m - 25) / 65, 0, 1)
    g = np.minimum(g, m + 8)                       # remove green spill from the edges
    return Image.fromarray(np.dstack([r, g, b, alpha * 255]).astype(np.uint8), "RGBA")


def save(im, name, height):
    im = im.crop(im.getbbox())
    w = round(im.width * height / im.height)
    im.resize((w, height), Image.LANCZOS).save(OUT / f"{name}.webp", quality=90, method=6)
    print(f"{name:7} {w}x{height}")


OUT.mkdir(parents=True, exist_ok=True)
row = key(HERE / "set-green.webp")
cols = (np.asarray(row)[..., 3] > 40).any(axis=0)
runs, start = [], None
for x, on in enumerate(list(cols) + [False]):          # the pieces are separated by empty columns
    if on and start is None:
        start = x
    elif not on and start is not None:
        if x - start > 40:
            runs.append((start, x))
        start = None
king_h = 0
for name, (x0, x1) in zip(NAMES, runs):
    im = row.crop((x0, 0, x1, row.height))
    h = im.crop(im.getbbox()).height
    king_h = h if name == "king" else king_h
    save(im, name, round(h * SCALE))
# the fallen king is shot closer up: make it as long as the standing king is tall
fallen = key(HERE / "fallen-king-green.webp")
fb = fallen.crop(fallen.getbbox())
save(fallen, "fallen-king", round(fb.height * king_h * SCALE / fb.width))
