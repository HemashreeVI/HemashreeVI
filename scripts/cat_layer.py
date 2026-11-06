"""The roaming cat: small animated scenes that build_cards.py drops into
existing cards, so the mascot keeps turning up around the README instead of
living in its own section.

Poses are in assets/cat/ (an original mascot, transparent PNGs):
walk1-4, sleep, peek, sit, wave. Each scene returns SVG markup (with its own
<style>) positioned in the host card's coordinates.
"""
import base64
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

CAT_DIR = Path(__file__).resolve().parent.parent / "assets" / "cat"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
ROYAL, SKY, ICE, SILVER, BG = "#416AE6", "#839DFB", "#CEDAFF", "#E6E9F0", "#10131F"


@lru_cache(None)
def _pose(name):
    """(data URI, width, height) for a pose PNG."""
    raw = (CAT_DIR / f"{name}.png").read_bytes()
    w = int.from_bytes(raw[16:20], "big")
    h = int.from_bytes(raw[20:24], "big")
    return "data:image/png;base64," + base64.b64encode(raw).decode(), w, h


def _img(name, x, y, height, extra=""):
    uri, w, h = _pose(name)
    width = w * height / h
    return f'<image href="{uri}" x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height}"{extra}/>', width


def _bubble(x, y, w, h, text, size, tail, cls, uid):
    """Rounded speech bubble; tail is 'right', 'left' or 'down' (pointing at the cat)."""
    if tail == "right":
        t = f"M{x + w - 2} {y + h * .45:.1f} L{x + w + 16} {y + h * .62:.1f} L{x + w - 2} {y + h * .75:.1f} Z"
    elif tail == "left":
        t = f"M{x + 2} {y + h * .45:.1f} L{x - 16} {y + h * .62:.1f} L{x + 2} {y + h * .75:.1f} Z"
    else:
        t = f"M{x + w * .62:.1f} {y + h - 2} L{x + w * .72:.1f} {y + h + 14} L{x + w * .78:.1f} {y + h - 2} Z"
    return (f'<g class="{cls}">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2:.0f}" fill="{BG}" stroke="{ROYAL}" stroke-width="2"/>'
            f'<path d="{t}" fill="{BG}" stroke="{ROYAL}" stroke-width="2" stroke-linejoin="round"/>'
            f'<text x="{x + w / 2}" y="{y + h / 2 + size * .36:.1f}" text-anchor="middle" font-family="{SANS}" '
            f'font-size="{size}" font-weight="700" fill="{SILVER}">{escape(text)}</text></g>')


REDUCED = "@media (prefers-reduced-motion:reduce){{{sel}{{animation:none!important}}}}"


def peek_hello(uid, x=880, bottom=104, height=92):
    """Pops up from the bottom edge, says hello, ducks back down. (01 About)"""
    img, w = _img("peek", x, bottom - height, height)
    css = f"""<style>
.{uid}-pk{{animation:{uid}-pk 8s cubic-bezier(.3,1.4,.5,1) .4s infinite;transform:translateY({height + 4}px)}}
@keyframes {uid}-pk{{0%{{transform:translateY({height + 4}px)}}7%,74%{{transform:none}}79%{{transform:translateY(6px)}}84%,100%{{transform:translateY({height + 4}px)}}}}
.{uid}-bb{{opacity:0;transform-origin:{x - 4}px 48px;animation:{uid}-bb 8s ease-out .4s infinite}}
@keyframes {uid}-bb{{0%,9%{{opacity:0;transform:scale(.3)}}13%,70%{{opacity:1;transform:none}}74%,100%{{opacity:0;transform:scale(.3)}}}}
{REDUCED.format(sel=f'.{uid}-pk,.{uid}-bb')}
</style>"""
    bubble = _bubble(x - 300, 20, 286, 40, "hi! welcome to my GitHub world 🌍", 15, "right", f"{uid}-bb", uid)
    return css + bubble + f'<g class="{uid}-pk">{img}</g>'


