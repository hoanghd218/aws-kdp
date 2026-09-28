---
name: kdp-image-generator
description: Generate or regenerate KDP coloring pages from plan.json with the built-in imagegen tool, normalize them to print-ready PNGs, and save every asset in the book output folder. Use for coloring-page generation, missing pages, or targeted page regeneration.
---

# KDP Image Generator

Use the built-in `imagegen` skill by default. It needs no project API key. The older `generate_images.py` provider stack is a legacy fallback and may be used only when the user explicitly asks for that CLI/API path.

## Workflow

1. Read `output/<theme>/plan.json`; verify `page_size`, `page_count`, style bible, and one prompt per page.
2. Create `output/<theme>/images/`.
3. For each distinct page prompt, issue one built-in `image_gen` call. Different pages require different calls; do not use one call with `n` as a batch substitute.
4. Prompt with use case `illustration-story`, intended trim, black-and-white line art, bold closed outlines, white background, safe margins, and explicit exclusions for color, shading, borders, text, watermark, signatures, and mockups. Add an anti-card constraint: draw directly on the white canvas, never as a photograph or scan of a sheet of paper and never inside an inset rectangle, rounded frame, page border, drop shadow, vignette, or gray edge.
5. Normalize each generated source:

```bash
python3 scripts/prepare_imagegen_asset.py \
  --input <source> \
  --output output/<theme>/images/page_XX.png \
  --size <8.5x8.5|8.5x11> \
  --mode line-art
```

6. Inspect each saved PNG. Regeneration is non-destructive at the source level; replace the project PNG only after deciding to redo it, using `--overwrite`.
7. Verify expected dimensions, 300-DPI metadata, nonzero file size, page numbering, and prompt-to-page mapping.

## Quality gate

Every final page must be:

- pure grayscale line art with a white background;
- correct ratio and 300-DPI project dimensions;
- readable bold lines and closed coloring regions;
- free of text, borders, gray fills, color remnants, anatomy errors, crop artifacts, page-within-page/card effects, rectangular boundary lines, drop shadows, and inset paper frames;
- consistent with the book's style bible while depicting a unique scene.

After generation, always use `$kdp-image-reviewer` before assembly.

## Fallback rule

If built-in imagegen is unavailable, stop and explain that the existing provider CLI requires configured credentials. Do not silently switch renderers. Continue only after the user explicitly chooses the fallback.
