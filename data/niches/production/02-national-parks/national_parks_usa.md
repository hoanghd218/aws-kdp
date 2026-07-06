---
theme_key: national_parks_usa
topic: US National Parks
audience: adults
style: bold_easy
season: evergreen/gift
primary_keyword: national parks coloring book for adults
price: 8.99
pages: 50
status: planned
priority: FLAGSHIP (produce first)
apify_data: REAL: Opp 4.14, 66/mo, rev 16 (MODERATE strong)
---

# US National Parks

**Niche:** National Parks  |  **Vol 1**  |  Theme key: `national_parks_usa`

## Concept / sub-angle
FLAGSHIP — iconic park vistas

## Primary keyword
`national parks coloring book for adults`

## Real Apify data
REAL: Opp 4.14, 66/mo, rev 16 (MODERATE strong)

## Differentiation (series spec)
US national park landscapes + wildlife. Evergreen travel-gift, peaks summer. Realistic-cozy, bold & easy.

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "national parks coloring book for adults" > data/niches/apify/national_parks_usa.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "US National Parks: FLAGSHIP — iconic park vistas"
# or manual:
python scripts/plan_book.py --concept "US National Parks: FLAGSHIP — iconic park vistas" --audience adults --pages 50 --theme-key national_parks_usa
python scripts/generate_images.py --plan output/national_parks_usa/plan.json --count 50
python scripts/build_pdf.py      --theme national_parks_usa --author "BoBo Art"
python scripts/generate_cover.py --theme national_parks_usa --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/national_parks_usa/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
