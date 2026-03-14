---
name: kdp-image-generator
description: Generate coloring page images using Gemini Nano Banana Pro API. USE WHEN user says 'generate coloring pages', 'create coloring images', 'generate images for book', 'run image generation', 'kdp generate images', 'make coloring page images', 'generate pages from plan'.
---

# KDP Image Generator

Generates coloring book page images using Gemini API with Nano Banana Pro model. This is the ONLY step that uses Gemini — for image generation only, not prompt writing.

---

## When to Use

- After prompts are written (by `kdp-prompt-writer` skill)
- User wants to generate or regenerate coloring page images
- The `/project:kdp-create-book` command reaches the generation phase

---

## Process

### Step 1: Verify Prerequisites

Check that:
1. Plan exists: `plans/{theme_key}_plan.json`
2. `.env` has `GOOGLE_API_KEY`
3. Dependencies installed: `pip install google-genai Pillow python-dotenv`

```bash
ls plans/{theme_key}_plan.json
```

### Step 2: Run Image Generation

**Plan-based (recommended):**
```bash
python generate_images.py --plan plans/{theme_key}_plan.json --count {num_pages}
```

**Theme-based (legacy, for existing themes in config.py):**
```bash
python generate_images.py --theme {theme_key} --count {num_pages}
```

**Resume from a specific page:**
```bash
python generate_images.py --plan plans/{theme_key}_plan.json --count {num_pages} --start {start_index}
```

### Step 3: Monitor Progress

The script outputs:
- `[page_num/total] Generating: {prompt_preview}...`
- `Saved: page_XX.png` on success
- `FAILED: Could not generate image` on failure

Note failed pages for regeneration.

### Step 4: Handle Failures

If pages fail:
1. The script auto-retries 3 times with delays
2. If still failing, wait and re-run with `--start` at the failed index
3. Rate limit: 5 seconds between requests (built-in)
4. If persistent failures, check API key and quota

### Step 5: Verify Output

```bash
ls -la output/images/{theme_key}/
```

Check:
- Expected number of `page_XX.png` files exist
- File sizes are reasonable (>50KB each)
- No zero-byte files

---

## Technical Details

- **Model**: `gemini-3.1-flash-image-preview` (Nano Banana Pro)
- **Aspect ratio**: 3:4 (portrait)
- **Post-processing**: Grayscale conversion, contrast +2.0, brightness +1.3
- **Output size**: 2550x3300px (8.5"x11" at 300 DPI)
- **Margins**: 0.25" (75px) — image centered on full page
- **Rate limit**: 5 seconds between API calls

---

## Output

- `output/images/{theme_key}/page_01.png` through `page_XX.png`
- Each image: 2550x3300px, grayscale, 300 DPI, PNG format

---

## Quality Criteria

- All requested pages generated (no missing files)
- Images are grayscale line art (not photos, not colored)
- Clean white background
- Lines are visible and bold
- No artifacts or distortion
- No zero-byte or corrupted files
