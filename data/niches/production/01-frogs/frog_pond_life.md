---
theme_key: frog_pond_life
topic: Frog Pond Life
audience: adults
style: bold_easy
season: evergreen/trend
primary_keyword: frog pond coloring book for adults
price: 8.99
pages: 50
status: planned
priority: series vol 3 (after flagship validates)
apify_data: pull before producing
---

# Frog Pond Life

**Niche:** Cottagecore Frogs  |  **Vol 3**  |  Theme key: `frog_pond_life`

## Concept / sub-angle
lily ponds, cattails, dragonflies

## Primary keyword
`frog pond coloring book for adults`

## Real Apify data
pull before producing

## Differentiation (series spec)
Cozy whimsical frogs in cottagecore scenes (toadstools, ponds, frog cottages, tea, reading, gardens, lanterns). Kawaii cozy, bold & easy. Female-leaning 20-45.

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "frog pond coloring book for adults" > data/niches/apify/frog_pond_life.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Frog Pond Life: lily ponds, cattails, dragonflies"
# or manual:
python scripts/plan_book.py --concept "Frog Pond Life: lily ponds, cattails, dragonflies" --audience adults --pages 50 --theme-key frog_pond_life
python scripts/generate_images.py --plan output/frog_pond_life/plan.json --count 50
python scripts/build_pdf.py      --theme frog_pond_life --author "BoBo Art"
python scripts/generate_cover.py --theme frog_pond_life --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/frog_pond_life/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
