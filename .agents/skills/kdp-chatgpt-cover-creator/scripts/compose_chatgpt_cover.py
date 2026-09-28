#!/usr/bin/env python3
"""Compose a KDP full-wrap cover from ChatGPT-generated front/back artwork."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DecodedStreamObject, NameObject

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover - handled at runtime
    PdfReader = None


REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import config  # noqa: E402
from generate_cover import calculate_cover_dimensions  # noqa: E402


def parse_author(author_obj: object) -> str:
    if isinstance(author_obj, dict):
        return f"{author_obj.get('first_name', '')} {author_obj.get('last_name', '')}".strip()
    if isinstance(author_obj, str):
        return author_obj.strip()
    return ""


def load_plan(theme: str) -> dict:
    path = REPO_ROOT / config.get_plan_path(theme)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def interior_page_count(theme: str, fallback_images: bool = True) -> int:
    interior = REPO_ROOT / config.get_interior_pdf_path(theme)
    if interior.exists() and PdfReader is not None:
        return len(PdfReader(str(interior)).pages)

    if fallback_images:
        images_dir = REPO_ROOT / config.get_images_dir(theme)
        count = len(list(images_dir.glob("page_[0-9][0-9].png"))) if images_dir.exists() else 0
        if count:
            return 2 + (count * 2) + 1

    return config.COLORING_PAGES_PER_BOOK * 2 + 4


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            if Path(candidate).exists():
                return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    cx: float,
    y: float,
    fnt: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    stroke_fill: tuple[int, int, int] | None = None,
    stroke_width: int = 0,
) -> None:
    bbox = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke_width)
    width = bbox[2] - bbox[0]
    draw.text(
        (cx - width / 2, y),
        text,
        font=fnt,
        fill=fill,
        stroke_fill=stroke_fill,
        stroke_width=stroke_width,
    )


def wrap_to_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    fnt: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    """Word-wrap text using rendered width instead of character guesses."""
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        bbox = draw.textbbox((0, 0), candidate, font=fnt)
        if bbox[2] - bbox[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def add_front_text(front: Image.Image, dims: dict, args: argparse.Namespace, plan: dict) -> Image.Image:
    """Overlay exact metadata in code so image generation never has to spell it."""
    if args.no_front_text:
        return front

    title = args.front_title if args.front_title is not None else str(plan.get("title", ""))
    subtitle = args.front_subtitle if args.front_subtitle is not None else str(plan.get("subtitle", ""))
    author = args.front_author if args.front_author is not None else parse_author(plan.get("author"))
    if not any((title, subtitle, author)):
        return front

    front = front.convert("RGB")
    safe = dims["safe_px"]
    bleed = dims["bleed_px"]
    max_width = front.width - bleed - (2 * safe)
    center_x = (front.width - bleed) / 2

    title_lines: list[str] = []
    title_font = None
    title_size = 154
    if title:
        while title_size >= 84:
            title_font = font(title_size, True)
            title_lines = wrap_to_width(ImageDraw.Draw(front), title, title_font, max_width)
            if len(title_lines) <= 4:
                break
            title_size -= 8
    line_height = int(title_size * 1.05)
    subtitle_font = font(58, False) if subtitle else None
    subtitle_lines = (
        wrap_to_width(ImageDraw.Draw(front), subtitle, subtitle_font, max_width)
        if subtitle and subtitle_font is not None
        else []
    )

    # A restrained translucent panel preserves legibility at Amazon thumbnail size.
    overlay = Image.new("RGBA", front.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    panel_top = bleed + safe
    text_height = 70 + len(title_lines) * line_height
    if subtitle_lines:
        text_height += 25 + len(subtitle_lines) * 70
    text_height += 70
    # Size the panel to its actual copy so short titles do not create a large
    # empty card over the generated artwork.
    panel_bottom = min(front.height - bleed - safe, panel_top + max(420, text_height))
    od.rounded_rectangle(
        [safe // 2, panel_top, front.width - bleed - safe // 2, panel_bottom],
        radius=54,
        fill=(255, 250, 239, 222),
        outline=(255, 255, 255, 232),
        width=6,
    )
    front = Image.alpha_composite(front.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(front)

    if title:
        y = panel_top + 70
        for line in title_lines:
            draw_centered(draw, line, center_x, y, title_font, (45, 38, 62), (255, 255, 255), 5)
            y += line_height
    else:
        y = panel_top + 70

    if subtitle:
        y += 25
        for line in subtitle_lines:
            draw_centered(draw, line, center_x, y, subtitle_font, (70, 56, 78))
            y += 70

    if author:
        author_font = font(54, True)
        author_y = front.height - bleed - safe - 88
        bbox = draw.textbbox((0, 0), author, font=author_font)
        author_width = bbox[2] - bbox[0]
        draw.rounded_rectangle(
            [center_x - author_width / 2 - 34, author_y - 18, center_x + author_width / 2 + 34, author_y + 66],
            radius=30,
            fill=(255, 250, 239),
        )
        draw_centered(draw, author, center_x, author_y, author_font, (45, 38, 62))
    return front


def backup_existing(book_dir: Path, names: list[str], label: str) -> None:
    backup_dir = book_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = int(time.time())
    for name in names:
        path = book_dir / name
        if path.exists():
            backup = backup_dir / f"{path.stem}_backup_before_{label}_{stamp}{path.suffix}"
            shutil.copy2(path, backup)


def add_back_text(back: Image.Image, dims: dict, args: argparse.Namespace) -> Image.Image:
    if args.no_back_text:
        return back

    back = back.convert("RGB")
    draw = ImageDraw.Draw(back)
    back_center_x = dims["bleed_px"] + dims["trim_w_px"] // 2
    safe = dims["safe_px"]
    full_h = dims["full_height_px"]

    if args.headline:
        lines = [line.strip() for line in args.headline.split("|") if line.strip()]
        area_top = args.headline_y
        area_height = 110 + max(0, len(lines) - 1) * 95
        overlay = Image.new("RGBA", back.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle(
            [
                dims["bleed_px"] + safe // 2,
                area_top - 28,
                dims["spine_start_x"] - safe // 2,
                area_top + area_height,
            ],
            radius=48,
            fill=(255, 246, 215, 228),
            outline=(255, 160, 188, 210),
            width=7,
        )
        back = Image.alpha_composite(back.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(back)
        for index, line in enumerate(lines):
            size = 110 if index == 0 else 82
            draw_centered(
                draw,
                line,
                back_center_x,
                area_top + index * 95,
                font(size, True),
                (48, 42, 72),
                (255, 255, 255),
                8 if index == 0 else 7,
            )

    if args.back_blurb:
        blurb_font = font(48, False)
        blurb_width = dims["trim_w_px"] - 2 * safe
        lines = wrap_to_width(draw, args.back_blurb, blurb_font, blurb_width)
        line_height = 64
        top = round(full_h * 0.27)
        left = dims["bleed_px"] + safe * 0.72
        right = dims["spine_start_x"] - safe * 0.72
        bottom = top + len(lines) * line_height + 100
        overlay = Image.new("RGBA", back.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle(
            [left, top - 48, right, bottom],
            radius=42,
            fill=(255, 252, 238, 218),
            outline=(255, 255, 255, 226),
            width=5,
        )
        back = Image.alpha_composite(back.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(back)
        y = top
        for line in lines:
            draw_centered(draw, line, back_center_x, y, blurb_font, (60, 54, 66))
            y += line_height

    badge_x = args.badge_x if args.badge_x is not None else dims["bleed_px"] + safe
    badge_y = args.badge_y if args.badge_y is not None else full_h - dims["bleed_px"] - safe - 310

    if args.feature_line:
        fnt = font(args.feature_size, True)
        bbox = draw.textbbox((0, 0), args.feature_line, font=fnt)
        width = bbox[2] - bbox[0]
        x = badge_x
        y = badge_y - 72
        draw.rounded_rectangle(
            [x - 22, y - 14, x + width + 22, y + 52],
            radius=28,
            fill=(255, 252, 238),
            outline=(244, 158, 80),
            width=4,
        )
        draw.text((x, y), args.feature_line, font=fnt, fill=(70, 55, 82))

    if args.badge_top or args.badge_bottom:
        badge_w = args.badge_width
        badge_h = args.badge_height
        shadow = Image.new("RGBA", back.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle(
            [badge_x + 10, badge_y + 12, badge_x + badge_w + 10, badge_y + badge_h + 12],
            radius=24,
            fill=(80, 40, 60, 45),
        )
        back = Image.alpha_composite(back.convert("RGBA"), shadow).convert("RGB")
        draw = ImageDraw.Draw(back)
        draw.rounded_rectangle(
            [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
            radius=24,
            fill=(255, 255, 255),
            outline=(72, 161, 192),
            width=6,
        )
        if args.badge_top:
            draw_centered(draw, args.badge_top, badge_x + badge_w / 2, badge_y + 34, font(52, True), (42, 60, 90))
        if args.badge_bottom:
            draw_centered(draw, args.badge_bottom, badge_x + badge_w / 2, badge_y + 100, font(66, True), (196, 68, 124))

    return back


def draw_barcode_zone(cover: Image.Image, dims: dict, args: argparse.Namespace) -> tuple[int, int, int, int]:
    draw = ImageDraw.Draw(cover)
    barcode_w = round(args.barcode_width_in * config.DPI)
    barcode_h = round(args.barcode_height_in * config.DPI)
    barcode_x = dims["bleed_px"] + dims["trim_w_px"] - dims["safe_px"] - barcode_w
    barcode_y = dims["full_height_px"] - dims["bleed_px"] - dims["safe_px"] - barcode_h
    pad = 4
    draw.rounded_rectangle(
        [barcode_x - pad, barcode_y - pad, barcode_x + barcode_w + pad, barcode_y + barcode_h + pad],
        radius=8,
        fill=(255, 255, 255),
    )
    draw.rectangle(
        [barcode_x, barcode_y, barcode_x + barcode_w, barcode_y + barcode_h],
        fill=(255, 255, 255),
        outline=(205, 205, 205),
        width=2,
    )
    return barcode_x, barcode_y, barcode_w, barcode_h


def strip_unused_cover_font(pdf_path: Path) -> None:
    """Remove ReportLab's empty default-font operation from an image-only PDF."""
    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    for page in reader.pages:
        contents = page.get_contents()
        if contents is not None:
            data = contents.get_data().replace(b"BT /F1 12 Tf 14.4 TL ET", b"")
            stream = DecodedStreamObject()
            stream.set_data(data)
            page[NameObject("/Contents")] = stream
        resources = page.get("/Resources")
        if resources is not None:
            resources = resources.get_object()
            resources.pop(NameObject("/Font"), None)
            procset = resources.get("/ProcSet")
            if procset is not None:
                resources[NameObject("/ProcSet")] = ArrayObject(
                    item for item in procset if item != NameObject("/Text")
                )
        writer.add_page(page)
    with pdf_path.open("wb") as stream:
        writer.write(stream)


