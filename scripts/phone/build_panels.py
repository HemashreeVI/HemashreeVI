#!/usr/bin/env python3
"""Builds the two animated side panels that stand next to the README phone.

  left:  Settings > About phone (specs, battery, status, a software update)
  right: notifications sliding in + home-screen widgets

    python3 scripts/phone/build_panels.py

Writes assets/phone/side-left-<hash>.svg and side-right-<hash>.svg (the hash
changes when the content does, so caches never show an old copy) and
assets/phone/panels.json with their names. Standard library only.
"""
import hashlib, json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "assets" / "phone"
M = json.loads((OUT / "manifest.json").read_text())
PHONE_W = 320
SCALE = PHONE_W / M["top"]["w"]
PHONE_H = sum(round(h * SCALE) for h in
              [M["top"]["h"], *[r[0]["h"] for r in M["rows"]], M["dots"]["h"], M["dock"][0]["h"], M["bottom"]["h"]])
W, H = 200, PHONE_H          # displayed size, matches the phone's height
VW, VH = 400, PHONE_H * 2    # drawing units (2x)

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
WHITE, MUTED, DIM = "#F4F2FF", "#A9A5C8", "#6E6A90"
CYAN, VIOLET, PINK, GOLD, MINT, RED = "#22D3EE", "#8B5CF6", "#F472B6", "#FCD34D", "#5EEAD4", "#FF0033"


def e(s):
    return escape(str(s), {'"': "&quot;"})


def t(x, y, s, size, fill=WHITE, weight=400, anchor="start", fam=SANS, extra=""):
    return f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{e(s)}</text>'


def card(x, y, w, h, r=26, fill="rgba(255,255,255,.06)", stroke="rgba(255,255,255,.13)"):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'


def frame(uid, body, title, desc):
    bg = f"""<defs>
<linearGradient id="{uid}bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#120B2A"/><stop offset=".55" stop-color="#0C0F24"/><stop offset="1" stop-color="#090B18"/></linearGradient>
<radialGradient id="{uid}glow" cx="50%" cy="0%" r="70%"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".35"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
</defs>
<rect x="2" y="2" width="{VW - 4}" height="{VH - 4}" rx="44" fill="url(#{uid}bg)" stroke="#2A2F4A" stroke-width="3"/>
<rect x="2" y="2" width="{VW - 4}" height="{VH * .45:.0f}" rx="44" fill="url(#{uid}glow)"/>"""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {VH}" width="{W}" height="{H}" role="img" aria-labelledby="{uid}t {uid}d">'
            f'<title id="{uid}t">{e(title)}</title><desc id="{uid}d">{e(desc)}</desc>{bg}{body}</svg>\n')


def cycle(i, n, period, dx):
    """SMIL for one of n cards sharing a slot: slide in, hold, slide out, wait for the others."""
    s, f = i / n, (i + 1) / n
    a = 0.06 / n * 4
    kt = [0, s, s + a, f - a, f, 1]
    op = [0, 0, 1, 1, 0, 0]
    tx = [dx, dx, 0, 0, -dx, -dx]
    pts = sorted({k: (o, x) for k, o, x in zip(kt, op, tx)}.items())
    keys = ";".join(f"{k:.4f}" for k, _ in pts)
    return (f'<animate attributeName="opacity" values="{";".join(str(o) for _, (o, _) in pts)}" keyTimes="{keys}" dur="{period}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="{";".join(f"{x} 0" for _, (_, x) in pts)}" keyTimes="{keys}" dur="{period}s" repeatCount="indefinite"/>')


def notif(x, y, w, icon_bg, icon, app, msg1, msg2, anim):
    return (f'<g opacity="0">{anim}'
            f'{card(x, y, w, 132, 28, "rgba(250,250,255,.93)", "rgba(255,255,255,.6)")}'
            f'<rect x="{x + 18}" y="{y + 22}" width="44" height="44" rx="12" fill="{icon_bg}"/>'
            f'{t(x + 40, y + 53, icon, 24, "#fff", 700, "middle")}'
            f'{t(x + 76, y + 40, app, 19, "#14111F", 700)}{t(x + w - 18, y + 40, "now", 16, "#6B6880", 500, "end")}'
            f'{t(x + 76, y + 70, msg1, 18, "#2C2940", 500)}{t(x + 76, y + 96, msg2, 18, "#2C2940", 500)}</g>')


