---
theme_key: dark_romance
topic: Dark Romance
audience: adults
style: bold_easy
season: trend evergreen
primary_keyword: dark romance coloring book
price: 8.99
pages: 50
status: planned
priority: FLAGSHIP (produce first)
apify_data: REAL: Opp 1.38, 44/mo, rev 32
---

# Dark Romance

**Niche:** Dark Romance (BookTok)  |  **Vol 1**  |  Theme key: `dark_romance`

## Concept / sub-angle
FLAGSHIP — moody gothic-floral romance motifs

## Primary keyword
`dark romance coloring book`

## Real Apify data
REAL: Opp 1.38, 44/mo, rev 32

## Differentiation (series spec)
BookTok-driven aesthetic. Moody floral/gothic + romantic motifs. KEEP ART GENERIC — no trademarked book titles or characters; no franchise names anywhere (IP).

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "dark romance coloring book" > data/niches/apify/dark_romance.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Dark Romance: FLAGSHIP — moody gothic-floral romance motifs"
# or manual:
python scripts/plan_book.py --concept "Dark Romance: FLAGSHIP — moody gothic-floral romance motifs" --audience adults --pages 50 --theme-key dark_romance
python scripts/generate_images.py --plan output/dark_romance/plan.json --count 50
python scripts/build_pdf.py      --theme dark_romance --author "BoBo Art"
python scripts/generate_cover.py --theme dark_romance --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/dark_romance/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
