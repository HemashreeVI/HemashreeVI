#!/usr/bin/env python3
"""Builds the animated robot banner used in READMEs.

    python3 scripts/build_robots.py                       # assets/cards/robots.svg (profile)
    python3 scripts/build_robots.py --theme light-dark --out path/to/robots.svg

Two original vector robots, animated with CSS inside the SVG (GitHub keeps
animations in SVG images): "Byte" floats and waves, "Mochi" flaps its wings
and sends hearts. Both blink and talk. Standard library only.
"""
import argparse
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 310
GROUND = 278

THEMES = {
    "profile": {
        "frame": True, "bg": "#14101F", "border": "#2D2647", "text": "#9A93B4", "shadow": "#000000",
        "bubble_bg": "#1C1630", "bubble_fg": "#E8E6F0", "bubble_border": "#3E3463", "spark": "#D9CEFF",
        "kicker": "HELLO FROM THE LAB",
        "byte": ["hi! I'm Byte ✦", "shipping code…"], "mochi": ["beep boop ♡", "you got this!"],
    },
    "light-dark": {
        "frame": False, "bg": None, "border": None, "text": "#8B949E", "shadow": "#5B5675",
        "bubble_bg": "#FFFFFF", "bubble_fg": "#1F1A2E", "bubble_border": "#8B949E", "spark": "#B7A4F2",
        "kicker": None,
        "byte": ["scanning X-rays…", "found 32 teeth!"], "mochi": ["beep boop ♡", "floss daily!"],
    },
}

DEFS = """
<defs>
  <radialGradient id="shell" cx="35%" cy="30%" r="80%">
    <stop offset="0" stop-color="#FFFFFF"/><stop offset=".6" stop-color="#F1F2F8"/><stop offset="1" stop-color="#C9CCDA"/>
  </radialGradient>
  <linearGradient id="visor" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#23222F"/><stop offset="1" stop-color="#07070C"/>
  </linearGradient>
  <linearGradient id="glow" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#7FE7FF"/><stop offset="1" stop-color="#A78BFA"/>
  </linearGradient>
  <radialGradient id="pink" cx="35%" cy="30%" r="80%">
    <stop offset="0" stop-color="#FFD9E4"/><stop offset=".7" stop-color="#F3A9BE"/><stop offset="1" stop-color="#E08AA3"/>
  </radialGradient>
  <linearGradient id="wing" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#FFE3EC"/><stop offset="1" stop-color="#F3A9BE"/>
  </linearGradient>
  <filter id="neon" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur stdDeviation="2.4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>"""

CSS = """
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace}
.fb{transform-box:fill-box;transform-origin:50% 50%}
.floatA{animation:floatA 3.2s ease-in-out infinite}
@keyframes floatA{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
.floatB{animation:floatB 2.6s ease-in-out -1.1s infinite}
@keyframes floatB{0%,100%{transform:translateY(-6px)}50%{transform:translateY(-20px)}}
.shA{transform-box:fill-box;transform-origin:50% 50%;animation:shA 3.2s ease-in-out infinite}
@keyframes shA{0%,100%{transform:scale(1);opacity:.35}50%{transform:scale(.78);opacity:.2}}
.shB{transform-box:fill-box;transform-origin:50% 50%;animation:shB 2.6s ease-in-out -1.1s infinite}
@keyframes shB{0%,100%{transform:scale(.85);opacity:.28}50%{transform:scale(.65);opacity:.16}}
.wave{transform-box:fill-box;transform-origin:15% 90%;animation:wave 1.6s ease-in-out infinite}
@keyframes wave{0%,100%{transform:rotate(-8deg)}50%{transform:rotate(22deg)}}
.blink{transform-box:fill-box;transform-origin:50% 50%;animation:blink 4.2s infinite}
.blink2{transform-box:fill-box;transform-origin:50% 50%;animation:blink 5.1s -2s infinite}
@keyframes blink{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.1)}}
.pulse{animation:pulse 2.2s ease-in-out infinite}@keyframes pulse{50%{opacity:.45}}
.wingL{transform-box:fill-box;transform-origin:100% 70%;animation:wingL .5s ease-in-out infinite alternate}
.wingR{transform-box:fill-box;transform-origin:0% 70%;animation:wingR .5s ease-in-out infinite alternate}
@keyframes wingL{from{transform:rotate(8deg)}to{transform:rotate(-16deg)}}
@keyframes wingR{from{transform:rotate(-8deg)}to{transform:rotate(16deg)}}
.heart{opacity:0;animation:heart 3s ease-out infinite}
@keyframes heart{0%{opacity:0;transform:translate(0,0) scale(.6)}15%{opacity:1}100%{opacity:0;transform:translate(14px,-60px) scale(1.1)}}
.say{opacity:0}.say2{animation:say2 8s infinite}
@keyframes say2{0%{opacity:0}5%,42%{opacity:1}47%,100%{opacity:0}}
.tw{animation:tw 2.8s ease-in-out infinite;opacity:.2}@keyframes tw{50%{opacity:.9}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.heart{opacity:0!important}.say{opacity:0!important}}
"""


