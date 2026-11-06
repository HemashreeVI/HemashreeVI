#!/usr/bin/env python3
"""Profile README chess: visitors play White, a Stockfish bot plays Black.

A visitor clicks a move link in the README, which opens a pre-filled issue
titled `chess|move|e2e4` (or `chess|new`). The chess workflow runs this script:

    ISSUE_TITLE=... ISSUE_USER=... python3 scripts/chess_game.py play
    python3 scripts/chess_game.py render        # redraw board + README only

It validates the move, plays the bot's reply, redraws chess/board.svg,
rewrites the README between the CHESS markers, and writes the issue comment
to chess/comment.md. State lives in chess/state.json.
Needs python-chess; uses Stockfish when installed, else a random legal move.
"""
import datetime as dt
import json
import os
import random
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

import chess
import chess.svg

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "chess"
STATE = DIR / "state.json"
BOARD = DIR / "board.svg"
COMMENT = DIR / "comment.md"
README = ROOT / "README.md"
REPO = os.environ.get("GITHUB_REPOSITORY", "HemashreeVI/HemashreeVI")
START, END = "<!-- CHESS:START -->", "<!-- CHESS:END -->"

# Profile palette
P = {"bg0": "#090B12", "bg1": "#10131F", "line": "#262E47", "line2": "#2B3963", "lav": "#839DFB",
     "lilac": "#CEDAFF", "silver": "#E6E9F0", "mist": "#C5CAD8", "muted": "#939BB4", "mint": "#8FE3C8"}
# Polished wood board
SQ = {"square light": "#EBD3AE", "square dark": "#A8744C",
      "square light lastmove": "#E6CF7A", "square dark lastmove": "#B99A45",
      "margin": "#2A1A10", "coord": "#E9D3B0", "inner border": "#1A0F08", "outer border": "#1A0F08"}

NAMES = {chess.PAWN: "Pawn", chess.KNIGHT: "Knight", chess.BISHOP: "Bishop", chess.ROOK: "Rook",
         chess.QUEEN: "Queen", chess.KING: "King"}
ICONS = {chess.PAWN: "♙", chess.KNIGHT: "♘", chess.BISHOP: "♗", chess.ROOK: "♖", chess.QUEEN: "♕", chess.KING: "♔"}


# ---------------------------------------------------------------- state
def load():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"game": 1, "moves": [], "players": {}, "results": {"visitors": 0, "bot": 0, "draws": 0}, "history": []}


def save(s):
    DIR.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2) + "\n", encoding="utf-8")


def board_of(s):
    b = chess.Board()
    for m in s["moves"]:
        b.push_uci(m["uci"])
    return b


# ---------------------------------------------------------------- bot
def bot_move(b):
    path = shutil.which("stockfish") or ("/usr/games/stockfish" if Path("/usr/games/stockfish").exists() else None)
    if path:
        import chess.engine
        try:
            with chess.engine.SimpleEngine.popen_uci(path) as eng:
                eng.configure({"Skill Level": 3})   # friendly, beatable
                return eng.play(b, chess.engine.Limit(time=0.2, depth=8)).move
        except Exception as ex:
            print(f"stockfish failed, playing a random move: {ex}")
    return random.choice(list(b.legal_moves))


# ---------------------------------------------------------------- outcome
def result_text(b):
    o = b.outcome(claim_draw=True)
    if not o:
        return None, None
    if o.winner is chess.WHITE:
        return "visitors", "Checkmate! The visitors win 🎉"
    if o.winner is chess.BLACK:
        return "bot", "Checkmate. The bot wins this one 🤖"
    reason = o.termination.name.replace("_", " ").lower()
    return "draws", f"Draw ({reason}) 🤝"


def finish(s, b, who):
    key, text = result_text(b)
    s["results"][key] += 1
    s["history"].insert(0, {"game": s["game"], "result": text, "moves": len(s["moves"]),
                            "date": dt.date.today().isoformat(), "last": who})
    s["history"] = s["history"][:5]
    return text


