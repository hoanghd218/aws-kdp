# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KDP Coloring Book Generator - automated pipeline to create coloring books (kids & adults) for Amazon Kindle Direct Publishing. Uses Gemini API (Nano Banana Pro) to plan books and generate illustrations, then assembles KDP-compliant PDFs.

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env   # Add GOOGLE_API_KEY

# End-to-end: use /kdp-create-book command (interviews you, plans, generates, builds)

# Or manual workflow:
# 1. Plan the book (Gemini generates title, description, keywords, prompts)
python plan_book.py --concept "cozy cats in a cafe" --audience adults --pages 25 --theme-key cozy_cat_cafe

# 2. Generate images from plan
python generate_images.py --plan output/cozy_cat_cafe/plan.json --count 25

# 3. Build PDF
python build_pdf.py --theme cozy_cat_cafe

# 4. Generate cover
python generate_cover.py --theme cozy_cat_cafe --author "Your Name"
```

## Architecture

- `config.py` - KDP specs (8.5x11", 300 DPI, 0.25" margins), THEMES dict, Gemini model (`gemini-3.1-flash-image-preview`), base prompt template
- `plan_book.py` - Gemini text-only call to generate SEO title, subtitle, description, 7 keywords, cover prompt, and 20-30 page prompts. Saves to `output/{theme}/plan.json` + `output/{theme}/prompts.txt`
- `generate_images.py` - Calls AI33 API per prompt, post-processes to grayscale line art. Supports both theme-based and plan-based modes. Saves to `output/{theme}/images/`
- `build_pdf.py` - Assembles ReportLab PDF: title → copyright → coloring pages on odd pages with blank backs → thank you. Ensures even page count. Saves to `output/{theme}/interior.pdf`. **Requires theme in config.py THEMES dict**
- `generate_cover.py` - Generates full KDP cover (front + spine + back) with AI33 artwork and Pillow text overlay. Saves to `output/{theme}/cover.png` + `cover.pdf`. **Requires theme in config.py THEMES dict**

**Important**: `build_pdf.py` and `generate_cover.py` only accept `--theme` values registered in `config.py` THEMES dict. After `plan_book.py` creates a new theme, you must add it to THEMES before building the PDF or cover. `generate_images.py --plan` bypasses this requirement.

## Custom Commands (Skills)

- `/kdp-create-book` - **End-to-end book creation**: interviews user, plans with Gemini, generates images, reviews, builds PDF, creates cover
- `/kdp-image-generator` - Generate coloring page images with Gemini API (theme-based or plan-based)
- `/kdp-image-reviewer` - Review image quality, check KDP compliance, identify pages needing regeneration
- `/kdp-cover-creator` - Generate full-color book covers with correct KDP dimensions and spine width

## Two Workflows

### 1. Plan-based (recommended for new books)
```
plan_book.py → generate_images.py --plan → build_pdf.py → generate_cover.py
```
- Gemini generates SEO-optimized title/description/keywords
- Full prompts per page (more detailed than simple subjects)
- Supports both kids and adults audiences

### 2. Theme-based (legacy, for existing themes)
```
generate_images.py --theme → build_pdf.py → generate_cover.py
```
- Uses BASE_PROMPT + simple subject lines from prompts/*.txt

## KDP Specifications

- Page: 8.5x11" | No bleed | 0.25" margins all sides | 300 DPI | Grayscale
- Image aspect ratio: 3:4 (portrait, from Gemini API)
- Post-process: contain fit (preserves ratio), center on page
- Even page count required
- Interior: single-sided coloring + blank backs

## Prompt Guidelines (from Hoja 1 guide)

### Adults (cozy/cute style):
- "cute cozy medium-detail" aesthetic
- Layered scenes: foreground + midground + background
- Large stylized shapes, NO dense small clusters
- Kawaii proportions, cozy environments

### Kids (6-12):
- Bold thick clean outlines
- Single subject centered, fills page
- NO shading/gradients/borders/frames
- Simple enough for crayons/markers

## Available Themes

Built-in: `cute_animals`, `dinosaurs`, `vehicles`, `unicorn_fantasy`
Custom: Any theme created via `plan_book.py` (saved in `output/{theme}/`)

## Output Structure

All book files are organized under `output/{theme_key}/`:
```
output/{theme_key}/
  ├── images/        — page_01.png, page_02.png, ...
  ├── plan.json      — book metadata + prompts
  ├── prompts.txt    — one prompt per line
  ├── interior.pdf   — KDP interior PDF
  ├── cover.png      — cover image
  └── cover.pdf      — cover PDF for KDP upload
```

## KDP Manual Review — Rejection Triggers

Based on [KDP Content Guidelines](https://kdp.amazon.com/en_US/help/topic/G202145060):

### Will Cause Rejection
- **Metadata mismatch**: title/author must match across title page, copyright page, cover, and spine
- **Template text not removed**: e.g., placeholder text like "BARCODE AREA" on cover
- **Binding terminology**: words like "spiral bound", "leather bound", "hard bound", "calendar" in metadata
- **Illegible text** or content extending past margins
- **Spine text on thin books**: spine text requires minimum 79 pages, with 0.0625" clearance per side

### Technical Requirements
- All images: minimum 300 DPI
- Line thickness: minimum 0.75pt (0.01" / 0.3mm) for graphics
- Grayscale fill: minimum 10% for gray backgrounds
- Font size: minimum 7pt
- Max 4 consecutive blank pages in body; max 10 at end
- Even page count required
- PDF must not be locked/encrypted, no crop marks/bookmarks/annotations
- Transparent objects must be flattened
- Max file size: 650MB

### Publishing Limits
- 10 titles per book format per week

## Key Conventions

- `generate_images.py --start N` resumes from index N (skips existing files)
- `build_pdf.py --author "Name"` adds author to title page + copyright (KDP metadata consistency)
- `.env` holds `GOOGLE_API_KEY` and `AI33_KEY` (never committed)
