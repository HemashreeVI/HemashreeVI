#!/usr/bin/env python3
"""Draws the Snow Globe theme toggle banner in two versions:

    assets/cards/toggle-light.svg   sunny pixel landscape, knob on the sun
    assets/cards/toggle-dark.svg    the same place at night, knob on the moon

The README shows one or the other with <picture> + prefers-color-scheme, so the
switch follows the visitor's GitHub theme. GitHub READMEs cannot run code, so it
is not clickable: it shows which mode you are in.

    python3 scripts/build_toggle.py

Standard library only.
"""
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/cards"

W, H = 1200, 400
PX = 8                                   # one "pixel" of the pixel art
SX, SY, SW, SH = 128, 72, 944, 208       # scene window inside the toggle
COLS, ROWS = SW // PX, SH // PX          # 118 × 26

THEMES = {
    "light": {
        "page": "#F4E9D8", "frame0": "#FBF3E6", "frame1": "#E2CFB3", "frame_edge": "#C9B190", "frame_shadow": "#D8C3A3",
        "sky": ["#F6C7A1", "#F4B488", "#F2A06F", "#EE8C5E", "#E77B57"],
        "far": "#C98AA0", "near": "#B0708C",
        "ground": ["#E8B055", "#DDA046", "#D19239"], "speck": "#C5833A",
        "wall": "#F2D7A6", "wall_dark": "#DDBD86", "roof": "#5C5A8C", "roof_dark": "#47457A", "door": "#3F3D6B",
        "window": "#3F3D6B", "chimney": "#B65E45",
        "leaf": ["#8FA84A", "#7A9440", "#667E36"], "trunk": "#8A5A3C",
        "orb": "#FFE7A0", "orb_core": "#FFF6D6", "cloud": "#FCE3CF",
        "text": "#3A2E28", "muted": "#8A7563", "accent": "#E07A3F",
        "label": "LIGHT MODE", "icon": "☀",
    },
    "dark": {
        "page": "#0A0C1C", "frame0": "#1B1F3B", "frame1": "#0F1228", "frame_edge": "#3A4068", "frame_shadow": "#07081A",
        "sky": ["#0B0E2A", "#121640", "#1B1E52", "#272463", "#352A70"],
        "far": "#3B2E6E", "near": "#2B2258",
        "ground": ["#1E2A4A", "#19233F", "#141C34"], "speck": "#24345A",
        "wall": "#4A5184", "wall_dark": "#3B4172", "roof": "#5B4A8C", "roof_dark": "#45387A", "door": "#15162F",
        "window": "#FFD36B", "chimney": "#5A3346",
        "leaf": ["#3F6B66", "#335A57", "#284A48"], "trunk": "#5A3E46",
        "orb": "#E8ECFF", "orb_core": "#FFFFFF", "cloud": None,
        "text": "#EEF0F7", "muted": "#9097B8", "accent": "#A9B8FF",
        "label": "DARK MODE", "icon": "☾",
    },
}

# knob centre (in scene columns): the sun sits right of centre, the moon left of it
ORB = {"light": (78, 10), "dark": (46, 9)}


def px(c, r, color, w=1, h=1):
    return f'<rect x="{SX + c * PX}" y="{SY + r * PX}" width="{w * PX}" height="{h * PX}" fill="{color}"/>'