def bubble(lines, t, cx, y, delay=0.0):
    out = []
    for i, line in enumerate(lines):
        w = int(len(line) * 7.4) + 22
        x = cx - w / 2
        out.append(
            f'<g class="say say2" style="animation-delay:{delay - i * 4}s">'
            f'<rect x="{x:.0f}" y="{y}" width="{w}" height="24" rx="8" fill="{t["bubble_bg"]}" stroke="{t["bubble_border"]}"/>'
            f'<path d="M{cx - 6:.0f} {y + 23}l6 7 6-7z" fill="{t["bubble_bg"]}" stroke="{t["bubble_border"]}"/>'
            f'<rect x="{cx - 6:.0f}" y="{y + 21}" width="12" height="4" fill="{t["bubble_bg"]}"/>'
            f'<text x="{cx:.0f}" y="{y + 16}" text-anchor="middle" class="mono" font-size="12.5" fill="{t["bubble_fg"]}">'
            f'{escape(line)}</text></g>')
    return "".join(out)


def byte(t, x):
    """White robot with a black visor, glowing arc eyes; waves its right arm."""
    head_y = -168
    return f"""
<g transform="translate({x},{GROUND})">
  <ellipse class="shA" cx="0" cy="6" rx="52" ry="8" fill="{t['shadow']}"/>
  <g class="floatA">
    <rect x="-36" y="-56" width="30" height="50" rx="14" fill="url(#shell)"/>
    <rect x="6" y="-56" width="30" height="50" rx="14" fill="url(#shell)"/>
    <rect x="-30" y="-20" width="18" height="5" rx="2.5" fill="url(#glow)" filter="url(#neon)" class="pulse"/>
    <rect x="12" y="-20" width="18" height="5" rx="2.5" fill="url(#glow)" filter="url(#neon)" class="pulse"/>
    <ellipse cx="-50" cy="-82" rx="15" ry="27" transform="rotate(18 -50 -82)" fill="url(#shell)"/>
    <rect x="-46" y="-116" width="92" height="76" rx="36" fill="url(#shell)"/>
    <g class="wave">
      <ellipse cx="60" cy="-122" rx="14" ry="27" transform="rotate(-32 60 -122)" fill="url(#shell)"/>
      <circle cx="72" cy="-144" r="8" fill="none" stroke="url(#glow)" stroke-width="3.5" filter="url(#neon)"/>
    </g>
    <ellipse cx="0" cy="-116" rx="32" ry="6" fill="none" stroke="url(#glow)" stroke-width="4" filter="url(#neon)" class="pulse"/>
    <ellipse cx="0" cy="{head_y}" rx="70" ry="62" fill="url(#shell)"/>
    <circle cx="-66" cy="{head_y}" r="17" fill="#E4E6F0"/>
    <circle cx="-66" cy="{head_y}" r="11" fill="none" stroke="url(#glow)" stroke-width="4" filter="url(#neon)"/>
    <ellipse cx="10" cy="{head_y - 2}" rx="50" ry="38" fill="url(#visor)"/>
    <ellipse cx="-12" cy="{head_y - 24}" rx="18" ry="6" fill="#FFFFFF" opacity=".16" transform="rotate(-18 -12 {head_y - 24})"/>
    <circle cx="44" cy="{head_y - 18}" r="2.2" fill="#FFFFFF" opacity=".5"/>
    <g class="blink" filter="url(#neon)">
      <path d="M-14 {head_y + 4}q11 -18 22 0" fill="none" stroke="url(#glow)" stroke-width="5.5" stroke-linecap="round"/>
      <path d="M18 {head_y + 8}q11 -18 22 0" fill="none" stroke="url(#glow)" stroke-width="5.5" stroke-linecap="round"/>
    </g>
  </g>
  {bubble(t['byte'], t, -150, -236)}
</g>"""


