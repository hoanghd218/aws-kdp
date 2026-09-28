---
name: kdp-book-builder
description: Assemble reviewed coloring pages and polished front matter into a KDP-ready interior PDF, build an imagegen-based full-wrap cover, and run preflight checks. Use after page review or when packaging a coloring book for KDP.
---

# KDP Book Builder

## Prerequisites

- valid `output/<theme>/plan.json`;
- every expected `images/page_XX.png` reviewed;
- composed title page, designed welcome/copyright page 2, and four-step instructions page 3;
- exact title, subtitle, author, trim, and page count finalized.

## Interior

Prefer the designed front-matter path:

```bash
python3 .agents/skills/kdp-frontmatter-pages/scripts/assemble_frontmatter.py <theme>
python3 scripts/pdf_qc.py --pdf output/<theme>/interior.pdf --trim <size>
```

Use `scripts/build_pdf.py` only when illustrated front matter is unavailable. Verify title/author consistency, the designed page 2 and page 3, all coloring pages, right-hand coloring pages with blank backs, correct trim, embedded fonts, and no excessive blank sequence. The closing/thank-you page must be the final manuscript page; never append a trailing blank merely to make the PDF page count even.

## Cover

Use `$kdp-chatgpt-cover-creator`: built-in imagegen creates the complete cover artwork with all final title, subtitle, author/brand, and back-cover copy already visible in the generated image. Code may assemble the full-wrap geometry and reserve the barcode area, but must not add or overlay cover typography. Compose with `--no-back-text`. The final upload asset is `cover.pdf`, not only `cover.png`.

## Preflight

Run `$kdp-cover-checker` and `$quality-reviewer`, then visually inspect rendered PDFs. Do not add spine text below 79 pages. Confirm 300-DPI assets, bleed, safe zones, clear barcode area, and truthful listing claims.

The upload handoff must remind the user to disclose AI-generated cover and interior images and not to classify a coloring book as low-content by default.

## Repair markers and author-suffixed folders

When the user asks to mark repaired books, add `production_status: "FIXED"`,
`folder_name`, and `fixed_date` to the plan, add a short `FIXED.md` marker in
the book folder, and put `Status: FIXED` in the production report. For the
user's current library convention, rename the deliverable folder to
`<theme_key>_<author_slug>` (for example, `rockets_astronauts_Lanternleaf_Studio`).
Keep the original `theme_key` as the stable catalog identifier and use
`folder_name` for the filesystem name so existing metadata and historical
references remain traceable.
