---
theme_key: gothic_bookshop
topic: Gothic Bookshop
audience: adults
style: bold_easy
season: seasonal Q4
primary_keyword: gothic coloring book for adults
price: 8.99
pages: 50
status: planned
priority: series vol 3 (after flagship validates)
apify_data: pull before producing
---

# Gothic Bookshop

**Niche:** Cozy Haunted Bookshop  |  **Vol 3**  |  Theme key: `gothic_bookshop`

## Concept / sub-angle
vintage gothic, Poe/Stoker quotes

## Primary keyword
`gothic coloring book for adults`

## Real Apify data
pull before producing

## Differentiation (series spec)
Bold & easy, alcohol-marker friendly. 'Cozy not gory': black cats in candle-lit libraries, ghosts reading, pumpkin-lit bookshop windows. Hooks: spooky TBR tracker + public-domain gothic quotes (Poe/Shelley/Stoker = 0 IP).

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "gothic coloring book for adults" > data/niches/apify/gothic_bookshop.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Gothic Bookshop: vintage gothic, Poe/Stoker quotes"
# or manual:
python scripts/plan_book.py --concept "Gothic Bookshop: vintage gothic, Poe/Stoker quotes" --audience adults --pages 50 --theme-key gothic_bookshop
python scripts/generate_images.py --plan output/gothic_bookshop/plan.json --count 50
python scripts/build_pdf.py      --theme gothic_bookshop --author "BoBo Art"
python scripts/generate_cover.py --theme gothic_bookshop --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/gothic_bookshop/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
