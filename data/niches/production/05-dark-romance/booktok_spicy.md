---
theme_key: booktok_spicy
topic: Spicy Reads
audience: adults
style: bold_easy
season: trend evergreen
primary_keyword: booktok coloring book
price: 8.99
pages: 50
status: planned
priority: series vol 5 (after flagship validates)
apify_data: pull + IP-check before producing
---

# Spicy Reads

**Niche:** Dark Romance (BookTok)  |  **Vol 5**  |  Theme key: `booktok_spicy`

## Concept / sub-angle
spicy-reader humor/aesthetic

## Primary keyword
`booktok coloring book`

## Real Apify data
pull + IP-check before producing

## Differentiation (series spec)
BookTok-driven aesthetic. Moody floral/gothic + romantic motifs. KEEP ART GENERIC — no trademarked book titles or characters; no franchise names anywhere (IP).

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "booktok coloring book" > data/niches/apify/booktok_spicy.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Spicy Reads: spicy-reader humor/aesthetic"
# or manual:
python scripts/plan_book.py --concept "Spicy Reads: spicy-reader humor/aesthetic" --audience adults --pages 50 --theme-key booktok_spicy
python scripts/generate_images.py --plan output/booktok_spicy/plan.json --count 50
python scripts/build_pdf.py      --theme booktok_spicy --author "BoBo Art"
python scripts/generate_cover.py --theme booktok_spicy --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/booktok_spicy/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
