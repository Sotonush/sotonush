import json
import os
import random
import re
import shutil
import sys
from urllib.parse import quote

import chess
import chess.engine
import chess.svg

from geass import CRIMSON, MUTED, PAPER, VIOLET, esc, gradient_defs, sigil

REPO = os.environ.get("GITHUB_REPOSITORY", "Sotonush/sotonush")
STATE = "chess/game.json"
BOARD = "chess/board.svg"
README = "README.md"
START, END = "<!-- ZERO-CHESS:START -->", "<!-- ZERO-CHESS:END -->"
COMMAND = re.compile(r"^chess\|(move\|([a-h][1-8][a-h][1-8][qrbn]?)|new)$")

PIECE_NAMES = {
    chess.KING: "♔ King",
    chess.QUEEN: "♕ Queen",
    chess.ROOK: "♖ Rook",
    chess.BISHOP: "♗ Bishop",
    chess.KNIGHT: "♘ Knight",
    chess.PAWN: "♙ Pawn",
}
VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}


def fresh_state(previous=None):
    previous = previous or {}
    return {
        "game": previous.get("game", 0) + 1,
        "fen": chess.STARTING_FEN,
        "moves": [],
        "players": previous.get("players", {}),
        "record": previous.get("record", {"zero": 0, "challengers": 0, "draws": 0}),
    }


def load():
    if not os.path.exists(STATE):
        return fresh_state()
    with open(STATE, encoding="utf-8") as file:
        return json.load(file)


def save(state):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w", encoding="utf-8") as file:
        json.dump(state, file, ensure_ascii=False, indent=2)


def zero_move(board):
    path = shutil.which("stockfish") or "/usr/games/stockfish"
    if os.path.exists(path):
        with chess.engine.SimpleEngine.popen_uci(path) as engine:
            engine.configure({"Skill Level": int(os.environ.get("ZERO_SKILL", "5"))})
            return engine.play(board, chess.engine.Limit(time=0.4)).move

    def score(move):
        captured = board.piece_at(move.to_square)
        board.push(move)
        mate = board.is_checkmate()
        check = board.is_check()
        board.pop()
        return (mate, VALUES[captured.piece_type] if captured else 0, check, random.random())

    return max(board.legal_moves, key=score)


def outcome_text(board):
    outcome = board.outcome()
    if outcome is None:
        return None
    if outcome.winner is chess.WHITE:
        return "challengers", "Checkmate. The challengers have defeated Zero."
    if outcome.winner is chess.BLACK:
        return "zero", "Checkmate. All of this world obeys Zero."
    return "draws", f"Draw by {outcome.termination.name.replace('_', ' ').lower()}."


def play(state, command, author):
    board = chess.Board(state["fen"])
    match = COMMAND.match(command.strip())
    if not match:
        return state, "Unknown command. Use the move links in the profile README."

    if match.group(1) == "new":
        if board.outcome() is None and state["moves"]:
            return state, "A game is still running. Finish it first."
        return fresh_state(state), f"Game #{state['game'] + 1} begins. Your move, @{author}."

    if board.outcome() is not None:
        return state, "This game is over. Start a new one from the README."

    move = chess.Move.from_uci(match.group(2))
    if move not in board.legal_moves:
        return state, f"`{match.group(2)}` is not legal in the current position. Someone may have moved first."

    state["moves"].append({"san": board.san(move), "uci": move.uci(), "by": author})
    board.push(move)
    state["players"][author] = state["players"].get(author, 0) + 1
    reply = f"@{author} played **{state['moves'][-1]['san']}**."

    if board.outcome() is None:
        answer = zero_move(board)
        state["moves"].append({"san": board.san(answer), "uci": answer.uci(), "by": "Zero"})
        board.push(answer)
        reply += f" Zero answered **{state['moves'][-1]['san']}**."

    result = outcome_text(board)
    if result:
        state["record"][result[0]] += 1
        reply += " " + result[1]

    state["fen"] = board.fen()
    return state, reply


