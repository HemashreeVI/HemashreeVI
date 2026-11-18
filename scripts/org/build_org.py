#!/usr/bin/env python3
"""Builds the Byte Decoded organization's banner (assets/org/banner.svg) in the same
black & silver style as the profile, with the marble knight and rook.
The org README (byte-decoded/.github, profile/README.md) shows it from this repo.

    python3 scripts/org/build_org.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build_cards as bc       # noqa: E402
import chess_layer             # noqa: E402

C, text = bc.C, bc.text
OUT = bc.ROOT / "assets" / "org"


def banner():
    W, H, u = 1200, 360, "org"
    knight, rook = chess_layer.piece("orgN", "knight", 1.0), chess_layer.piece("orgR", "rook", .9)
    body = f"""
{bc.frame(W, H, u, (0.78, 0.35))}
{bc.stars(W, H, 26, 9)}
{chess_layer.defs("orgN")}{chess_layer.defs("orgR")}
{text(64, 74, "OPEN SOURCE  ·  CHROME EXTENSIONS  ·  DEV VIDEOS", 12, C['lav'], 'mono', 'start', 'letter-spacing="4"')}
<text x="60" y="176" class="serif" font-size="92" fill="url(#{u}-silver)" letter-spacing="6">BYTE</text>
<text x="60" y="262" class="serif" font-size="92" font-style="italic" fill="url(#{u}-sweep)" letter-spacing="2">Decoded.</text>
<rect x="64" y="288" width="520" height="1.2" fill="url(#{u}-rule)"/>
{text(64, 320, "Small tools that make developers' days easier, built in the open.", 16, C['mist'], 'sans')}
<g transform="translate(930 312)"><g>
  <animateTransform attributeName="transform" type="translate" values="0 0;0 -6;0 0" dur="5s" repeatCount="indefinite"/>{knight}</g></g>
<g transform="translate(1050 312)">{rook}</g>
{text(W - 40, 340, "by HemashreeVI", 11, C['muted'], 'mono', 'end', 'letter-spacing="2"')}
"""
    desc = "Byte Decoded: open-source tools, Chrome extensions and dev videos by HemashreeVI. Small tools that make developers' days easier, built in the open."
    return bc.svg(W, H, u, "Byte Decoded", desc, body)


OUT.mkdir(parents=True, exist_ok=True)
# section titles for the org README, numbered on their own (they land in assets/cards/ with the others)
bc.build_title("01", "CHROME EXTENSIONS", "Tools for", "the browser.", "5 EXTENSIONS · FREE · OPEN SOURCE", "org-tools",
               extra=chess_layer.knight_hops("orgTN"))
bc.build_title("02", "YOUTUBE", "Byte", "Decoded.", "BUILDS · WALKTHROUGHS · TECH VLOGS", "org-youtube")
(OUT / "banner.svg").write_text(banner(), encoding="utf-8")
print("assets/org/banner.svg")
