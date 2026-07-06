#!/usr/bin/env python3
"""Build output/<theme>/image_prompts.json — a flat render queue for generating
all of a book's art in an EXTERNAL tool, then dropping the PNGs back into the
book folder before assembly.

Queue order (book order):
    front_artwork.png         (from plan.cover_prompt)
    back_artwork.png          (from plan.back_cover_prompt)
    frontmatter/1.png         (Title — from frontmatter/1.txt, if present)
    frontmatter/2.png         (This Book Belongs To — from frontmatter/2.txt)
    images/page_01.png .. NN  (from plan.page_prompts)
    frontmatter/3.png         (Thank You — from frontmatter/3.txt, if present)

The frontmatter prompts are the personalized text Claude writes via the
kdp-frontmatter-pages skill (output/<theme>/frontmatter/{1,2,3}.txt). They are
included only when those .txt files exist, so this script is safe to run before
or after frontmatter prompts are written.

Each item: {"prompt": str, "size": "1:1"|"3:4", "filename": str}
  size is the aspect ratio: 8.5x8.5 -> "1:1", 8.5x11 -> "3:4".

Usage:
    python scripts/build_image_prompts.py <theme_key> [--size 1:1|3:4]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIZE_BY_TRIM = {"8.5x8.5": "1:1", "8.5x11": "3:4"}


def _read_txt(path: Path) -> str | None:
    if path.exists():
        text = path.read_text(encoding="utf-8").strip()
        if text:
            return text
    return None


def build(theme_key: str, size: str | None = None) -> Path:
    book_dir = ROOT / "output" / theme_key
    plan_path = book_dir / "plan.json"
    if not plan_path.exists():
        sys.exit(f"plan.json not found: {plan_path}")

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    size = size or SIZE_BY_TRIM.get(plan.get("page_size", "8.5x11"), "3:4")
    fm = book_dir / "frontmatter"

    queue: list[dict] = []

    if plan.get("cover_prompt"):
        queue.append({"prompt": plan["cover_prompt"], "size": size,
                      "filename": "front_artwork.png"})
    if plan.get("back_cover_prompt"):
        queue.append({"prompt": plan["back_cover_prompt"], "size": size,
                      "filename": "back_artwork.png"})

    # Frontmatter: Title (1) + Belongs-To (2) go before the coloring pages.
    for n, fname in ((1, "frontmatter/1.png"), (2, "frontmatter/2.png")):
        prompt = _read_txt(fm / f"{n}.txt")
        if prompt:
            queue.append({"prompt": prompt, "size": size, "filename": fname})

    for i, prompt in enumerate(plan.get("page_prompts", []), 1):
        queue.append({"prompt": prompt, "size": size,
                      "filename": f"images/page_{i:02d}.png"})

    # Thank-you (3) is the last page of the book.
    thank_you = _read_txt(fm / "3.txt")
    if thank_you:
        queue.append({"prompt": thank_you, "size": size,
                      "filename": "frontmatter/3.png"})

    out_path = book_dir / "image_prompts.json"
    out_path.write_text(json.dumps(queue, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    n_fm = sum(1 for q in queue if q["filename"].startswith("frontmatter/"))
    n_pages = sum(1 for q in queue if q["filename"].startswith("images/"))
    print(f"Wrote {out_path}  ({len(queue)} items: "
          f"cover+back, {n_fm} frontmatter, {n_pages} pages)  size={size}")
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("theme_key")
    ap.add_argument("--size", choices=["1:1", "3:4"], default=None,
                    help="Aspect ratio override (default: inferred from page_size)")
    args = ap.parse_args()
    build(args.theme_key, args.size)


if __name__ == "__main__":
    main()
