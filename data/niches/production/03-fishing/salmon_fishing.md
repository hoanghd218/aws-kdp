---
theme_key: salmon_fishing
topic: Salmon Fishing
audience: adults
style: bold_easy
season: evergreen/male gift
primary_keyword: salmon fishing coloring book
price: 8.99
pages: 50
status: planned
priority: series vol 6 (after flagship validates)
apify_data: REAL: Opp 1.23, rev 9
---

# Salmon Fishing

**Niche:** Fishing (male hobby series)  |  **Vol 6**  |  Theme key: `salmon_fishing`

## Concept / sub-angle
salmon runs

## Primary keyword
`salmon fishing coloring book`

## Real Apify data
REAL: Opp 1.23, rev 9

## Differentiation (series spec)
Realistic masculine style (NOT kawaii). Action scenes + detailed fish. Gift hooks 'for Dad/Grandpa'. Lowest review barrier of any niche.

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "salmon fishing coloring book" > data/niches/apify/salmon_fishing.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Salmon Fishing: salmon runs"
# or manual:
python scripts/plan_book.py --concept "Salmon Fishing: salmon runs" --audience adults --pages 50 --theme-key salmon_fishing
python scripts/generate_images.py --plan output/salmon_fishing/plan.json --count 50
python scripts/build_pdf.py      --theme salmon_fishing --author "BoBo Art"
python scripts/generate_cover.py --theme salmon_fishing --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/salmon_fishing/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
