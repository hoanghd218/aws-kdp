---
name: kdp-frontmatter-pages
description: Create polished illustrated title, copyright/welcome, instructions, ownership, and closing pages for a KDP coloring book using built-in imagegen for text-free art and deterministic code for exact copy, then merge and QC the interior. Use for front matter, title pages, copyright pages, instruction pages, thank-you pages, or "This Book Belongs To" pages.
---

# KDP Frontmatter Pages

Use the canonical project implementation in `.agents/skills/kdp-frontmatter-pages/`. Do not maintain a second divergent front-matter workflow under `.claude`.

## Workflow

1. Read `output/<theme>/plan.json`, the content strategy, and representative page prompts.
2. Follow `.agents/skills/kdp-frontmatter-pages/SKILL.md` completely.
3. Load `.agents/skills/kdp-frontmatter-pages/references/prompt-templates.md` for text-free artwork prompts.
4. Use built-in imagegen for each artwork asset; normalize every accepted result into the project.
5. Render all exact production text with the canonical compositor:

```bash
python3 .agents/skills/kdp-frontmatter-pages/scripts/compose_frontmatter.py <theme>
```

6. Assemble and QC with:

```bash
python3 .agents/skills/kdp-frontmatter-pages/scripts/assemble_frontmatter.py <theme>
python3 scripts/pdf_qc.py --pdf output/<theme>/interior.pdf --trim <size>
```

## Default adult page order

`Title (1)` → `Designed welcome/copyright (2)` → `Instructions (3)` → `Blank layout back (4)` → coloring pages on odd right-hand pages with blank backs → `Closing` as the true final page.

The page-4 blank is intentional and keeps the first coloring page on a right-hand page. Never append a blank after the closing page solely to force an even page count.

## Required quality rules

- Generate front-matter artwork without words, letters, numbers, logos, borders, watermarks, or mockups.
- Compose the exact title, author/brand, welcome, legal copy, instructions, closing copy, and review request with code.
- Page 2 must be visually designed and book-specific, not a raw legal text page.
- Page 3 must provide four useful instructions: tools, page protection, a simple technique, and creative freedom, adapted to the audience and book.
- Adult books skip the ownership page unless the user explicitly requests one.
- Review title, pages 2–3, first and last coloring pages, closing page, and trim/margins from rendered PDF images.