# ---------------------------------------------------------------- left: About phone
def left():
    p = []
    p.append(t(36, 70, "Settings", 18, MUTED, 600, extra='letter-spacing="2"'))
    p.append(t(34, 110, "About phone", 34, WHITE, 800))
    # device card
    p.append(card(24, 140, 352, 190))
    p.append(f'<g transform="translate(52 170)"><rect width="56" height="96" rx="12" fill="none" stroke="{CYAN}" stroke-width="4"/>'
             f'<rect x="20" y="8" width="16" height="4" rx="2" fill="{CYAN}"/><circle cx="28" cy="82" r="4" fill="{CYAN}"/></g>')
    p.append(t(130, 200, "Hemashree's", 25, WHITE, 800))
    p.append(t(130, 230, "phone", 25, WHITE, 800))
    p.append(t(130, 266, "Model HVI · VIT '27", 18, MUTED, 500))
    p.append(t(130, 294, "Chennai, India", 18, MUTED, 500))
    rows = [
        ("PROCESSOR", ["Java · Python · Spring"], None),
        ("MEMORY", ["Kafka · Redis · Postgres"], None),
        ("STORAGE", ["67 LeetCode solved"], ("bar", .67, MINT)),
        ("PATENTS", ["2 pending 📜"], None),
        ("LANGUAGES", ["Tamil · English", "Hindi · 日本語"], None),
        ("BATTERY", ["☕ 100% charged"], ("batt",)),
        ("STATUS", ["Open to work"], ("dot",)),
    ]
    y = 380
    for label, vals, extra in rows:
        p.append(t(36, y, label, 16, DIM, 700, extra='letter-spacing="2"'))
        for i, v in enumerate(vals):
            x0 = 64 if extra and extra[0] == "dot" else 36
            p.append(t(x0, y + 34 + i * 30, v, 23, WHITE, 600))
        if extra and extra[0] == "bar":
            p.append(f'<rect x="36" y="{y + 50}" width="328" height="10" rx="5" fill="rgba(255,255,255,.1)"/>'
                     f'<rect x="36" y="{y + 50}" width="0" height="10" rx="5" fill="{extra[2]}"><animate attributeName="width" from="0" to="{328 * extra[1]:.0f}" dur="1.6s" fill="freeze"/></rect>')
        if extra and extra[0] == "batt":
            bx, by = 300, y + 12
            p.append(f'<rect x="{bx}" y="{by}" width="54" height="26" rx="6" fill="none" stroke="{WHITE}" stroke-width="2.5"/><rect x="{bx + 56}" y="{by + 8}" width="4" height="10" rx="2" fill="{WHITE}"/>'
                     f'<rect x="{bx + 4}" y="{by + 4}" width="46" height="18" rx="3" fill="{MINT}"><animate attributeName="width" values="8;46;46" keyTimes="0;.6;1" dur="3s" repeatCount="indefinite"/></rect>')
        if extra and extra[0] == "dot":
            p.append(f'<circle cx="45" cy="{y + 26}" r="8" fill="{MINT}"><animate attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/></circle>'
                     f'<circle cx="45" cy="{y + 26}" r="8" fill="none" stroke="{MINT}" stroke-width="2"><animate attributeName="r" values="8;18" dur="1.6s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;0" dur="1.6s" repeatCount="indefinite"/></circle>')
        y += 74 + (len(vals) - 1) * 30 + (20 if extra and extra[0] == "bar" else 0)
        p.append(f'<rect x="36" y="{y - 30}" width="328" height="1.5" fill="rgba(255,255,255,.08)"/>')
    # software update card
    uy = y - 4
    p.append(card(24, uy, 352, 210))
    p.append(f'<circle cx="62" cy="{uy + 46}" r="18" fill="{VIOLET}"/>' + t(62, uy + 54, "↻", 22, "#fff", 800, "middle"))
    p.append(t(94, uy + 42, "Software update", 21, WHITE, 800))
    p.append(t(94, uy + 66, "4 new projects installing", 17, MUTED, 500))
    for i, name in enumerate(["Pulse", "PortPilot", "BST Playground", "Pit Wall 🏎️"]):
        yy = uy + 104 + i * 26
        p.append(t(48, yy, name, 17, WHITE, 500))
        p.append(f'<rect x="210" y="{yy - 10}" width="140" height="8" rx="4" fill="rgba(255,255,255,.1)"/>'
                 f'<rect x="210" y="{yy - 10}" width="0" height="8" rx="4" fill="{[CYAN, VIOLET, PINK, GOLD][i]}">'
                 f'<animate attributeName="width" values="0;{[28, 60, 96, 120][i]};{[28, 60, 96, 120][i]};0" keyTimes="0;.45;.92;1" dur="{5 + i}s" repeatCount="indefinite"/></rect>')
    # patent notifications sliding in at the bottom
    ny = uy + 236
    n = [("📜", "Patent filed", "Smart Walker:", "predicts falls early"),
         ("📜", "Patent filed", "Hazard Rover: maps", "disaster-zone hazards")]
    for i, (ic, app, m1, m2) in enumerate(n):
        p.append(notif(24, ny, 352, PINK, ic, app, m1, m2, cycle(i, len(n), 8, -60)))
    # easter eggs
    ey = ny + 154
    p.append(card(24, ey, 352, VH - 26 - ey))
    p.append(t(48, ey + 42, "EASTER EGGS", 16, GOLD, 700, extra='letter-spacing="2"'))
    for i, line in enumerate(["🏎️ F1 fan, building Pit Wall", "🎨 Design Lead by night", "🐱 2 cats live in my intro", "♟️ press D on my portfolio"]):
        p.append(t(48, ey + 82 + i * 32, line, 17, WHITE if i % 2 == 0 else MUTED, 500))
    desc = ("About phone: Hemashree's phone, model HVI, VIT '27, Chennai. Processor Java, Python, Spring. Memory Kafka, Redis, Postgres. "
            "Storage 67 LeetCode solved. 2 patents pending. Languages Tamil, English, Hindi, Japanese. Battery: coffee, 100%. Status: open to work. "
            "Software update: Pulse, PortPilot, BST Playground and Pit Wall installing. Notifications: patents filed for the Smart Walker and the Hazard Rover.")
    return frame("L", "".join(p), "About Hemashree's phone", desc)


