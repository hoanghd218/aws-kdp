---
name: kdp-cover-checker
description: >
  Validate KDP book cover PDFs against Amazon's dimension, bleed, and DPI specifications,
  AND check that no cover TEXT sits in the trim-unsafe margin (the #1 reject reason).
  Checks cover width/height based on page count and spine calculation, verifies 0.125" bleed
  on all sides, ensures minimum 300 DPI, and renders a safe-zone overlay. Supports both
  8.5x11 (portrait) and 8.5x8.5 (square) trim sizes. Can check a single book or scan all
  books in output/ folder. USE WHEN user says 'check cover', 'verify cover', 'validate cover',
  'kiem tra bia', 'cover dimensions', 'cover size check', 'kdp cover check', 'cover compliance',
  'check all covers', 'are my covers correct', 'cover specs', 'kiem tra kich thuoc bia',
  'text too close to edge', 'cover bi tu choi', 'safe zone', 'chu sat mep'.
---

# KDP Cover Checker

Validate KDP book cover PDFs against Amazon's exact dimension and quality specifications.

---

## When to Run

- After generating covers with `/kdp-cover-creator` or `generate_cover.py`
- Before uploading to KDP to catch dimension errors
- When KDP rejects a cover for wrong dimensions
- To audit all books in the output/ folder at once

## How to Run

Execute the checker script:

```bash
# Check ALL books in output/
python .claude/skills/kdp-cover-checker/scripts/check_covers.py

# Check a single book
python .claude/skills/kdp-cover-checker/scripts/check_covers.py --theme cozy_cats_daily_life

# Verbose mode (show all details even for passing books)
python .claude/skills/kdp-cover-checker/scripts/check_covers.py --verbose
```

## KDP Cover Specifications

These are the exact rules the checker validates:

### Bleed (mandatory for covers)
- All covers MUST include 0.125" bleed on all 4 sides
- This is non-negotiable — KDP rejects covers without bleed

### Spine Width Formula
```
spine_width = total_pages * 0.002252"
```
Where `total_pages` = the interior PDF page count (white paper, black ink).

### Full Cover Dimensions
```
width  = 8.5" (back) + spine + 8.5" (front) + 0.125" (bleed left) + 0.125" (bleed right)
height = trim_height + 0.125" (bleed top) + 0.125" (bleed bottom)
```

### Example for 8.5x8.5 square, 104 pages
- Spine: 104 * 0.002252 = 0.234"
- Width: 8.5 + 0.234 + 8.5 + 0.125 + 0.125 = **17.484"**
- Height: 8.5 + 0.125 + 0.125 = **8.750"**
- At 300 DPI: 5245 x 2625 px

### Example for 8.5x11 portrait, 56 pages
- Spine: 56 * 0.002252 = 0.126"
- Width: 8.5 + 0.126 + 8.5 + 0.125 + 0.125 = **17.376"**
- Height: 11 + 0.125 + 0.125 = **11.250"**
- At 300 DPI: 5213 x 3375 px

### DPI
- Minimum 300 DPI required

### Text safe zone (the #1 reject — ALWAYS check this)
KDP trims the wrap ~0.125" in (bleed) and the printer can drift another ~0.25", so **any
TEXT within 0.375" of the trim line (= 0.5" / 150px from the file edge at 300 DPI) can be
shaved off.** The rejection email reads *"move all text at least 0.375 inches (9.5 mm) away
from all edges."* This is the most common reason a cover comes back.

Run the safe-zone checker — it writes `output/{theme}/cover_safe_check.png` (green = trim,
red = text-safe line) and prints per-edge ink %:

```bash
python scripts/check_cover_safezone.py <theme_key>
# or on an explicit file:  python scripts/check_cover_safezone.py --png output/<theme>/cover.png
```

**The overlay is the real gate, not the number.** OPEN `cover_safe_check.png` and confirm
**no letter, number, or text badge crosses the RED line.** Decorative art (balloons, confetti,
sparkles, gift boxes, bunting) crossing the red line is FINE — only text must stay inside.
On full-bleed vibrant covers the ink % runs high on every edge (decoration bleeds); trust the
picture. If any text crosses: for AI-baked front text, re-roll the front with the title/badges/
author pulled into the central ~75% (see the kdp-chatgpt-cover-creator prompt rules); for code
overlays, move them inward (`--headline-y`, `--badge-x`, etc.).

### Tolerance
- Dimension tolerance: +/- 0.01" (3 pixels at 300 DPI)
- This accounts for rounding in pixel-to-inch conversion

## Understanding the Output

The checker reports for each book:

```
[PASS] cozy_cats_daily_life
  Pages: 104 | Size: 8.5x8.5 | Spine: 0.234"
  Expected: 17.484" x 8.750" | Actual: 17.484" x 8.750"

[FAIL] farm_animals_bold — WIDTH MISMATCH
  Pages: 56 | Size: 8.5x11 | Spine: 0.126"
  Expected: 17.376" x 11.250" | Actual: 17.250" x 11.250"
  Delta: width off by -0.126" (missing spine width?)

[SKIP] dragons_cute_friendly — no cover.pdf found
```

## What to Do with Failures

- **Width too small**: Usually means spine width wasn't included or page count changed after cover was generated. Regenerate the cover.
- **Height wrong**: Check if the correct page size (8.5x11 vs 8.5x8.5) was used.
- **DPI too low**: The cover image was saved at less than 300 DPI. Regenerate with `--dpi 300` or check the source image resolution.
- **Missing cover.pdf**: Run `/kdp-cover-creator` for that theme.

## Page Count Detection

The script determines page count by:
1. Counting PNG images in `output/{theme}/images/` directory
2. Calculating total pages: `2 (title + copyright) + (num_images * 2) + 1 (thank you)`, rounded up to even

This matches the logic in `generate_cover.py` and `build_pdf.py`.
