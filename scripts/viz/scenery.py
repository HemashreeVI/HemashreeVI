"""Scenery around Contribution City: sky, moon, clouds, mountains, the far shore,
the river and harbour with reflections, quays and street lamps, a cable-stayed
bridge, a ferry and boats, a plane and a helicopter.

Everything is plain SVG (gradients, filters with procedural noise, SMIL motion),
so it renders inside a README <img> and stays small.
"""
import math
import random

COS, SIN = math.cos(math.radians(30)), math.sin(math.radians(30))


def defs():
    return """
<filter id="ripple" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.0035 0.11" numOctaves="3" seed="4"/>
  <feColorMatrix values="0 0 0 0 .78  0 0 0 0 .86  0 0 0 0 1  0 0 2.1 0 -1.2"/></filter>
<filter id="warp" x="-20%" y="-10%" width="140%" height="160%"><feTurbulence type="fractalNoise" baseFrequency="0.01 0.16" numOctaves="2" seed="9" result="t"/>
  <feDisplacementMap in="SourceGraphic" in2="t" scale="12" xChannelSelector="R" yChannelSelector="G" result="d"/><feGaussianBlur in="d" stdDeviation=".7 1.8"/></filter>
<filter id="clouds" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.0042 0.012" numOctaves="5" seed="12"/>
  <feColorMatrix values="0 0 0 0 .55  0 0 0 0 .6  0 0 0 0 .78  2.6 0 0 0 -1.32"/><feGaussianBlur stdDeviation="1.2"/></filter>
<filter id="wisps" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.0028 0.03" numOctaves="4" seed="31"/>
  <feColorMatrix values="0 0 0 0 .5  0 0 0 0 .55  0 0 0 0 .72  2.2 0 0 0 -1.1"/></filter>
<filter id="craters" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".09" numOctaves="3" seed="2"/>
  <feColorMatrix values="0 0 0 0 .55  0 0 0 0 .5  0 0 0 0 .55  0 0 0 -2.2 1.4"/><feComposite in2="SourceGraphic" operator="in"/></filter>
<filter id="soft"><feGaussianBlur stdDeviation="6"/></filter>
<radialGradient id="moonG" cx="38%" cy="34%" r="70%"><stop offset="0" stop-color="#FFFBEA"/><stop offset=".7" stop-color="#EDE6CF"/><stop offset="1" stop-color="#BDB49A"/></radialGradient>
<radialGradient id="halo" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#C7D2FE" stop-opacity=".28"/><stop offset=".4" stop-color="#A5B4FC" stop-opacity=".08"/><stop offset="1" stop-color="#A5B4FC" stop-opacity="0"/></radialGradient>
<radialGradient id="nightTree" cx="70%" cy="25%" r="80%"><stop offset="0" stop-color="#3E5A52"/><stop offset=".35" stop-color="#1E3329"/><stop offset="1" stop-color="#0A1410"/></radialGradient>
<radialGradient id="lampG" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#FFE7A3" stop-opacity=".75"/><stop offset="1" stop-color="#FFE7A3" stop-opacity="0"/></radialGradient>
<radialGradient id="cityglow" cx="50%" cy="60%" r="55%"><stop offset="0" stop-color="#F59E0B" stop-opacity=".22"/><stop offset=".5" stop-color="#EC4899" stop-opacity=".08"/><stop offset="1" stop-color="#EC4899" stop-opacity="0"/></radialGradient>
<linearGradient id="farM" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4A5A88"/><stop offset=".25" stop-color="#2A3762"/><stop offset="1" stop-color="#1B2448"/></linearGradient>
<linearGradient id="midM" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2C3961"/><stop offset="1" stop-color="#141B36"/></linearGradient>
<linearGradient id="nearM" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1C2546"/><stop offset="1" stop-color="#0D1226"/></linearGradient>
<linearGradient id="haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7C86B8" stop-opacity="0"/><stop offset=".7" stop-color="#8B5E8C" stop-opacity=".22"/><stop offset="1" stop-color="#E08A5B" stop-opacity=".18"/></linearGradient>
<linearGradient id="land" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1A2027"/><stop offset="1" stop-color="#0F1418"/></linearGradient>
<linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16244A"/><stop offset=".35" stop-color="#0E1A38"/><stop offset="1" stop-color="#060B1C"/></linearGradient>
<linearGradient id="fadeV" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".25" stop-color="#fff" stop-opacity="1"/><stop offset=".75" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="fadeH" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".15" stop-color="#fff" stop-opacity="1"/><stop offset=".85" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F8FAFF" stop-opacity=".45"/><stop offset="1" stop-color="#F8FAFF" stop-opacity="0"/></linearGradient>
<linearGradient id="streak" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFD9A0" stop-opacity=".55"/><stop offset="1" stop-color="#FFD9A0" stop-opacity="0"/></linearGradient>
<pattern id="stone" width="16" height="7" patternUnits="userSpaceOnUse"><rect width="16" height="7" fill="#2A2E3D"/><path d="M0 .5H16M8 .5V3.5M0 3.5H16M4 3.5V7M12 3.5V7" stroke="#1A1D28" stroke-width=".8"/></pattern>
"""


