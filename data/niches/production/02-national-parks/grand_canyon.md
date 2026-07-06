---
theme_key: grand_canyon
topic: Grand Canyon
audience: adults
style: bold_easy
season: evergreen/gift
primary_keyword: grand canyon coloring book
price: 8.99
pages: 50
status: planned
priority: series vol 4 (after flagship validates)
apify_data: pull before producing
---

# Grand Canyon

**Niche:** National Parks  |  **Vol 4**  |  Theme key: `grand_canyon`

## Concept / sub-angle
canyon layers, river, sunsets

## Primary keyword
`grand canyon coloring book`

## Real Apify data
pull before producing

## Differentiation (series spec)
US national park landscapes + wildlife. Evergreen travel-gift, peaks summer. Realistic-cozy, bold & easy.

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "grand canyon coloring book" > data/niches/apify/grand_canyon.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Grand Canyon: canyon layers, river, sunsets"
# or manual:
python scripts/plan_book.py --concept "Grand Canyon: canyon layers, river, sunsets" --audience adults --pages 50 --theme-key grand_canyon
python scripts/generate_images.py --plan output/grand_canyon/plan.json --count 50
python scripts/build_pdf.py      --theme grand_canyon --author "BoBo Art"
python scripts/generate_cover.py --theme grand_canyon --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/grand_canyon/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