def mochi(t, x):
    """White-and-pink robot with headphones, a visor smile and wings."""
    hy = -178
    wing_l = ("M0 0c-18-22-46-26-58-10 6 2 12 6 14 12-10-2-20 4-20 12 8-2 16 0 20 6"
              "-8 2-12 10-8 16 14-6 34-8 52-22z")
    return f"""
<g transform="translate({x},{GROUND})">
  <ellipse class="shB" cx="0" cy="6" rx="48" ry="8" fill="{t['shadow']}"/>
  <g class="floatB">
    <g transform="translate(-42,-104)"><path class="wingL" d="{wing_l}" fill="url(#wing)" stroke="#E79AB2" stroke-width="1.2"/></g>
    <g transform="translate(42,-104) scale(-1,1)"><path class="wingL" d="{wing_l}" fill="url(#wing)" stroke="#E79AB2" stroke-width="1.2"/></g>
    <g transform="translate(-48,{hy + 6})"><path class="wingL" d="M0 0c-10-16-30-20-38-8 8 0 12 4 14 8-8 0-14 6-12 12 12-2 26-4 36-12z" fill="url(#wing)" stroke="#E79AB2"/></g>
    <g transform="translate(48,{hy + 6}) scale(-1,1)"><path class="wingL" d="M0 0c-10-16-30-20-38-8 8 0 12 4 14 8-8 0-14 6-12 12 12-2 26-4 36-12z" fill="url(#wing)" stroke="#E79AB2"/></g>
    <rect x="-34" y="-54" width="28" height="30" rx="8" fill="#B9BDCB"/>
    <rect x="6" y="-54" width="28" height="30" rx="8" fill="#B9BDCB"/>
    <rect x="-40" y="-34" width="36" height="30" rx="12" fill="url(#pink)"/>
    <rect x="4" y="-34" width="36" height="30" rx="12" fill="url(#pink)"/>
    <rect x="-40" y="-34" width="36" height="8" rx="4" fill="#FFFFFF" opacity=".55"/>
    <rect x="4" y="-34" width="36" height="8" rx="4" fill="#FFFFFF" opacity=".55"/>
    <circle cx="-52" cy="-92" r="7" fill="#9EA3B5"/><circle cx="52" cy="-92" r="7" fill="#9EA3B5"/>
    <rect x="-74" y="-90" width="30" height="36" rx="14" fill="url(#pink)"/>
    <rect x="44" y="-90" width="30" height="36" rx="14" fill="url(#pink)"/>
    <rect x="-44" y="-118" width="88" height="70" rx="28" fill="url(#shell)"/>
    <circle cx="0" cy="-86" r="15" fill="url(#pink)"/><circle cx="0" cy="-86" r="9" fill="none" stroke="#FFFFFF" stroke-width="2.5" class="pulse"/>
    <rect x="22" y="-102" width="8" height="2.5" rx="1" fill="#9EA3B5"/><rect x="22" y="-97" width="8" height="2.5" rx="1" fill="#9EA3B5"/>
    <rect x="-14" y="-128" width="28" height="14" rx="5" fill="#9EA3B5"/>
    <ellipse cx="0" cy="{hy}" rx="70" ry="58" fill="url(#shell)"/>
    <path d="M-34 {hy - 50}q34 -18 68 0v10q-34 -12 -68 0z" fill="url(#pink)"/>
    <circle cx="-68" cy="{hy + 4}" r="18" fill="url(#pink)"/><circle cx="-68" cy="{hy + 4}" r="9" fill="none" stroke="#FFFFFF" stroke-width="3"/>
    <circle cx="68" cy="{hy + 4}" r="18" fill="url(#pink)"/><circle cx="68" cy="{hy + 4}" r="9" fill="none" stroke="#FFFFFF" stroke-width="3"/>
    <rect x="-52" y="{hy - 30}" width="104" height="66" rx="24" fill="url(#visor)" stroke="#F3A9BE" stroke-width="3"/>
    <ellipse cx="-24" cy="{hy - 20}" rx="16" ry="4.5" fill="#FFFFFF" opacity=".14"/>
    <g class="blink2" filter="url(#neon)" stroke="#7FE7FF" stroke-width="5" stroke-linecap="round" fill="none">
      <path d="M-30 {hy}q10 -16 20 0"/><path d="M10 {hy}q10 -16 20 0"/>
    </g>
    <path d="M-10 {hy + 14}q10 10 20 0" fill="none" stroke="#7FE7FF" stroke-width="4.5" stroke-linecap="round" filter="url(#neon)"/>
    <g fill="#F48FB1">
      <path class="heart" style="animation-delay:0s" d="M60 {hy - 40}c-4-6-12-2-8 4l8 8 8-8c4-6-4-10-8-4z"/>
      <path class="heart" style="animation-delay:1.5s" d="M-62 {hy - 34}c-3-5-10-2-7 3l7 7 7-7c3-5-4-8-7-3z"/>
    </g>
  </g>
  {bubble(t['mochi'], t, 160, -246, delay=-2)}
</g>"""


