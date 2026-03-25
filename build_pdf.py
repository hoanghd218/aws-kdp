#!/usr/bin/env python3
"""
Build a KDP-ready PDF coloring book from generated images.
Layout: title page, copyright, coloring pages on odd pages with blank backs.
"""

import argparse
import os
import sys

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

import config


def get_sorted_images(theme: str) -> list[str]:
    """Get sorted list of generated image files for a theme."""
    image_dir = os.path.join(config.OUTPUT_IMAGES_DIR, theme)
    if not os.path.exists(image_dir):
        print(f"Error: Image directory not found: {image_dir}")
        print(f"Run 'python generate_images.py --theme {theme}' first")
        sys.exit(1)

    images = sorted(
        [
            os.path.join(image_dir, f)
            for f in os.listdir(image_dir)
            if f.endswith(".png")
        ]
    )

    if not images:
        print(f"Error: No PNG images found in {image_dir}")
        sys.exit(1)

    return images


def _load_plan_meta(theme: str) -> dict:
    """Load audience and page_size from plan file."""
    import json
    plan_path = os.path.join("plans", f"{theme}_plan.json")
    meta = {"audience": "kids", "page_size": None}
    if os.path.exists(plan_path):
        with open(plan_path) as f:
            plan = json.load(f)
            meta["audience"] = plan.get("audience", "kids")
            meta["page_size"] = plan.get("page_size")
    return meta


