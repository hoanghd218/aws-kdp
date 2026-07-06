---
theme_key: fae_court
topic: Fae Court Romance
audience: adults
style: bold_easy
season: trend evergreen
primary_keyword: fae coloring book for adults
price: 8.99
pages: 50
status: planned
priority: series vol 3 (after flagship validates)
apify_data: pull + IP-check before producing
---

# Fae Court Romance

**Niche:** Dark Romance (BookTok)  |  **Vol 3**  |  Theme key: `fae_court`

## Concept / sub-angle
fae/fantasy romance aesthetic

## Primary keyword
`fae coloring book for adults`

## Real Apify data
pull + IP-check before producing

## Differentiation (series spec)
BookTok-driven aesthetic. Moody floral/gothic + romantic motifs. KEEP ART GENERIC — no trademarked book titles or characters; no franchise names anywhere (IP).

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "fae coloring book for adults" > data/niches/apify/fae_court.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Fae Court Romance: fae/fantasy romance aesthetic"
# or manual:
python scripts/plan_book.py --concept "Fae Court Romance: fae/fantasy romance aesthetic" --audience adults --pages 50 --theme-key fae_court
python scripts/generate_images.py --plan output/fae_court/plan.json --count 50
python scripts/build_pdf.py      --theme fae_court --author "BoBo Art"
python scripts/generate_cover.py --theme fae_court --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/fae_court/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
