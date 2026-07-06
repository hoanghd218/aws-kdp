#!/usr/bin/env python3
"""Rebuild a KDP coloring book interior.pdf using illustrated front/back matter.

Replaces the plain-text title / copyright / thank-you pages with hand-made
illustrations and (optionally) inserts a "This Book Belongs To" page.

Expected images in  output/<theme>/frontmatter/ :
    1.png  -> Title page            (REQUIRED)
    2.png  -> This Book Belongs To   (optional — skipped if missing)
    3.png  -> Thank You page         (REQUIRED)

The illustrations should already contain their own text (baked in by the image
model). This script only places them, adds a plain copyright page, keeps
coloring pages on right-hand pages with blank backs, and forces an even total.

Run from the repo root:
    python3 .agents/skills/kdp-frontmatter-pages/scripts/assemble_frontmatter.py <theme_key>

Options:
    --size 8.5x11|8.5x8.5   override trim (default: plan.json page_size)
    --author "Name"          override author for copyright line
    --age 3-7                override age range shown on copyright page
    --no-copyright           omit the plain copyright text page
"""
import os, sys, glob, json, re, argparse, datetime, shutil, time

sys.path.insert(0, "scripts")
import config
from PIL import Image
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONTS = [
    ("Arial", "/System/Library/Fonts/Supplemental/Arial.ttf"),
    ("Arial-Bold", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    ("Arial-Italic", "/System/Library/Fonts/Supplemental/Arial Italic.ttf"),
    ("Helvetica", "/System/Library/Fonts/Supplemental/Arial.ttf"),
]


def load_plan(theme):
    path = config.get_plan_path(theme)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def author_from_plan(plan):
    a = plan.get("author", {})
    if isinstance(a, dict):
        return f"{a.get('first_name','')} {a.get('last_name','')}".strip()
    if isinstance(a, str):
        return a
    return ""


def age_from_title(title, fallback):
    m = re.search(r"[Aa]ges?\s*(\d+\s*[-–]\s*\d+)", title or "")
    return m.group(1).replace(" ", "") if m else fallback


def fm_reader(path, target_px):
    """Grayscale + upscale a frontmatter PNG so it prints at >=300 DPI."""
    im = Image.open(path).convert("L")
    if im.width < target_px:
        im = im.resize((target_px, target_px), Image.LANCZOS)
    return ImageReader(im)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("theme")
    ap.add_argument("--size", default=None)
    ap.add_argument("--author", default=None)
    ap.add_argument("--age", default=None)
    ap.add_argument("--no-copyright", action="store_true")
    args = ap.parse_args()

    theme = args.theme
    plan = load_plan(theme)

    fm_dir = os.path.join(config.get_book_dir(theme), "frontmatter")
    title_png = os.path.join(fm_dir, "1.png")
    belongs_png = os.path.join(fm_dir, "2.png")
    thanks_png = os.path.join(fm_dir, "3.png")

    for required in (title_png, thanks_png):
        if not os.path.exists(required):
            sys.exit(f"ERROR: missing required image: {required}")
    has_belongs = os.path.exists(belongs_png)

    size = args.size or plan.get("page_size") or config.DEFAULT_PAGE_SIZE
    if size not in config.PAGE_SIZES:
        size = config.DEFAULT_PAGE_SIZE
    audience = plan.get("audience", "kids")
    author = args.author or author_from_plan(plan) or config.DEFAULT_AUTHOR
    age = args.age or age_from_title(plan.get("title", ""), config.TARGET_AGE)

    images = sorted(glob.glob(os.path.join(config.get_images_dir(theme), "page_*.png")))
    if not images:
        sys.exit(f"ERROR: no coloring images in {config.get_images_dir(theme)}")
    print(f"Coloring pages: {len(images)} | size: {size} | author: {author} | belongs page: {has_belongs}")

    # --- front-matter page list (each entry rendered on its own page) ---
    front = ["title"]
    if not args.no_copyright:
        front.append("copyright")
    if has_belongs:
        front.append("belongs")
    # pad so coloring pages start on an odd (right-hand) page
    if len(front) % 2 != 0:
        front.append("blank")

    total = len(front) + len(images) * 2 + 1
    if total % 2 != 0:
        total += 1

    dims = config.get_page_dims(size, page_count=total)
    page_w = dims["width_inches"] * inch
    page_h = dims["height_inches"] * inch
    margin = dims["margin_inches"] * inch
    gutter = dims["gutter_margin_inches"] * inch
    target_px = dims["width_px"]
    print(f"Total pages: {total} | gutter {dims['gutter_margin_inches']}\" outside {dims['margin_inches']}\"")

    out_path = config.get_interior_pdf_path(theme)
    if os.path.exists(out_path):
        bak = out_path.replace(".pdf", f"_backup_{int(time.time())}.pdf")
        shutil.copy(out_path, bak)
        print(f"Backed up old interior -> {bak}")

    for name, p in FONTS:
        pdfmetrics.registerFont(TTFont(name, p))

    c = canvas.Canvas(out_path, pagesize=(page_w, page_h))
    c.setFont("Arial", 12)
    page_num = 0

    def content_area(n):
        if n % 2 == 1:
            left, right = gutter, margin
        else:
            left, right = margin, gutter
        return left, margin, page_w - left - right, page_h - 2 * margin

    def image_page(reader):
        nonlocal page_num
        page_num += 1
        x, y, w, h = content_area(page_num)
        c.drawImage(reader, x, y, width=w, height=h,
                    preserveAspectRatio=True, anchor="c", mask="auto")
        c.showPage()

    def blank():
        nonlocal page_num
        page_num += 1
        c.showPage()

    def copyright_page():
        nonlocal page_num
        page_num += 1
        x, y, w, h = content_area(page_num)
        cx = x + w / 2
        year = datetime.datetime.now().year
        who = "adults" if audience == "adults" else "children"
        designed = (f"This coloring book is designed for {who} ages {age}."
                    if who == "children" else
                    "This coloring book is designed for adults who enjoy relaxing coloring.")
        lines = [
            f"Copyright (c) {year} {author}. All rights reserved.", "",
            "No part of this book may be reproduced or used in any manner",
            "without written permission of the copyright owner.", "",
            designed, "",
            "For personal use only. Not for resale.", "",
            "Made with love for creative colorists everywhere!",
        ]
        c.setFont("Arial", 11)
        yy = page_h * 0.6
        for ln in lines:
            c.drawCentredString(cx, yy, ln)
            yy -= 18
        c.showPage()

    readers = {
        "title": lambda: fm_reader(title_png, target_px),
        "belongs": lambda: fm_reader(belongs_png, target_px),
    }
    for kind in front:
        if kind == "copyright":
            copyright_page()
        elif kind == "blank":
            blank()
        else:
            image_page(readers[kind]())

    for img in images:
        image_page(ImageReader(img))   # coloring page (right)
        blank()                         # blank back (left)

    if (page_num + 1) % 2 != 0:
        blank()
    image_page(fm_reader(thanks_png, target_px))  # thank you, last page

    c.save()
    print(f"DONE: {out_path}  ({page_num} pages)")
    print(f"Next: python3 scripts/pdf_qc.py --pdf {out_path} --trim {size} --require-even-pages")


if __name__ == "__main__":
    main()
