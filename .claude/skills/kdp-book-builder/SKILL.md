---
name: kdp-book-builder
description: Assemble coloring pages into KDP-ready PDF and generate full book cover. USE WHEN user says 'build coloring book', 'assemble pdf', 'create book pdf', 'build kdp pdf', 'make book cover', 'generate cover', 'kdp book assembly', 'package coloring book'.
---

# KDP Book Builder

Assembles all approved coloring pages into a KDP-compliant PDF interior and generates the full cover (front + spine + back).

---

## When to Use

- After images pass quality review (by `kdp-image-reviewer` skill)
- User wants to build the final PDF and/or cover
- The `/project:kdp-create-book` command reaches the build phase

---

## Process

### Step 1: Verify Prerequisites

Check that:
1. Images exist: `output/images/{theme_key}/`
2. Theme is registered in `config.py`
3. Plan exists: `plans/{theme_key}_plan.json` (for title/subtitle)

If theme not in config.py, register it:
```python
"{theme_key}": {
    "name": "{Title}",
    "book_title": "{Full Title}",
    "prompt_file": "prompts/{theme_key}.txt",
},
```

### Step 2: Build Interior PDF

```bash
python build_pdf.py --theme {theme_key}
```

With custom title/subtitle (from plan):
```bash
python build_pdf.py --theme {theme_key} --title "Book Title" --subtitle "Subtitle Text"
```

**PDF Structure:**
1. Title page — centered title + subtitle + "Bold & Easy Designs"
2. Copyright page — standard copyright notice
3. Coloring pages — each on an odd page with blank back (prevents bleed-through)
4. Thank you page — "Thank You!" + review request
5. Extra blank page if needed (KDP requires even page count)

**Specs:** Page size auto-detected from plan JSON (`page_size` field) or theme config. Supported: 8.5"x11" (portrait) or 8.5"x8.5" (square). No bleed, single-sided coloring pages.

### Step 3: Verify PDF

Check the output:
- File exists: `output/books/{theme_key}_coloring_book.pdf`
- Total page count is even
- Page size is 8.5" x 11"
- All coloring pages are present

### Step 4: Generate Cover

```bash
python generate_cover.py --theme {theme_key} --author "Author Name"
```

With custom title:
```bash
python generate_cover.py --theme {theme_key} --author "Author Name" --title "Custom Title"
```

**Cover layout (left to right):**
- **Back cover**: Light background + description text + barcode placeholder
- **Spine**: Colored bar (text only if 79+ pages)
- **Front cover**: Gemini-generated artwork + title overlay + subtitle + author

**Cover dimensions** are auto-calculated based on page count:
- Spine width = total_pages x 0.002252" (white paper thickness)
- Full width = (2 x 8.5") + spine + (2 x 0.125" bleed)
- Full height = 11" + (2 x 0.125" bleed)

### Step 5: Verify Cover

Check:
- File exists: `covers/{theme_key}_cover.png`
- Front artwork matches theme
- Title/subtitle text is readable
- Author name displays correctly
- Barcode area is clear on back cover

### Step 6: Present Deliverables

Report to user:
```
BOOK COMPLETE!

Interior PDF: output/books/{theme_key}_coloring_book.pdf
  - Pages: {total} (even count)
  - Size: 8.5" x 11"
  - Coloring pages: {num_images} (single-sided with blank backs)

Cover: covers/{theme_key}_cover.png
  - Dimensions: {width}px x {height}px
  - Spine: {spine_width}"

Plan: plans/{theme_key}_plan.json
  - Title: {title}
  - Keywords: {keywords}

NEXT STEPS FOR KDP UPLOAD:
1. Go to kdp.amazon.com
2. Create new Paperback
3. Upload interior PDF
4. Upload cover image
5. Set trim size to 8.5" x 11" (no bleed)
6. Use title, description, and keywords from the plan
```

---

## Output

- `output/books/{theme_key}_coloring_book.pdf` — KDP-ready interior
- `covers/{theme_key}_cover.png` — Full cover at 300 DPI

---

## Quality Criteria

### PDF
- [ ] Even page count
- [ ] Correct page size (8.5"x11" or 8.5"x8.5" per plan)
- [ ] Title page displays correctly
- [ ] All coloring pages present with blank backs
- [ ] Copyright page included
- [ ] Thank you page at the end

### Cover
- [ ] Correct dimensions (auto-calculated for page count)
- [ ] Front artwork is relevant and high-quality
- [ ] Title text is readable over artwork
- [ ] Author name visible
- [ ] Barcode area clear on back
- [ ] 300 DPI resolution
