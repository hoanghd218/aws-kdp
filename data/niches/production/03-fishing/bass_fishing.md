---
theme_key: bass_fishing
topic: Bass Fishing
audience: adults
style: bold_easy
season: evergreen/male gift
primary_keyword: bass fishing coloring book
price: 8.99
pages: 50
status: planned
priority: FLAGSHIP (produce first)
apify_data: REAL: Opp 2.31, rev 8, 2 under BSR100k — best balance
---

# Bass Fishing

**Niche:** Fishing (male hobby series)  |  **Vol 1**  |  Theme key: `bass_fishing`

## Concept / sub-angle
FLAGSHIP — bass action/lakes

## Primary keyword
`bass fishing coloring book`

## Real Apify data
REAL: Opp 2.31, rev 8, 2 under BSR100k — best balance

## Differentiation (series spec)
Realistic masculine style (NOT kawaii). Action scenes + detailed fish. Gift hooks 'for Dad/Grandpa'. Lowest review barrier of any niche.

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "bass fishing coloring book" > data/niches/apify/bass_fishing.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Bass Fishing: FLAGSHIP — bass action/lakes"
# or manual:
python scripts/plan_book.py --concept "Bass Fishing: FLAGSHIP — bass action/lakes" --audience adults --pages 50 --theme-key bass_fishing
python scripts/generate_images.py --plan output/bass_fishing/plan.json --count 50
python scripts/build_pdf.py      --theme bass_fishing --author "BoBo Art"
python scripts/generate_cover.py --theme bass_fishing --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/bass_fishing/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
