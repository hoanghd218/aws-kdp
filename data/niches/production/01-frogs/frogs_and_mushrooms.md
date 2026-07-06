---
theme_key: frogs_and_mushrooms
topic: Frogs & Mushrooms
audience: adults
style: bold_easy
season: evergreen/trend
primary_keyword: frog and mushroom coloring book
price: 8.99
pages: 50
status: planned
priority: series vol 2 (after flagship validates)
apify_data: pull before producing
---

# Frogs & Mushrooms

**Niche:** Cottagecore Frogs  |  **Vol 2**  |  Theme key: `frogs_and_mushrooms`

## Concept / sub-angle
frog + mushroom forest combo

## Primary keyword
`frog and mushroom coloring book`

## Real Apify data
pull before producing

## Differentiation (series spec)
Cozy whimsical frogs in cottagecore scenes (toadstools, ponds, frog cottages, tea, reading, gardens, lanterns). Kawaii cozy, bold & easy. Female-leaning 20-45.

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "frog and mushroom coloring book" > data/niches/apify/frogs_and_mushrooms.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Frogs & Mushrooms: frog + mushroom forest combo"
# or manual:
python scripts/plan_book.py --concept "Frogs & Mushrooms: frog + mushroom forest combo" --audience adults --pages 50 --theme-key frogs_and_mushrooms
python scripts/generate_images.py --plan output/frogs_and_mushrooms/plan.json --count 50
python scripts/build_pdf.py      --theme frogs_and_mushrooms --author "BoBo Art"
python scripts/generate_cover.py --theme frogs_and_mushrooms --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/frogs_and_mushrooms/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
