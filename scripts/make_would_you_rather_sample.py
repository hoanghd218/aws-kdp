"""Generate a single-page 'Would You Rather' card-style PDF sample.

Mimics the Amazon 'Would You Rather' family card game look:
- Bright yellow background
- White rounded card with double orange border
- "Would you rather" header (italic)
- Two bold options separated by "or", auto-wrapped and auto-scaled to fit
- Category tag at the bottom
"""
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent.parent / "output" / "would_you_rather_sample.pdf"

PAGE_W = 8.5 * inch
PAGE_H = 8.5 * inch

BG_YELLOW = HexColor("#FFD23F")
CARD_WHITE = HexColor("#FFFFFF")
BORDER_ORANGE = HexColor("#F58634")
TEXT_BLACK = HexColor("#111111")


def wrap_text(text: str, font: str, size: float, max_width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for w in words:
        candidate = f"{current} {w}".strip()
        if stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def fit_lines(text: str, font: str, max_size: float, min_size: float, max_width: float) -> tuple[list[str], float]:
    """Return (lines, font_size) that fit the text into max_width, shrinking if needed."""
    size = max_size
    while size >= min_size:
        lines = wrap_text(text, font, size, max_width)
        if all(stringWidth(l, font, size) <= max_width for l in lines):
            return lines, size
        size -= 1
    return wrap_text(text, font, min_size, max_width), min_size


def draw_card(
    c: canvas.Canvas,
    question_top: str,
    question_bottom: str,
    category: str,
) -> None:
    c.setFillColor(BG_YELLOW)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    outer_margin = 0.6 * inch
    card_x = outer_margin
    card_y = outer_margin
    card_w = PAGE_W - 2 * outer_margin
    card_h = PAGE_H - 2 * outer_margin
    radius = 0.45 * inch

    c.setFillColor(CARD_WHITE)
    c.roundRect(card_x, card_y, card_w, card_h, radius, fill=1, stroke=0)

    border_inset = 0.22 * inch
    c.setStrokeColor(BORDER_ORANGE)
    c.setLineWidth(5)
    c.roundRect(
        card_x + border_inset,
        card_y + border_inset,
        card_w - 2 * border_inset,
        card_h - 2 * border_inset,
        radius * 0.75,
        fill=0,
        stroke=1,
    )

    cx = card_x + card_w / 2
    text_pad = 0.9 * inch
    text_max_width = card_w - 2 * text_pad

    c.setFillColor(TEXT_BLACK)
    header_size = 22
    c.setFont("Helvetica-Oblique", header_size)
    c.drawCentredString(cx, card_y + card_h - 1.6 * inch, "Would you rather")

    question_font = "Helvetica-BoldOblique"
    or_font = "Helvetica-Bold"

    top_lines, top_size = fit_lines(question_top, question_font, 30, 18, text_max_width)
    bot_lines, bot_size = fit_lines(question_bottom, question_font, 30, 18, text_max_width)
    q_size = min(top_size, bot_size)
    top_lines = wrap_text(question_top, question_font, q_size, text_max_width)
    bot_lines = wrap_text(question_bottom, question_font, q_size, text_max_width)

    or_size = 26
    line_gap = q_size * 1.25

    block_top = card_y + card_h - 2.6 * inch
    y = block_top
    for line in top_lines:
        c.setFont(question_font, q_size)
        c.drawCentredString(cx, y, line)
        y -= line_gap

    y -= or_size * 0.3
    c.setFont(or_font, or_size)
    c.drawCentredString(cx, y, "or")
    y -= or_size * 1.3

    for line in bot_lines:
        c.setFont(question_font, q_size)
        c.drawCentredString(cx, y, line)
        y -= line_gap

    c.setFillColor(BORDER_ORANGE)
    c.setFont("Helvetica-Bold", 15)
    tracked = "   ".join(list(category.upper()))
    c.drawCentredString(cx, card_y + 0.75 * inch, tracked)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=(PAGE_W, PAGE_H))
    draw_card(
        c,
        question_top="communicate with extraterrestrials",
        question_bottom="animals?",
        category="Mad Scientist",
    )
    c.showPage()
    c.save()
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
