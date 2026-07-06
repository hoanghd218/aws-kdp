---
theme_key: hiking_trails
topic: Hiking & Trails
audience: adults
style: bold_easy
season: evergreen/gift
primary_keyword: hiking coloring book for adults
price: 8.99
pages: 50
status: planned
priority: series vol 6 (after flagship validates)
apify_data: pull before producing
---

# Hiking & Trails

**Niche:** National Parks  |  **Vol 6**  |  Theme key: `hiking_trails`

## Concept / sub-angle
trail scenes, gear, vistas

## Primary keyword
`hiking coloring book for adults`

## Real Apify data
pull before producing

## Differentiation (series spec)
US national park landscapes + wildlife. Evergreen travel-gift, peaks summer. Realistic-cozy, bold & easy.

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "hiking coloring book for adults" > data/niches/apify/hiking_trails.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Hiking & Trails: trail scenes, gear, vistas"
# or manual:
python scripts/plan_book.py --concept "Hiking & Trails: trail scenes, gear, vistas" --audience adults --pages 50 --theme-key hiking_trails
python scripts/generate_images.py --plan output/hiking_trails/plan.json --count 50
python scripts/build_pdf.py      --theme hiking_trails --author "BoBo Art"
python scripts/generate_cover.py --theme hiking_trails --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/hiking_trails/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
