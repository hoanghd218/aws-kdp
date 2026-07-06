---
theme_key: kayak_fishing
topic: Kayak Fishing
audience: adults
style: bold_easy
season: evergreen/male gift
primary_keyword: kayak fishing coloring book
price: 8.99
pages: 50
status: planned
priority: series vol 4 (after flagship validates)
apify_data: REAL: Opp 1.70, rev 9
---

# Kayak Fishing

**Niche:** Fishing (male hobby series)  |  **Vol 4**  |  Theme key: `kayak_fishing`

## Concept / sub-angle
modern/trend

## Primary keyword
`kayak fishing coloring book`

## Real Apify data
REAL: Opp 1.70, rev 9

## Differentiation (series spec)
Realistic masculine style (NOT kawaii). Action scenes + detailed fish. Gift hooks 'for Dad/Grandpa'. Lowest review barrier of any niche.

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "kayak fishing coloring book" > data/niches/apify/kayak_fishing.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Kayak Fishing: modern/trend"
# or manual:
python scripts/plan_book.py --concept "Kayak Fishing: modern/trend" --audience adults --pages 50 --theme-key kayak_fishing
python scripts/generate_images.py --plan output/kayak_fishing/plan.json --count 50
python scripts/build_pdf.py      --theme kayak_fishing --author "BoBo Art"
python scripts/generate_cover.py --theme kayak_fishing --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/kayak_fishing/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