# ---------------------------------------------------------------- play
def play(title, user):
    s = load()
    b = board_of(s)
    m = re.fullmatch(r"chess\|(new|move\|([a-h][1-8][a-h][1-8][qrbn]?))", title.strip())
    if not m:
        return "That doesn't look like a chess move. Use the links on the profile README to play. ♟️", False
    if m.group(1) == "new":
        if s["moves"] and not b.is_game_over(claim_draw=True) and len(s["moves"]) < 6:
            return "A game has only just started. Make a move on the board instead! ♟️", False
        if s["moves"] and not b.is_game_over(claim_draw=True):
            s["history"].insert(0, {"game": s["game"], "result": "Abandoned, new game started", "moves": len(s["moves"]),
                                    "date": dt.date.today().isoformat(), "last": user})
            s["history"] = s["history"][:5]
        s["game"] += 1
        s["moves"] = []
        save(s)
        return f"New game started (game {s['game']}). You're White: [make the first move](https://github.com/{REPO}). ♟️", True
    if b.is_game_over(claim_draw=True):
        return "This game is over. [Start a new one](https://github.com/" + REPO + ") from the profile README. ♟️", False
    move = chess.Move.from_uci(m.group(2))
    if move not in b.legal_moves:
        # Someone else may have moved first; the visitor's page was out of date.
        return (f"`{m.group(2)}` isn't legal on the current board. Someone may have moved just before you: "
                f"[refresh the profile](https://github.com/{REPO}) and pick a move again. ♟️"), False

    san = b.san(move)
    b.push(move)
    s["moves"].append({"uci": move.uci(), "san": san, "by": user})
    s["players"][user] = s["players"].get(user, 0) + 1
    lines = [f"You played **{san}**."]
    if b.is_game_over(claim_draw=True):
        lines.append(finish(s, b, user))
    else:
        reply = bot_move(b)
        rsan = b.san(reply)
        b.push(reply)
        s["moves"].append({"uci": reply.uci(), "san": rsan, "by": "bot"})
        lines.append(f"The bot replied **{rsan}**.")
        if b.is_game_over(claim_draw=True):
            lines.append(finish(s, b, user))
        else:
            lines.append(f"[Your move again](https://github.com/{REPO}) (the board updates in about a minute).")
    save(s)
    return " ".join(lines) + " ♟️", True


# ---------------------------------------------------------------- render
PIECE_GRADIENTS = """
<linearGradient id="ivory" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#FFFDF6"/><stop offset=".45" stop-color="#F1E6CF"/><stop offset="1" stop-color="#C9B48E"/></linearGradient>
<linearGradient id="ebony" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#5A5560"/><stop offset=".35" stop-color="#23242B"/><stop offset="1" stop-color="#0B0A0D"/></linearGradient>"""


def carve(svg):
    """Shade the flat piece set like turned ivory and ebony."""
    head, sep, rest = svg.partition("<defs>")
    defs, sep2, tail = rest.partition("</defs>")
    parts = re.split(r'(?=<g id="(?:white|black)-)', defs)
    out = []
    for part in parts:
        if part.startswith('<g id="white-'):
            part = re.sub(r'fill="#fff(?:fff)?"', 'fill="url(#ivory)"', part)
            part = re.sub(r'fill:\s*#fff(?:fff)?', 'fill:url(#ivory)', part)
            part = part.replace('stroke="#000"', 'stroke="#3B2A1A"')
        elif part.startswith('<g id="black-'):
            part = re.sub(r'fill="#000(?:000)?"', 'fill="url(#ebony)"', part)
            part = re.sub(r'fill:\s*#000(?:000)?', 'fill:url(#ebony)', part)
        out.append(part)
    return head + sep + PIECE_GRADIENTS + "".join(out) + sep2 + tail


