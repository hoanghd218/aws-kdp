---
theme_key: cottagecore_frogs
topic: Cottagecore Frogs
audience: adults
style: bold_easy
season: evergreen/trend
primary_keyword: cottagecore frog coloring book
price: 8.99
pages: 50
status: planned
priority: FLAGSHIP (produce first)
apify_data: REAL: Opp 7.28, 173/mo, rev 24 (BLUE_OCEAN) — plan.json DONE
---

# Cottagecore Frogs

**Niche:** Cottagecore Frogs  |  **Vol 1**  |  Theme key: `cottagecore_frogs`

## Concept / sub-angle
FLAGSHIP — toadstools/pond/cottage/tea mix

## Primary keyword
`cottagecore frog coloring book`

## Real Apify data
REAL: Opp 7.28, 173/mo, rev 24 (BLUE_OCEAN) — plan.json DONE

## Differentiation (series spec)
Cozy whimsical frogs in cottagecore scenes (toadstools, ponds, frog cottages, tea, reading, gardens, lanterns). Kawaii cozy, bold & easy. Female-leaning 20-45.

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "cottagecore frog coloring book" > data/niches/apify/cottagecore_frogs.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Cottagecore Frogs: FLAGSHIP — toadstools/pond/cottage/tea mix"
# or manual:
python scripts/plan_book.py --concept "Cottagecore Frogs: FLAGSHIP — toadstools/pond/cottage/tea mix" --audience adults --pages 50 --theme-key cottagecore_frogs
python scripts/generate_images.py --plan output/cottagecore_frogs/plan.json --count 50
python scripts/build_pdf.py      --theme cottagecore_frogs --author "BoBo Art"
python scripts/generate_cover.py --theme cottagecore_frogs --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/cottagecore_frogs/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
