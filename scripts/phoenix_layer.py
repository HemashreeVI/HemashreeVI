"""The fire phoenix (photos generated with ChatGPT on a green screen, cut out by
scripts/phoenix/cut_phoenix.py into assets/phoenix/*.webp) and the warm ember
atmosphere that goes with it, so the bird sits naturally in the black & silver
cards: a soft red-orange glow, a little warm smoke and a few rising sparks.
Used by the footer (build_cards.py) and the streak card (stats_cards.py).
"""
import base64
import random
import struct
from pathlib import Path

ART = Path(__file__).resolve().parent.parent / "assets" / "phoenix"
EMBER, FLAME, DEEP = "#FFB15C", "#FF6A2B", "#C2261B"
_cache = {}


def _load(name):
    if name not in _cache:
        data = (ART / f"{name}.webp").read_bytes()
        kind = data[12:16]
        if kind == b"VP8X":
            w, h = 1 + int.from_bytes(data[24:27], "little"), 1 + int.from_bytes(data[27:30], "little")
        elif kind == b"VP8L":
            v = int.from_bytes(data[21:25], "little")
            w, h = 1 + (v & 0x3FFF), 1 + ((v >> 14) & 0x3FFF)
        else:
            w, h = (n & 0x3FFF for n in struct.unpack("<HH", data[26:30]))
        _cache[name] = (base64.b64encode(data).decode(), w, h)
    return _cache[name]


def image(name, x, y, s, extra=""):
    """The pose `name` with its top-left corner at (x, y), s SVG units per pixel."""
    b64, w, h = _load(name)
    return f'<image x="{x:.1f}" y="{y:.1f}" width="{w * s:.1f}" height="{h * s:.1f}" href="data:image/webp;base64,{b64}" {extra}/>'


def size(name, s):
    _, w, h = _load(name)
    return w * s, h * s


def warmth(uid, cx, cy, rx, ry, strength=1.0, sparks=10, seed=7, rise=60):
    """Ember glow + warm smoke + rising sparks around (cx, cy), to sit under or behind the phoenix."""
    rnd = random.Random(seed)
    out = [f"""<defs>
  <radialGradient id="{uid}-heat" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="{FLAME}" stop-opacity="{.30 * strength:.2f}"/>
    <stop offset=".45" stop-color="{DEEP}" stop-opacity="{.12 * strength:.2f}"/>
    <stop offset="1" stop-color="{DEEP}" stop-opacity="0"/>
  </radialGradient>
  <filter id="{uid}-wsmoke" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.012 0.02" numOctaves="3" seed="{seed}"/>
    <feColorMatrix values="0 0 0 0 1  0 0 0 0 .42  0 0 0 0 .2  2.4 0 0 0 -1.1"/>
    <feGaussianBlur stdDeviation="5"/>
  </filter>
  <radialGradient id="{uid}-smask" cx="50%" cy="60%" r="50%">
    <stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/>
  </radialGradient>
  <mask id="{uid}-m"><rect x="{cx - rx}" y="{cy - ry}" width="{2 * rx}" height="{2 * ry}" fill="url(#{uid}-smask)"/></mask>
</defs>""",
           f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#{uid}-heat)">'
           f'<animate attributeName="opacity" values="1;.75;1" dur="3.2s" repeatCount="indefinite"/></ellipse>',
           # warm smoke drifting slowly upward, only around the bird
           f'<g mask="url(#{uid}-m)" opacity="{.22 * strength:.2f}"><rect x="{cx - rx}" y="{cy - ry}" width="{2 * rx}" height="{4 * ry}" filter="url(#{uid}-wsmoke)">'
           f'<animateTransform attributeName="transform" type="translate" values="0 0;0 {-2 * ry}" dur="24s" repeatCount="indefinite"/></rect></g>']
    for i in range(sparks):
        x = cx + rnd.uniform(-rx * .55, rx * .55)
        y = cy + rnd.uniform(-ry * .1, ry * .5)
        d, b, r = rnd.uniform(2.2, 4.2), rnd.uniform(0, 4), rnd.choice([1, 1.2, 1.5, 1.8])
        drift = rnd.uniform(-14, 14)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{rnd.choice([EMBER, FLAME, EMBER])}" opacity="0">'
                   f'<animate attributeName="opacity" values="0;.95;.6;0" dur="{d:.1f}s" begin="{b:.1f}s" repeatCount="indefinite"/>'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;{drift:.0f} {-rise}" dur="{d:.1f}s" begin="{b:.1f}s" repeatCount="indefinite"/>'
                   f'</circle>')
    return "\n".join(out)


def flapping(x, y, s, period=.6):
    """The phoenix flapping in place (three wing positions), its box's top-left at (x, y)."""
    vis = {"flap-up": "1;0;0;0", "flap-level": "0;1;0;1", "flap-down": "0;0;1;0"}
    return "".join(image(n, x, y, s, f'opacity="{v[0]}"').replace(
        "/>", f'><animate attributeName="opacity" values="{v}" keyTimes="0;.25;.5;.75" calcMode="discrete" dur="{period}s" repeatCount="indefinite"/></image>')
        for n, v in vis.items())


def rises(uid, start, end, s0, s1, dur, appear, leave):
    """The phoenix bursts out at `start` and flies, flapping and growing, to `end`.
    appear/leave are fractions of the `dur` loop, so it can follow another animation's timeline."""
    (x0, y0), (x1, y1) = start, end
    _, fw, fh = _load("flap-level")
    mid = (x0 + (x1 - x0) * .25 + 40, y0 + (y1 - y0) * .55)      # a gentle curve up and to the left
    kt = f"0;{appear:.3f};{leave:.3f};1"
    burst = f"0;{appear - .01:.3f};{appear + .01:.3f};{appear + .14:.3f};1"
    return f"""
<ellipse cx="{x0}" cy="{y0 + 10}" rx="90" ry="34" fill="url(#{uid}-heat)" opacity="0">
  <animate attributeName="opacity" dur="{dur}s" repeatCount="indefinite" keyTimes="{burst}" values="0;0;1;0;0"/></ellipse>
<g opacity="0">
  <animate attributeName="opacity" dur="{dur}s" repeatCount="indefinite" keyTimes="0;{appear:.3f};{appear + .03:.3f};{leave - .05:.3f};{leave:.3f};1" values="0;0;1;1;0;0"/>
  <animateMotion dur="{dur}s" repeatCount="indefinite" keyPoints="0;0;1;1" keyTimes="{kt}" calcMode="linear"
    path="M{x0} {y0} Q{mid[0]:.0f} {mid[1]:.0f} {x1} {y1}"/>
  <g><animateTransform attributeName="transform" type="scale" dur="{dur}s" repeatCount="indefinite" keyTimes="{kt}" values="{s0};{s0};{s1};{s1}"/>
    {flapping(-fw / 2, -fh * .55, 1, .5)}
  </g>
</g>"""


def perched(uid, cx, base_y, s):
    """The perched phoenix standing on (cx, base_y), breathing gently."""
    w, h = size("perched", s)
    return f"""<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -1.5;0 0" dur="3.2s" repeatCount="indefinite"/>
  {image("perched", cx - w * .52, base_y - h, s)}
</g>"""
