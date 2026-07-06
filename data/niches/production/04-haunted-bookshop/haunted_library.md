---
theme_key: haunted_library
topic: Haunted Library
audience: adults
style: bold_easy
season: seasonal Q4
primary_keyword: haunted library coloring book
price: 8.99
pages: 50
status: planned
priority: series vol 2 (after flagship validates)
apify_data: pull before producing
---

# Haunted Library

**Niche:** Cozy Haunted Bookshop  |  **Vol 2**  |  Theme key: `haunted_library`

## Concept / sub-angle
library twist

## Primary keyword
`haunted library coloring book`

## Real Apify data
pull before producing

## Differentiation (series spec)
Bold & easy, alcohol-marker friendly. 'Cozy not gory': black cats in candle-lit libraries, ghosts reading, pumpkin-lit bookshop windows. Hooks: spooky TBR tracker + public-domain gothic quotes (Poe/Shelley/Stoker = 0 IP).

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "haunted library coloring book" > data/niches/apify/haunted_library.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Haunted Library: library twist"
# or manual:
python scripts/plan_book.py --concept "Haunted Library: library twist" --audience adults --pages 50 --theme-key haunted_library
python scripts/generate_images.py --plan output/haunted_library/plan.json --count 50
python scripts/build_pdf.py      --theme haunted_library --author "BoBo Art"
python scripts/generate_cover.py --theme haunted_library --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/haunted_library/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