def walker(uid, card_w=1200, ground=96, height=72, duration=18):
    """Walks across the card with a 4-frame leg cycle. (04 Selected work)"""
    _, fw, fh = _pose("walk1")
    w = fw * height / fh
    frames = []
    step = 0.13  # seconds per frame
    for k in range(4):
        img, _ = _img(f"walk{k + 1}", 0, ground - height, height)
        frames.append(f'<g class="{uid}-f" style="animation-delay:-{k * step:.2f}s">{img}</g>')
    css = f"""<style>
.{uid}-wk{{animation:{uid}-wk {duration}s linear infinite}}
@keyframes {uid}-wk{{from{{transform:translateX({-w - 20:.0f}px)}}to{{transform:translateX({card_w + 20}px)}}}}
.{uid}-f{{opacity:0;animation:{uid}-f {step * 4:.2f}s linear infinite}}
@keyframes {uid}-f{{0%,24.9%{{opacity:1}}25%,100%{{opacity:0}}}}
.{uid}-sh{{animation:{uid}-wk {duration}s linear infinite}}
{REDUCED.format(sel=f'.{uid}-wk,.{uid}-f,.{uid}-sh')}
@media (prefers-reduced-motion:reduce){{.{uid}-f:first-child{{opacity:1}}.{uid}-wk{{transform:translateX(900px)}}}}
</style>"""
    shadow = (f'<ellipse class="{uid}-sh" cx="{w / 2:.0f}" cy="{ground}" rx="{w * .38:.0f}" ry="3.5" '
              f'fill="{ROYAL}" opacity=".55"/>')
    return css + shadow + f'<g class="{uid}-wk">{"".join(frames)}</g>'


def sitter(uid, x=920, ground=96, height=88):
    """Sits on the title line, breathing, with the odd head tilt. (06 Toolkit)"""
    img, w = _img("sit", x, ground - height, height)
    cx = x + w / 2
    css = f"""<style>
.{uid}-br{{transform-origin:{cx:.0f}px {ground}px;animation:{uid}-br 3.2s ease-in-out infinite}}
@keyframes {uid}-br{{0%,100%{{transform:none}}50%{{transform:scale(1.015,1.035)}}}}
.{uid}-tl{{transform-origin:{cx:.0f}px {ground}px;animation:{uid}-tl 7s ease-in-out infinite}}
@keyframes {uid}-tl{{0%,60%,100%{{transform:none}}66%,76%{{transform:rotate(-5deg)}}82%{{transform:rotate(2deg)}}}}
{REDUCED.format(sel=f'.{uid}-br,.{uid}-tl')}
</style>"""
    shadow = f'<ellipse cx="{cx:.0f}" cy="{ground}" rx="{w * .4:.0f}" ry="3.5" fill="{ROYAL}" opacity=".55"/>'
    return css + shadow + f'<g class="{uid}-tl"><g class="{uid}-br">{img}</g></g>'


def player(uid, x=930, ground=96, height=86):
    """Bats at a bouncing ball. (08 Play)"""
    img, w = _img("wave", x, ground - height, height)
    cx = x + w / 2
    bx = x - 2
    css = f"""<style>
.{uid}-ball{{animation:{uid}-ball 1.4s cubic-bezier(.45,0,.55,1) infinite}}
@keyframes {uid}-ball{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(-14px,-44px)}}}}
.{uid}-hop{{transform-origin:{cx:.0f}px {ground}px;animation:{uid}-hop 1.4s ease-in-out infinite}}
@keyframes {uid}-hop{{0%,100%{{transform:none}}40%{{transform:translateY(-6px) rotate(-4deg)}}55%{{transform:translateY(0) scale(1.03,.97)}}}}
.{uid}-bsh{{transform-origin:{bx - 7}px {ground}px;animation:{uid}-bsh 1.4s cubic-bezier(.45,0,.55,1) infinite}}
@keyframes {uid}-bsh{{0%,100%{{transform:none;opacity:.6}}50%{{transform:scaleX(.45);opacity:.2}}}}
{REDUCED.format(sel=f'.{uid}-ball,.{uid}-hop,.{uid}-bsh')}
</style>"""
    ball = (f'<ellipse class="{uid}-bsh" cx="{bx - 7}" cy="{ground}" rx="9" ry="2.5" fill="{ROYAL}"/>'
            f'<g class="{uid}-ball"><circle cx="{bx - 7}" cy="{ground - 10}" r="10" fill="{ROYAL}"/>'
            f'<path d="M{bx - 17} {ground - 10} Q{bx - 7} {ground - 2} {bx + 3} {ground - 10}" fill="none" stroke="{ICE}" stroke-width="2"/>'
            f'<circle cx="{bx - 10}" cy="{ground - 14}" r="2.5" fill="#fff" opacity=".8"/></g>')
    shadow = f'<ellipse cx="{cx:.0f}" cy="{ground}" rx="{w * .32:.0f}" ry="3.5" fill="{ROYAL}" opacity=".55"/>'
    return css + ball + shadow + f'<g class="{uid}-hop">{img}</g>'


