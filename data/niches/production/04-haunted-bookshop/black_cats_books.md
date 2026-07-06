---
theme_key: black_cats_books
topic: Black Cats & Books
audience: adults
style: bold_easy
season: seasonal Q4
primary_keyword: black cat coloring book halloween
price: 8.99
pages: 50
status: planned
priority: series vol 6 (after flagship validates)
apify_data: pull before producing
---

# Black Cats & Books

**Niche:** Cozy Haunted Bookshop  |  **Vol 6**  |  Theme key: `black_cats_books`

## Concept / sub-angle
cats x bookshop

## Primary keyword
`black cat coloring book halloween`

## Real Apify data
pull before producing

## Differentiation (series spec)
Bold & easy, alcohol-marker friendly. 'Cozy not gory': black cats in candle-lit libraries, ghosts reading, pumpkin-lit bookshop windows. Hooks: spooky TBR tracker + public-domain gothic quotes (Poe/Shelley/Stoker = 0 IP).

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "black cat coloring book halloween" > data/niches/apify/black_cats_books.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Black Cats & Books: cats x bookshop"
# or manual:
python scripts/plan_book.py --concept "Black Cats & Books: cats x bookshop" --audience adults --pages 50 --theme-key black_cats_books
python scripts/generate_images.py --plan output/black_cats_books/plan.json --count 50
python scripts/build_pdf.py      --theme black_cats_books --author "BoBo Art"
python scripts/generate_cover.py --theme black_cats_books --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/black_cats_books/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