def ridge(x0, x1, base, amp, rnd, rough=.55, depth=7):
    """A natural mountain ridge by midpoint displacement; returns points across [x0, x1]."""
    pts = [(x0, base - rnd.uniform(.2, .6) * amp), (x1, base - rnd.uniform(.2, .6) * amp)]
    disp = amp * .9
    for _ in range(depth):
        nxt = [pts[0]]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            my = (ay + by) / 2 + rnd.uniform(-disp, disp)
            nxt += [((ax + bx) / 2, min(base - 4, max(base - amp * 1.25, my))), (bx, by)]
        pts, disp = nxt, disp * rough
    return pts


def path(pts, close_to=None):
    d = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    if close_to is not None:
        d += f"L{pts[-1][0]:.1f} {close_to:.1f}L{pts[0][0]:.1f} {close_to:.1f}Z"
    return d


def backdrop(W, H, yH, sky_top, rnd, moon):
    """Sky details, moon, clouds, mountains, haze and the far land. yH = horizon line."""
    mx, my, mr = moon
    o = []
    # moon with craters and a soft halo
    o.append(f'<circle cx="{mx}" cy="{my}" r="{mr * 5}" fill="url(#halo)"/>'
             f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="url(#moonG)"/><circle cx="{mx}" cy="{my}" r="{mr}" fill="#fff" filter="url(#craters)" opacity=".55"/>')
    # cloud bank, faded at the edges so there are no hard borders, drifting slowly
    ch = max(60, yH - sky_top - 70)
    o.append(f'<mask id="cmask"><rect x="0" y="{sky_top}" width="{W}" height="{ch}" fill="url(#fadeV)"/></mask>'
             f'<g mask="url(#cmask)" opacity=".62"><g><rect x="-200" y="{sky_top}" width="{W + 400}" height="{ch}" filter="url(#clouds)"/>'
             f'<animateTransform attributeName="transform" type="translate" values="0 0;140 0;0 0" dur="90s" repeatCount="indefinite"/></g></g>')
    # three mountain ranges: far (moonlit, hazy), middle, near hills
    room = max(40, (yH - sky_top - 10) / 1.25)          # keep the peaks below the header
    for k, (amp, grad, rough, op, ridge_op) in enumerate([(150, "farM", .58, .95, .45), (95, "midM", .55, 1, .3), (48, "nearM", .5, 1, .2)]):
        amp = min(amp, room * (1, .7, .4)[k])
        base = yH + 6 - k * 2
        pts = ridge(-20, W + 20, base - k * 8, amp, rnd, rough)
        o.append(f'<path d="{path(pts, base + 4)}" fill="url(#{grad})" opacity="{op}"/>'
                 f'<path d="{path(pts)}" stroke="#9FB0E0" stroke-opacity="{ridge_op}" stroke-width=".9" fill="none"/>')
        if k == 0:   # snow on the highest peaks, lit by the moon
            o.append(f'<clipPath id="peaks"><path d="{path(pts, base)}"/></clipPath>'
                     f'<rect x="0" y="{base - amp * 1.3:.0f}" width="{W}" height="{amp * .42:.0f}" fill="#DCE4FF" opacity=".22" clip-path="url(#peaks)"/>')
        if k == 1:   # thin mist drifting between the ranges
            o.append(f'<g opacity=".35"><rect x="-150" y="{base - amp * .7:.0f}" width="{W + 300}" height="{amp * .7:.0f}" filter="url(#wisps)">'
                     f'<animateTransform attributeName="transform" type="translate" values="0 0;-120 0;0 0" dur="70s" repeatCount="indefinite"/></rect></g>')
    o.append(f'<rect x="0" y="{yH - 70}" width="{W}" height="76" fill="url(#haze)"/>')
    o.append(f'<rect x="0" y="{yH}" width="{W}" height="{H - yH}" fill="url(#land)"/>')
    return "".join(o)


def far_lights(W, yH, inside, rnd, n=170):
    """Towns on the far land and shore: tiny lights that thin out with distance."""
    o = []
    for _ in range(n * 4):
        if len(o) >= n:
            break
        x, y = rnd.uniform(0, W), yH + rnd.betavariate(1.2, 4) * 120
        if not inside(x, y):
            continue
        col = rnd.choice(["#FFE3A1", "#FFD27A", "#FFF3D6", "#BFE3FF"])
        r = rnd.choice([.6, .7, .8, 1, 1.2])
        glow = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 3.5:.1f}" fill="{col}" opacity=".12"/>' if r > .9 else ""
        o.append(f'{glow}<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" opacity="{rnd.uniform(.5, .95):.2f}"/>')
    return "".join(o)


