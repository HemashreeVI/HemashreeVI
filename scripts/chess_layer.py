"""Animated marble chess pieces for the README's section titles and footer.

The pieces are real photos (generated with ChatGPT on a green screen, cut out by
scripts/chess_pieces/cut_pieces.py into assets/chess/*.webp) embedded in the SVGs.
Each function returns an SVG group to drop into a card. A piece is placed with
(0, 0) at the middle of its base, so it stands on whatever line it is put on.
"""
import base64
import struct
from pathlib import Path

PIECES = Path(__file__).resolve().parent.parent / "assets" / "chess"
_cache = {}


def _webp_size(data):
    """Width and height of a WebP (VP8, VP8L or VP8X), so no imaging library is needed."""
    kind = data[12:16]
    if kind == b"VP8X":
        return 1 + int.from_bytes(data[24:27], "little"), 1 + int.from_bytes(data[27:30], "little")
    if kind == b"VP8L":
        b = int.from_bytes(data[21:25], "little")
        return 1 + (b & 0x3FFF), 1 + ((b >> 14) & 0x3FFF)
    w, h = struct.unpack("<HH", data[26:30])
    return w & 0x3FFF, h & 0x3FFF


def _load(kind):
    if kind not in _cache:
        data = (PIECES / f"{kind}.webp").read_bytes()
        _cache[kind] = (base64.b64encode(data).decode(), *_webp_size(data))
    return _cache[kind]


def defs(uid):
    return f"""<defs><radialGradient id="{uid}-sh" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="#000" stop-opacity=".6"/><stop offset="1" stop-color="#000" stop-opacity="0"/>
</radialGradient></defs>"""


def piece(uid, kind, s, shadow=True):
    """One piece standing on (0, 0); s = SVG units per pixel of the cut-out photo."""
    b64, w, h = _load(kind)
    w, h = w * s, h * s
    sh = f'<ellipse cx="0" cy="0" rx="{w * .62:.1f}" ry="{w * .1:.1f}" fill="url(#{uid}-sh)"/>' if shadow else ""
    return f'{sh}<image x="{-w / 2:.1f}" y="{-h:.1f}" width="{w:.1f}" height="{h:.1f}" href="data:image/webp;base64,{b64}"/>'


T = .32      # size in the section titles (the queen is ~52 units tall)


def queen_rises(uid, x=1080, y=95):
    """About: the queen rises from behind the title line, stays, and sinks back down."""
    return f"""{defs(uid)}
<clipPath id="{uid}-clip"><rect x="{x - 40}" y="0" width="80" height="{y + 2}"/></clipPath>
<g clip-path="url(#{uid}-clip)"><g>
  <animateTransform attributeName="transform" type="translate" dur="9s" repeatCount="indefinite" calcMode="spline"
    keyTimes="0;.12;.24;.85;.95;1" values="{x} {y + 60};{x} {y + 60};{x} {y};{x} {y};{x} {y + 60};{x} {y + 60}"
    keySplines="0 0 1 1;.3 0 .2 1;0 0 1 1;.5 0 .8 .4;0 0 1 1"/>
  {piece(uid, 'queen', T)}
</g></g>"""


def knight_hops(uid, x0=960, x1=1110, y=95):
    """Projects: the knight jumps along the line in L-shaped hops, then jumps back."""
    step = (x1 - x0) / 3
    hop = lambda a, b: f"L{a:.0f} {y - 14} L{b:.0f} {y - 14} L{b:.0f} {y}"   # up, across, down: an L
    path = f"M{x0} {y} " + " ".join(hop(x0 + step * i, x0 + step * (i + 1)) for i in range(3))
    back = " ".join(hop(x1 - step * i, x1 - step * (i + 1)) for i in range(3))
    return f"""{defs(uid)}
<g><animateMotion dur="10s" repeatCount="indefinite" calcMode="spline" keyPoints="0;0;.5;.5;1;1" keyTimes="0;.08;.42;.55;.92;1"
   keySplines=".4 0 .6 1;.4 0 .6 1;.4 0 .6 1;.4 0 .6 1;.4 0 .6 1" path="{path} {back}"/>
  {piece(uid, 'knight', T)}
</g>"""


def rook_slides(uid, x0=930, x1=1100, y=95):
    """Play: the rook slides along the line and back, like castling."""
    return f"""{defs(uid)}
<g><animateTransform attributeName="transform" type="translate" dur="8s" repeatCount="indefinite" calcMode="spline"
   keyTimes="0;.15;.45;.6;.9;1" values="{x0} {y};{x0} {y};{x1} {y};{x1} {y};{x0} {y};{x0} {y}"
   keySplines=".5 0 .3 1;.5 0 .3 1;.5 0 .3 1;.5 0 .3 1;.5 0 .3 1"/>
  {piece(uid, 'rook', T)}
</g>"""


def pawn_marches(uid, x0=930, y=95, squares=5, sq=36):
    """Commit log: the pawn advances one square at a time (one step every day), then fades and starts again."""
    times, vals = [0], [x0]
    for i in range(squares):                 # wait, then step to the next square
        t = .08 + i * .16
        times += [t, t + .06]
        vals += [x0 + i * sq, x0 + (i + 1) * sq]
    times.append(1); vals.append(x0 + squares * sq)
    return f"""{defs(uid)}
<g><animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0;.04;.93;.98;1" values="0;1;1;0;0"/>
  <animateTransform attributeName="transform" type="translate" dur="9s" repeatCount="indefinite"
    keyTimes="{';'.join(f'{k:.3f}' for k in times)}" values="{';'.join(f'{v:.0f} {y}' for v in vals)}"/>
  {piece(uid, 'pawn', T)}
</g>"""


def checkmate(uid, x=1040, y=304, s=.5):
    """Footer: the queen stands; the king beside her tips over and lies fallen (checkmate), then stands again."""
    _, kw, kh = _load("king")
    _, fw, fh = _load("fallen-king")
    kx = x + 62                                   # the king's base
    fx0 = kx - kw * s / 2                         # the fallen king lies to the right, base where the king stood
    piv = f"{kw * s / 2:.1f} 0"                   # tips over its right-hand edge
    dur, KT = "10s", "0;.28;.36;.40;.82;.88;1"
    return f"""{defs(uid)}
<g transform="translate({x} {y})">{piece(uid, 'queen', s)}</g>
<g transform="translate({kx} {y})"><g>
  <animateTransform attributeName="transform" type="rotate" dur="{dur}" repeatCount="indefinite" calcMode="spline"
    keyTimes="{KT}" values="0 {piv};0 {piv};24 {piv};24 {piv};24 {piv};0 {piv};0 {piv}"
    keySplines="0 0 1 1;.6 0 1 1;0 0 1 1;0 0 1 1;.3 0 .4 1;0 0 1 1"/>
  <animate attributeName="opacity" dur="{dur}" repeatCount="indefinite" keyTimes="{KT}" values="1;1;1;0;0;1;1"/>
  {piece(uid, 'king', s)}
</g></g>
<g opacity="0"><animate attributeName="opacity" dur="{dur}" repeatCount="indefinite" keyTimes="{KT}" values="0;0;0;1;1;0;0"/>
  <ellipse cx="{fx0 + fw * s / 2:.1f}" cy="{y}" rx="{fw * s * .55:.1f}" ry="{fw * s * .06:.1f}" fill="url(#{uid}-sh)"/>
  <image x="{fx0:.1f}" y="{y - fh * s:.1f}" width="{fw * s:.1f}" height="{fh * s:.1f}" href="data:image/webp;base64,{_load('fallen-king')[0]}"/>
</g>"""
