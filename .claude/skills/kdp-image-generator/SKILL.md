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
2. `.env` has `GOOGLE_API_KEY` (for Gemini renderer) or `AI33_KEY` (for AI33 renderer)
3. Dependencies installed: `pip install google-genai Pillow python-dotenv requests`

```bash
ls plans/{theme_key}_plan.json
```

### Step 2: Run Image Generation

**Plan-based with Gemini (default):**
```bash
python generate_images.py --plan plans/{theme_key}_plan.json --count {num_pages}
```
The script auto-detects `page_size` from the plan JSON (`"8.5x11"` or `"8.5x8.5"`). For 8.5x8.5, images are generated with 1:1 (square) aspect ratio. You can override with `--size 8.5x8.5`.

**Plan-based with AI33 renderer:**
```bash
python generate_images.py --plan plans/{theme_key}_plan.json --count {num_pages} --renderer ai33
```

**Theme-based (legacy, for existing themes in config.py):**
```bash
python generate_images.py --theme {theme_key} --count {num_pages}
```

**Resume from a specific page:**
```bash
python generate_images.py --plan plans/{theme_key}_plan.json --count {num_pages} --start {start_index}
```

**Renderer options:**
- `--renderer gemini` (default) — Direct Gemini API, requires `GOOGLE_API_KEY` in `.env`
- `--renderer ai33` — AI33 proxy API (uses model `gemini-3.1-flash-image-preview` at 2K resolution), requires `AI33_KEY` in `.env`. Submits async tasks and polls for results.

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
- **Post-processing**: Grayscale conversion, contrast +2.0, brightness +1.3
- **Margins**: 0.25" (75px) — image centered on full page
- **Rate limit**: 5 seconds between API calls

**Page sizes (`--size`):**
| Size | Dimensions | Aspect Ratio | Pixels (300 DPI) |
|------|-----------|--------------|------------------|
| `8.5x11` (default) | 8.5" x 11" portrait | 3:4 | 2550 x 3300 |
| `8.5x8.5` | 8.5" x 8.5" square | 1:1 | 2550 x 2550 |

---

## Output

- `output/images/{theme_key}/page_01.png` through `page_XX.png`
- Each image: grayscale, 300 DPI, PNG format
  - 8.5x11: 2550x3300px (portrait)
  - 8.5x8.5: 2550x2550px (square)

---

## Quality Criteria

- All requested pages generated (no missing files)
- Images are grayscale line art (not photos, not colored)
- Clean white background
- Lines are visible and bold
- No artifacts or distortion
- No zero-byte or corrupted files
