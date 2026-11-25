#!/usr/bin/env python3
"""Small Snow Globe switches for the README's collapsible sections.

For each section it writes four images to assets/cards/toggles/:

    <section>-off-dark.svg / <section>-off-light.svg   night scene, knob on the moon: "show …"
    <section>-on-dark.svg  / <section>-on-light.svg    day scene, knob slides onto the sun: "… open"

The README puts the "off" switch inside <summary> (clicking it opens the
<details>), and the "on" switch as the first line of the opened content.
dark/light only changes the text colours, for GitHub's dark and light themes.

    python3 scripts/build_section_toggles.py

Standard library only.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_toggle import pill  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "assets/cards/toggles"

SECTIONS = {
    "about": ("Show full profile", "Full profile open"),
    "projects": ("Show project deep-dives", "Project deep-dives open"),
    "work": ("Show work & research", "Work & research open"),
}

TEXT = {   # README theme → (heading, hint, accent)
    "dark": ("#EEF0F7", "#9097B8", "#A9B8FF"),
    "light": ("#2A211C", "#7A6A5B", "#5B4FC4"),
}

W, H = 620, 96


def build(section, state, theme):
    show, shown = SECTIONS[section]
    head, hint, accent = TEXT[theme]
    scene = "light" if state == "on" else "dark"      # on = day + sun, off = night + moon
    defs, toggle = pill(scene, slide=(state == "on"))
    title = show if state == "off" else shown
    sub = "click the switch to expand ▾" if state == "off" else "click the switch above to close ▴"
    icon = "☾" if state == "off" else "☀"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" role="img" aria-label="{title.replace("&", "and")}: a snow-globe switch, {"off" if state == "off" else "on"}.">'
           + defs
           + f'<svg x="0" y="4" width="300" height="{H - 8}" viewBox="60 20 1080 320">{toggle}</svg>'
           + f'<text x="320" y="44" font-family="Inter,\'Segoe UI\',Arial,sans-serif" font-size="21" font-weight="800" fill="{head}">'
             f'{icon}  {title.replace("&", "&amp;")}</text>'
           + f'<text x="322" y="70" font-family="\'JetBrains Mono\',Menlo,Consolas,monospace" font-size="12.5" letter-spacing=".5" '
             f'fill="{hint}">{sub}</text>'
           + f'<rect x="322" y="80" width="46" height="3" rx="1.5" fill="{accent}"/>'
           + "</svg>")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{section}-{state}-{theme}.svg").write_text(svg)


if __name__ == "__main__":
    for sec in SECTIONS:
        for st in ("off", "on"):
            for th in ("dark", "light"):
                build(sec, st, th)
    print("wrote", len(list(OUT.glob("*.svg"))), "switches to", OUT)
