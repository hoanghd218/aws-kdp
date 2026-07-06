"""
Deterministic chess board diagram renderer for the chess strategy book interior.

No AI image generation involved — diagrams are drawn programmatically from an
actual chess position, so they are always legal and reproducible. A position is
specified one of two ways:

  - moves: a list of SAN moves replayed from the standard start position (or an
    optional starting FEN) via python-chess, which raises on any illegal move.
    This is the preferred way to build a diagram — it guarantees the position
    is reachable and legal.
  - setup: an explicit list of {"square": "e4", "piece": "wK"} placements for
    positions (mostly bare endgame studies) that aren't naturally reachable in
    a short move sequence. Not legality-checked beyond "no two pieces share a
    square" and "at most one king per side".

Piece glyphs come from Apple Symbols.ttf (U+2654-265F), which renders classic
outline-for-white / solid-for-black chess figurines — no network call needed.
"""
from __future__ import annotations

import os

import chess
from PIL import Image, ImageDraw, ImageFont

PIECE_FONT_PATH = "/System/Library/Fonts/Apple Symbols.ttf"

# python-chess piece symbol -> Apple Symbols glyph (white outline / black solid)
_GLYPHS = {
    "K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙",
    "k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟",
}

# Grayscale-friendly board colors (prints cleanly on KDP black-and-white interior)
LIGHT_SQUARE = (245, 245, 240)
DARK_SQUARE = (176, 176, 176)
LINE_COLOR = (20, 20, 20)
HIGHLIGHT_COLOR = (40, 40, 40)


class DiagramError(ValueError):
    """Raised when a diagram spec (moves or setup) can't be resolved to a position."""


def board_from_spec(moves: list[str] | None = None, setup: list[dict] | None = None,
                     start_fen: str | None = None) -> chess.Board:
    """Resolve a diagram spec into a chess.Board. Exactly one of moves/setup should be given."""
    if moves is not None:
        board = chess.Board(start_fen) if start_fen else chess.Board()
        for i, san in enumerate(moves):
            clean_san = san.rstrip("!?")  # strip annotation suffixes like "??" or "!!"
            try:
                board.push_san(clean_san)
            except (ValueError, chess.IllegalMoveError, chess.InvalidMoveError) as e:
                raise DiagramError(
                    f"Illegal/invalid move {i + 1} ({san!r}) from position "
                    f"{board.fen()!r}: {e}"
                ) from e
        return board

    if setup is not None:
        board = chess.Board(None)
        board.clear()
        seen_squares = set()
        king_counts = {"w": 0, "k": 0}  # white/black king count (lowercased piece for black)
        for item in setup:
            sq_name = item["square"]
            piece_str = item["piece"]  # e.g. "wK", "bP"
            if sq_name in seen_squares:
                raise DiagramError(f"Two pieces placed on the same square: {sq_name}")
            seen_squares.add(sq_name)
            try:
                square = chess.parse_square(sq_name)
            except ValueError as e:
                raise DiagramError(f"Bad square name {sq_name!r}: {e}") from e
            color_char, kind_char = piece_str[0].lower(), piece_str[1].lower()
            piece_type = {"p": chess.PAWN, "n": chess.KNIGHT, "b": chess.BISHOP,
                          "r": chess.ROOK, "q": chess.QUEEN, "k": chess.KING}[kind_char]
            color = chess.WHITE if color_char == "w" else chess.BLACK
            if piece_type == chess.KING:
                key = "w" if color == chess.WHITE else "k"
                king_counts[key] += 1
                if king_counts[key] > 1:
                    raise DiagramError(f"More than one {'white' if color else 'black'} king in setup")
            board.set_piece_at(square, chess.Piece(piece_type, color))
        return board

    raise DiagramError("Diagram spec needs either 'moves' or 'setup'")


