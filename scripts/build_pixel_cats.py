#!/usr/bin/env python3
"""Builds the animated pixel-cat banner used in READMEs.

    python3 scripts/build_pixel_cats.py                       # assets/cards/pixel-cats.svg (profile)
    python3 scripts/build_pixel_cats.py --theme light-dark --out path/to/cats.svg

The cats are pixel art drawn from the character grids below and animated with
CSS inside the SVG, which GitHub keeps when the SVG is shown as an image.
Standard library only.
"""
import argparse
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 180
P = 4                      # screen pixels per art pixel
GROUND = 150               # y of the ground line
CAT_W, CAT_H = 16 * P, 17 * P

# ---------------------------------------------------------------- art
# o outline · b body · l belly · e eye · w eye glint · p nose · r blush
HEAD_BODY = [
    "..o..........o..",
    ".obo........obo.",
    ".opbo......obpo.",
    "obbbboooooobbbbo",
    "obbbbbbbbbbbbbbo",
    "obbbbbbbbbbbbbbo",
    "obbwebbbbbbwebbo",
    "obbeebbbbbbeebbo",
    "obbbbbbppbbbbbbo",
    "obrbbbobbobbbrbo",
    "obbbbbboobbbbbbo",
    ".obbbbbbbbbbbbo.",
    "..oooooooooooo..",
    "...obbllllbbo...",
    "...obbllllbbo...",
]
LEGS = {
    "a":   ["...obo....ooo...", "...ooo.........."],
    "b":   ["...ooo....obo...", "..........ooo..."],
    "sit": ["...obo....obo...", "...ooo....ooo..."],
}
CLOSED_EYES = [  # drawn over rows 6-7 to blink or sleep
    "..bbbb....bbbb..",
    "..oooo....oooo..",
]

THEMES = {
    # Profile cards: framed, dark lavender like the other cards.
    "profile": {
        "frame": True, "bg": "#14101F", "border": "#2D2647", "ground": "#3E3463",
        "outline": "#0B0912", "eye": "#1A1426", "text": "#9A93B4", "bubble_bg": "#1C1630",
        "bubble_fg": "#E8E6F0", "bubble_border": "#3E3463", "star": "#D9CEFF",
        "kicker": "THE BUILD CREW · they ship while I sleep",
        "lines": {
            "walker1": ["git push!"],
            "walker2": ["LGTM ✓"],
            "hopper": ["こんにちは!"],
            "coder": ["fixing bugs…", "git commit -m \"✨\"", "tests green ✓"],
        },
    },
    # Project READMEs: transparent, readable on GitHub light and dark.
    "light-dark": {
        "frame": False, "bg": None, "border": None, "ground": "#8B949E",
        "outline": "#1F1A2E", "eye": "#1A1426", "text": "#8B949E", "bubble_bg": "#FFFFFF",
        "bubble_fg": "#1F1A2E", "bubble_border": "#8B949E", "star": "#B7A4F2",
        "kicker": None,
        "lines": {
            "walker1": ["mAP ↑ pls"],
            "walker2": ["tooth 36~ ?"],
            "hopper": ["HiResCAM!"],
            "coder": ["pytest ✓", "no data leaks!", "32 teeth found"],
        },
    },
}

CATS = {   # body, belly, accessory
    "lav":    ("#B7A4F2", "#E4DCFF", "shades"),
    "rose":   ("#F0A8D0", "#FCE1EF", None),
    "mint":   ("#8FE3C8", "#D6F7EC", None),
    "sun":    ("#FFD36E", "#FFF0C7", "glasses"),
    "sky":    ("#7AA7FF", "#D3E2FF", None),
}


def runs(rows, colors, y_off=0):
    """One <rect> per horizontal run of identical colour."""
    out = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            ch = row[x]
            if ch == ".":
                x += 1
                continue
            start = x
            while x < len(row) and row[x] == ch:
                x += 1
            out.append(f'<rect x="{start * P}" y="{(y + y_off) * P}" width="{(x - start) * P}" '
                       f'height="{P}" fill="{colors[ch]}"/>')
    return "".join(out)


def palette(t, body, belly):
    return {"o": t["outline"], "b": body, "l": belly, "e": t["eye"], "w": "#FFFFFF",
            "p": "#F27BA6", "r": "#F7A1C4"}


def accessory(kind, t):
    if kind == "shades":
        rows = [".oooooo..oooooo.", "..oooo....oooo.."]
        return runs(rows, {"o": "#111018"}, 6) + f'<rect x="{2 * P}" y="{6 * P}" width="{P}" height="{P}" fill="#FFFFFF" opacity=".7"/>'
    if kind == "glasses":
        rows = [".oooo.....oooo..", ".o..oooooo..o...", ".oooo.....oooo.."]
        return runs(rows, {"o": "#3A2D5C"}, 5)
    return ""


