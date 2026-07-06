---
theme_key: spooky_cafe_bookshop
topic: Spooky Cafe & Bookshop
audience: adults
style: bold_easy
season: seasonal Q4
primary_keyword: spooky cafe coloring book
price: 8.99
pages: 50
status: planned
priority: series vol 4 (after flagship validates)
apify_data: pull before producing
---

# Spooky Cafe & Bookshop

**Niche:** Cozy Haunted Bookshop  |  **Vol 4**  |  Theme key: `spooky_cafe_bookshop`

## Concept / sub-angle
cafe + books

## Primary keyword
`spooky cafe coloring book`

## Real Apify data
pull before producing

## Differentiation (series spec)
Bold & easy, alcohol-marker friendly. 'Cozy not gory': black cats in candle-lit libraries, ghosts reading, pumpkin-lit bookshop windows. Hooks: spooky TBR tracker + public-domain gothic quotes (Poe/Shelley/Stoker = 0 IP).

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "spooky cafe coloring book" > data/niches/apify/spooky_cafe_bookshop.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Spooky Cafe & Bookshop: cafe + books"
# or manual:
python scripts/plan_book.py --concept "Spooky Cafe & Bookshop: cafe + books" --audience adults --pages 50 --theme-key spooky_cafe_bookshop
python scripts/generate_images.py --plan output/spooky_cafe_bookshop/plan.json --count 50
python scripts/build_pdf.py      --theme spooky_cafe_bookshop --author "BoBo Art"
python scripts/generate_cover.py --theme spooky_cafe_bookshop --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/spooky_cafe_bookshop/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
