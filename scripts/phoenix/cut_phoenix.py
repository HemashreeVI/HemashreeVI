#!/usr/bin/env python3
"""Cuts the phoenix poses out of the green-screen sheet (generated with ChatGPT)
and writes assets/phoenix/*.webp for the footer and the streak card.
Needs numpy and Pillow.

    python3 scripts/phoenix/cut_phoenix.py
"""
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / "assets" / "phoenix"

a = np.asarray(Image.open(HERE / "phoenix-green.webp").convert("RGB")).astype(float)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
m = np.maximum(r, b)
alpha = np.clip(1 - (g - m - 25) / 65, 0, 1)
sheet = np.dstack([r, np.minimum(g, m + 8), b, alpha * 255]).astype(np.uint8)

# (name, columns the pose occupies, rows, crop box or None for a tight crop, output width)
# the three flap frames share one box size, placed on the bird's head, so the body stays still while the wings move
POSES = [
    ("rising",  (34, 512),   (0, 585),   None, 300),
    ("perched", (566, 818),  (0, 585),   None, 150),
    ("flying",  (892, 1506), (0, 585),   None, 300),
    ("flap-up",    (86, 434),   (585, 1024), (310 - 300, 590, 310 + 220, 1020), 260),
    ("flap-level", (503, 1005), (585, 1024), (790 - 300, 590, 790 + 220, 1020), 260),
    ("flap-down",  (1024, 1474), (585, 1024), (1300 - 300, 590, 1300 + 220, 1020), 260),
]
OUT.mkdir(parents=True, exist_ok=True)
for name, (c0, c1), (r0, r1), box, width in POSES:
    part = np.zeros_like(sheet)
    part[r0:r1, c0:c1] = sheet[r0:r1, c0:c1]          # only this pose, nothing from its neighbours
    im = Image.fromarray(part, "RGBA")
    im = im.crop(box) if box else im.crop(im.getbbox())
    h = round(im.height * width / im.width)
    im.resize((width, h), Image.LANCZOS).save(OUT / f"{name}.webp", quality=88, method=6)
    print(f"{name:11} {width}x{h}")
