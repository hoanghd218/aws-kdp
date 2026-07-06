---
theme_key: bold_easy_parks
topic: Bold & Easy Parks
audience: adults
style: bold_easy
season: evergreen/gift
primary_keyword: bold and easy national parks coloring book
price: 8.99
pages: 50
status: planned
priority: series vol 7 (after flagship validates)
apify_data: pull before producing
---

# Bold & Easy Parks

**Niche:** National Parks  |  **Vol 7**  |  Theme key: `bold_easy_parks`

## Concept / sub-angle
large print

## Primary keyword
`bold and easy national parks coloring book`

## Real Apify data
pull before producing

## Differentiation (series spec)
US national park landscapes + wildlife. Evergreen travel-gift, peaks summer. Realistic-cozy, bold & easy.

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "bold and easy national parks coloring book" > data/niches/apify/bold_easy_parks.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Bold & Easy Parks: large print"
# or manual:
python scripts/plan_book.py --concept "Bold & Easy Parks: large print" --audience adults --pages 50 --theme-key bold_easy_parks
python scripts/generate_images.py --plan output/bold_easy_parks/plan.json --count 50
python scripts/build_pdf.py      --theme bold_easy_parks --author "BoBo Art"
python scripts/generate_cover.py --theme bold_easy_parks --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/bold_easy_parks/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