def compose(args: argparse.Namespace) -> None:
    forbidden_overlays = {
        "--headline": args.headline,
        "--feature-line": args.feature_line,
        "--badge-top": args.badge_top,
        "--badge-bottom": args.badge_bottom,
        "--front-title": args.front_title,
        "--front-subtitle": args.front_subtitle,
        "--front-author": args.front_author,
    }
    used = [name for name, value in forbidden_overlays.items() if value]
    if used or not args.no_back_text:
        details = f" Forbidden option(s): {', '.join(used)}." if used else ""
        raise SystemExit(
            "Cover typography must already be baked into the generated front/back artwork. "
            "Compose with --no-back-text; code text overlays are disabled." + details
        )

    theme = args.theme
    plan = load_plan(theme)
    page_size = args.size or plan.get("page_size") or config.DEFAULT_PAGE_SIZE
    if page_size not in config.PAGE_SIZES:
        raise SystemExit(f"Unsupported page size: {page_size}")

    trim = config.get_page_dims(page_size)
    manuscript_page_count = args.page_count or interior_page_count(theme)
    # KDP calculates an odd-page manuscript as the next even page count when
    # determining the spine and cover template dimensions.
    page_count = manuscript_page_count + (manuscript_page_count % 2)
    if args.kdp_width and args.kdp_height:
        spine_width = args.kdp_width - (2 * trim["width_inches"]) - (2 * 0.125)
        dims = calculate_cover_dimensions(page_count, trim_w=trim["width_inches"], trim_h=trim["height_inches"])
        dims["spine_width_inches"] = spine_width
        dims["full_width_inches"] = args.kdp_width
        dims["full_height_inches"] = args.kdp_height
        dims["spine_w_px"] = round(spine_width * config.DPI)
        dims["full_width_px"] = 2 * dims["bleed_px"] + 2 * dims["trim_w_px"] + dims["spine_w_px"]
        dims["full_height_px"] = 2 * dims["bleed_px"] + round(trim["height_inches"] * config.DPI)
        dims["spine_start_x"] = dims["bleed_px"] + dims["trim_w_px"]
        dims["front_start_x"] = dims["spine_start_x"] + dims["spine_w_px"]
    else:
        dims = calculate_cover_dimensions(page_count, trim_w=trim["width_inches"], trim_h=trim["height_inches"])

    book_dir = REPO_ROOT / config.get_book_dir(theme)
    book_dir.mkdir(parents=True, exist_ok=True)
    backup_existing(book_dir, ["cover.pdf", "cover.png", "front_artwork.png", "back_artwork.png"], "chatgpt_cover")

    front_src = Path(args.front).expanduser()
    back_src = Path(args.back).expanduser()
    if not front_src.is_absolute():
        front_src = REPO_ROOT / front_src
    if not back_src.is_absolute():
        back_src = REPO_ROOT / back_src
    if not front_src.exists():
        raise SystemExit(f"Front artwork not found: {front_src}")
    if not back_src.exists():
        raise SystemExit(f"Back artwork not found: {back_src}")

    front_dest = book_dir / "front_artwork.png"
    back_dest = book_dir / "back_artwork.png"
    if front_src.resolve() != front_dest.resolve():
        shutil.copy2(front_src, front_dest)
    if back_src.resolve() != back_dest.resolve():
        shutil.copy2(back_src, back_dest)

    full_w, full_h = dims["full_width_px"], dims["full_height_px"]
    back_w = dims["spine_start_x"]
    front_w = full_w - dims["front_start_x"]
    spine_w = dims["spine_w_px"]

    front = Image.open(front_src).convert("RGB").resize((front_w, full_h), Image.Resampling.LANCZOS)
    back = Image.open(back_src).convert("RGB").resize((back_w, full_h), Image.Resampling.LANCZOS)
    # Front typography is already baked into the generated image. Never add
    # title, subtitle, author, badges, or marketing copy in this composer.
    back = add_back_text(back, dims, args)

    cover = Image.new("RGB", (full_w, full_h), (255, 245, 249))
    cover.paste(back, (0, 0))

    left_edge = back.crop((back_w - 10, 0, back_w, full_h)).resize((spine_w, full_h), Image.Resampling.BICUBIC)
    right_edge = front.crop((0, 0, 10, full_h)).resize((spine_w, full_h), Image.Resampling.BICUBIC)
    spine = Image.blend(left_edge, right_edge, 0.45).filter(ImageFilter.GaussianBlur(radius=4))
    cover.paste(spine, (dims["spine_start_x"], 0))
    cover.paste(front, (dims["front_start_x"], 0))

    barcode_rect = draw_barcode_zone(cover, dims, args)

    png_path = book_dir / "cover.png"
    pdf_path = book_dir / "cover.pdf"
    cover.save(png_path, "PNG", dpi=(config.DPI, config.DPI), optimize=True)

    page_w_pt = dims["full_width_inches"] * 72
    page_h_pt = dims["full_height_inches"] * 72
    c = canvas.Canvas(str(pdf_path), pagesize=(page_w_pt, page_h_pt))
    c.drawImage(ImageReader(cover), 0, 0, width=page_w_pt, height=page_h_pt)
    c.save()
    strip_unused_cover_font(pdf_path)

    print(f"Cover PNG: {png_path.relative_to(REPO_ROOT)}")
    print(f"Cover PDF: {pdf_path.relative_to(REPO_ROOT)}")
    print(f"Manuscript pages: {manuscript_page_count}")
    print(f"KDP cover page count: {page_count}")
    print(f"Cover inches: {dims['full_width_inches']:.6f} x {dims['full_height_inches']:.3f}")
    print(f"Cover pixels: {full_w} x {full_h}")
    print(f"Barcode rect px: {barcode_rect}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--theme", required=True)
    parser.add_argument("--front", required=True, help="Path to selected ChatGPT-generated front artwork")
    parser.add_argument("--back", required=True, help="Path to selected ChatGPT-generated back artwork")
    parser.add_argument("--size", choices=config.PAGE_SIZES.keys(), default=None)
    parser.add_argument("--page-count", type=int, default=None)
    parser.add_argument("--kdp-width", type=float, default=None)
    parser.add_argument("--kdp-height", type=float, default=None)
    parser.add_argument("--headline", default="", help='Use "|" between lines, e.g. "A SUPER CUTE|COLORING ADVENTURE"')
    parser.add_argument("--headline-y", type=int, default=98)
    parser.add_argument("--back-blurb", default="", help="Short exact back-cover description")
    parser.add_argument("--feature-line", default="")
    parser.add_argument("--feature-size", type=int, default=42)
    parser.add_argument("--badge-top", default="")
    parser.add_argument("--badge-bottom", default="")
    parser.add_argument("--badge-x", type=int, default=None)
    parser.add_argument("--badge-y", type=int, default=None)
    parser.add_argument("--badge-width", type=int, default=760)
    parser.add_argument("--badge-height", type=int, default=210)
    parser.add_argument("--no-back-text", action="store_true")
    parser.add_argument("--front-title", default=None, help="Exact title; defaults to plan.json")
    parser.add_argument("--front-subtitle", default=None, help="Exact subtitle; defaults to plan.json")
    parser.add_argument("--front-author", default=None, help="Exact author; defaults to plan.json")
    parser.add_argument("--no-front-text", action="store_true")
    parser.add_argument("--barcode-width-in", type=float, default=2.0)
    parser.add_argument("--barcode-height-in", type=float, default=1.2)
    args = parser.parse_args()
    compose(args)


if __name__ == "__main__":
    main()
