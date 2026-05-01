---
name: kdp-book-builder
description: Build KDP interior PDF and full cover from reviewed images. USE WHEN user says 'build pdf', 'tạo pdf', 'assemble book', 'build cover', 'tạo bìa', 'đóng gói sách', 'build coloring book'.
metadata:
  openclaw:
    emoji: "📚"
    requires:
      bins: ["python3"]
---

# KDP Book Builder

Assembles reviewed coloring pages into a KDP-compliant interior PDF and generates the full cover.

## Process

### Step 1: Read plan details

```bash
python -c "
import json
d = json.load(open('output/{theme_key}/plan.json'))
print('Title:', d.get('title'))
print('Author:', d.get('author', ''))
print('Pages:', len(d.get('page_prompts', [])))
print('Size:', d.get('page_size', '8.5x11'))
"
```

### Step 2: Build interior PDF

```bash
python build_pdf.py --theme {theme_key} --author "{author}"
```

With title override:
```bash
python build_pdf.py --theme {theme_key} --title "{title}" --subtitle "{subtitle}" --author "{author}"
```

Verify output:
```bash
ls -lh output/{theme_key}/interior.pdf
```

### Step 3: Generate cover

```bash
python generate_cover.py --theme {theme_key} --author "{author}"
```

Verify output:
```bash
ls -lh output/{theme_key}/cover.png output/{theme_key}/cover.pdf
```

### Step 4: KDP pre-flight checklist

- [ ] `interior.pdf` exists and > 1MB
- [ ] `cover.pdf` exists and > 500KB
- [ ] Page count is even
- [ ] Title on interior title page matches cover title
- [ ] Author name consistent across interior + cover
- [ ] No spine text if book < 79 pages
- [ ] Barcode area clear on back cover (no template text)

### Step 5: Report deliverables

Tell user:
```
✅ BOOK READY

Interior: output/{theme_key}/interior.pdf
Cover:    output/{theme_key}/cover.pdf

Title: {title}
Pages: {total} (even count)
Size: {page_size}
Spine: {spine_width}"
```

## Notes

- Author name must be consistent across interior and cover — KDP rejects mismatches
- Spine text only appears if 79+ pages
- Even page count is enforced automatically by `build_pdf.py`
