---
theme_key: morally_grey
topic: Morally Grey
audience: adults
style: bold_easy
season: trend evergreen
primary_keyword: morally grey coloring book
price: 8.99
pages: 50
status: planned
priority: series vol 2 (after flagship validates)
apify_data: pull + IP-check before producing
---

# Morally Grey

**Niche:** Dark Romance (BookTok)  |  **Vol 2**  |  Theme key: `morally_grey`

## Concept / sub-angle
trope-themed (generic art)

## Primary keyword
`morally grey coloring book`

## Real Apify data
pull + IP-check before producing

## Differentiation (series spec)
BookTok-driven aesthetic. Moody floral/gothic + romantic motifs. KEEP ART GENERIC — no trademarked book titles or characters; no franchise names anywhere (IP).

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "morally grey coloring book" > data/niches/apify/morally_grey.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Morally Grey: trope-themed (generic art)"
# or manual:
python scripts/plan_book.py --concept "Morally Grey: trope-themed (generic art)" --audience adults --pages 50 --theme-key morally_grey
python scripts/generate_images.py --plan output/morally_grey/plan.json --count 50
python scripts/build_pdf.py      --theme morally_grey --author "BoBo Art"
python scripts/generate_cover.py --theme morally_grey --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/morally_grey/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