def sleeper(uid, x=960, ground=96, height=62):
    """Naps on the title line with drifting z's. (09 Commit log)"""
    img, w = _img("sleep", x, ground - height, height)
    cx = x + w / 2
    hx, hy = x + w * .2, ground - height + 8
    zs = []
    for i, (dx, size) in enumerate(((0, 13), (12, 16), (26, 20))):
        zs.append(f'<text class="{uid}-z" x="{hx + dx:.0f}" y="{hy:.0f}" font-family="{SANS}" font-weight="700" '
                  f'font-size="{size}" fill="{SKY}" style="animation-delay:{i * 1.1:.1f}s">z</text>')
    css = f"""<style>
.{uid}-br{{transform-origin:{cx:.0f}px {ground}px;animation:{uid}-br 3.6s ease-in-out infinite}}
@keyframes {uid}-br{{0%,100%{{transform:none}}50%{{transform:scale(1.02,1.05)}}}}
.{uid}-z{{opacity:0;animation:{uid}-z 3.3s ease-out infinite}}
@keyframes {uid}-z{{0%{{opacity:0;transform:translate(0,0)}}20%{{opacity:1}}100%{{opacity:0;transform:translate(-18px,-34px)}}}}
{REDUCED.format(sel=f'.{uid}-br,.{uid}-z')}
</style>"""
    shadow = f'<ellipse cx="{cx:.0f}" cy="{ground}" rx="{w * .42:.0f}" ry="3.5" fill="{ROYAL}" opacity=".55"/>'
    return css + shadow + f'<g class="{uid}-br">{img}</g>' + "".join(zs)


def waver_bye(uid, x=1012, ground=312, height=140):
    """Waves goodbye from the corner with a speech bubble. (footer)"""
    img, w = _img("wave", x, ground - height, height)
    cx = x + w / 2
    css = f"""<style>
.{uid}-sw{{transform-origin:{cx:.0f}px {ground}px;animation:{uid}-sw 1.5s ease-in-out infinite alternate}}
@keyframes {uid}-sw{{from{{transform:rotate(-4deg)}}to{{transform:rotate(4deg)}}}}
.{uid}-bb{{transform-origin:{cx:.0f}px {ground - height - 6}px;animation:{uid}-bb 6s ease-out infinite}}
@keyframes {uid}-bb{{0%{{opacity:0;transform:scale(.3)}}8%,85%{{opacity:1;transform:none}}95%,100%{{opacity:0;transform:scale(.3)}}}}
{REDUCED.format(sel=f'.{uid}-sw,.{uid}-bb')}
</style>"""
    bubble = _bubble(cx - 120, ground - height - 54, 196, 38, "see you soon 👋", 15, "down", f"{uid}-bb", uid)
    shadow = f'<ellipse cx="{cx:.0f}" cy="{ground}" rx="{w * .34:.0f}" ry="5" fill="{ROYAL}" opacity=".55"/>'
    return css + shadow + f'<g class="{uid}-sw">{img}</g>' + bubble
