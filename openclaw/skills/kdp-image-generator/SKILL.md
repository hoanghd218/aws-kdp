---
name: kdp-image-generator
description: Generate coloring page images for a KDP book. USE WHEN user says 'generate images', 'tạo ảnh tô màu', 'generate coloring pages', 'run image generation', 'tạo ảnh cho sách'.
metadata:
  openclaw:
    emoji: "🎨"
    requires:
      bins: ["python3"]
      env: ["IMAGE_RENDERER"]
---

# KDP Image Generator

Generates coloring book page images using the configured image renderer (`IMAGE_RENDERER` in `.env`).

## Process

### Step 1: Verify plan exists

```bash
ls output/{theme_key}/plan.json
```

If missing, tell user to run `kdp-create-book` first.

### Step 2: Generate images

```bash
python generate_images.py --plan output/{theme_key}/plan.json --count {num_pages}
```

To resume from a specific page:
```bash
python generate_images.py --plan output/{theme_key}/plan.json --count {num_pages} --start {N}
```

For flow renderer (max 4 workers):
```bash
python generate_images.py --plan output/{theme_key}/plan.json --renderer flow --workers 4
```

### Step 3: Verify output

```bash
ls -la output/{theme_key}/images/
```

Check:
- Expected number of `page_XX.png` files exist
- No zero-byte files (size > 50KB each)

### Step 4: Report

Tell user how many pages were generated and if any failed. List failed pages by number if any.

## Notes

- Renderer is set via `IMAGE_RENDERER` in `.env` (`ai33`, `bimai`, `nanopic`, `kie`, `flow`)
- Override per-run with `--renderer <name>`
- Skip-if-exists: script skips pages that already exist — safe to re-run
- Never delete `page_01.png` separately — it causes data loss
