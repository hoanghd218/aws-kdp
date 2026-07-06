---
theme_key: yosemite
topic: Yosemite
audience: adults
style: bold_easy
season: evergreen/gift
primary_keyword: yosemite coloring book
price: 8.99
pages: 50
status: planned
priority: series vol 3 (after flagship validates)
apify_data: pull before producing
---

# Yosemite

**Niche:** National Parks  |  **Vol 3**  |  Theme key: `yosemite`

## Concept / sub-angle
granite cliffs, waterfalls, sequoias

## Primary keyword
`yosemite coloring book`

## Real Apify data
pull before producing

## Differentiation (series spec)
US national park landscapes + wildlife. Evergreen travel-gift, peaks summer. Realistic-cozy, bold & easy.

## Specs
8.5x11 | ~50 single-sided designs | 300 DPI | $8.99 | crisp clean line art (no pixelation) | single-sided 'no bleed-through' in listing | NO borders/frames | no blank-page padding | same author+brand for series cross-sell

## Production commands
```bash
# 0) confirm niche still open right before producing:
python3 scripts/apify_research.py top10 "yosemite coloring book" > data/niches/apify/yosemite.json && python3 scripts/rank_niches.py
# 1) build end-to-end:
/kdp-create-book "Yosemite: granite cliffs, waterfalls, sequoias"
# or manual:
python scripts/plan_book.py --concept "Yosemite: granite cliffs, waterfalls, sequoias" --audience adults --pages 50 --theme-key yosemite
python scripts/generate_images.py --plan output/yosemite/plan.json --count 50
python scripts/build_pdf.py      --theme yosemite --author "BoBo Art"
python scripts/generate_cover.py --theme yosemite --author "BoBo Art"
python scripts/pdf_qc.py         --pdf output/yosemite/interior.pdf --trim 8.5x11 --require-even-pages
```

## Status checklist
- [ ] keyword re-pulled + still open
- [ ] plan.json written
- [ ] images generated + reviewed
- [ ] interior.pdf built + QC pass
- [ ] cover built + checked
- [ ] KDP listing (kdp-book-detail)
- [ ] published
