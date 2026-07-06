---
name: kdp-chatgpt-cover-creator
description: Create KDP-ready coloring book cover PNG/PDF using ChatGPT built-in image generation for front/back artwork, then deterministic Python composition for spine, back-cover text, barcode/stamp safe zone, bleed, DPI, and PDF dimensions. Use when the user asks to create, regenerate, fix, or rebuild a KDP cover with ChatGPT imagegen, especially when prompt-generated text, prompt-generated blank barcode areas, or manual cover composition caused errors.
---

# KDP ChatGPT Cover Creator

Create a full-wrap KDP paperback cover from ChatGPT-generated front/back artwork while keeping fragile production details in code.

Use the built-in `image_gen` tool for artwork. Use `scripts/compose_chatgpt_cover.py` for cover math, PDF output, back-cover text overlays, spine blending, and the KDP barcode/stamp safe zone.

## Core Rules

1. **Keep cover text away from the outer edge.** KDP trims the wrap after
   printing (0.125" bleed removed + ~0.25" blade drift), so any letter within
   ~0.375" of an edge can be cut. The front title/subtitle/author are baked into
   the AI artwork, so the prompt must demand a wide empty margin on all sides and
   keep all text inside the central ~80% of the panel. Code overlays already
   respect the 0.375" safe margin.
2. **Never ask image generation to reserve a barcode/stamp blank area.**
   Prompt-generated blank boxes are unreliable. Generate full artwork
   edge-to-edge, then add exactly one barcode/stamp zone by code.

## Workflow

1. Read the book context:
   - `output/<theme>/plan.json`
   - `output/<theme>/interior.pdf`
   - existing `output/<theme>/cover.png` if fixing a cover
   - `scripts/generate_cover.py` and `scripts/kdp_config.py` only when cover dimensions or barcode conventions are unclear

2. Generate front artwork with built-in `image_gen`:
   - Make a square or portrait front panel matching `plan.json.page_size`.
   - Include title/subtitle/author in the prompt only when the user wants text to be part of the image.
   - Spell exact text explicitly, especially author names like `BoBoArt`.
   - Do not include barcode, ISBN, QR code, watermark, or publisher marks.

3. Generate back artwork with built-in `image_gen`:
   - Generate a complete decorative back panel with no blank stamp/barcode area.
   - For coloring books, include sample page cards, decorations, or background art.
   - Avoid all random text unless the user explicitly wants image-generated text.
   - If adding stable text such as a headline or feature list, prefer code overlays via the compose script.

4. Copy selected generated images from `$CODEX_HOME/generated_images/...` into the project:
   - `output/<theme>/front_artwork.png`
   - `output/<theme>/back_artwork.png`
   Keep the original generated files in place.

5. Compose the cover:
   ```bash
   python .agents/skills/kdp-chatgpt-cover-creator/scripts/compose_chatgpt_cover.py \
     --theme <theme> \
     --front output/<theme>/front_artwork.png \
     --back output/<theme>/back_artwork.png \
     --headline "A SUPER CUTE|COLORING ADVENTURE" \
     --feature-line "36 bold and easy pages for kids ages 3-7" \
     --badge-top "BIRTHDAY PARTY" \
     --badge-bottom "Coloring Book"
   ```

6. Validate:
   ```bash
   python scripts/pdf_qc.py --pdf output/<theme>/cover.pdf --cover \
     --expected-width <computed_width> --expected-height <computed_height>
   pdftoppm -png -r 72 output/<theme>/cover.pdf tmp/pdfs/<theme>_cover/cover
   ```
   Inspect the rendered PNG before delivery.

## Prompt Patterns

Front cover prompt essentials:

```text
Use case: ads-marketing
Asset type: Amazon KDP coloring book front cover
Primary request: Create a complete full-color front cover illustration.
Text (verbatim): "<title>"; "<subtitle>"; "<author>"
Constraints: all requested cover text must be part of the generated image itself; keep text inside safe margins; no barcode; no ISBN; no QR code; no watermark; no extra words.
Avoid: misspelled text, distorted letters, cropped title, blank boxes, mockup.
```

Back cover prompt essentials:

```text
Use case: ads-marketing
Asset type: Amazon KDP coloring book back cover artwork
Primary request: Create a complete decorative back cover image.
Composition/framing: fill the entire panel with artwork; include sample coloring-page cards if useful.
Constraints: no barcode, no ISBN, no QR code, no blank stamp area, no white rectangle, no large empty placeholder.
Avoid: prompt-generated blank boxes, random words, mockup.
```

## Barcode/Stamp Rules

- Add the barcode/stamp zone only in code.
- Use the repo convention from `scripts/generate_cover.py`: `2.0in x 1.2in`, bottom-right of the back cover, inside the safe margin.
- Do not write `BARCODE AREA`, `ISBN`, or any placeholder text inside the zone.
- If KDP supplies an exact required cover size, pass `--kdp-width` and `--kdp-height` to the compose script.

## Output

The compose script writes:

- `output/<theme>/cover.png`
- `output/<theme>/cover.pdf`

It backs up existing cover files into `output/<theme>/backups/` before overwriting.