# ---------------------------------------------------------------- right: notifications + widgets
def right():
    p = []
    p.append(t(36, 70, "Notifications", 18, MUTED, 600, extra='letter-spacing="2"'))
    p.append(f'<circle cx="352" cy="62" r="16" fill="{RED}"/>' + t(352, 69, "4", 18, "#fff", 800, "middle"))
    msgs = [
        ("#BE185D", "🎟", "SeatLock", "0 double-bookings", "under k6 load ✅"),
        ("#0E7490", "🔍", "RootLens", "incident fixed in", "under 2 minutes 🚀"),
        (RED, "▶", "Byte Decoded", "new video is up,", "come watch me build"),
        ("#5A8A2A", "♞", "Chess.com", "hemashreevi wants", "to play a game"),
    ]
    for i, (bg, ic, app, m1, m2) in enumerate(msgs):
        p.append(notif(24, 92, 352, bg, ic, app, m1, m2, cycle(i, len(msgs), 14, 60)))
    # LeetCode ring widget
    y = 256
    p.append(card(24, y, 352, 250))
    cx, cy, r = 112, y + 125, 70
    circ = 2 * 3.14159 * r
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="rgba(255,255,255,.1)" stroke-width="16"/>'
             f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#FFA116" stroke-width="16" stroke-linecap="round" '
             f'stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}" transform="rotate(-90 {cx} {cy})">'
             f'<animate attributeName="stroke-dashoffset" from="{circ:.1f}" to="{circ * (1 - .67):.1f}" dur="1.8s" fill="freeze"/></circle>')
    p.append(t(cx, cy + 8, "67", 40, WHITE, 800, "middle") + t(cx, cy + 34, "solved", 15, MUTED, 600, "middle"))
    p.append(t(206, y + 60, "LeetCode", 22, WHITE, 800))
    for i, (lab, n, col) in enumerate([("Easy", 37, "#00B8A3"), ("Medium", 23, "#FFC01E"), ("Hard", 7, "#FF375F")]):
        yy = y + 104 + i * 40
        p.append(f'<circle cx="214" cy="{yy - 7}" r="6" fill="{col}"/>' + t(228, yy, lab, 18, MUTED, 600) + t(356, yy, n, 20, WHITE, 800, "end"))
    # Now building widget
    y = 530
    p.append(card(24, y, 352, 230))
    p.append(t(48, y + 44, "NOW BUILDING", 16, CYAN, 700, extra='letter-spacing="2"'))
    p.append(t(48, y + 88, "Pulse", 30, WHITE, 800))
    p.append(t(48, y + 118, "a free status page on", 17, MUTED, 500))
    p.append(t(48, y + 142, "GitHub Actions + Pages", 17, MUTED, 500))
    p.append(f'<rect x="48" y="{y + 170}" width="304" height="12" rx="6" fill="rgba(255,255,255,.1)"/>'
             f'<rect x="48" y="{y + 170}" width="61" height="12" rx="6" fill="{CYAN}"><animate attributeName="opacity" values="1;.45;1" dur="2s" repeatCount="indefinite"/></rect>')
    p.append(t(48, y + 210, "step 1 of 5", 15, DIM, 600) + t(352, y + 210, "20%", 15, CYAN, 700, "end"))
    # Byte Decoded widget
    y = 784
    p.append(card(24, y, 352, 220))
    p.append(f'<rect x="48" y="{y + 28}" width="150" height="96" rx="16" fill="{RED}"/><path d="M110 {y + 56}l28 20-28 20Z" fill="#fff"/>')
    for k in range(5):
        hh = 18 + (k * 13) % 30
        p.append(f'<rect x="{220 + k * 28}" y="{y + 110 - hh}" width="16" height="{hh}" rx="4" fill="{[PINK, CYAN, GOLD, VIOLET, MINT][k]}">'
                 f'<animate attributeName="height" values="{hh};{hh + 34};{hh}" dur="{1 + k * .23:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="y" values="{y + 110 - hh};{y + 76 - hh};{y + 110 - hh}" dur="{1 + k * .23:.2f}s" repeatCount="indefinite"/></rect>')
    p.append(t(48, y + 162, "Byte Decoded", 24, WHITE, 800))
    p.append(t(48, y + 192, "60+ videos · tech · AI · code", 17, MUTED, 500))
    # chess widget
    y = 1028
    p.append(card(24, y, 352, 190))
    sq = 26
    for r_ in range(4):
        for c_ in range(4):
            p.append(f'<rect x="{48 + c_ * sq}" y="{y + 32 + r_ * sq}" width="{sq}" height="{sq}" fill="{"#EBECD0" if (r_ + c_) % 2 == 0 else "#779556"}"/>')
    p.append(f'<g transform="translate({48 + 1 * sq + sq / 2} {y + 32 + 2 * sq + sq / 2})"><g>'
             f'<circle cx="0" cy="-8" r="6" fill="#fff" stroke="#333" stroke-width="1.5"/><path d="M-6 -2h12l-2 3h-8Z M-5 1h10l3 9h-16Z" fill="#fff" stroke="#333" stroke-width="1.5"/>'
             f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 -{sq};0 -{sq};0 -{2 * sq};0 -{2 * sq};0 0" keyTimes="0;.2;.3;.5;.6;.85;1" dur="6s" repeatCount="indefinite"/></g></g>')
    p.append(t(176, y + 66, "Chess.com", 22, WHITE, 800))
    p.append(t(176, y + 96, "hemashreevi", 17, "#95C95B", 700, fam=MONO))
    p.append(t(176, y + 128, "challenge me ♞", 17, MUTED, 500))
    p.append(t(176, y + 156, "e4 is my move", 15, DIM, 500))
    # location / time widget
    y = 1242
    p.append(card(24, y, 352, 150))
    p.append(t(48, y + 48, "📍 Chennai, India", 21, WHITE, 700))
    p.append(t(48, y + 82, "Open to remote · on-site", 17, MUTED, 500))
    p.append(t(48, y + 116, "replies within a day ✉️", 17, MUTED, 500))
    # GitHub contributions widget
    y = 1414
    p.append(card(24, y, 352, VH - 28 - y))
    p.append(t(48, y + 40, "GitHub", 20, WHITE, 800) + t(352, y + 40, "always green 🟩", 15, MUTED, 600, "end"))
    import random
    rnd = random.Random(7)
    greens = ["#0E4429", "#006D32", "#26A641", "#39D353"]
    for c_ in range(14):
        for r_ in range(5):
            last = c_ == 13 and r_ == 4
            col = "#39D353" if last else greens[min(3, int(rnd.random() * 4.6))]
            cell = f'<rect x="{48 + c_ * 22}" y="{y + 58 + r_ * 18}" width="16" height="14" rx="3" fill="{col}"'
            p.append(cell + ('><animate attributeName="opacity" values="1;.3;1" dur="1.4s" repeatCount="indefinite"/></rect>' if last else "/>"))
    desc = ("Notifications: SeatLock had 0 double-bookings under k6 load; RootLens fixed an incident in under 2 minutes; a new video on Byte Decoded; "
            "hemashreevi wants to play on Chess.com. Widgets: LeetCode 67 solved (37 easy, 23 medium, 7 hard); now building Pulse, a free status page, step 1 of 5; "
            "Byte Decoded, 60+ videos; Chess.com profile hemashreevi; Chennai, India, open to remote and on-site.")
    return frame("R", "".join(p), "Notifications and widgets", desc)


def main():
    for old in OUT.glob("side-*.svg"):
        old.unlink()
    names = {}
    for side, svg in (("left", left()), ("right", right())):
        h = hashlib.sha1(svg.encode()).hexdigest()[:8]
        name = f"side-{side}-{h}.svg"
        (OUT / name).write_text(svg, encoding="utf-8")
        names[side] = name
        print(f"  {name}  {len(svg.encode()) / 1024:.1f} KB  ({W}x{H})")
    (OUT / "panels.json").write_text(json.dumps({**names, "w": W, "h": H}, indent=1))


if __name__ == "__main__":
    main()
