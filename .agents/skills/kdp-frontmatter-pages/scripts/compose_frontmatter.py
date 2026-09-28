#!/usr/bin/env python3
"""Compose exact front/back-matter text over imagegen artwork.

Image generation supplies decorative artwork only. This script owns every word,
which prevents misspellings and turns generic filler into book-specific copy.
"""

from __future__ import annotations

import argparse
import datetime
import json
import shutil
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import config  # noqa: E402


def load_plan(theme: str) -> dict:
    path = REPO_ROOT / config.get_plan_path(theme)
    if not path.exists():
        raise SystemExit(f"Plan not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def parse_author(value: object) -> str:
    if isinstance(value, dict):
        return f"{value.get('first_name', '')} {value.get('last_name', '')}".strip()
    return str(value or "").strip()


def font(size: int, bold: bool = False, italic: bool = False) -> ImageFont.FreeTypeFont:
    if bold:
        candidates = (
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        )
    elif italic:
        candidates = (
            "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        )
    else:
        candidates = (
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        )
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def prepare_art(path: Path, target: tuple[int, int]) -> Image.Image:
    if not path.exists():
        raise SystemExit(f"Artwork not found: {path}")
    with Image.open(path) as raw:
        art = ImageOps.exif_transpose(raw)
        art = ImageOps.grayscale(art)
        art = ImageOps.autocontrast(art, cutoff=1)
        art = ImageEnhance.Contrast(art).enhance(1.12)
        contained = ImageOps.contain(art, target, Image.Resampling.LANCZOS)
    page = Image.new("L", target, 255)
    page.paste(contained, ((target[0] - contained.width) // 2, (target[1] - contained.height) // 2))
    return page.convert("RGB")


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in str(text or "").splitlines() or [""]:
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            bbox = draw.textbbox((0, 0), candidate, font=fnt)
            if bbox[2] - bbox[0] <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def center(draw: ImageDraw.ImageDraw, text: str, cx: float, y: float, fnt: ImageFont.FreeTypeFont, fill=(28, 28, 28)) -> None:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    draw.text((cx - (bbox[2] - bbox[0]) / 2, y), text, font=fnt, fill=fill)


def text_panel(page: Image.Image, box: tuple[int, int, int, int]) -> ImageDraw.ImageDraw:
    overlay = Image.new("RGBA", page.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle(box, radius=52, fill=(255, 255, 255, 232), outline=(90, 90, 90, 130), width=4)
    page.paste(Image.alpha_composite(page.convert("RGBA"), overlay).convert("RGB"))
    return ImageDraw.Draw(page)


def title_page(art: Image.Image, plan: dict, copy: dict) -> Image.Image:
    page = art.copy()
    w, h = page.size
    margin = int(w * 0.09)
    draw = text_panel(page, (margin, int(h * 0.16), w - margin, int(h * 0.78)))
    cx = w / 2
    max_width = w - 2 * margin - 120
    kicker = copy.get("title_kicker") or ("A COLORING ESCAPE FOR ADULTS" if plan.get("audience") == "adults" else "A COLORING ADVENTURE")
    center(draw, kicker.upper(), cx, int(h * 0.21), font(int(w * 0.035), True), (82, 82, 82))

    title = str(plan.get("title", "")).strip()
    title_size = int(w * 0.060)
    while title_size >= int(w * 0.045):
        title_font = font(title_size, True)
        title_lines = wrap(draw, title, title_font, max_width)
        if len(title_lines) <= 4:
            break
        title_size -= 8
    y = int(h * 0.28)
    for line in title_lines:
        center(draw, line, cx, y, title_font)
        y += int(title_size * 1.12)

    subtitle = str(plan.get("subtitle", "")).strip()
    if subtitle:
        y += 28
        sub_font = font(int(w * 0.029))
        for line in wrap(draw, subtitle, sub_font, max_width):
            center(draw, line, cx, y, sub_font, (58, 58, 58))
            y += int(w * 0.038)

    author = parse_author(plan.get("author"))
    if author:
        author_y = min(int(h * 0.72), y + int(h * 0.018))
        center(draw, f"by {author}", cx, author_y, font(int(w * 0.034), True))
    return page


def belongs_page(art: Image.Image, copy: dict) -> Image.Image:
    page = art.copy()
    w, h = page.size
    margin = int(w * 0.10)
    draw = text_panel(page, (margin, int(h * 0.12), w - margin, int(h * 0.66)))
    heading = copy.get("ownership_heading") or "THIS BOOK BELONGS TO"
    # Ownership copy is deterministic code-rendered text.  Keep the complete
    # heading inside the panel even when a plan uses a longer kid-specific
    # phrase such as “THIS SPACE BOOK BELONGS TO”.
    heading_max_width = w - 2 * margin - 120
    heading_size = int(w * 0.055)
    while heading_size > int(w * 0.032):
        heading_font = font(heading_size, True)
        bbox = draw.textbbox((0, 0), heading, font=heading_font)
        if bbox[2] - bbox[0] <= heading_max_width:
            break
        heading_size -= 4
    else:
        heading_font = font(int(w * 0.032), True)
    heading_lines = wrap(draw, heading, heading_font, heading_max_width)
    heading_y = int(h * 0.18)
    for line in heading_lines:
        center(draw, line, w / 2, heading_y, heading_font)
        heading_y += int(heading_size * 1.12)
    line_left, line_right = int(w * 0.22), int(w * 0.78)
    for y in (int(h * 0.37), int(h * 0.49)):
        draw.line((line_left, y, line_right, y), fill=(40, 40, 40), width=max(4, w // 600))
    center(draw, "NAME", w / 2, int(h * 0.32), font(int(w * 0.026), True), (95, 95, 95))
    center(draw, "FAVORITE COLOR", w / 2, int(h * 0.44), font(int(w * 0.026), True), (95, 95, 95))
    return page


def copyright_page(art: Image.Image, plan: dict, copy: dict) -> Image.Image:
    page = art.copy()
    w, h = page.size
    margin = int(w * 0.10)
    draw = text_panel(page, (margin, int(h * 0.08), w - margin, int(h * 0.82)))
    cx = w / 2
    max_width = int(w * 0.66)
    kicker = copy.get("copyright_kicker") or "WELCOME TO YOUR GARDEN ESCAPE"
    heading = copy.get("copyright_heading") or "A NOTE BEFORE YOU BEGIN"
    message = copy.get("copyright_message") or (
        "These single-sided scenes were created for calm, unhurried coloring. "
        "Choose the tools and colors that feel good today, and enjoy each garden moment at your own pace."
    )

    center(draw, kicker.upper(), cx, int(h * 0.13), font(int(w * 0.029), True), (88, 88, 88))
    center(draw, heading.upper(), cx, int(h * 0.19), font(int(w * 0.052), True))

    body_font = font(int(w * 0.030))
    y = int(h * 0.29)
    for line in wrap(draw, message, body_font, max_width):
        center(draw, line, cx, y, body_font, (52, 52, 52))
        y += int(w * 0.045)

    rule_y = max(int(h * 0.49), y + int(h * 0.018))
    draw.line((int(w * 0.28), rule_y, int(w * 0.72), rule_y), fill=(115, 115, 115), width=3)

    author = parse_author(plan.get("author")) or config.DEFAULT_AUTHOR
    year = datetime.datetime.now().year
    legal_lines = [
        f"Copyright © {year} {author}. All rights reserved.",
        "For personal use only. Not for resale.",
        "No part of this book may be reproduced or distributed",
        "without written permission from the copyright owner.",
    ]
    legal_font = font(int(w * 0.025))
    y = rule_y + int(h * 0.035)
    for line in legal_lines:
        center(draw, line, cx, y, legal_font, (72, 72, 72))
        y += int(w * 0.037)
    return page


def instructions_page(art: Image.Image, copy: dict) -> Image.Image:
    page = art.copy()
    w, h = page.size
    margin = int(w * 0.115)
    draw = text_panel(page, (margin, int(h * 0.07), w - margin, int(h * 0.92)))
    kicker = copy.get("instructions_kicker") or "A SIMPLE, RELAXING WAY TO COLOR"
    heading = copy.get("instructions_heading") or "HOW TO ENJOY THIS BOOK"
    steps = copy.get("instructions_steps") or [
        {"title": "CHOOSE YOUR FAVORITES", "body": "Colored pencils, crayons, gel pens, or markers all work. Use what feels comfortable."},
        {"title": "PROTECT THE NEXT PAGE", "body": "Slip a spare sheet of paper behind the page before using markers or wet media."},
        {"title": "BUILD COLOR GENTLY", "body": "Start with light layers, then deepen shadows and details at your own pace."},
        {"title": "MAKE THE GARDEN YOURS", "body": "Realistic greens are optional. Choose any palette that makes the scene feel like home."},
    ]
    steps = [step for step in steps if isinstance(step, dict)][:4]
    cx = w / 2
    center(draw, kicker.upper(), cx, int(h * 0.115), font(int(w * 0.027), True), (88, 88, 88))
    heading_text = heading.upper()
    heading_size = int(w * 0.050)
    heading_font = font(heading_size, True)
    max_heading_width = int(w * 0.76)
    while heading_size > int(w * 0.030):
        bbox = draw.textbbox((0, 0), heading_text, font=heading_font)
        if bbox[2] - bbox[0] <= max_heading_width:
            break
        heading_size -= 4
        heading_font = font(heading_size, True)
    center(draw, heading_text, cx, int(h * 0.17), heading_font)
    draw.line((int(w * 0.29), int(h * 0.245), int(w * 0.71), int(h * 0.245)), fill=(110, 110, 110), width=3)

    row_y = [0.285, 0.435, 0.585, 0.735]
    circle_x = int(w * 0.205)
    text_x = int(w * 0.275)
    text_width = int(w * 0.50)
    for index, (step, y_ratio) in enumerate(zip(steps, row_y), start=1):
        y = int(h * y_ratio)
        radius = int(w * 0.024)
        draw.ellipse((circle_x - radius, y - radius, circle_x + radius, y + radius), outline=(55, 55, 55), width=4)
        number_font = font(int(w * 0.027), True)
        bbox = draw.textbbox((0, 0), str(index), font=number_font)
        draw.text((circle_x - (bbox[2] - bbox[0]) / 2, y - (bbox[3] - bbox[1]) / 2 - bbox[1]), str(index), font=number_font, fill=(35, 35, 35))

        title_font = font(int(w * 0.028), True)
        body_font = font(int(w * 0.023))
        draw.text((text_x, y - int(w * 0.035)), str(step.get("title", "")).upper(), font=title_font, fill=(30, 30, 30))
        body_y = y + int(w * 0.006)
        for line in wrap(draw, str(step.get("body", "")), body_font, text_width):
            draw.text((text_x, body_y), line, font=body_font, fill=(64, 64, 64))
            body_y += int(w * 0.032)

    footer = copy.get("instructions_footer") or "Take your time. There is no wrong way to color a quiet garden moment."
    footer_font = font(int(w * 0.024), italic=True)
    for line_index, line in enumerate(wrap(draw, footer, footer_font, int(w * 0.63))):
        center(draw, line, cx, int(h * 0.865) + line_index * int(w * 0.032), footer_font, (78, 78, 78))
    return page


def closing_page(art: Image.Image, plan: dict, copy: dict) -> Image.Image:
    page = art.copy()
    w, h = page.size
    margin = int(w * 0.08)
    draw = text_panel(page, (margin, int(h * 0.12), w - margin, int(h * 0.84)))
    adult = plan.get("audience") == "adults"
    heading = copy.get("closing_heading") or ("A QUIET MOMENT, BEAUTIFULLY YOURS" if adult else "YOU MADE THESE PAGES YOUR OWN!")
    concept = str(plan.get("concept") or "this coloring adventure").strip()
    message = copy.get("closing_message") or (
        f"Thank you for spending time with {concept}. May the colors you chose and the calm you found stay with you beyond these pages."
        if adult else
        f"Every color, scribble, and bright idea turned these {concept} pages into something only you could create. Keep imagining, keep coloring, and be proud of what you made."
    )
    review = copy.get("review_request") or (
        "If you enjoyed the experience, an honest Amazon review helps fellow colorists discover the book."
        if adult else
        "Grown-ups: if this book brought a happy coloring moment, an honest Amazon review helps other families discover it."
    )

    cx = w / 2
    heading_font = font(int(w * 0.055), True)
    y = int(h * 0.19)
    for line in wrap(draw, heading, heading_font, int(w * 0.72)):
        center(draw, line, cx, y, heading_font)
        y += int(w * 0.068)
    y += int(h * 0.05)
    body_font = font(int(w * 0.034))
    for line in wrap(draw, message, body_font, int(w * 0.69)):
        center(draw, line, cx, y, body_font, (50, 50, 50))
        y += int(w * 0.048)

    rule_y = int(h * 0.67)
    draw.line((int(w * 0.28), rule_y, int(w * 0.72), rule_y), fill=(110, 110, 110), width=3)
    review_font = font(int(w * 0.028), italic=True)
    y = rule_y + int(h * 0.035)
    for line in wrap(draw, review, review_font, int(w * 0.66)):
        center(draw, line, cx, y, review_font, (75, 75, 75))
        y += int(w * 0.041)
    return page


def save(page: Image.Image, path: Path, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise SystemExit(f"Output exists (use --overwrite): {path}")
    if path.exists():
        backup = path.parent / "backups"
        backup.mkdir(exist_ok=True)
        shutil.copy2(path, backup / f"{path.stem}_{int(time.time())}{path.suffix}")
    page.save(path, "PNG", dpi=(config.DPI, config.DPI), optimize=True)
    print(f"Saved: {path.relative_to(REPO_ROOT)}")


def resolve_art(value: str | None, default: Path) -> Path:
    path = Path(value).expanduser() if value else default
    return path if path.is_absolute() else REPO_ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("theme")
    parser.add_argument("--title-art", default=None)
    parser.add_argument("--belongs-art", default=None)
    parser.add_argument("--thanks-art", default=None)
    parser.add_argument("--copyright-art", default=None)
    parser.add_argument("--instructions-art", default=None)
    parser.add_argument("--skip-belongs", action="store_true")
    parser.add_argument("--skip-instructions", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    plan = load_plan(args.theme)
    size = plan.get("page_size") or config.DEFAULT_PAGE_SIZE
    dims = config.get_page_dims(size)
    target = (dims["width_px"], dims["height_px"])
    fm_dir = REPO_ROOT / config.get_book_dir(args.theme) / "frontmatter"
    fm_dir.mkdir(parents=True, exist_ok=True)
    title_art = resolve_art(args.title_art, fm_dir / "1_artwork.png")
    belongs_art = resolve_art(args.belongs_art, fm_dir / "2_artwork.png")
    thanks_art = resolve_art(args.thanks_art, fm_dir / "3_artwork.png")
    copyright_art = resolve_art(args.copyright_art, fm_dir / "copyright_artwork.png")
    instructions_art = resolve_art(args.instructions_art, fm_dir / "instructions_artwork.png")

    copy = plan.get("front_matter") if isinstance(plan.get("front_matter"), dict) else {}
    save(title_page(prepare_art(title_art, target), plan, copy), fm_dir / "1.png", args.overwrite)
    if copyright_art.exists():
        save(copyright_page(prepare_art(copyright_art, target), plan, copy), fm_dir / "copyright.png", args.overwrite)
    if not args.skip_instructions and instructions_art.exists():
        save(instructions_page(prepare_art(instructions_art, target), copy), fm_dir / "instructions.png", args.overwrite)
    if not args.skip_belongs and plan.get("audience") != "adults":
        save(belongs_page(prepare_art(belongs_art, target), copy), fm_dir / "2.png", args.overwrite)
    save(closing_page(prepare_art(thanks_art, target), plan, copy), fm_dir / "3.png", args.overwrite)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
