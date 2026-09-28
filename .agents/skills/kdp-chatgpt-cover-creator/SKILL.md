---
name: kdp-chatgpt-cover-creator
description: Create or rebuild KDP coloring-book cover PNG/PDF with ChatGPT built-in image generation. Use when the user asks to create, fix, regenerate, or validate a KDP cover. All visible cover typography must be baked into the generated front/back artwork; code may only assemble the wrap, blend the spine, calculate bleed/DPI/dimensions, and stamp the barcode zone.
---

# KDP ChatGPT Cover Creator

Create a complete full-wrap paperback cover from two generated panels:

- Front artwork already contains the exact title, subtitle, badges, and author.
- Back artwork already contains its headline/tagline and preview-card layout.
- Python only joins back + spine + front, stamps one barcode zone, and writes the correctly sized PNG/PDF.

Use built-in `image_gen` for both panels. Never add visible cover copy with PIL, ReportLab, HTML, SVG, Canvas, or another code overlay.

## Non-negotiable Rules

1. **Bake every visible word into image generation.** The only words permitted are the exact verbatim strings declared in the prompt. Reject and regenerate any image with a misspelling, gibberish, duplicated text, incidental signs, labels, book titles, or extra words.
2. **Never overlay cover typography in code.** Do not use `--headline`, `--feature-line`, `--badge-top`, `--badge-bottom`, `--front-title`, `--front-subtitle`, or `--front-author`. Compose with `--no-back-text`.
3. **Keep every letter trim-safe.** Keep all text and the complete banner/badge outlines inside the central 72-75% of each panel, with at least 15% breathing room on all edges. Put the author around 68-72% of panel height and end the author/accent by 75-78%, leaving continuing artwork below.
4. **Never ask image generation for a barcode box.** Generate full-bleed artwork with no barcode, ISBN, QR code, white rectangle, or placeholder. Code stamps exactly one 2.0 × 1.2 inch barcode zone on the back.
5. **Protect the back-cover preview grid from the barcode.** End every preview card by about 68-70% of panel height. Fill the bottom 25% with continuing themed artwork, not a blank area.
6. **No spine text below 79 pages.** The default composer blends a clean spine and never adds spine text.

## Workflow

### 1. Read context

Read:

- `output/<theme>/plan.json`
- `output/<theme>/interior.pdf` for the authoritative page count
- existing `output/<theme>/cover.png` when fixing a cover
- `references/cover-pitfalls.md` the first time the skill is used

Treat `cover_prompt` as stale if it says text-free, artwork-only, reserved space for typography, or lacks a `Text (verbatim)` clause. Rewrite stale front/back prompts and save them to `plan.json` before generating.

### 2. Generate the front panel

The prompt must specify:

- Marketplace-ready front-cover artwork matching `page_size` (`1:1` for 8.5×8.5; `3:4` for 8.5×11).
- Exact verbatim title, subtitle, tagline/badge, and author.
- Those are the only allowed words anywhere.
- No readable signs, labels, posters, chalkboards, book spines, product labels, or plaques.
- All text and banner shapes inside the safe central area.
- Full-bleed themed artwork continuing below the author.

Open the generated source at original resolution. REDO if one character is wrong, text is duplicated, any extra writing appears, or the author sits too low.

### 3. Generate the back panel

Default coloring-book layout:

- Exact baked headline/tagline; no code copy.
- Compact 2×3 grid of exactly six equal preview cards.
- Square cards for 8.5×8.5 books; portrait cards for 8.5×11 books.
- Top row: exactly three fully colored examples.
- Bottom row: exactly three black-and-white line-art examples.
- Every card ends by about 68-70% of panel height.
- Bottom 25% is normal full-color themed artwork that can safely receive the barcode stamp.
- No prompt-generated barcode or blank placeholder.

When useful, pass up to five reviewed coloring pages through `referenced_image_paths` so preview cards reflect the actual book.

Open the generated source at original resolution. REDO if text is wrong, the grid count/shape is wrong, rows are not 3 colored + 3 line art, or a card enters the barcode region.

### 4. Normalize accepted panels

Keep original generated files. Normalize accepted assets into stable project paths:

```bash
python3 scripts/prepare_imagegen_asset.py \
  --input <generated-front.png> \
  --output output/<theme>/front_artwork.png \
  --size <page_size> --mode color-art --overwrite

python3 scripts/prepare_imagegen_asset.py \
  --input <generated-back.png> \
  --output output/<theme>/back_artwork.png \
  --size <page_size> --mode color-art --overwrite
```

### 5. Compose without text overlays

```bash
python .agents/skills/kdp-chatgpt-cover-creator/scripts/compose_chatgpt_cover.py \
  --theme <theme> \
  --front output/<theme>/front_artwork.png \
  --back output/<theme>/back_artwork.png \
  --no-back-text
```

The composer may only:

- read the real interior page count and, when it is odd, use KDP's next-even
  calculated page count for spine and cover dimensions;
- calculate spine, bleed, pixel dimensions, and PDF dimensions;
- resize the two complete panels;
- blend the spine;
- stamp one blank barcode zone;
- flatten the wrap and write `cover.png` and `cover.pdf`.

The final PDF must be image-only with no font resources.

### 6. Validate

```bash
python scripts/pdf_qc.py --pdf output/<theme>/cover.pdf --cover \
  --expected-width <full_width_in> --expected-height <full_height_in>
python .agents/skills/kdp-cover-checker/scripts/check_covers.py \
  --theme <theme> --verbose
pdffonts output/<theme>/cover.pdf
```

Open both `cover.png` and `cover_safe_check.png`. Confirm:

- all front and back text is spelled exactly as `plan.json`;
- no text or complete banner/badge outline crosses the red safe line;
- barcode does not cover a preview card or important focal object;
- no AI-drawn barcode box or stray text exists;
- spine blend is clean and text-free;
- cover dimensions and 300 DPI checks pass;
- `pdffonts` reports no fonts;
- the final rendered PDF has no clipping, overlap, transparency, or crop marks;
- cover PDF remains under 40 MB when practical.

## Prompt Skeletons

Front:

```text
Use case: ads-marketing. Asset type: Amazon KDP <square|portrait> coloring-book FRONT COVER artwork.
Primary request: one complete marketplace-ready cover; ALL typography is integral to the generated image, never added later.
Text (verbatim), and these are the ONLY words allowed: "<title>"; "<subtitle>"; "<badge>"; "<author>".
Composition: keep every letter and complete banner/badge inside the central 72-75%; author around 68-72% height; continuing full-bleed artwork below.
Constraints: no incidental signs/labels, barcode, ISBN, QR code, mockup, watermark, publisher mark, extra words, or gibberish.
```

Back:

```text
Use case: ads-marketing. Asset type: Amazon KDP <square|portrait> coloring-book BACK COVER artwork.
Text (verbatim), and these are the ONLY words allowed: "<headline>"; "<tagline>".
Subject: compact 2×3 grid of exactly six equal <square|portrait> cards; top three fully colored, bottom three black-and-white line art.
Composition: every card ends by 68-70% height; bottom 25% contains continuing themed illustration with no card.
Constraints: no barcode, ISBN, QR code, blank rectangle, placeholder, logo, author, extra words, or gibberish.
```

## Output

- `output/<theme>/front_artwork.png`
- `output/<theme>/back_artwork.png`
- `output/<theme>/cover.png`
- `output/<theme>/cover.pdf`
- `output/<theme>/cover_safe_check.png`

Existing cover assets are backed up before replacement.

## Reference

- `references/cover-pitfalls.md`