def board_svg(state):
    board = chess.Board(state["fen"])
    last = chess.Move.from_uci(state["moves"][-1]["uci"]) if state["moves"] else None
    check = board.king(board.turn) if board.is_check() else None
    inner = chess.svg.board(
        board,
        lastmove=last,
        check=check,
        size=480,
        coordinates=True,
        colors={
            "square light": "#b9a6d4",
            "square dark": "#57318a",
            "square light lastmove": "#ff8fa6",
            "square dark lastmove": "#c2184a",
            "margin": "#0b0610",
            "coord": "#9a8cae",
        },
    )
    inner = re.sub(r'<svg([^>]*?)\swidth="\d+"\sheight="\d+"', r'<svg\1', inner, count=1)
    inner = inner.replace("<svg", '<svg x="40" y="96" width="480" height="480"', 1)

    result = outcome_text(board)
    if result:
        status = result[1]
    elif board.turn == chess.WHITE:
        status = "Your move, challenger"
    else:
        status = "Zero is thinking"
    record = state["record"]

    return "\n".join([
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 560 640" width="560" height="640">',
        "<defs>" + gradient_defs() + "<style>"
        ".mono{font-family:'JetBrains Mono','Fira Code',Consolas,monospace}"
        ".serif{font-family:'Cormorant Garamond','Palatino Linotype',Georgia,serif}"
        ".pulse{animation:pulse 3.6s ease-in-out infinite}"
        "@keyframes pulse{0%,100%{opacity:.8}50%{opacity:1}}"
        "@media (prefers-reduced-motion:reduce){.pulse{animation:none}}"
        "</style></defs>",
        f'<rect x="1" y="1" width="558" height="638" rx="14" fill="#0b0610" stroke="{VIOLET}" stroke-opacity=".55"/>',
        '<g class="pulse">' + sigil(500, 52, 0.32, extra='filter="url(#glow)"') + "</g>",
        f'<text x="40" y="44" class="mono" font-size="12" letter-spacing="4" fill="{CRIMSON}">GAME #{state["game"]} · ZERO REQUIEM</text>',
        f'<text x="40" y="76" class="serif" font-size="26" font-style="italic" fill="{PAPER}">{esc(status)}</text>',
        inner,
        f'<text x="40" y="612" class="mono" font-size="12" fill="{MUTED}">Zero {record["zero"]} · Challengers {record["challengers"]} · Draws {record["draws"]}</text>',
        f'<text x="520" y="612" text-anchor="end" class="mono" font-size="12" fill="{MUTED}">moves {len(state["moves"])}</text>',
        "</svg>",
    ])


def issue_link(title, label):
    body = "Just press **Submit new issue**. Zero answers in about a minute and the board in the profile updates."
    return f"[{label}](https://github.com/{REPO}/issues/new?title={quote(title)}&body={quote(body)})"


def readme_block(state):
    board = chess.Board(state["fen"])
    lines = [START, "", '<div align="center">', "", f'<img src="https://raw.githubusercontent.com/{REPO}/main/{BOARD}?game={state["game"]}&move={len(state["moves"])}" width="520" alt="Chess board"/>', "", "</div>", ""]

    if board.outcome() is not None:
        lines += ["**The game is over.** " + issue_link("chess|new", "⚔ Start a new game against Zero"), ""]
    else:
        lines += ["**You play White. Pick a move and Zero will answer.**", ""]
        groups = {}
        for move in board.legal_moves:
            piece = board.piece_at(move.from_square).piece_type
            if move.promotion not in (None, chess.QUEEN):
                continue
            groups.setdefault(piece, []).append(move)
        for piece in (chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING):
            moves = sorted(groups.get(piece, []), key=lambda move: board.san(move))
            if moves:
                links = " · ".join(issue_link(f"chess|move|{move.uci()}", board.san(move)) for move in moves)
                lines.append(f"**{PIECE_NAMES[piece]}** — {links}  ")
        lines.append("")

    if state["moves"]:
        recent = state["moves"][-6:]
        start = len(state["moves"]) - len(recent)
        shown = []
        for index, move in enumerate(recent, start):
            who = "Zero" if move["by"] == "Zero" else f"@{move['by']}"
            prefix = f"{index // 2 + 1}." if index % 2 == 0 else f"{index // 2 + 1}…"
            shown.append(f"`{prefix} {move['san']}` {who}")
        lines += ["<sub>Last moves: " + " · ".join(shown) + "</sub>", ""]

    top = sorted(state["players"].items(), key=lambda item: item[1], reverse=True)[:5]
    if top:
        lines += ["<sub>Knights of the board: " + " · ".join(f"@{name} ({count})" for name, count in top) + "</sub>", ""]

    lines.append(END)
    return "\n".join(lines)


def write_readme(state):
    with open(README, encoding="utf-8") as file:
        text = file.read()
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    with open(README, "w", encoding="utf-8") as file:
        file.write(head + readme_block(state) + tail)


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "render"
    author = os.environ.get("ISSUE_AUTHOR", "someone")
    state = load()
    reply = ""
    if command != "render":
        state, reply = play(state, command, author)
    save(state)
    with open(BOARD, "w", encoding="utf-8") as file:
        file.write(board_svg(state))
    write_readme(state)
    reply_file = os.environ.get("REPLY_FILE")
    if reply_file:
        with open(reply_file, "w", encoding="utf-8") as file:
            file.write(reply)
    print(reply)


if __name__ == "__main__":
    main()
