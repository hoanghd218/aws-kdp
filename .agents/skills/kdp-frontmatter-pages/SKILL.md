---
name: kdp-frontmatter-pages
description: Create polished illustrated title, copyright/welcome, instructions, ownership, and closing pages for a KDP coloring book using built-in imagegen for text-free art and deterministic code for exact copy, then merge and QC the interior. Use for front matter, title pages, copyright pages, instruction pages, thank-you pages, or "This Book Belongs To" pages.
---

# KDP Frontmatter Pages

Create designed book pages without trusting an image model to spell text. Built-in imagegen supplies themed grayscale artwork; `compose_frontmatter.py` supplies exact title, author, ownership lines, closing copy, and review request.

## 1. Write book-specific copy

Read `plan.json`, the content strategy, and several page prompts. Add or improve:

```json
"front_matter": {
  "title_kicker": "specific promise, not generic filler",
  "copyright_kicker": "short themed welcome line",
  "copyright_heading": "A NOTE BEFORE YOU BEGIN",
  "copyright_message": "2 concise sentences tied to the book's actual experience",
  "instructions_kicker": "short practical promise",
  "instructions_heading": "HOW TO ENJOY THIS BOOK",
  "instructions_steps": [
    {"title": "specific action", "body": "one useful sentence"},
    {"title": "specific action", "body": "one useful sentence"},
    {"title": "specific action", "body": "one useful sentence"},
    {"title": "specific action", "body": "one useful sentence"}
  ],
  "instructions_footer": "one warm, theme-specific permission to experiment",
  "ownership_heading": "THIS BOOK BELONGS TO",
  "closing_heading": "theme-specific closing headline",
  "closing_message": "2–3 warm, concrete sentences tied to this book",
  "review_request": "neutral request for an honest Amazon review"
}
```

Reject generic copy such as “Thank you for being here,” “Made with love,” or vague text that could appear in any book. Do not request a positive or five-star rating.

For coloring books, make the four instruction steps genuinely useful: recommend suitable tools, a protective sheet for markers, a simple layering approach, and permission to choose a personal palette. Adapt the wording to the audience and medium instead of copying a generic block unchanged.

## 2. Generate text-free artwork

Read `references/prompt-templates.md`. Make one built-in imagegen call per asset:

- `1_artwork.png`: title-page decoration with central negative space;
- `copyright_artwork.png`: welcoming copyright-page decoration with central negative space;
- `instructions_artwork.png`: light perimeter motifs with a clean field for practical guidance;
- `2_artwork.png`: optional kids ownership-page decoration;
- `3_artwork.png`: closing-page decoration with central negative space.

Require grayscale line art, correct trim ratio, safe white margins, and no text, letters, numbers, logos, watermark, border, or mockup. Save generated sources to the project and normalize with `scripts/prepare_imagegen_asset.py --mode grayscale-art`.

## 3. Compose exact text

```bash
python3 .agents/skills/kdp-frontmatter-pages/scripts/compose_frontmatter.py <theme>
```

Use `--skip-belongs` for adult books. Use `--overwrite` only after reviewing the existing final pages; the script backs up replaced pages.

Outputs:

- `frontmatter/1.png` — exact title/subtitle/author;
- `frontmatter/copyright.png` — designed welcome and legal copy;
- `frontmatter/instructions.png` — exact book-use guidance;
- `frontmatter/2.png` — kids ownership page, optional;
- `frontmatter/3.png` — polished closing copy and honest-review request.

## 4. Inspect, merge, and QC

Open each composed PNG and verify spelling, metadata consistency, visual hierarchy, safe margins, and trim ratio. Then run:

```bash
python3 .agents/skills/kdp-frontmatter-pages/scripts/assemble_frontmatter.py <theme>
python3 scripts/pdf_qc.py --pdf output/<theme>/interior.pdf --trim <size>
```

Render the title, copyright, ownership, first coloring page, last coloring page, and closing page for visual inspection.

Default adult page order:

`Title (1)` → `Designed welcome/copyright (2)` → `Instructions (3)` → `Blank layout back (4)` → coloring pages on odd right-hand pages with blank backs → `Closing` as the true final page.

The page-4 blank is intentional: it is the reverse of the instructions leaf and keeps the first coloring page on a right-hand page. It is not interchangeable with a trailing blank after the closing page.

## Rules

- Exact production text is always code-rendered.
- Every code-rendered heading must be measured against the panel's inner width and auto-scaled or wrapped before saving; never allow ownership, title, instruction, or closing text to clip at the page edge.
- The legal copyright page stays deterministic and separate.
- Page 2 should combine welcoming, theme-specific copy with concise deterministic legal text; do not ship a visually raw legal page.
- Page 3 should contain four concise, practical instructions with clear hierarchy and audience-appropriate language.
- Front-matter art must match the interior style bible without duplicating a coloring page.
- The closing page may request an honest review but cannot incentivize, pressure, or specify a star rating.
- The closing page is the final interior page. Do not append a blank page solely to force an even page count.
- Built-in imagegen is the default. Do not silently use the legacy provider script.
