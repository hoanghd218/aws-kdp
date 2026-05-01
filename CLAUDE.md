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

- `config.py` - KDP specs, page sizes (`8.5x11` portrait, `8.5x8.5` square), gutter margin calculator (`get_gutter_margin`), path helpers, image provider constants, `THEMES` proxy (auto-discovers from `output/` subdirs + legacy hardcoded themes)
- `plan_book.py` - Gemini text-only call to generate SEO title, subtitle, description, 7 keywords, cover prompt, and 20-30 page prompts. Saves to `output/{theme}/plan.json` + `output/{theme}/prompts.txt`
- `image_providers.py` - Shared image generation providers (AI33, Bimai, NanoPic, flow). Default renderer set via `IMAGE_RENDERER` in `.env`. NanoPic supports a comma-separated pool of `NANOPIC_ACCESS_TOKEN`s for parallel throughput.
- `generate_images.py` - Calls configured image renderer per prompt, post-processes to grayscale line art. Supports both theme-based (`--theme`) and plan-based (`--plan`) modes. Always uses `ThreadPoolExecutor` (parallel even for 1 page). Saves to `output/{theme}/images/`
- `build_pdf.py` - Assembles ReportLab PDF: title → copyright → coloring pages on odd pages with blank backs → thank you. Ensures even page count. Gutter margin auto-calculated from page count per KDP rules. Saves to `output/{theme}/interior.pdf`.
- `generate_cover.py` - Generates full KDP cover (front + spine + back) with AI-generated artwork and Pillow text overlay. Reuses saved `front_artwork.png` unless `--regenerate` passed. Sample pages on back cover are evenly spaced across the book. Saves to `output/{theme}/cover.png` + `cover.pdf`.
- `batch_generate_images.py` - Scans all `output/` subdirs, finds missing page images, generates them using nanopic + ai33 in parallel (12 threads by default).
- `batch_plan_generator.py` - Reads idea markdown files from `ideas/`, writes `plan.json` for each without calling AI (prompts hand-written by Claude).
- `scripts/batch_rebuild_cover.py` - Rebuilds covers for all books in `output/` in parallel (6 workers).
- `scripts/batch_rebuild_interior.py` - Rebuilds interior PDFs for all books in `output/` in parallel.
- `services/` - Flow renderer backend: `flow_server.py` (aiohttp WebSocket + HTTP server), `flow_client.py` (singleton client state), `flow_sdk.py` (async SDK wrapping the Flow Recaptcha Chrome extension protocol).

**Theme resolution**: `THEMES` is a dynamic proxy — `build_pdf.py` and `generate_cover.py` auto-discover any theme that has `output/{theme}/plan.json` or `output/{theme}/prompts.txt`. No manual registration needed for plan-based themes.

## Image Renderers

Set `IMAGE_RENDERER` in `.env` to one of: `ai33`, `bimai`, `nanopic`, `kie`, `flow`.

Override per-run with `--renderer <name>`. NanoPic supports a comma-separated `NANOPIC_ACCESS_TOKEN` pool for parallel throughput.

## Square Books (8.5x8.5)

Pass `--size 8.5x8.5` to `plan_book.py`, `generate_images.py`, `build_pdf.py`, and `generate_cover.py` to produce square-format books. The default is `8.5x11` portrait.

## Flow Renderer (Google Flow / Flowboard Bridge)

The `flow` renderer uses a Chrome extension instead of an API key:
1. Install the Flow Recaptcha extension; open labs.google in Chrome
2. Start the local bridge server: `python services/flow_server.py`
3. Run generation with `--renderer flow --workers 4` (higher values overload the single browser connection)

To regenerate specific pages — **delete only those pages, then run once**:
```bash
rm output/{theme}/images/page_03.png output/{theme}/images/page_15.png
python generate_images.py --plan output/{theme}/plan.json --renderer flow --workers 4
# skip-if-exists logic skips all other pages automatically
```
Never delete `page_01.png` separately — it causes data loss.

## Custom Commands (Skills)

- `/kdp-create-book` - **End-to-end book creation**: interviews user, plans, generates images, reviews, builds PDF, creates cover
- `/kdp-image-generator` - Generate coloring page images with configured renderer from `.env` (theme-based or plan-based)
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
- `.env` holds `IMAGE_RENDERER` (default renderer: `ai33`, `bimai`, or `nanopic`), API keys (`GOOGLE_API_KEY`, `AI33_KEY`, `BIMAI_API_KEY`, `NANOPIC_API_KEY`), and author info (never committed)
