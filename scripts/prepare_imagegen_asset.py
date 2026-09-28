#!/usr/bin/env python3
"""Normalize a built-in imagegen result for KDP production.

The built-in image generator writes its own source file. This script performs
the deterministic, project-local step: correct trim ratio, grayscale cleanup
for line art, 300-DPI metadata, and a stable output filename.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

import config


MODES = ("line-art", "grayscale-art", "color-art")


def _prepare(source: Image.Image, target: tuple[int, int], mode: str) -> Image.Image:
    source = ImageOps.exif_transpose(source)

    if mode == "color-art":
        # Cover panels must run edge-to-edge. Prompts already request the target
        # ratio; fit only removes a small mismatch introduced by the generator.
        return ImageOps.fit(source.convert("RGB"), target, Image.Resampling.LANCZOS)

    gray = ImageOps.grayscale(source)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    if mode == "line-art":
        gray = ImageEnhance.Contrast(gray).enhance(1.35)
        gray = ImageEnhance.Brightness(gray).enhance(1.06)
    else:
        gray = ImageEnhance.Contrast(gray).enhance(1.18)
        gray = ImageEnhance.Brightness(gray).enhance(1.03)

    contained = ImageOps.contain(gray, target, Image.Resampling.LANCZOS)
    page = Image.new("L", target, 255)
    x = (target[0] - contained.width) // 2
    y = (target[1] - contained.height) // 2
    page.paste(contained, (x, y))
    return page


def _ink_ratio(image: Image.Image) -> float:
    gray = image.convert("L").resize((256, 256), Image.Resampling.BILINEAR)
    histogram = gray.histogram()
    return sum(histogram[:240]) / float(256 * 256)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Generated source image")
    parser.add_argument("--output", required=True, help="Project-local PNG path")
    parser.add_argument("--size", choices=config.PAGE_SIZES.keys(), required=True)
    parser.add_argument("--mode", choices=MODES, default="line-art")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    source_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser()
    if not output_path.is_absolute():
        output_path = (Path.cwd() / output_path).resolve()

    if not source_path.is_file():
        parser.error(f"input image not found: {source_path}")
    if output_path.exists() and not args.overwrite:
        parser.error(f"output exists (use --overwrite to replace it): {output_path}")

    dims = config.get_page_dims(args.size)
    target = (dims["width_px"], dims["height_px"])
    with Image.open(source_path) as source:
        prepared = _prepare(source, target, args.mode)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prepared.save(output_path, "PNG", dpi=(config.DPI, config.DPI), optimize=True)

    ratio = _ink_ratio(prepared)
    print(f"Saved: {output_path}")
    print(f"Mode: {args.mode} | Size: {prepared.width}x{prepared.height} | DPI: {config.DPI}")
    print(f"Ink coverage estimate: {ratio:.1%}")
    if args.mode == "line-art" and not 0.015 <= ratio <= 0.60:
        print("WARNING: unusual ink coverage; visually review this page before assembly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
