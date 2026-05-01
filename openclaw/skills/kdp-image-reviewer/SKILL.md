---
name: kdp-image-reviewer
description: Review coloring book images for quality and KDP compliance, then regenerate bad pages. USE WHEN user says 'review images', 'kiểm tra ảnh', 'check image quality', 'review coloring pages', 'which pages need redo', 'quality check'.
metadata:
  openclaw:
    emoji: "🔍"
    requires:
      bins: ["python3"]
---

# KDP Image Reviewer

Visually reviews every coloring page image, scores PASS / WARN / REDO, then regenerates bad pages.

## Process

### Step 1: Read plan to get audience

```bash
python -c "import json; d=json.load(open('output/{theme_key}/plan.json')); print(d.get('audience','kids'), d.get('page_size','8.5x11'))"
```

### Step 2: Technical scan

```bash
python -c "
from PIL import Image
import os, glob, json

theme = '{theme_key}'
img_dir = f'output/{theme}/images/'
plan = json.load(open(f'output/{theme}/plan.json')) if os.path.exists(f'output/{theme}/plan.json') else {}
size = plan.get('page_size', '8.5x11')
ew, eh = (2550, 2550) if size == '8.5x8.5' else (2550, 3300)

for f in sorted(glob.glob(os.path.join(img_dir, '*.png'))):
    img = Image.open(f)
    name = os.path.basename(f)
    w, h = img.size
    kb = os.path.getsize(f) / 1024
    flag = ''
    if w != ew or h != eh: flag += f' WRONG_SIZE({w}x{h})'
    if img.mode not in ('L','LA'): flag += f' NOT_GRAYSCALE({img.mode})'
    if kb < 50: flag += f' TOO_SMALL({kb:.0f}KB)'
    print(f'{name}: {w}x{h} {img.mode} {kb:.0f}KB{flag}')
"
```

### Step 3: Visual review

Open and visually inspect every image at `output/{theme_key}/images/page_XX.png`.

Score each page: **PASS**, **WARN** (minor issue, usable), or **REDO** (must regenerate).

#### Kids criteria:
- Single subject centered, fills the page
- Bold thick outlines — suitable for crayons
- NO shading, gradients, or gray fills
- No borders/frames, no text in image

#### Adults (cozy/cute) criteria:
- Layered scene: foreground + midground + background
- Large stylized shapes, no dense micro-patterns
- Kawaii proportions, cozy environment
- Clean consistent line weight

#### Always check (CRITICAL):
- **Duplicate character**: mirror/reflection creating a 2nd person → REDO
- **Multiple characters** when prompt says single → REDO
- **Missing/extra limbs**, malformed head, body horror → REDO
- **Solid black fills** instead of outline hatching → REDO
- **Color remnants** (not pure grayscale) → REDO
- **Lines too thin** (below 0.75pt / hairline) → REDO

### Step 4: Report summary table

| Page | Score | Issue |
|------|-------|-------|
| page_01.png | PASS | - |
| page_03.png | REDO | Mirror creates duplicate character |

Then: **Total**: X | **PASS**: X | **WARN**: X | **REDO**: X

### Step 5: Regenerate REDO pages

Ask user to confirm. Then:

1. Delete all REDO pages in one command (never delete page_01 separately):
```bash
rm output/{theme_key}/images/page_03.png output/{theme_key}/images/page_07.png
```

2. Re-run generation once — skip-if-exists handles targeting automatically:
```bash
python generate_images.py --plan output/{theme_key}/plan.json --workers 4
```

3. Re-review regenerated pages visually before proceeding.