def build_pdf(theme: str, title: str | None = None, subtitle: str | None = None, size: str = config.DEFAULT_PAGE_SIZE):
    """Build KDP-ready PDF coloring book."""
    theme_config = config.THEMES.get(theme)
    if not theme_config:
        print(f"Error: Unknown theme '{theme}'")
        sys.exit(1)

    # Auto-detect page size from plan/theme config if not explicitly set
    plan_meta = _load_plan_meta(theme)
    audience = plan_meta["audience"]
    if size == config.DEFAULT_PAGE_SIZE:
        # Check plan first, then theme config
        if plan_meta["page_size"] and plan_meta["page_size"] in config.PAGE_SIZES:
            size = plan_meta["page_size"]
        elif "page_size" in theme_config and theme_config["page_size"] in config.PAGE_SIZES:
            size = theme_config["page_size"]

    if title is None:
        title = theme_config["book_title"]
    if subtitle is None:
        if audience == "adults":
            subtitle = "A Relaxing Coloring Book for Adults"
        else:
            subtitle = f"Coloring Book for Kids Ages {config.TARGET_AGE}"

    images = get_sorted_images(theme)
    print(f"Found {len(images)} coloring pages")

    # Output path
    os.makedirs(config.OUTPUT_BOOKS_DIR, exist_ok=True)
    safe_title = theme.replace(" ", "_")
    output_path = os.path.join(config.OUTPUT_BOOKS_DIR, f"{safe_title}_coloring_book.pdf")

    # Page size from --size option
    dims = config.get_page_dims(size)
    page_w = dims["width_inches"] * inch
    page_h = dims["height_inches"] * inch

    c = canvas.Canvas(output_path, pagesize=(page_w, page_h))

    # --- Page 1: Title Page ---
    c.setFont("Helvetica-Bold", 36)
    # Draw title centered, wrapped if needed
    title_lines = _wrap_text(title, max_chars=25)
    y_start = page_h * 0.55
    for i, line in enumerate(title_lines):
        c.drawCentredString(page_w / 2, y_start - (i * 45), line)

    # Draw subtitle wrapped
    c.setFont("Helvetica", 16)
    subtitle_lines = _wrap_text(subtitle, max_chars=45)
    y_sub = page_h * 0.35
    for i, line in enumerate(subtitle_lines):
        c.drawCentredString(page_w / 2, y_sub - (i * 22), line)

    c.setFont("Helvetica-Oblique", 14)
    if audience == "adults":
        c.drawCentredString(page_w / 2, page_h * 0.25, "Cozy & Relaxing Designs")
    else:
        c.drawCentredString(page_w / 2, page_h * 0.25, "Bold & Easy Designs")
    c.showPage()

    # --- Page 2: Copyright / Info Page ---
    c.setFont("Helvetica", 11)
    if audience == "adults":
        copyright_lines = [
            f"Copyright (c) 2026. All rights reserved.",
            "",
            "No part of this book may be reproduced or used in any manner",
            "without written permission of the copyright owner.",
            "",
            "This coloring book is designed for adults who enjoy relaxing,",
            "creative coloring sessions.",
            "",
            "For personal use only. Not for resale.",
            "",
            "We hope you enjoy every page!",
        ]
    else:
        copyright_lines = [
            f"Copyright (c) 2026. All rights reserved.",
            "",
            "No part of this book may be reproduced or used in any manner",
            "without written permission of the copyright owner.",
            "",
            f"This coloring book is designed for children ages {config.TARGET_AGE}.",
            "",
            "For personal use only. Not for resale.",
            "",
            "Made with love for creative kids everywhere!",
        ]
    y = page_h * 0.6
    for line in copyright_lines:
        c.drawCentredString(page_w / 2, y, line)
        y -= 18
    c.showPage()

    # --- Coloring Pages (odd pages) with blank backs (even pages) ---
    for i, image_path in enumerate(images):
        # Odd page: coloring image
        # Draw image to fill page (image already includes margins from post-processing)
        c.drawImage(
            image_path,
            0,
            0,
            width=page_w,
            height=page_h,
            preserveAspectRatio=True,
            anchor="c",
        )
        c.showPage()

        # Even page: blank (prevents bleed-through when coloring)
        c.showPage()

    # --- Last Page: Thank You ---
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(page_w / 2, page_h * 0.55, "Thank You!")
    c.setFont("Helvetica", 16)
    c.drawCentredString(page_w / 2, page_h * 0.45, "We hope you enjoyed coloring!")
    c.setFont("Helvetica", 14)
    c.drawCentredString(
        page_w / 2, page_h * 0.38, "If you liked this book, please leave a review."
    )
    c.showPage()

    # Ensure even total page count (KDP requirement)
    total_pages = 2 + (len(images) * 2) + 1  # title + copyright + pages + thank you
    if total_pages % 2 != 0:
        c.showPage()  # Add blank page

    c.save()

    final_pages = total_pages if total_pages % 2 == 0 else total_pages + 1
    print(f"PDF created: {output_path}")
    print(f"Total pages: {final_pages}")
    print(f"  - Title page: 1")
    print(f"  - Copyright: 1")
    print(f"  - Coloring pages: {len(images)} (with {len(images)} blank backs)")
    print(f"  - Thank you: 1")
    print(f"Page size: {dims['width_inches']}\" x {dims['height_inches']}\"")


def _wrap_text(text: str, max_chars: int = 25) -> list[str]:
    """Simple word-wrap for title text."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 > max_chars and current_line:
            lines.append(current_line.strip())
            current_line = word
        else:
            current_line += " " + word
    if current_line.strip():
        lines.append(current_line.strip())
    return lines


def main():
    parser = argparse.ArgumentParser(description="Build KDP-ready coloring book PDF")
    parser.add_argument(
        "--theme",
        required=True,
        choices=config.THEMES.keys(),
        help="Coloring book theme",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Custom book title (default: from config)",
    )
    parser.add_argument(
        "--subtitle",
        type=str,
        default=None,
        help="Custom subtitle",
    )
    parser.add_argument(
        "--size",
        choices=config.PAGE_SIZES.keys(),
        default=config.DEFAULT_PAGE_SIZE,
        help=f"Page size (default: {config.DEFAULT_PAGE_SIZE})",
    )
    args = parser.parse_args()

    build_pdf(args.theme, args.title, args.subtitle, args.size)


if __name__ == "__main__":
    main()