def scene(t, mode):
    rnd = random.Random(7)
    out = []
    # sky in flat pixel bands
    bands = t["sky"]
    for i, col in enumerate(bands):
        out.append(px(0, i * 3, col, COLS, 3 if i < len(bands) - 1 else 15))
    # stars at night
    if mode == "dark":
        for _ in range(55):
            c, r = rnd.randrange(COLS), rnd.randrange(0, 12)
            out.append(f'<rect x="{SX + c * PX + 3}" y="{SY + r * PX + 3}" width="2" height="2" fill="#FFFFFF" opacity="{rnd.choice((.5, .7, 1))}">'
                       f'<animate attributeName="opacity" values="1;.2;1" dur="{rnd.uniform(2, 5):.1f}s" begin="{rnd.uniform(0, 3):.1f}s" repeatCount="indefinite"/></rect>')
    # sun or moon (pixel disc)
    oc, orow = ORB[mode]
    for dr in range(-3, 4):
        for dc in range(-3, 4):
            if dc * dc + dr * dr <= 10:
                out.append(px(oc + dc, orow + dr, t["orb_core"] if dc * dc + dr * dr <= 3 else t["orb"]))
    if mode == "dark":                       # a few craters on the full moon
        for dc, dr in ((-1, -1), (1, 1), (2, -1), (-2, 1)):
            out.append(px(oc + dc, orow + dr, "#C9CEEA"))
    # clouds by day
    if t["cloud"]:
        for cc, cr, wdt in ((58, 3, 7), (96, 5, 6), (30, 2, 5)):
            out.append(px(cc, cr, t["cloud"], wdt, 1) + px(cc + 1, cr - 1, t["cloud"], wdt - 3, 1))
    # far and near hills with a stepped top
    for c in range(COLS):
        top_far = 13 + round(2 * math.sin(c / 9.0))
        top_near = 16 + round(1.5 * math.sin(c / 6.0 + 1))
        out.append(px(c, top_far, t["far"], 1, ROWS - top_far))
        out.append(px(c, top_near, t["near"], 1, ROWS - top_near))
    # ground with texture
    for i, col in enumerate(t["ground"]):
        out.append(px(0, 19 + i * 2, col, COLS, ROWS - 19 - i * 2))
    for _ in range(90):
        out.append(px(rnd.randrange(COLS), rnd.randrange(20, ROWS), t["speck"]))
    # path from the door
    for k in range(6):
        out.append(px(17 + k, 20 + k // 2, t["ground"][0] if mode == "light" else "#2A3A5E", 2, 1))
    # house
    out.append(px(7, 12, t["wall"], 20, 8))
    out.append(px(7, 18, t["wall_dark"], 20, 2))
    for r in range(7):                        # roof as stacked rows
        out.append(px(11 - r, 5 + r, t["roof"], 12 + 2 * r, 1))
    out.append(px(4, 11, t["roof_dark"], 26, 1))
    out.append(px(21, 4, t["chimney"], 2, 4))
    if mode == "dark":
        out.append(f'<rect x="{SX + 21 * PX}" y="{SY + 2 * PX}" width="{2 * PX}" height="{PX}" fill="#8A8FB8" opacity=".5">'
                   f'<animate attributeName="y" values="{SY + 3 * PX};{SY}" dur="3s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values=".6;0" dur="3s" repeatCount="indefinite"/></rect>')
    for wc in (10, 22):                       # windows with frames
        out.append(px(wc - 1, 13, t["roof_dark"], 4, 4))
        out.append(px(wc, 14, t["window"], 2, 2))
    if mode == "dark":                        # warm window glow
        for wc in (10, 22):
            out.append(f'<rect x="{SX + (wc - 2) * PX}" y="{SY + 12 * PX}" width="{6 * PX}" height="{6 * PX}" fill="#FFD36B" opacity=".12"/>')
    out.append(px(15, 15, t["door"], 3, 5))
    # tree
    trunk_c = 99
    out.append(px(trunk_c, 13, t["trunk"], 2, 8))
    blob = [(0, 8, 6), (1, 7, 8), (2, 6, 10), (3, 5, 12), (4, 5, 12), (5, 5, 12), (6, 6, 10), (7, 7, 8)]
    for i, (r, c0, wdt) in enumerate(blob):
        out.append(px(trunk_c - 6 + (c0 - 5), 5 + r, t["leaf"][1], wdt, 1))
    for _ in range(26):
        r = rnd.randrange(5, 13)
        c = trunk_c - 5 + rnd.randrange(0, 11)
        out.append(px(c, r, rnd.choice((t["leaf"][0], t["leaf"][2]))))
    # fence
    for c in range(32, 52, 3):
        out.append(px(c, 18, t["wall_dark"], 1, 2))
    out.append(px(32, 18, t["wall_dark"], 19, 1))
    return "".join(out)


def pill(mode, slide=True):
    """defs + toggle (frame, scene window, glass knob), in banner coordinates."""
    t = THEMES[mode]
    oc, orow = ORB[mode]
    kx = SX + oc * PX + PX / 2                # knob rests on the sun / moon
    ky = SY + SH / 2
    other = ORB["dark" if mode == "light" else "light"][0]
    kx0 = SX + other * PX + PX / 2           # and slides in from the other side
    r = 96
    defs = f'''<defs>
  <linearGradient id="fr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t['frame0']}"/><stop offset="1" stop-color="{t['frame1']}"/></linearGradient>
  <radialGradient id="glass" cx=".35" cy=".3" r=".75">
    <stop offset="0" stop-color="#FFFFFF" stop-opacity=".55"/><stop offset=".45" stop-color="#FFFFFF" stop-opacity=".08"/>
    <stop offset="1" stop-color="#FFFFFF" stop-opacity=".22"/></radialGradient>
  <clipPath id="win"><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="{SH / 2}"/></clipPath>
  <clipPath id="ball"><circle cx="0" cy="0" r="{r}"/></clipPath>
  <filter id="sh" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000" flood-opacity=".25"/></filter>
  <g id="scene">{scene(t, mode)}</g>
</defs>'''
    frame = (f'<rect x="{SX - 44}" y="{SY - 40}" width="{SW + 88}" height="{SH + 80}" rx="{(SH + 80) / 2}" fill="url(#fr)" '
             f'stroke="{t["frame_edge"]}" stroke-width="2" filter="url(#sh)"/>'
             f'<rect x="{SX - 10}" y="{SY - 8}" width="{SW + 20}" height="{SH + 16}" rx="{(SH + 16) / 2}" fill="{t["frame_shadow"]}"/>')
    window = f'<g clip-path="url(#win)"><use href="#scene"/></g>'
    # glass knob: the scene magnified behind a glossy sphere, sliding in on load
    mag = 1.35
    slide_anim = (f'<animateTransform attributeName="transform" type="translate" from="{kx0} {ky}" to="{kx} {ky}" dur="1.4s" '
                  f'calcMode="spline" keyTimes="0;1" keySplines=".25 .1 .25 1" fill="freeze"/>') if slide else ""
    knob = (f'<g transform="translate({kx} {ky})">' + slide_anim +
            f'<circle r="{r + 5}" fill="#000" opacity=".2" cy="10"/>'
            f'<g clip-path="url(#ball)"><g id="magnify">'
            f'<use href="#scene" transform="scale({mag}) translate({-kx} {-ky})"/>'
            f'</g></g>'
            f'<circle r="{r}" fill="url(#glass)" stroke="#FFFFFF" stroke-opacity=".75" stroke-width="3"/>'
            f'<ellipse cx="{-r * .38}" cy="{-r * .45}" rx="{r * .32}" ry="{r * .16}" fill="#FFFFFF" opacity=".6" transform="rotate(-28 {-r * .38} {-r * .45})"/>'
            + "".join(
                f'<circle cx="{c}" cy="0" r="2.2" fill="#FFFFFF" opacity=".85">'
                f'<animate attributeName="cy" values="{-r * .7:.0f};{r * .7:.0f}" dur="{d}s" begin="{b}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;.9;.9;0" keyTimes="0;.15;.8;1" dur="{d}s" begin="{b}s" repeatCount="indefinite"/></circle>'
                for c, d, b in ((-40, 4.2, 0), (-12, 5.1, 1.3), (18, 3.8, .6), (44, 4.6, 2.1), (-62, 5.4, 2.8), (60, 4.0, 3.3), (2, 4.9, 1.9)))
            + '</g>')
    return defs, frame + window + knob


def build(mode):
    t = THEMES[mode]
    defs, toggle = pill(mode)
    label = (f'<text x="{W / 2}" y="{SY + SH + 82}" text-anchor="middle" font-family="\'JetBrains Mono\',Menlo,Consolas,monospace" '
             f'font-size="15" letter-spacing="4" font-weight="700" fill="{t["muted"]}">{t["icon"]}  {t["label"]}</text>'
             f'<rect x="{W / 2 - 36}" y="{SY + SH + 96}" width="72" height="3" rx="1.5" fill="{t["accent"]}"/>'
             f'<text x="{W / 2}" y="{SY + SH + 122}" text-anchor="middle" font-family="Inter,\'Segoe UI\',Arial,sans-serif" '
             f'font-size="13" fill="{t["muted"]}">switch your GitHub theme to flip the switch</text>')
    body = f'<rect width="{W}" height="{H + 30}" rx="20" fill="{t["page"]}"/>' + toggle + label
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H + 30}" '
           f'viewBox="0 0 {W} {H + 30}" role="img" aria-label="A pill-shaped theme toggle with a glass snow-globe knob over a pixel-art '
           f'{"sunny landscape" if mode == "light" else "night landscape"}: a small house, a fence, hills and a tree. {t["label"].title()}.">'
           + defs + body + "</svg>")
    (OUT / f"toggle-{mode}.svg").write_text(svg)
    print("wrote", OUT / f"toggle-{mode}.svg")


if __name__ == "__main__":
    for m in ("light", "dark"):
        build(m)