def sparkles(t):
    pts = [(170, 70, 5), (300, 190, 4), (360, 60, 3), (610, 120, 4), (880, 70, 5), (1010, 180, 3), (1080, 90, 4)]
    out = []
    for i, (x, y, r) in enumerate(pts):
        out.append(f'<path class="tw" style="animation-delay:{i * .4:.1f}s" fill="{t["spark"]}" '
                   f'd="M{x} {y - 3 * r}q1 {2 * r} {3 * r} {3 * r}q-{2 * r} 1 -{3 * r} {3 * r}q-1 -{2 * r} -{3 * r} -{3 * r}q{2 * r} -1 {3 * r} -{3 * r}z"/>')
    return "".join(out)


def build(theme):
    t = THEMES[theme]
    body = []
    if t["frame"]:
        body.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="{t["bg"]}" stroke="{t["border"]}"/>')
        body.append(f'<ellipse cx="610" cy="180" rx="360" ry="120" fill="#7B61D9" opacity=".12" filter="url(#soft)"/>')
    if t["kicker"]:
        body.append(f'<text x="40" y="38" class="mono" font-size="12" letter-spacing="2" fill="{t["text"]}">{escape(t["kicker"])}</text>')
    body.append(sparkles(t))
    body.append(byte(t, 500))
    body.append(mochi(t, 720))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="robots-t">'
            f'<title id="robots-t">Two cute robots: Byte, white with glowing eyes, floats and waves; Mochi, white and pink with wings, flaps and sends hearts.</title>'
            f'{DEFS}<style>{CSS}</style>{"".join(body)}</svg>\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--theme", choices=THEMES, default="profile")
    ap.add_argument("--out", type=Path, default=ROOT / "assets" / "cards" / "robots.svg")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(build(args.theme), encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
