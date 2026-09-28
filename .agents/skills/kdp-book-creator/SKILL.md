---
name: kdp-book-creator
description: "Create a complete KDP coloring book from a concept: commercial validation, plan and polished front matter, built-in imagegen artwork, visual review, PDF assembly, imagegen cover, and KDP preflight. Use when the user asks to create, build, or make a coloring book end to end, including Vietnamese requests such as 'tạo sách tô màu'."
---

# KDP Book Creator

Run the pipeline inline. Do not use subagents unless the user explicitly requests delegation. Codex writes all prompts, metadata, and book copy. Use the built-in `imagegen` skill for every generated raster asset; do not call Gemini or a provider CLI unless the user explicitly chooses that fallback.

## Execution contract

- Pause only for the interview and plan approval.
- Continue automatically between all other phases.
- Never leave a project asset only under `$CODEX_HOME/generated_images`; normalize and save it under `output/<theme>/`.
- Keep interior and front-matter artwork text-free, then render their exact copy with code. For the cover only, follow `$kdp-chatgpt-cover-creator`: bake the exact title, author/brand, and back-cover typography into the generated front/back panels; code may only assemble the wrap and stamp the barcode zone.
- Do not silently replace built-in imagegen with an API/CLI renderer. If imagegen is unavailable, explain the fallback and wait for explicit approval.

## Pipeline

```
0. Commercial gate (when profit/niche matters)
1. Interview                                      [pause]
2. Product plan + prompts + polished book copy
3. Plan review                                    [pause]
4. Built-in imagegen: interiors + front matter
5. Visual review + targeted regeneration
6. Interior assembly
7. Built-in imagegen: cover art + code composition
8. Preflight + delivery
```

## Phase 0 — Commercial gate

If the user wants a profitable book, a niche recommendation, or has not validated the concept:

1. Use `$kdp-niche-finder` before production.
2. Require fresh Amazon evidence, at least 60% relevant top results, at least 5 usable BSR/review observations, demand depth, no single-winner distortion, and an IP-risk check.
3. Save the verdict in `plan.json.niche_validation`.
4. Produce only the flagship first. Do not batch a series until the flagship has real sales/conversion evidence.

If the user explicitly wants a creative/personal project, record `commercial_validation: "user_skipped"` and proceed without pretending the niche is validated.

## Phase 1 — Interview

Collect only missing inputs:

1. Concept and differentiating angle.
2. Audience: adults or kids, with age range for kids.
3. Trim: `8.5x8.5` (default for bold/easy) or `8.5x11`.
4. Number of unique coloring pages; recommend 30–40 for a market product.
5. Theme key (snake_case).
6. Author/pen name.
7. Tone/style references and any prohibited subjects.

Proceed immediately once answered.

## Phase 2 — Product plan, prompts, and copy

Read the appropriate prompt guide in `.agents/skills/kdp-prompt-writer/references/` and create `output/<theme>/plan.json`.

### Product and content strategy

Before writing page prompts, define:

- one-sentence buyer promise;
- a visual style bible: character/subject invariants, line weight, detail density, palette for cover art, and forbidden elements;
- a content arc split into 4–6 sections, with deliberate changes in setting, activity, mood, pose, and composition;
- a duplication matrix proving no two pages repeat the same subject + activity + setting;
- exact production facts: unique page count, single-sided layout, trim, audience, and media suitability.

### Editorial standard

Write book-specific front matter. Generic filler such as “Thank you for being here,” “Made with love,” or a vague introduction is not acceptable.

Required `front_matter` fields:

```json
{
  "title_kicker": "short audience-appropriate promise",
  "copyright_kicker": "short themed welcome line",
  "copyright_heading": "A NOTE BEFORE YOU BEGIN",
  "copyright_message": "2 concise sentences tied to the actual book experience",
  "instructions_kicker": "short practical promise",
  "instructions_heading": "HOW TO ENJOY THIS BOOK",
  "instructions_steps": [
    {"title": "tool choice", "body": "one useful sentence"},
    {"title": "page protection", "body": "one useful sentence"},
    {"title": "coloring technique", "body": "one useful sentence"},
    {"title": "creative permission", "body": "one useful sentence"}
  ],
  "instructions_footer": "one warm, theme-specific closing line",
  "ownership_heading": "kids only; exact heading",
  "closing_heading": "theme-specific closing headline",
  "closing_message": "2–3 warm sentences tied to real scenes or feelings in this book",
  "review_request": "one neutral request for an honest Amazon review; no rating incentive"
}
```

The exact title, subtitle, and author/brand on the title page must match the KDP listing and cover. Read the configured default author from `config.DEFAULT_AUTHOR` when present; never hardcode a legacy brand into prompts or templates.

### Imagegen prompts

Use the `illustration-story` taxonomy for interior/front-matter artwork and `ads-marketing` for cover artwork.

Every coloring prompt must include:

- asset type and intended trim/aspect ratio;
- scene, subject, style, composition, and detail density;
- pure black-and-white line art, white background, bold clean closed outlines, no shading/gray/color;
- no border/frame, text, letters, numbers, signature, watermark, crop marks, or page mockup;
- anatomy and count invariants;
- enough safe white margin for no-bleed printing.

Front-matter prompts create artwork only and require usable negative space for deterministic code-rendered copy. Cover prompts are the exception: include a strict `Text (verbatim)` clause so required cover typography is baked into the panel artwork, while forbidding every extra word, incidental label, ISBN, barcode, QR code, blank placeholder box, and mockup.

### Plan schema