def render_diagram(
    moves: list[str] | None = None,
    setup: list[dict] | None = None,
    start_fen: str | None = None,
    highlight: list[str] | None = None,
    arrows: list[tuple[str, str]] | None = None,
    flipped: bool = False,
    square_px: int = 110,
    label_squares: bool = True,
) -> tuple[Image.Image, str]:
    """Render a board position to a PIL Image. Returns (image, resolved_fen)."""
    board = board_from_spec(moves=moves, setup=setup, start_fen=start_fen)
    fen = board.fen()

    margin = int(square_px * 0.32) if label_squares else 0
    board_px = square_px * 8
    total = board_px + margin
    img = Image.new("RGB", (total, total), "white")
    draw = ImageDraw.Draw(img)

    piece_font = ImageFont.truetype(PIECE_FONT_PATH, int(square_px * 0.82))
    label_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", int(square_px * 0.22))

    def square_to_xy(square: int) -> tuple[int, int]:
        file_idx = chess.square_file(square)  # 0=a..7=h
        rank_idx = chess.square_rank(square)   # 0=1..7=8
        col = file_idx if not flipped else 7 - file_idx
        row = 7 - rank_idx if not flipped else rank_idx
        x = margin + col * square_px
        y = row * square_px
        return x, y

    # Squares
    for square in chess.SQUARES:
        x, y = square_to_xy(square)
        is_light = (chess.square_file(square) + chess.square_rank(square)) % 2 == 1
        color = LIGHT_SQUARE if is_light else DARK_SQUARE
        draw.rectangle([x, y, x + square_px, y + square_px], fill=color)

    # Highlights (bordered box, grayscale-safe)
    if highlight:
        for sq_name in highlight:
            square = chess.parse_square(sq_name)
            x, y = square_to_xy(square)
            for w in range(4):
                draw.rectangle([x + w, y + w, x + square_px - w, y + square_px - w], outline=HIGHLIGHT_COLOR)

    # Pieces
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue
        x, y = square_to_xy(square)
        glyph = _GLYPHS[piece.symbol()]
        bbox = draw.textbbox((0, 0), glyph, font=piece_font)
        gw, gh = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = x + (square_px - gw) / 2 - bbox[0]
        ty = y + (square_px - gh) / 2 - bbox[1]
        draw.text((tx, ty), glyph, font=piece_font, fill=LINE_COLOR)

    # Arrows (last-move / plan indicators)
    if arrows:
        for frm, to in arrows:
            fsq, tsq = chess.parse_square(frm), chess.parse_square(to)
            fx, fy = square_to_xy(fsq)
            tx_, ty_ = square_to_xy(tsq)
            cx1, cy1 = fx + square_px / 2, fy + square_px / 2
            cx2, cy2 = tx_ + square_px / 2, ty_ + square_px / 2
            _draw_arrow(draw, cx1, cy1, cx2, cy2, width=max(4, square_px // 14))

    # Border around the board
    draw.rectangle([margin, 0, margin + board_px - 1, board_px - 1], outline=LINE_COLOR, width=3)

    # Coordinate labels
    if label_squares:
        files = "abcdefgh" if not flipped else "hgfedcba"
        ranks = "87654321" if not flipped else "12345678"
        for i, f in enumerate(files):
            cx = margin + i * square_px + square_px / 2
            draw.text((cx, board_px + 4), f, font=label_font, fill=LINE_COLOR, anchor="ma")
        for i, r in enumerate(ranks):
            cy = i * square_px + square_px / 2
            draw.text((margin - 6, cy), r, font=label_font, fill=LINE_COLOR, anchor="rm")

    return img, fen


def _draw_arrow(draw: ImageDraw.ImageDraw, x1, y1, x2, y2, width: int = 8):
    """Draw a solid arrow from (x1,y1) to (x2,y2), shortened at both ends so it
    doesn't cover the piece glyphs, with a filled triangular head."""
    import math
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 1:
        return
    ux, uy = dx / length, dy / length
    shrink_start = length * 0.32
    shrink_end = length * 0.30
    sx, sy = x1 + ux * shrink_start, y1 + uy * shrink_start
    ex, ey = x2 - ux * shrink_end, y2 - uy * shrink_end
    draw.line([sx, sy, ex, ey], fill=LINE_COLOR, width=width)
    head_len = width * 3.2
    head_w = width * 2.0
    px, py = -uy, ux
    hx, hy = ex, ey
    bx, by = hx - ux * head_len, hy - uy * head_len
    left = (bx + px * head_w, by + py * head_w)
    right = (bx - px * head_w, by - py * head_w)
    draw.polygon([(hx, hy), left, right], fill=LINE_COLOR)


def save_diagram(out_path: str, **kwargs) -> str:
    """Render and save a diagram PNG at 300 DPI. Returns the resolved FEN."""
    img, fen = render_diagram(**kwargs)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, dpi=(300, 300))
    return fen


if __name__ == "__main__":
    # Smoke test: starting position, a short opening, and an endgame setup.
    out_dir = "/private/tmp/claude-501/-Users-tonyhoang-Documents-GitHub-aws-kdp/796efcd5-659f-4603-a592-594465bd3a0c/scratchpad/diagrams"
    fen1 = save_diagram(f"{out_dir}/start.png", moves=[])
    print("start:", fen1)

    fen2 = save_diagram(
        f"{out_dir}/scholars_mate.png",
        moves=["e4", "e5", "Bc4", "Nc6", "Qh5", "Nf6??", "Qxf7#"],
        arrows=[("h5", "f7")],
    )
    print("scholars mate:", fen2)

    fen3 = save_diagram(
        f"{out_dir}/krk.png",
        setup=[
            {"square": "e1", "piece": "wK"},
            {"square": "a1", "piece": "wR"},
            {"square": "e8", "piece": "bK"},
        ],
        highlight=["a1"],
    )
    print("krk:", fen3)

    fen4 = save_diagram(
        f"{out_dir}/center_control.png",
        moves=["e4"],
        highlight=["d4", "e4", "d5", "e5"],
    )
    print("center control:", fen4)
