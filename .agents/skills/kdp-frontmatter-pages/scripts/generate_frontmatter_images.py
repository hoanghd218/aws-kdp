#!/usr/bin/env python3
"""Generate illustrated KDP frontmatter PNGs from frontmatter/*.txt prompts.

Expected prompts in output/<theme>/frontmatter/:
    1.txt -> Title page              (required)
    2.txt -> This Book Belongs To    (optional)
    3.txt -> Thank You page          (required)

Run from the repo root:
    python3 .agents/skills/kdp-frontmatter-pages/scripts/generate_frontmatter_images.py <theme_key>
"""
from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv
from PIL import Image, ImageEnhance, ImageOps

sys.path.insert(0, "scripts")
import config
from image_providers import DEFAULT_RENDERER, RENDERER_CHOICES, generate_image

load_dotenv()

PAGE_LABELS = {
    "1": "title",
    "2": "this book belongs to",
    "3": "thank you",
}


def load_plan(theme: str) -> dict:
    path = config.get_plan_path(theme)
    if not os.path.exists(path):
        return {}
    import json

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def prompt_path(frontmatter_dir: str, page: str) -> str:
    return os.path.join(frontmatter_dir, f"{page}.txt")


def output_path(frontmatter_dir: str, page: str) -> str:
    return os.path.join(frontmatter_dir, f"{page}.png")


def post_process(image: Image.Image, size_key: str) -> Image.Image:
    """Prepare a generated frontmatter image for print without cropping text."""
    dims = config.get_page_dims(size_key)
    target = (dims["width_px"], dims["height_px"])

    image = ImageOps.grayscale(image)
    image = ImageOps.contain(image, target, Image.Resampling.LANCZOS)

    image = ImageEnhance.Contrast(image).enhance(1.45)
    image = ImageEnhance.Brightness(image).enhance(1.08)

    full_page = Image.new("L", target, 255)
    paste_x = (target[0] - image.size[0]) // 2
    paste_y = (target[1] - image.size[1]) // 2
    full_page.paste(image, (paste_x, paste_y))
    return full_page


def parse_pages(value: str) -> list[str]:
    pages = [p.strip() for p in value.split(",") if p.strip()]
    invalid = [p for p in pages if p not in PAGE_LABELS]
    if invalid:
        raise argparse.ArgumentTypeError(f"invalid page(s): {', '.join(invalid)}")
    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate KDP frontmatter images")
    parser.add_argument("theme", help="Theme key under output/<theme>/")
    parser.add_argument(
        "--pages",
        type=parse_pages,
        default=["1", "2", "3"],
        help="Comma-separated page numbers to generate, e.g. 1,3",
    )
    parser.add_argument(
        "--size",
        choices=config.PAGE_SIZES.keys(),
        default=None,
        help="Override page size. Defaults to plan.json page_size.",
    )
    parser.add_argument(
        "--renderer",
        choices=RENDERER_CHOICES,
        default=DEFAULT_RENDERER,
        help=f"Image renderer (default: {DEFAULT_RENDERER} from .env)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate pages even when PNGs already exist.",
    )
    args = parser.parse_args()

    plan = load_plan(args.theme)
    size_key = args.size or plan.get("page_size") or config.DEFAULT_PAGE_SIZE
    if size_key not in config.PAGE_SIZES:
        print(f"Warning: unknown page_size '{size_key}', using {config.DEFAULT_PAGE_SIZE}")
        size_key = config.DEFAULT_PAGE_SIZE

    dims = config.get_page_dims(size_key)
    frontmatter_dir = os.path.join(config.get_book_dir(args.theme), "frontmatter")
    if not os.path.isdir(frontmatter_dir):
        print(f"ERROR: frontmatter folder not found: {frontmatter_dir}")
        return 1

    ar = dims["bimai_aspect_ratio"] if args.renderer == "bimai" else dims["ai33_aspect_ratio"]
    print(f"Theme: {args.theme}")
    print(f"Renderer: {args.renderer}")
    print(f"Page size: {config.PAGE_SIZES[size_key]['label']}")
    print(f"Aspect ratio: {ar}")
    print(f"Output: {frontmatter_dir}/")
    print()

    success = 0
    attempted = 0

    for page in args.pages:
        txt = prompt_path(frontmatter_dir, page)
        png = output_path(frontmatter_dir, page)

        if not os.path.exists(txt):
            required = page in {"1", "3"}
            message = "ERROR" if required else "Skipping optional"
            print(f"{message}: missing prompt {txt}")
            if required:
                return 1
            continue

        if os.path.exists(png) and not args.overwrite:
            print(f"Skipping existing {os.path.basename(png)}")
            success += 1
            continue

        with open(txt, encoding="utf-8") as f:
            prompt = f.read().strip()
        if not prompt:
            print(f"ERROR: empty prompt: {txt}")
            return 1

        attempted += 1
        label = PAGE_LABELS[page]
        print(f"[{page}] Generating {label} page...")
        image = generate_image(prompt, renderer=args.renderer, aspect_ratio=ar)
        if image is None:
            print(f"FAILED: could not generate {png}")
            continue

        processed = post_process(image, size_key)
        processed.save(png, "PNG", dpi=(config.DPI, config.DPI))
        print(f"Saved: {png}")
        success += 1

    print()
    print(f"Done: {success}/{len(args.pages)} available page(s) ready. Generated {attempted} new image(s).")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
