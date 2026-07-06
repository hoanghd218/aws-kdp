---
theme_key: bold_easy_frogs
topic: Bold & Easy Frogs
audience: adults
style: bold_easy
season: evergreen/trend
primary_keyword: bold and easy frog coloring book
price: 8.99
pages: 50
status: planned
priority: series vol 7 (after flagship validates)
apify_data: pull before producing
---

# Bold & Easy Frogs

**Niche:** Cottagecore Frogs  |  **Vol 7**  |  Theme key: `bold_easy_frogs`

## Concept / sub-angle
large print seniors/beginners

## Primary keyword
`bold and easy frog coloring book`

## Real Apify data
pull before producing

## Differentiation (series spec)
Cozy whimsical frogs in cottagecore scenes (toadstools, ponds, frog cottages, tea, reading, gardens, lanterns). Kawaii cozy, bold & easy. Female-leaning 20-45.

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "bold and easy frog coloring book" > data/niches/apify/bold_easy_frogs.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Bold & Easy Frogs: large print seniors/beginners"
# or manual:
python scripts/plan_book.py --concept "Bold & Easy Frogs: large print seniors/beginners" --audience adults --pages 50 --theme-key bold_easy_frogs
python scripts/generate_images.py --plan output/bold_easy_frogs/plan.json --count 50
python scripts/build_pdf.py      --theme bold_easy_frogs --author "BoBo Art"
python scripts/generate_cover.py --theme bold_easy_frogs --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/bold_easy_frogs/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
