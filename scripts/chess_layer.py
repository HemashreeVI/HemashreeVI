"""Small animated silver chess pieces for the README's section titles and footer
(they took over from the cats). Each function returns an SVG group to drop
into a card; pieces are drawn around (0, 0) = the middle of their base, about
40 wide and 60 tall, so they stand on whatever line they are placed on.
"""

DARK = "#2A2C31"


def defs(uid):
    return f"""<defs>
  <linearGradient id="{uid}-pc" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#FFFFFF"/><stop offset=".45" stop-color="#D3D7DD"/><stop offset="1" stop-color="#6E737C"/>
  </linearGradient>
  <radialGradient id="{uid}-sh" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset="1" stop-color="#000" stop-opacity="0"/>
  </radialGradient>
</defs>"""


BASE = '<path d="M-17 0h34v-4c0-2.5-2-4-4.5-4h-25c-2.5 0-4.5 1.5-4.5 4z"/><path d="M-14 -8h28l-2 -3h-24z"/>'
SHAPES = {
    "pawn": BASE + '<path d="M-11 -11C-11 -17 -5 -20 -5 -25h10c0 5 6 8 6 14z"/>'
                   '<ellipse cx="0" cy="-26" rx="8.5" ry="2.8"/><circle cx="0" cy="-35" r="8.5"/>',
    "rook": BASE + '<path d="M-11 -11L-9 -38h18L11 -11z"/><path d="M-12.5 -37h25v2h-25z"/>'
                   '<path d="M-12 -37V-51h6v5h3.5v-5h5v5h3.5v-5h6V-37z"/>',
    "knight": BASE + '<path d="M-11 -11C-11 -19 -5 -23 -7 -30C-13 -28 -17 -32 -15 -36C-12 -42 -5 -48 1 -52L3 -59L7 -52'
                     'C14 -47 15 -33 12 -11z"/>',
    "bishop": BASE + '<path d="M-11 -11C-11 -18 -5 -22 -5 -31h10c0 9 6 13 6 20z"/><ellipse cx="0" cy="-32" rx="8" ry="2.6"/>'
                     '<ellipse cx="0" cy="-44" rx="7" ry="11"/><circle cx="0" cy="-57" r="3"/>',
    "queen": BASE + '<path d="M-12 -11C-12 -20 -6 -26 -6 -39h12c0 13 6 19 6 28z"/><ellipse cx="0" cy="-40" rx="9" ry="3"/>'
                    '<path d="M-9 -43L-11.5 -55L-5 -48L0 -58L5 -48L11.5 -55L9 -43z"/><circle cx="0" cy="-61" r="3"/>'
                    '<circle cx="-11.5" cy="-56" r="1.8"/><circle cx="11.5" cy="-56" r="1.8"/>',
    "king": BASE + '<path d="M-12 -11C-12 -20 -6 -26 -6 -39h12c0 13 6 19 6 28z"/><ellipse cx="0" cy="-40" rx="9" ry="3"/>'
                   '<path d="M-8 -43C-10 -53 10 -53 8 -43z"/><path d="M-1.6 -63h3.2v11h-3.2z"/><path d="M-5 -59.5h10v3.2h-10z"/>',
}
DETAIL = {   # dark accents drawn over the silver
    "knight": f'<circle cx="2" cy="-45" r="1.4" fill="{DARK}"/><path d="M8 -50C11 -44 11 -36 10 -30" fill="none" stroke="{DARK}" stroke-width=".8" opacity=".6"/>',
    "bishop": f'<path d="M3 -50L-3 -41" stroke="{DARK}" stroke-width="1.4"/>',
}


def piece(uid, kind, scale=1.0):
    """One piece, standing on (0, 0), with a soft shadow under it."""
    return (f'<ellipse cx="0" cy="1" rx="{20 * scale:.1f}" ry="{4 * scale:.1f}" fill="url(#{uid}-sh)"/>'
            f'<g transform="scale({scale})" fill="url(#{uid}-pc)" stroke="{DARK}" stroke-width=".8" stroke-linejoin="round">'
            f'{SHAPES[kind]}{DETAIL.get(kind, "")}</g>')