def cat(name, t, legs="walk", eyes="open", blink_delay=0.0):
    body, belly, acc = CATS[name]
    col = palette(t, body, belly)
    parts = [runs(HEAD_BODY, col)]
    if legs == "walk":
        parts.append(f'<g class="la">{runs(LEGS["a"], col, 15)}</g>')
        parts.append(f'<g class="lb">{runs(LEGS["b"], col, 15)}</g>')
    else:
        parts.append(runs(LEGS["sit"], col, 15))
    closed = runs(CLOSED_EYES, {"b": body, "o": t["outline"]}, 6)
    if eyes == "closed":
        parts.append(closed)
    else:
        parts.append(f'<g class="blink" style="animation-delay:{blink_delay}s">{closed}</g>')
    parts.append(accessory(acc, t))
    return "".join(parts)


def bubble(lines, t, cls, x, y):
    """Speech bubble(s) centred above the cat; several lines cycle."""
    out = []
    n = len(lines)
    for i, line in enumerate(lines):
        w = int(sum(14.4 if ord(ch) > 0x2E7F else 7.2 for ch in line)) + 20   # CJK is double width
        bx = x - w / 2
        style = f'animation-delay:{-i * 3}s' if n > 1 else ''
        klass = f"{cls} say{n}" if n > 1 else cls
        out.append(
            f'<g class="{klass}" style="{style}">'
            f'<rect x="{bx:.0f}" y="{y}" width="{w}" height="22" rx="6" fill="{t["bubble_bg"]}" '
            f'stroke="{t["bubble_border"]}"/>'
            f'<path d="M{x - 5:.0f} {y + 22}l5 6 5-6" fill="{t["bubble_bg"]}" stroke="{t["bubble_border"]}"/>'
            f'<rect x="{x - 4:.0f}" y="{y + 20}" width="8" height="3" fill="{t["bubble_bg"]}"/>'
            f'<text x="{x:.0f}" y="{y + 15}" text-anchor="middle" class="mono" font-size="12" '
            f'fill="{t["bubble_fg"]}">{escape(line)}</text></g>')
    return "".join(out)


def walker(name, t, lines, base_x, duration, delay, direction=1, hop=False, blink=0.0):
    start, end = (-base_x - 120, W - base_x + 60) if direction > 0 else (W - base_x + 60, -base_x - 120)
    kf = f"w-{name}"
    css = (f"@keyframes {kf}{{from{{transform:translateX({start}px)}}to{{transform:translateX({end}px)}}}}"
           f".{kf}{{animation:{kf} {duration}s linear {delay}s infinite}}")
    lean = "lean-r" if direction > 0 else "lean-l"
    motion = "hop" if hop else "bob"
    svg = (f'<g class="{kf}"><g transform="translate({base_x},{GROUND - CAT_H})">'
           f'<g class="{motion}"><g class="{lean}">{cat(name, t, blink_delay=blink)}</g></g>'
           f'{bubble(lines, t, "say-walk", CAT_W / 2, -34)}'
           f'</g></g>')
    return css, svg


def laptop_cat(t, lines, x):
    body, belly, _ = CATS["sun"]
    laptop = (
        f'<rect x="{1 * P}" y="{12 * P}" width="{14 * P}" height="{4 * P}" rx="2" fill="#C9C5D8" stroke="{t["outline"]}" stroke-width="2"/>'
        f'<rect x="{0}" y="{16 * P}" width="{16 * P}" height="{P}" fill="#9A93B4" stroke="{t["outline"]}" stroke-width="2"/>'
        f'<text x="{8 * P}" y="{15 * P}" text-anchor="middle" class="mono" font-size="11" font-weight="700" fill="#7B61D9">&lt;/&gt;</text>'
    )
    paws = (f'<g class="tapA"><rect x="{3 * P}" y="{11 * P}" width="{2 * P}" height="{P}" fill="{body}" stroke="{t["outline"]}"/></g>'
            f'<g class="tapB"><rect x="{11 * P}" y="{11 * P}" width="{2 * P}" height="{P}" fill="{body}" stroke="{t["outline"]}"/></g>')
    glow = f'<ellipse cx="{8 * P}" cy="{9 * P}" rx="{9 * P}" ry="{5 * P}" fill="#B7A4F2" class="glow"/>'
    return (f'<g transform="translate({x},{GROUND - CAT_H})">{glow}'
            f'{cat("sun", t, legs="sit", blink_delay=1.3)}{laptop}{paws}'
            f'{bubble(lines, t, "say-code", CAT_W / 2, -34)}</g>')


def sleeping_cat(t, x):
    zs = "".join(f'<text x="{CAT_W - 6 + i * 9}" y="{4 - i * 2}" class="mono z" font-size="{12 + i * 3}" '
                 f'fill="{t["text"]}" style="animation-delay:{i * 0.8}s">z</text>' for i in range(3))
    return (f'<g transform="translate({x},{GROUND - CAT_H})"><g class="breathe">'
            f'{cat("sky", t, legs="sit", eyes="closed")}</g>{zs}</g>')


