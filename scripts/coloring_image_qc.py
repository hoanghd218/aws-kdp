#!/usr/bin/env python3
"""Technical scan of KDP coloring-page PNGs; visual review is still required."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


SIZES = {"8.5x8.5": (2550, 2550), "8.5x11": (2550, 3300)}


def frame_sides(image: Image.Image) -> dict[str, float]:
    """Measure long dark rules near all four edges of a downsampled page."""
    sample = image.convert("L").resize((512, 512), Image.Resampling.BOX)
    pixels = sample.load()
    lo, hi = 51, 461

    def row_score(y: int) -> float:
        return sum(pixels[x, y] < 95 for x in range(lo, hi)) / (hi - lo)

    def col_score(x: int) -> float:
        return sum(pixels[x, y] < 95 for y in range(lo, hi)) / (hi - lo)

    return {
        "top": max(row_score(y) for y in range(10, 62)),
        "bottom": max(row_score(y) for y in range(450, 502)),
        "left": max(col_score(x) for x in range(10, 62)),
        "right": max(col_score(x) for x in range(450, 502)),
    }


def scan(book_dir: Path) -> dict:
    plan = json.loads((book_dir / "plan.json").read_text(encoding="utf-8"))
    expected_size = SIZES[plan["page_size"]]
    images = sorted((book_dir / "images").glob("page_*.png"))
    expected_count = plan.get("page_count") or len(plan.get("page_prompts", []))
    issues = []
    if len(images) != expected_count:
        issues.append({"page": None, "issue": f"Expected {expected_count} pages, found {len(images)}"})
    for path in images:
        with Image.open(path) as image:
            if image.size != expected_size:
                issues.append({"page": path.name, "issue": f"Size {image.size}; expected {expected_size}"})
            if image.mode not in ("L", "LA"):
                issues.append({"page": path.name, "issue": f"Color mode {image.mode}; expected grayscale"})
            sides = frame_sides(image)
            if all(score >= 0.70 for score in sides.values()):
                issues.append({"page": path.name, "issue": "Likely full-page frame", "edge_scores": sides})
    return {"book": str(book_dir), "pages_checked": len(images),
            "verdict": "REDO" if issues else "PASS", "issues": issues,
            "visual_review_required": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book_dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = scan(args.book_dir)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['verdict']}: {result['pages_checked']} pages scanned")
        for issue in result["issues"]:
            print(f"  {issue['page'] or 'book'}: {issue['issue']}")
        print("Visual review is still required for anatomy, stray text, and style.")
    return 1 if result["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
