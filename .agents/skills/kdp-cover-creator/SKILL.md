---
name: kdp-cover-creator
description: Create a KDP-ready full-wrap coloring-book cover using built-in imagegen for text-free front/back artwork and deterministic code for exact title, subtitle, author, back copy, spine, bleed, barcode zone, PNG, and PDF. Use for new, rebuilt, or corrected KDP covers.
---

# KDP Cover Creator

Use `$kdp-chatgpt-cover-creator` as the implementation workflow. Despite the compatibility name, it uses the built-in `imagegen` tool.

## Required approach

1. Read `output/<theme>/plan.json` and the final interior page count.
2. Generate front and back panel artwork in separate built-in imagegen calls.
3. Generate artwork only: no title, subtitle, author, words, ISBN, barcode, QR code, logo, placeholder box, watermark, or mockup.
4. Save the selected images under `output/<theme>/front_artwork.png` and `back_artwork.png`.
5. Use `compose_chatgpt_cover.py` to render all exact text and production geometry.
6. Validate the PDF dimensions and visually inspect full-size and thumbnail renders.

The legacy `scripts/generate_cover.py` renderer path is not the default. Use it only when the user explicitly asks for the configured provider/API workflow.

## Quality gate

- exact metadata match across cover, title page, and listing;
- text inside safe zones and readable at Amazon thumbnail size;
- one continuous full-wrap PDF with bleed;
- no spine text below 79 pages;
- correct trim/aspect ratio and 300-DPI assets;
- clean barcode area added by code, never by image generation.