def boat_box(u, v, L, Wd, Hh, hull, deck, cabin=None, s=1):
    """An isometric boat hull (box with a pointed bow) heading along u."""
    def pt(a, b, z=0):
        return (u[0] * a + v[0] * b, u[1] * a + v[1] * b - z)
    def pg(pts, fill, extra=""):
        return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}" {extra}/>'
    hl, hw = L / 2, Wd / 2
    bow = [pt(hl * 1.25, 0)]
    o = [pg([pt(-hl, -hw), pt(hl, -hw)] + bow + [pt(hl, hw), pt(-hl, hw)], "#000", 'opacity=".3"')]
    o.append(pg([pt(-hl, hw), pt(hl, hw), pt(hl * 1.25, 0, 0), pt(hl * 1.25, 0, Hh), pt(hl, hw, Hh), pt(-hl, hw, Hh)], hull))
    o.append(pg([pt(-hl, -hw, Hh), pt(hl, -hw, Hh), pt(hl * 1.25, 0, Hh), pt(hl, hw, Hh), pt(-hl, hw, Hh)], deck))
    if cabin:
        cl, cw, chh, ccol, lit = cabin
        o.append(pg([pt(-cl / 2 - hl * .15, cw / 2, Hh), pt(cl / 2 - hl * .15, cw / 2, Hh), pt(cl / 2 - hl * .15, cw / 2, Hh + chh), pt(-cl / 2 - hl * .15, cw / 2, Hh + chh)], ccol))
        o.append(pg([pt(-cl / 2 - hl * .15, -cw / 2, Hh + chh), pt(cl / 2 - hl * .15, -cw / 2, Hh + chh), pt(cl / 2 - hl * .15, cw / 2, Hh + chh), pt(-cl / 2 - hl * .15, cw / 2, Hh + chh)], "#E5E7EB"))
        n = 6
        for k in range(n):
            a0 = -cl / 2 - hl * .15 + (k + .2) * cl / n
            o.append(pg([pt(a0, cw / 2, Hh + chh * .35), pt(a0 + cl / n * .6, cw / 2, Hh + chh * .35), pt(a0 + cl / n * .6, cw / 2, Hh + chh * .75), pt(a0, cw / 2, Hh + chh * .75)], lit))
    # wake: two foam lines spreading behind the stern
    sx, sy = pt(-hl, 0)
    for side in (-1, 1):
        ex, ey = pt(-hl * 4.5, side * hw * 4)
        o.insert(0, f'<path d="M{sx:.1f} {sy:.1f}L{ex:.1f} {ey:.1f}" stroke="#E6F0FF" stroke-opacity=".35" stroke-width="1.6" stroke-linecap="round"/>')
    tx, ty = pt(-hl * 3, 0)
    o.insert(0, f'<path d="M{sx:.1f} {sy:.1f}L{tx:.1f} {ty:.1f}" stroke="#E6F0FF" stroke-opacity=".18" stroke-width="{Wd * .6:.1f}" stroke-linecap="round"/>')
    return "".join(o)


def plane(W, y):
    body = ('<g><path d="M-14 0L12 -1.2L15 0L12 1.2Z" fill="#9AA6C4"/><path d="M-1 0L-6 -9L-3 -9L4 0L-3 9L-6 9Z" fill="#6F7B9A"/><path d="M-12 0L-15 -4L-13 -4L-9 0Z" fill="#6F7B9A"/>'
            '<circle cx="-6" cy="-9" r="1.3" fill="#FF3B3B"><animate attributeName="opacity" values="1;.2;1" dur="1s" repeatCount="indefinite"/></circle>'
            '<circle cx="-6" cy="9" r="1.3" fill="#3BFF7A"><animate attributeName="opacity" values="1;.2;1" dur="1s" repeatCount="indefinite"/></circle>'
            '<circle cx="15" cy="0" r="1.6" fill="#fff"><animate attributeName="opacity" values="0;0;1;0" keyTimes="0;.85;.9;1" dur="1.4s" repeatCount="indefinite"/></circle></g>')
    return (f'<g>{body}<animateMotion dur="38s" repeatCount="indefinite" path="M-60 {y + 30}L{W + 60} {y - 25}"/></g>')


def helicopter(cx, cy):
    """Circles the landmark tower with its searchlight on it."""
    heli = ('<g><polygon points="-6,8 6,8 34,92 -34,92" fill="url(#beam)" opacity=".55"/>'
            '<ellipse cx="0" cy="0" rx="9" ry="4.5" fill="#2E3446"/><path d="M-8 -1L-22 -3" stroke="#2E3446" stroke-width="2"/>'
            '<ellipse cx="0" cy="-5" rx="17" ry="2.4" fill="#C9D2E3" opacity=".35"><animate attributeName="rx" values="17;12;17" dur=".18s" repeatCount="indefinite"/></ellipse>'
            '<circle cx="-22" cy="-3" r="1.4" fill="#FF3355"><animate attributeName="opacity" values="1;.1;1" dur=".9s" repeatCount="indefinite"/></circle></g>')
    return (f'<g>{heli}<animateMotion dur="16s" repeatCount="indefinite" path="M{cx - 75:.0f} {cy:.0f}a75 22 0 1 0 150 0a75 22 0 1 0 -150 0"/></g>')
