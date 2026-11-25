#!/usr/bin/env python3
"""Draws assets/cards/edu.svg: a strip with VIT, NUS and IBM logos.

    python3 scripts/build_edu.py

Logos are read from assets/logos/ (vit.png|svg, nus.png|svg, ibm.svg) and
embedded, so the card works as a single image on GitHub. A missing logo is
drawn as a lettered badge instead. Standard library only.
"""
import base64
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from build_cards import C  # noqa: E402

LOGOS = ROOT / "assets/logos"

ITEMS = [
    ("vit", "VIT", "VIT Chennai", "B.Tech Computer Science Engineering", "AUG 2023 → NOW"),
    (("nus", "ntu"), "NUS · NTU", "NUS & NTU, Singapore", "Introduction to Industry 4.0 Programme", "JUN 2025 · SINGAPORE"),
    ("superai", "SUPERAI", "SuperAI 2025", "AI conference · Marina Bay Sands", "18–19 JUN 2025 · SINGAPORE"),
    ("ibm", "IBM", "IBM", "Generative AI certification · watsonx", "2025"),
]

DARK_PANELS = {"superai"}   # logos designed for a dark background


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def logo(key, fallback, x, y, w, h):
    """Embed the logo centred in a w×h box on white, or draw a lettered badge."""
    for ext, mime in (("svg", "image/svg+xml"), ("png", "image/png"), ("webp", "image/webp"), ("jpg", "image/jpeg")):
        f = LOGOS / f"{key}.{ext}"
        if f.exists():
            data = f.read_bytes()
            if ext == "svg" and key == "ibm":           # single-path icon: draw it in IBM blue
                path = re.search(r'<path d="([^"]+)"', data.decode()).group(1)
                s = h / 24 * 1.6
                return (f'<path d="{path}" fill="#0F62FE" '
                        f'transform="translate({x + w / 2 - 12 * s:.1f} {y + h / 2 - 12 * s:.1f}) scale({s:.3f})"/>')
            uri = f"data:{mime};base64,{base64.b64encode(data).decode()}"
            return f'<image href="{uri}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet"/>'
    color = "#FFFFFF" if key in DARK_PANELS else "#1F2A5A"
    return (f'<text x="{x + w / 2}" y="{y + h / 2 + 9}" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" '
            f'font-size="26" font-weight="800" letter-spacing="2" fill="{color}">{fallback}</text>')


def build():
    w, h = 1200, 350
    tile_w, tile_h, gap = 548, 124, 24
    x0 = (w - 2 * tile_w - gap) // 2
    panel_w = 210
    parts = [f'<defs><linearGradient id="edu-dark" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5B2BD9"/>'
             f'<stop offset=".45" stop-color="#1E1F6B"/><stop offset="1" stop-color="#121A4A"/></linearGradient></defs>',
             f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18" fill="{C["bg1"]}" stroke="{C["line"]}" stroke-width="2"/>',
             f'<text x="40" y="40" font-family="JetBrains Mono,Menlo,monospace" font-size="12" letter-spacing="3" fill="{C["muted"]}">EDUCATION &amp; PROGRAMS</text>']
    for i, (key, fb, name, line, when) in enumerate(ITEMS):
        x = x0 + (i % 2) * (tile_w + gap)
        y = 60 + (i // 2) * (tile_h + gap)
        px, py, ph = x + 12, y + 12, tile_h - 24
        dark = key in DARK_PANELS
        if isinstance(key, tuple):
            art = (logo(key[0], fb, px + 6, py + 8, panel_w / 2 - 12, ph - 16)
                   + f'<line x1="{px + panel_w / 2}" y1="{py + 14}" x2="{px + panel_w / 2}" y2="{py + ph - 14}" stroke="#D0D4E4"/>'
                   + logo(key[1], fb, px + panel_w / 2 + 6, py + 8, panel_w / 2 - 12, ph - 16))
        else:
            art = logo(key, fb, px + 10, py + 8, panel_w - 20, ph - 16)
        tx = px + panel_w + 22
        parts.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{0.2 + i * 0.2}s" dur=".6s" fill="freeze"/>'
                     f'<rect x="{x}" y="{y}" width="{tile_w}" height="{tile_h}" rx="14" fill="{C["panel"]}" stroke="{C["line2"]}"/>'
                     f'<rect x="{px}" y="{py}" width="{panel_w}" height="{ph}" rx="10" fill="{"url(#edu-dark)" if dark else "#FFFFFF"}"/>'
                     + art
                     + f'<text x="{tx}" y="{y + 46}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="17" font-weight="700" fill="{C["silver"]}">{esc(name)}</text>'
                     f'<text x="{tx}" y="{y + 70}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="13" fill="{C["mist"]}">{esc(line)}</text>'
                     f'<text x="{tx}" y="{y + 94}" font-family="JetBrains Mono,Menlo,monospace" font-size="11" letter-spacing="1.5" fill="{C["violet"]}">{esc(when)}</text></g>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
           f'aria-label="Education and programs: VIT Chennai, B.Tech CSE; NUS and NTU Singapore, Introduction to Industry 4.0 Programme, June 2025; SuperAI 2025 conference, Marina Bay Sands, Singapore, June 2025; IBM, Generative AI certification with watsonx.">'
           + "".join(parts) + "</svg>")
    out = ROOT / "assets/cards/edu.svg"
    out.write_text(svg)
    print("wrote", out)


if __name__ == "__main__":
    build()