def render_board(s, b):
    last = chess.Move.from_uci(s["moves"][-1]["uci"]) if s["moves"] else None
    check = b.king(b.turn) if b.is_check() else None
    inner = chess.svg.board(b, size=560, lastmove=last, check=check, coordinates=True, colors=SQ, borders=True)
    inner = inner.replace("<svg ", '<svg x="40" y="76" ', 1)
    # Real-feel pieces: soft drop shadow, plus a light sheen over the board.
    inner = inner.replace("<defs>", '<defs><filter id="pc" x="-20%" y="-20%" width="140%" height="150%">'
                          '<feDropShadow dx="1.2" dy="2.2" stdDeviation="1.4" flood-color="#000" flood-opacity=".55"/></filter>', 1)
    inner = re.sub(r'<use href="#(white|black)-', r'<use filter="url(#pc)" href="#\1-', inner)
    inner = carve(inner)
    inner = re.sub(r'<use xlink:href="#(white|black)-', r'<use filter="url(#pc)" xlink:href="#\1-', inner)

    turn = "White to move: your turn" if b.turn == chess.WHITE else "Black to move"
    key, text = result_text(b)
    status = text or turn
    recent = [f"{(i // 2) + 1}{'.' if i % 2 == 0 else '…'} {m['san']}" for i, m in enumerate(s["moves"])][-8:]
    r = s["results"]
    side = []
    y = 110
    side.append(f'<text x="640" y="{y}" class="m" font-size="12" fill="{P["lav"]}" letter-spacing="3">GAME {s["game"]}</text>')
    side.append(f'<text x="640" y="{y + 40}" class="s" font-size="26" fill="{P["silver"]}">{status}</text>')
    side.append(f'<text x="640" y="{y + 90}" class="m" font-size="12" fill="{P["lav"]}" letter-spacing="3">RECENT MOVES</text>')
    for i, mv in enumerate(recent):
        side.append(f'<text x="{640 + (i % 2) * 150}" y="{y + 122 + (i // 2) * 28}" class="m" font-size="16" '
                    f'fill="{P["mist"] if i % 2 == 0 else P["muted"]}">{mv}</text>')
    if not recent:
        side.append(f'<text x="640" y="{y + 122}" class="m" font-size="15" fill="{P["muted"]}">no moves yet: open with e4?</text>')
    sy = y + 250
    side.append(f'<text x="640" y="{sy}" class="m" font-size="12" fill="{P["lav"]}" letter-spacing="3">SCOREBOARD</text>')
    for i, (label, val, col) in enumerate([("Visitors", r["visitors"], P["mint"]), ("Bot", r["bot"], P["lilac"]),
                                           ("Draws", r["draws"], P["muted"])]):
        x = 640 + i * 160
        side.append(f'<text x="{x}" y="{sy + 50}" class="s" font-size="38" fill="{col}">{val}</text>')
        side.append(f'<text x="{x}" y="{sy + 74}" class="m" font-size="12" fill="{P["muted"]}">{label}</text>')
    side.append(f'<text x="640" y="{sy + 130}" class="s" font-size="17" font-style="italic" fill="{P["lilac"]}">You play White. A Stockfish bot plays Black.</text>')
    side.append(f'<text x="640" y="{sy + 156}" class="m" font-size="12" fill="{P["muted"]}">Pick a move below the board to play.</text>')

    W, H = 1200, 700
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">Profile chess, game {s['game']}</title>
<desc id="d">{status}. Position (FEN): {b.fen()}. Recent moves: {', '.join(recent) or 'none'}. Visitors {r['visitors']}, bot {r['bot']}, draws {r['draws']}.</desc>
<style>.s{{font-family:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif}}.m{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}</style>
<defs>
<radialGradient id="bg" cx="30%" cy="30%" r="90%"><stop offset="0" stop-color="#161C30"/><stop offset=".55" stop-color="{P['bg1']}"/><stop offset="1" stop-color="{P['bg0']}"/></radialGradient>
<radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#416AE6" stop-opacity=".45"/><stop offset="1" stop-color="#416AE6" stop-opacity="0"/></radialGradient>
<linearGradient id="sheen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".16"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".18"/></linearGradient>
<filter id="lift" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="14" stdDeviation="14" flood-color="#000" flood-opacity=".6"/></filter>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="url(#bg)" stroke="{P['line']}"/>
<ellipse cx="320" cy="360" rx="420" ry="360" fill="url(#glow)"/>
<text x="40" y="50" class="m" font-size="12" fill="{P['lav']}" letter-spacing="3">LIVE BOARD · UPDATES AFTER EVERY MOVE</text>
<rect x="36" y="72" width="568" height="568" rx="10" fill="#1A0F08" filter="url(#lift)"/>
{inner}
<rect x="40" y="76" width="560" height="560" rx="6" fill="url(#sheen)" pointer-events="none"/>
{''.join(side)}
</svg>
"""
    BOARD.write_text(svg, encoding="utf-8")


def issue_link(title, body):
    return f"https://github.com/{REPO}/issues/new?title={quote(title, safe='')}&body={quote(body, safe='')}"


def render_readme(s, b):
    v = len(s["moves"]) + s["game"] * 1000
    out = [START, "", '<p align="center">',
           f'  <a href="#chess-moves"><img src="./chess/board.svg?v={v}" width="100%" alt="Profile chess board, game {s["game"]}. You play White against a Stockfish bot. Pick your move from the list below the board."></a>',
           "</p>", "", '<a id="chess-moves"></a>', ""]
    body = "Press **Create** to play this move. The bot replies and the board updates in about a minute."
    if b.is_game_over(claim_draw=True) or b.turn == chess.BLACK:
        out.append(f'<p align="center"><b>This game is over.</b> <a href="{issue_link("chess|new", body)}">♟️ Start a new game</a></p>')
    else:
        groups = {}
        for mv in sorted(b.legal_moves, key=lambda m: (b.piece_type_at(m.from_square), chess.square_name(m.from_square), m.uci())):
            groups.setdefault(mv.from_square, []).append(mv)
        out += ['<p align="center"><b>How to play:</b> the board above is a picture, so pieces can\'t be dragged here (they can on <a href="https://hemashreevi.github.io/chess/">my portfolio</a>). '
                'Pick your move from this list instead: click it, press <b>Create</b> on the page GitHub opens, '
                'and come back in about a minute to see your move and the bot\'s reply.</p>', "",
                "| Piece | From | Moves |", "| :-- | :-: | :-- |"]
        for sq, mvs in groups.items():
            pt = b.piece_type_at(sq)
            links = " · ".join(f'[{b.san(m)}]({issue_link("chess|move|" + m.uci(), body)})' for m in mvs)
            out.append(f"| {ICONS[pt]} {NAMES[pt]} | `{chess.square_name(sq)}` | {links} |")
        if len(s["moves"]) >= 6:
            out += ["", f'<p align="center"><sub>Stuck? <a href="{issue_link("chess|new", body)}">Start a new game</a></sub></p>']
    top = sorted(s["players"].items(), key=lambda kv: -kv[1])[:5]
    if top or s["history"]:
        out += ["", "<details><summary><b>🏆 Top players and recent games</b></summary>", "<br/>", ""]
        if top:
            out += ["| Player | Moves played |", "| :-- | --: |"] + [f"| [@{u}](https://github.com/{u}) | {n} |" for u, n in top] + [""]
        if s["history"]:
            out += ["| Game | Result | Moves | Date |", "| :-: | :-- | --: | :-- |"] + \
                   [f"| {h['game']} | {h['result']} | {h['moves']} | {h['date']} |" for h in s["history"]] + [""]
        out.append("</details>")
    out += ["", END]
    text = README.read_text(encoding="utf-8")
    a, z = text.index(START), text.index(END) + len(END)
    README.write_text(text[:a] + "\n".join(out) + text[z:], encoding="utf-8")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "render"
    s = load()
    if cmd == "play":
        msg, changed = play(os.environ.get("ISSUE_TITLE", ""), os.environ.get("ISSUE_USER", "someone"))
        COMMENT.write_text(msg + "\n", encoding="utf-8")
        print(msg)
        if not changed:
            return 0
        s = load()
    b = board_of(s)
    save(s)
    render_board(s, b)
    render_readme(s, b)
    return 0


if __name__ == "__main__":
    sys.exit(main())
