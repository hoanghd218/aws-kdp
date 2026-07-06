---
theme_key: national_park_wildlife
topic: National Park Wildlife
audience: adults
style: bold_easy
season: evergreen/gift
primary_keyword: national park wildlife coloring book
price: 8.99
pages: 50
status: planned
priority: series vol 5 (after flagship validates)
apify_data: pull before producing
---

# National Park Wildlife

**Niche:** National Parks  |  **Vol 5**  |  Theme key: `national_park_wildlife`

## Concept / sub-angle
bears, elk, eagles

## Primary keyword
`national park wildlife coloring book`

## Real Apify data
pull before producing

## Differentiation (series spec)
US national park landscapes + wildlife. Evergreen travel-gift, peaks summer. Realistic-cozy, bold & easy.

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "national park wildlife coloring book" > data/niches/apify/national_park_wildlife.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "National Park Wildlife: bears, elk, eagles"
# or manual:
python scripts/plan_book.py --concept "National Park Wildlife: bears, elk, eagles" --audience adults --pages 50 --theme-key national_park_wildlife
python scripts/generate_images.py --plan output/national_park_wildlife/plan.json --count 50
python scripts/build_pdf.py      --theme national_park_wildlife --author "BoBo Art"
python scripts/generate_cover.py --theme national_park_wildlife --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/national_park_wildlife/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