def stars(t):
    pts = [(560, 40), (690, 24), (820, 52), (930, 30), (1110, 34), (470, 88), (640, 96), (980, 92)]
    out = []
    for i, (x, y) in enumerate(pts):
        out.append(f'<g class="tw" style="animation-delay:{i * 0.45:.2f}s" fill="{t["star"]}">'
                   f'<rect x="{x - 1}" y="{y - 4}" width="3" height="9"/><rect x="{x - 4}" y="{y - 1}" width="9" height="3"/></g>')
    return "".join(out)


BASE_CSS = """
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace}
.la{animation:la .42s steps(1) infinite}.lb{animation:lb .42s steps(1) infinite}
@keyframes la{0%{opacity:1}50%{opacity:0}}@keyframes lb{0%{opacity:0}50%{opacity:1}}
.bob{animation:bob .42s steps(1) infinite}@keyframes bob{0%{transform:translateY(0)}50%{transform:translateY(-4px)}}
.hop{animation:hop 2.4s ease-in-out infinite}
@keyframes hop{0%,58%{transform:translateY(0)}68%{transform:translateY(-14px)}74%{transform:translateY(-20px)}82%{transform:translateY(-10px)}90%,100%{transform:translateY(0)}}
.lean-r,.lean-l{transform-box:fill-box;transform-origin:50% 100%}
.lean-r{transform:rotate(3deg)}.lean-l{transform:rotate(-3deg)}
.blink{opacity:0;animation:blink 4.6s infinite}
@keyframes blink{0%,93%{opacity:0}94%,97%{opacity:1}98%,100%{opacity:0}}
.say-walk{opacity:0;animation:say 7s infinite}
@keyframes say{0%,30%{opacity:0}34%,70%{opacity:1}74%,100%{opacity:0}}
.say-code{opacity:0}.say3{animation:say3 9s infinite}
@keyframes say3{0%{opacity:0}4%,30%{opacity:1}33%,100%{opacity:0}}
.tapA{animation:tap .3s steps(1) infinite}.tapB{animation:tap .3s steps(1) -.15s infinite}
@keyframes tap{0%{transform:translateY(0)}50%{transform:translateY(-3px)}}
.glow{opacity:.12;animation:glow 1.8s ease-in-out infinite}@keyframes glow{50%{opacity:.25}}
.breathe{transform-box:fill-box;transform-origin:50% 100%;animation:breathe 3s ease-in-out infinite}
@keyframes breathe{50%{transform:scaleY(.96)}}
.z{opacity:0;animation:z 2.4s ease-out infinite}
@keyframes z{0%{opacity:0;transform:translate(0,0)}20%{opacity:.9}100%{opacity:0;transform:translate(8px,-22px)}}
.tw{animation:tw 2.6s ease-in-out infinite;opacity:.25}@keyframes tw{50%{opacity:.9}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.blink,.say-walk,.say-code,.z{opacity:0!important}}
"""


def build(theme):
    t = THEMES[theme]
    L = t["lines"]
    css, body = [BASE_CSS], []
    c1, s1 = walker("lav", t, L["walker1"], 260, 26, -4, direction=1, blink=0.4)
    c2, s2 = walker("rose", t, L["walker2"], 760, 31, -17, direction=-1, blink=2.1)
    c3, s3 = walker("mint", t, L["hopper"], 520, 38, -25, direction=1, hop=True, blink=3.2)
    css += [c1, c2, c3]

    if t["frame"]:
        body.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="{t["bg"]}" stroke="{t["border"]}"/>')
    body.append(stars(t))
    if t["kicker"]:
        body.append(f'<text x="40" y="34" class="mono" font-size="12" letter-spacing="2" fill="{t["text"]}">'
                    f'{escape(t["kicker"])}</text>')
    body.append(f'<rect x="24" y="{GROUND + P}" width="{W - 48}" height="2" fill="{t["ground"]}" opacity=".6"/>')
    for gx in range(60, W - 40, 96):   # little grass tufts
        body.append(f'<rect x="{gx}" y="{GROUND}" width="{P}" height="{P}" fill="{t["ground"]}" opacity=".5"/>'
                    f'<rect x="{gx + 2 * P}" y="{GROUND - P}" width="{P}" height="{2 * P}" fill="{t["ground"]}" opacity=".5"/>')
    body.append(laptop_cat(t, L["coder"], 140))
    body.append(sleeping_cat(t, 1000))
    body += [s1, s2, s3]

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'role="img" aria-labelledby="cats-t" shape-rendering="crispEdges">'
            f'<title id="cats-t">Five pixel-art cats: three walk and hop across, one types on a laptop, one naps.</title>'
            f'<style>{"".join(css)}</style>{"".join(body)}</svg>\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--theme", choices=THEMES, default="profile")
    ap.add_argument("--out", type=Path, default=ROOT / "assets" / "cards" / "pixel-cats.svg")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(build(args.theme), encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