def queen_rises(uid, x=1080, y=95):
    """About: the queen rises from behind the title line, settles, and sinks back down."""
    return f"""{defs(uid)}
<clipPath id="{uid}-clip"><rect x="{x - 40}" y="0" width="80" height="{y + 1}"/></clipPath>
<g clip-path="url(#{uid}-clip)"><g>
  <animateTransform attributeName="transform" type="translate" dur="9s" repeatCount="indefinite"
    keyTimes="0;.12;.2;.24;.28;.85;.95;1" values="{x} {y + 60};{x} {y + 60};{x} {y - 4};{x} {y};{x} {y};{x} {y};{x} {y + 60};{x} {y + 60}"/>
  {piece(uid, 'queen', .8)}
</g></g>"""


def knight_hops(uid, x0=960, x1=1110, y=95):
    """Projects: the knight jumps along the line in L-shaped hops, then jumps back."""
    step = (x1 - x0) / 3
    hop = lambda a, b: f"L{a:.0f} {y - 14} L{b:.0f} {y - 14} L{b:.0f} {y}"   # up, across, down: an L
    path = f"M{x0} {y} " + " ".join(hop(x0 + step * i, x0 + step * (i + 1)) for i in range(3))
    back = f"M{x1} {y} " + " ".join(hop(x1 - step * i, x1 - step * (i + 1)) for i in range(3))
    return f"""{defs(uid)}
<g><animateMotion dur="10s" repeatCount="indefinite" calcMode="spline" keyPoints="0;0;1;1;0;0" keyTimes="0;.08;.42;.55;.92;1"
   keySplines=".4 0 .6 1;.4 0 .6 1;.4 0 .6 1;.4 0 .6 1;.4 0 .6 1" path="{path} {back.replace('M', 'L', 1)}"/>
  {piece(uid, 'knight', .75)}
</g>"""


def rook_slides(uid, x0=930, x1=1100, y=95):
    """Play: the rook slides along the line and back, like castling."""
    return f"""{defs(uid)}
<g><animateTransform attributeName="transform" type="translate" dur="8s" repeatCount="indefinite" calcMode="spline"
   keyTimes="0;.15;.45;.6;.9;1" values="{x0} {y};{x0} {y};{x1} {y};{x1} {y};{x0} {y};{x0} {y}"
   keySplines=".5 0 .3 1;.5 0 .3 1;.5 0 .3 1;.5 0 .3 1;.5 0 .3 1"/>
  {piece(uid, 'rook', .75)}
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
<g opacity="1"><animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0;.04;.93;.98;1" values="0;1;1;0;0"/>
  <animateTransform attributeName="transform" type="translate" dur="9s" repeatCount="indefinite"
    keyTimes="{';'.join(f'{k:.3f}' for k in times)}" values="{';'.join(f'{v:.0f} {y}' for v in vals)}"/>
  {piece(uid, 'pawn', .75)}
</g>"""


def checkmate(uid, x=1030, y=300):
    """Footer: the queen stands; the king beside her slowly topples over, then stands back up."""
    return f"""{defs(uid)}
<g transform="translate({x} {y})">{piece(uid, 'queen', 1.0)}</g>
<g transform="translate({x + 46} {y})"><g>
  <animateTransform attributeName="transform" type="rotate" dur="10s" repeatCount="indefinite" calcMode="spline"
    keyTimes="0;.3;.42;.48;.8;.92;1" values="0 13 0;0 13 0;82 13 0;78 13 0;78 13 0;0 13 0;0 13 0"
    keySplines=".5 0 .3 1;.6 0 1 1;.3 0 .5 1;.5 0 .5 1;.5 0 .3 1;.5 0 .5 1"/>
  {piece(uid, 'king', .95)}
</g></g>"""
