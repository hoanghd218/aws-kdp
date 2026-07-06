---
theme_key: fishing_for_kids
topic: Fishing for Kids
audience: adults
style: bold_easy
season: evergreen/male gift
primary_keyword: fishing coloring book for kids
price: 8.99
pages: 50
status: planned
priority: series vol 8 (after flagship validates)
apify_data: REAL: Opp 1.46, 153/mo, rev 105 (more competitive)
---

# Fishing for Kids

**Niche:** Fishing (male hobby series)  |  **Vol 8**  |  Theme key: `fishing_for_kids`

## Concept / sub-angle
big demand, diff audience

## Primary keyword
`fishing coloring book for kids`

## Real Apify data
REAL: Opp 1.46, 153/mo, rev 105 (more competitive)

## Differentiation (series spec)
Realistic masculine style (NOT kawaii). Action scenes + detailed fish. Gift hooks 'for Dad/Grandpa'. Lowest review barrier of any niche.

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "fishing coloring book for kids" > data/niches/apify/fishing_for_kids.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Fishing for Kids: big demand, diff audience"
# or manual:
python scripts/plan_book.py --concept "Fishing for Kids: big demand, diff audience" --audience adults --pages 50 --theme-key fishing_for_kids
python scripts/generate_images.py --plan output/fishing_for_kids/plan.json --count 50
python scripts/build_pdf.py      --theme fishing_for_kids --author "BoBo Art"
python scripts/generate_cover.py --theme fishing_for_kids --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/fishing_for_kids/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
