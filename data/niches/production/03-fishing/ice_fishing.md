---
theme_key: ice_fishing
topic: Ice Fishing
audience: adults
style: bold_easy
season: evergreen/male gift
primary_keyword: ice fishing coloring book
price: 8.99
pages: 50
status: planned
priority: series vol 7 (after flagship validates)
apify_data: REAL: Opp 1.01, rev 15
---

# Ice Fishing

**Niche:** Fishing (male hobby series)  |  **Vol 7**  |  Theme key: `ice_fishing`

## Concept / sub-angle
winter bonus

## Primary keyword
`ice fishing coloring book`

## Real Apify data
REAL: Opp 1.01, rev 15

## Differentiation (series spec)
Realistic masculine style (NOT kawaii). Action scenes + detailed fish. Gift hooks 'for Dad/Grandpa'. Lowest review barrier of any niche.

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "ice fishing coloring book" > data/niches/apify/ice_fishing.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Ice Fishing: winter bonus"
# or manual:
python scripts/plan_book.py --concept "Ice Fishing: winter bonus" --audience adults --pages 50 --theme-key ice_fishing
python scripts/generate_images.py --plan output/ice_fishing/plan.json --count 50
python scripts/build_pdf.py      --theme ice_fishing --author "BoBo Art"
python scripts/generate_cover.py --theme ice_fishing --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/ice_fishing/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
