---
name: kdp-create-book
description: End-to-end KDP coloring book creation pipeline. USE WHEN user says 'tạo sách', 'create coloring book', 'make a book', 'tạo sách tô màu', 'làm sách kdp', 'create book about', 'tạo sách về'.
metadata:
  openclaw:
    emoji: "📖"
    requires:
      bins: ["python3"]
      env: ["GOOGLE_API_KEY", "IMAGE_RENDERER"]
---

# KDP Create Book

Full pipeline: plan → generate images → review → build PDF → build cover → upload to Google Drive → report link.

## Step 1: Interview user

Ask if not already provided:
- **Concept**: what is the book about? (e.g. "mèo cute trong quán cà phê")
- **Audience**: `kids` (6-12) or `adults` or `anime`
- **Pages**: how many coloring pages? (20-30 recommended)
- **Theme key**: short snake_case folder name (e.g. `cozy_cat_cafe`)
- **Author name**: for cover and title page

Confirm before proceeding:
```
Concept: {concept}
Audience: {audience}
Pages: {pages}
Theme key: {theme_key}
Author: {author}
```

## Step 2: Plan the book

```bash
python plan_book.py --concept "{concept}" --audience {audience} --pages {pages} --theme-key {theme_key}
```

For anime/manga style:
```bash
python plan_book.py --concept "{concept}" --audience anime --pages {pages} --theme-key {theme_key} --style "anime manga action"
```

Verify:
```bash
python -c "import json; d=json.load(open('output/{theme_key}/plan.json')); print('Title:', d['title']); print('Prompts:', len(d['page_prompts']))"
```

Tell user the generated title and keyword summary.

## Step 3: Generate images

```bash
python generate_images.py --plan output/{theme_key}/plan.json --count {pages}
```

Monitor progress. If any pages fail after 3 retries, note them and continue.

Verify all pages exist:
```bash
ls output/{theme_key}/images/ | wc -l
```

## Step 4: Review images

Visually inspect every image at `output/{theme_key}/images/page_XX.png`.

Score each: **PASS**, **WARN**, or **REDO**.

#### Kids criteria:
- Single subject, bold thick outlines, no shading, no borders

#### Adults/anime criteria:
- Layered scene, clean lines, no solid black fills, no duplicate characters

#### Always REDO if:
- Mirror/reflection creates duplicate character
- Multiple characters when only one intended
- Solid black fills instead of outline hatching
- Color remnants (not pure grayscale)
- Hairline-thin lines (below 0.75pt)
- Missing/extra limbs or body horror

If REDO pages found — delete them all at once, then regenerate:
```bash
rm output/{theme_key}/images/page_03.png output/{theme_key}/images/page_07.png
python generate_images.py --plan output/{theme_key}/plan.json --workers 4
```

Re-review regenerated pages. Repeat until all pages are PASS or WARN.

## Step 5: Build interior PDF

```bash
python build_pdf.py --theme {theme_key} --author "{author}"
```

Verify:
```bash
ls -lh output/{theme_key}/interior.pdf
```

## Step 6: Build cover

```bash
python generate_cover.py --theme {theme_key} --author "{author}"
```

Verify:
```bash
ls -lh output/{theme_key}/cover.png output/{theme_key}/cover.pdf
```

## Step 7: Upload to Google Drive

Use the GOG skill to upload both files to Google Drive:

1. Upload interior PDF:
   > "Upload file output/{theme_key}/interior.pdf to Google Drive folder KDP Books/{theme_key}"

2. Upload cover PDF:
   > "Upload file output/{theme_key}/cover.pdf to Google Drive folder KDP Books/{theme_key}"

Save both Drive links returned by GOG.

## Step 8: Report to user

```
✅ SÁCH HOÀN THÀNH!

📚 {title}
👤 Tác giả: {author}
📄 Trang: {total_pages}
🎨 Ảnh: {num_images} trang tô màu

🔗 Google Drive:
  Interior PDF: {drive_link_interior}
  Cover PDF:    {drive_link_cover}

📋 KDP Upload checklist:
  1. kdp.amazon.com → Create Paperback
  2. Upload interior PDF
  3. Upload cover PDF  
  4. Trim size: {page_size} (no bleed)
  5. Dùng title/description/keywords từ plan.json
```

## Notes

- Never delete `page_01.png` separately — causes data loss
- Author name must be identical on interior and cover — KDP rejects mismatches
- Spine text only if 79+ pages
- GOG skill must be installed and authorized for Google Drive upload: `openclaw skills install gog`
