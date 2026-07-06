---
theme_key: cozy_haunted_bookshop
topic: The Cozy Haunted Bookshop
audience: adults
style: bold_easy
season: seasonal Q4
primary_keyword: cozy haunted bookshop coloring book
price: 8.99
pages: 50
status: planned
priority: FLAGSHIP (produce first)
apify_data: REAL: intersection EMPTY (kw returns general halloween); Opp 13.2* (off-season/thin)
---

# The Cozy Haunted Bookshop

**Niche:** Cozy Haunted Bookshop  |  **Vol 1**  |  Theme key: `cozy_haunted_bookshop`

## Concept / sub-angle
FLAGSHIP — warm-spooky reading scenes

## Primary keyword
`cozy haunted bookshop coloring book`

## Real Apify data
REAL: intersection EMPTY (kw returns general halloween); Opp 13.2* (off-season/thin)

## Differentiation (series spec)
Bold & easy, alcohol-marker friendly. 'Cozy not gory': black cats in candle-lit libraries, ghosts reading, pumpkin-lit bookshop windows. Hooks: spooky TBR tracker + public-domain gothic quotes (Poe/Shelley/Stoker = 0 IP).

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "cozy haunted bookshop coloring book" > data/niches/apify/cozy_haunted_bookshop.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "The Cozy Haunted Bookshop: FLAGSHIP — warm-spooky reading scenes"
# or manual:
python scripts/plan_book.py --concept "The Cozy Haunted Bookshop: FLAGSHIP — warm-spooky reading scenes" --audience adults --pages 50 --theme-key cozy_haunted_bookshop
python scripts/generate_images.py --plan output/cozy_haunted_bookshop/plan.json --count 50
python scripts/build_pdf.py      --theme cozy_haunted_bookshop --author "BoBo Art"
python scripts/generate_cover.py --theme cozy_haunted_bookshop --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/cozy_haunted_bookshop/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
