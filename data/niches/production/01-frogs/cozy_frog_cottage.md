---
theme_key: cozy_frog_cottage
topic: Cozy Frog Cottage
audience: adults
style: bold_easy
season: evergreen/trend
primary_keyword: cozy frog coloring book
price: 8.99
pages: 50
status: planned
priority: series vol 5 (after flagship validates)
apify_data: pull before producing
---

# Cozy Frog Cottage

**Niche:** Cottagecore Frogs  |  **Vol 5**  |  Theme key: `cozy_frog_cottage`

## Concept / sub-angle
frog cottage interiors

## Primary keyword
`cozy frog coloring book`

## Real Apify data
pull before producing

## Differentiation (series spec)
Cozy whimsical frogs in cottagecore scenes (toadstools, ponds, frog cottages, tea, reading, gardens, lanterns). Kawaii cozy, bold & easy. Female-leaning 20-45.

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "cozy frog coloring book" > data/niches/apify/cozy_frog_cottage.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Cozy Frog Cottage: frog cottage interiors"
# or manual:
python scripts/plan_book.py --concept "Cozy Frog Cottage: frog cottage interiors" --audience adults --pages 50 --theme-key cozy_frog_cottage
python scripts/generate_images.py --plan output/cozy_frog_cottage/plan.json --count 50
python scripts/build_pdf.py      --theme cozy_frog_cottage --author "BoBo Art"
python scripts/generate_cover.py --theme cozy_frog_cottage --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/cozy_frog_cottage/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
