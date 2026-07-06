#!/usr/bin/env python3
"""
Assemble the "Checkmate Made Simple" interior PDF from manuscript chapter JSON files.

Each chapter file (output/{theme}/manuscript/chapter_NN.json) follows the schema:
{
  "chapter_number": int,
  "chapter_title": str,
  "sections": [
    {
      "heading": str,               # "" for a lead-in section with no subheading
      "paragraphs": [str, ...],
      "bullets": [str, ...],        # optional
      "callout": {"label": str, "text": str},  # optional
      "diagram": {                   # optional
        "moves": [str, ...],         # SAN moves from the standard start position
        "setup": [{"square": str, "piece": str}, ...],  # OR explicit placement
        "start_fen": str,            # optional starting FEN override
        "highlight": [str, ...],
        "arrows": [[str, str], ...],
        "flipped": bool,
        "caption": str
      }
    }
  ]
}

Renders every diagram once (cached to disk by a content hash) and lays the
chapter out in a two-column book page, matching the style of well-known
beginner chess books: a full-width chapter-opening page, then two-column
body text with inline diagrams, callout boxes, and bullet lists.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, HRFlowable, NextPageTemplate,
    PageBreak, PageTemplate, Paragraph, Spacer,
)

import chess_diagram
import config

THEME_KEY = "chess_mastery_beginners"
FONT_DIR = "/System/Library/Fonts/Supplemental/"

INK = HexColor("#1A1A1A")
RULE = HexColor("#8A1F11")          # single accent color (prints as dark gray on B&W interior)
CALLOUT_BG = HexColor("#F0F0EC")
CALLOUT_BORDER = HexColor("#8A1F11")
MUTED = HexColor("#55524C")


def register_fonts():
    pdfmetrics.registerFont(TTFont("Georgia", FONT_DIR + "Georgia.ttf"))
    pdfmetrics.registerFont(TTFont("Georgia-Bold", FONT_DIR + "Georgia Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Georgia-Italic", FONT_DIR + "Georgia Italic.ttf"))
    pdfmetrics.registerFont(TTFont("Georgia-BoldItalic", FONT_DIR + "Georgia Bold Italic.ttf"))
    pdfmetrics.registerFont(TTFont("Arial", FONT_DIR + "Arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", FONT_DIR + "Arial Bold.ttf"))


def build_styles():
    return {
        "body": ParagraphStyle(
            "body", fontName="Georgia", fontSize=10.3, leading=15.2,
            alignment=TA_JUSTIFY, spaceAfter=8, textColor=INK,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName="Georgia", fontSize=10.3, leading=14.8,
            alignment=TA_LEFT, leftIndent=14, firstLineIndent=-14,
            spaceAfter=4, textColor=INK,
        ),
        "heading": ParagraphStyle(
            "heading", fontName="Georgia-Bold", fontSize=13.2, leading=16,
            alignment=TA_LEFT, spaceBefore=6, spaceAfter=8, textColor=RULE,
        ),
        "callout_label": ParagraphStyle(
            "callout_label", fontName="Arial-Bold", fontSize=8.6, leading=11,
            alignment=TA_LEFT, textColor=RULE, spaceAfter=2,
        ),
        "callout_text": ParagraphStyle(
            "callout_text", fontName="Georgia-Italic", fontSize=10, leading=13.6,
            alignment=TA_LEFT, textColor=INK,
        ),
        "caption": ParagraphStyle(
            "caption", fontName="Georgia-Italic", fontSize=8.9, leading=11.6,
            alignment=TA_CENTER, textColor=MUTED,
        ),
        "chapter_kicker": ParagraphStyle(
            "chapter_kicker", fontName="Arial-Bold", fontSize=12, leading=16,
            alignment=TA_CENTER, textColor=RULE, spaceAfter=10,
        ),
        "chapter_title": ParagraphStyle(
            "chapter_title", fontName="Georgia-Bold", fontSize=27, leading=32,
            alignment=TA_CENTER, textColor=INK, spaceAfter=4,
        ),
        "title_main": ParagraphStyle(
            "title_main", fontName="Georgia-Bold", fontSize=40, leading=46,
            alignment=TA_CENTER, textColor=INK,
        ),
        "title_sub": ParagraphStyle(
            "title_sub", fontName="Georgia-Italic", fontSize=16, leading=22,
            alignment=TA_CENTER, textColor=MUTED,
        ),
    }


NUMBER_WORDS = ["ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN",
                "EIGHT", "NINE", "TEN", "ELEVEN", "TWELVE", "THIRTEEN"]


class DiagramFlowable(Flowable):
    """A chess diagram image with a centered caption beneath it."""

    def __init__(self, img_path: str, caption: str, styles: dict, width_frac: float = 0.86):
        super().__init__()
        self.img_path = img_path
        self.caption_para = Paragraph(caption, styles["caption"]) if caption else None
        self.width_frac = width_frac

    def wrap(self, avail_width, avail_height):
        self._frame_w = avail_width
        self.img_size = avail_width * self.width_frac
        self.offset_x = (avail_width - self.img_size) / 2
        cap_h = 0
        if self.caption_para:
            _, cap_h = self.caption_para.wrap(avail_width, avail_height)
            cap_h += 5
        self._h = self.img_size + 6 + cap_h
        self._cap_h = cap_h
        return avail_width, self._h

    def draw(self):
        self.canv.drawImage(
            self.img_path, self.offset_x, self._cap_h + 6,
            width=self.img_size, height=self.img_size,
            preserveAspectRatio=True, mask="auto",
        )
        if self.caption_para:
            self.caption_para.drawOn(self.canv, 0, 0)


class CalloutFlowable(Flowable):
    """A shaded, bordered box for KEY TAKEAWAY / TIP / WARNING callouts."""

    PAD = 9

    def __init__(self, label: str, text: str, styles: dict):
        super().__init__()
        self.label_para = Paragraph(f"{label}", styles["callout_label"])
        self.text_para = Paragraph(text, styles["callout_text"])

    def wrap(self, avail_width, avail_height):
        inner_w = avail_width - 2 * self.PAD
        _, lh = self.label_para.wrap(inner_w, avail_height)
        _, th = self.text_para.wrap(inner_w, avail_height)
        self._w = avail_width
        self._h = lh + th + 2 * self.PAD + 4
        self._inner_w = inner_w
        return self._w, self._h

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(CALLOUT_BG)
        c.setStrokeColor(CALLOUT_BORDER)
        c.setLineWidth(1.1)
        c.roundRect(0, 0, self._w, self._h, 5, fill=1, stroke=1)
        c.restoreState()
        y = self._h - self.PAD
        _, lh = self.label_para.wrap(self._inner_w, self._h)
        y -= lh
        self.label_para.drawOn(c, self.PAD, y)
        y -= 4
        _, th = self.text_para.wrap(self._inner_w, self._h)
        y -= th
        self.text_para.drawOn(c, self.PAD, y)


def diagram_cache_path(theme_key: str, spec: dict) -> str:
    key = json.dumps(spec, sort_keys=True)
    digest = hashlib.sha1(key.encode()).hexdigest()[:16]
    return os.path.join(config.get_book_dir(theme_key), "diagrams", f"diag_{digest}.png")


def render_and_cache_diagram(theme_key: str, spec: dict) -> str:
    path = diagram_cache_path(theme_key, spec)
    if os.path.exists(path):
        return path
    kwargs = {}
    if "moves" in spec:
        kwargs["moves"] = spec["moves"]
    if "setup" in spec:
        kwargs["setup"] = [{"square": p["square"], "piece": p["piece"]} for p in spec["setup"]]
    if spec.get("start_fen"):
        kwargs["start_fen"] = spec["start_fen"]
    if spec.get("highlight"):
        kwargs["highlight"] = spec["highlight"]
    if spec.get("arrows"):
        kwargs["arrows"] = [tuple(a) for a in spec["arrows"]]
    if spec.get("flipped"):
        kwargs["flipped"] = spec["flipped"]
    chess_diagram.save_diagram(path, square_px=140, **kwargs)
    return path


def build_chapter_flowables(chapter: dict, styles: dict, theme_key: str, col_width: float) -> list:
    flow = [NextPageTemplate("chapter_open"), PageBreak()]
    num = chapter["chapter_number"]
    word = NUMBER_WORDS[num] if num < len(NUMBER_WORDS) else str(num)
    flow.append(Spacer(1, 1.6 * inch))
    flow.append(Paragraph(f"C H A P T E R&nbsp;&nbsp;{word}", styles["chapter_kicker"]))
    flow.append(HRFlowable(width="30%", thickness=1.2, color=RULE, spaceAfter=14, hAlign="CENTER"))
    flow.append(Paragraph(chapter["chapter_title"], styles["chapter_title"]))
    flow.append(HRFlowable(width="16%", thickness=0.8, color=RULE, spaceBefore=10, hAlign="CENTER"))
    flow.append(NextPageTemplate("twocol"))
    flow.append(PageBreak())

    for section in chapter["sections"]:
        heading = section.get("heading", "")
        if heading:
            flow.append(Paragraph(heading, styles["heading"]))
            flow.append(HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=8))
        for para in section.get("paragraphs", []):
            flow.append(Paragraph(para, styles["body"]))
        bullets = section.get("bullets", [])
        if bullets:
            for b in bullets:
                flow.append(Paragraph(f"•&nbsp;&nbsp;{b}", styles["bullet"]))
            flow.append(Spacer(1, 6))
        diagram = section.get("diagram")
        if diagram:
            img_path = render_and_cache_diagram(theme_key, diagram)
            flow.append(Spacer(1, 4))
            flow.append(DiagramFlowable(img_path, diagram.get("caption", ""), styles))
            flow.append(Spacer(1, 8))
        callout = section.get("callout")
        if callout:
            flow.append(Spacer(1, 3))
            flow.append(CalloutFlowable(callout["label"], callout["text"], styles))
            flow.append(Spacer(1, 10))
    return flow


def _footer(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFont("Georgia", 8.5)
    canvas_obj.setFillColor(MUTED)
    page_num = canvas_obj.getPageNumber()
    canvas_obj.drawCentredString(doc.pagesize[0] / 2, 0.5 * inch, str(page_num))
    canvas_obj.restoreState()


def build_pdf(chapter_files: list[str], out_path: str, title: str, subtitle: str, author: str):
    register_fonts()
    styles = build_styles()

    page_w, page_h = letter
    margin = 0.75 * inch
    col_gap = 0.32 * inch
    top_margin = 0.85 * inch
    bottom_margin = 0.85 * inch
    col_width = (page_w - 2 * margin - col_gap) / 2

    doc = BaseDocTemplate(out_path, pagesize=letter,
                           topMargin=top_margin, bottomMargin=bottom_margin,
                           leftMargin=margin, rightMargin=margin)

    onecol_frame = Frame(margin, bottom_margin, page_w - 2 * margin, page_h - top_margin - bottom_margin,
                          id="onecol", topPadding=0, bottomPadding=0)
    chapter_open_frame = Frame(margin, bottom_margin, page_w - 2 * margin, page_h - top_margin - bottom_margin,
                                id="chapter_open", topPadding=0, bottomPadding=0)
    left_frame = Frame(margin, bottom_margin, col_width, page_h - top_margin - bottom_margin,
                        id="left", topPadding=0, bottomPadding=0)
    right_frame = Frame(margin + col_width + col_gap, bottom_margin, col_width,
                         page_h - top_margin - bottom_margin, id="right", topPadding=0, bottomPadding=0)

    doc.addPageTemplates([
        PageTemplate(id="onecol", frames=[onecol_frame], onPage=_footer),
        PageTemplate(id="chapter_open", frames=[chapter_open_frame], onPage=_footer),
        PageTemplate(id="twocol", frames=[left_frame, right_frame], onPage=_footer),
    ])

    story = []
    # --- Title page ---
    story.append(Spacer(1, 2.3 * inch))
    story.append(Paragraph(title, styles["title_main"]))
    story.append(Spacer(1, 14))
    story.append(Paragraph(subtitle, styles["title_sub"]))
    story.append(Spacer(1, 40))
    if author:
        story.append(Paragraph(f"by {author}", ParagraphStyle(
            "author", fontName="Georgia", fontSize=13, alignment=TA_CENTER, textColor=MUTED)))

    for cf in chapter_files:
        with open(cf) as f:
            chapter = json.load(f)
        story.extend(build_chapter_flowables(chapter, styles, THEME_KEY, col_width))

    doc.build(story)
    print(f"Built {out_path} ({doc.page} pages)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapters", nargs="*", default=None,
                         help="Specific chapter JSON files (default: all in manuscript/)")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    book_dir = config.get_book_dir(THEME_KEY)
    manuscript_dir = os.path.join(book_dir, "manuscript")
    if args.chapters:
        chapter_files = args.chapters
    else:
        chapter_files = sorted(glob.glob(os.path.join(manuscript_dir, "chapter_*.json")))

    out_path = args.out or os.path.join(book_dir, "interior_draft.pdf")
    build_pdf(
        chapter_files,
        out_path,
        title="Checkmate Made Simple",
        subtitle="The Beginner's Guide to Chess Openings, Tactics, and Winning Strategies",
        author=config.DEFAULT_AUTHOR,
    )


if __name__ == "__main__":
    main()