```json
{
  "theme_key": "...",
  "concept": "...",
  "audience": "adults|kids",
  "age_range": "...",
  "page_size": "8.5x8.5|8.5x11",
  "page_count": 36,
  "title": "...",
  "subtitle": "...",
  "description": "...",
  "keywords": ["7 exact backend phrases"],
  "categories": ["...", "..."],
  "author": {"first_name": "...", "last_name": "..."},
  "ai_disclosure": {"interior_images": "ai_generated", "cover_artwork": "ai_generated"},
  "niche_validation": {},
  "content_strategy": {
    "buyer_promise": "...",
    "style_bible": {},
    "sections": [],
    "duplication_matrix": []
  },
  "front_matter": {},
  "frontmatter_art_prompts": {
    "title": "artwork only",
    "copyright": "artwork only",
    "instructions": "artwork only",
    "belongs_to": "artwork only or null",
    "closing": "artwork only"
  },
  "cover_prompt": "complete front panel with exact baked typography",
  "back_cover_prompt": "complete back panel with exact baked typography",
  "page_prompts": ["one distinct structured prompt per page"]
}
```

Validate JSON and also write `output/<theme>/prompts.txt`.

## Phase 3 — Plan review

Show:

- niche evidence/confidence and any commercial caveat;
- title, subtitle, listing description, keywords, categories, author;
- buyer promise, section arc, style bible, and duplicate-risk summary;
- exact title-page, page-2 welcome/copyright, page-3 instructions, and closing-page copy;
- 5 representative page prompts plus front/back cover artwork prompts.

Ask for approval to generate. Apply requested edits directly and show the delta.

## Phase 4 — Generate interiors and front-matter art with imagegen

For each distinct prompt, make one built-in `image_gen` call. Do not use `n` to represent different pages.

For each returned coloring-page source:

```bash
python3 scripts/prepare_imagegen_asset.py \
  --input <generated-source-path> \
  --output output/<theme>/images/page_XX.png \
  --size <page_size> --mode line-art
```

Generate front-matter artwork separately and normalize it to:

```
output/<theme>/frontmatter/1_artwork.png
output/<theme>/frontmatter/copyright_artwork.png
output/<theme>/frontmatter/instructions_artwork.png
output/<theme>/frontmatter/2_artwork.png   # kids only
output/<theme>/frontmatter/3_artwork.png
```

Use `--mode grayscale-art`. Then compose exact text:

```bash
python3 .agents/skills/kdp-frontmatter-pages/scripts/compose_frontmatter.py <theme>
```

Record the final prompt set and built-in imagegen as the renderer in the production report.

## Phase 5 — Review every image

Open every page with the image-viewing tool. Score PASS/WARN/REDO using `$kdp-image-reviewer`.

Any of these is REDO: color/heavy shading, border, text, broken line art, duplicate/merged anatomy, extra/missing limbs, unintended second figure, distorted object, obvious crop, inconsistent style, or prompt mismatch.

For a REDO, make one targeted prompt change, regenerate that asset with built-in imagegen, normalize with `--overwrite`, and review again. Maximum two regeneration attempts per page. If more than 20% remain unresolved, stop for a systemic prompt/style correction instead of shipping a weak book.

## Phase 6 — Assemble the interior

Use illustrated front matter when available:

```bash
python3 .agents/skills/kdp-frontmatter-pages/scripts/assemble_frontmatter.py <theme>
python3 scripts/pdf_qc.py --pdf output/<theme>/interior.pdf --trim <page_size>
```

Use `scripts/build_pdf.py` only as a polished deterministic fallback. For adult coloring books, default to title page 1, designed welcome/copyright page 2, practical instructions page 3, a layout blank on page 4, then coloring pages on odd right-hand pages with blank backs. End on the closing page; never append a trailing blank solely to force an even manuscript count. Verify title/author consistency, correct trim, right-hand coloring pages, blank backs, and no excessive blank runs.

## Phase 7 — Generate and compose the cover

1. Generate full-color front and back panel artwork in two separate built-in imagegen calls.
2. Save sources inside the project as `front_artwork.png` and `back_artwork.png`.
3. Bake all visible cover typography into the generated front/back artwork. The prompts must declare exact verbatim strings and forbid extra words, incidental labels, barcodes, and placeholders.
4. Use code only to assemble the wrap, calculate dimensions, blend the spine, and stamp the barcode zone:

```bash
python3 .agents/skills/kdp-chatgpt-cover-creator/scripts/compose_chatgpt_cover.py \
  --theme <theme> \
  --front output/<theme>/front_artwork.png \
  --back output/<theme>/back_artwork.png \
  --no-back-text
```

Do not add spine text below 79 interior pages. Render the cover PDF to PNG and inspect it at full size and thumbnail size.

## Phase 8 — Preflight and delivery

Run the cover checker and quality reviewer. Confirm:

- cover/interior/listing metadata match exactly;
- cover is one PDF with correct bleed, dimensions, safe zones, and 300-DPI assets;
- barcode area is clear and contains no placeholder text;
- every listing claim matches the actual book;
- no trademarked characters, logos, artist imitation, or misleading claims;
- the KDP upload is marked **AI-generated** for both interior images and cover artwork;
- coloring books are not marked low-content by default; Amazon says they are generally not low-content.

Deliver absolute clickable paths for `interior.pdf`, `cover.pdf`, `cover.png`, and `plan.json`, plus PASS/WARN counts and unresolved issues.

## Failure handling

- Built-in imagegen failure: retry once; then report the blocker. Offer CLI/provider fallback only with explicit user approval.
- Bad generated text: this should not occur because production text is code-rendered. Fix the plan copy or compositor, not the image prompt.
- Systemic visual failure: revise the style bible/base prompt and regenerate the affected set.
- Cover/front-matter typo: fix `plan.json` and rerun the deterministic compositor.
- Never publish or upload automatically; delivery ends with verified local artifacts and upload guidance.
