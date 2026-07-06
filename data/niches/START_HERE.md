# 👉 START HERE — KDP niche research & production (resume guide)

Last updated: 2026-06-27. Open this file first next time.

## The decision (5 money niches, verified by real Apify data)
| # | Niche | Opp | demand/mo | rev | Read |
|---|-------|----:|----:|----:|------|
| 1 | 🐸 Cottagecore Frogs | 7.28 | 173 | 24 | 🌊 BLUE_OCEAN (clean) — BEST. Producing now. |
| 2 | 🏞 National Parks | 4.14 | 66 | 16 | 🌤 strong, reliable |
| 3 | 🎣 Fishing (bass/deep-sea series) | 2.3 / 5.2 | 18-30 | 6-8 | lowest barrier; 8-book series |
| 4 | 🎃 Cozy Haunted Bookshop | 13.2* | 26 | 2 | *Opp inflated (off-season+thin); "open lane". Q4, ship by Aug 5 |
| 5 | 💀 Dark Romance (BookTok) | 1.38 | 44 | 32 | trend, beatable |

Full detail + series breakdowns: **TOP5_MONEY_NICHES.md**

## Where everything is saved
- **TOP5_MONEY_NICHES.md** — the 5 niches + 5-10 book series for each + production order.
- **MASTER_VERIFIED.md** — all 18+ niches ranked by real Opp (incl. the AVOID list).
- **FISHING_SERIES_PLAN.md** — verified 8-book fishing series.
- **APIFY_REALDATA_ANALYSIS.md** — first 4 flagship hard-data pulls + WebSearch corrections.
- **apify/*.json** — 40 raw Apify top10 pulls (BSR/reviews/price per keyword).
- **production/** — per-niche folders with resumable book briefs (fishing/halloween/christmas/grief; frogs+parks TODO).
- **output/cottagecore_frogs/plan.json** — the frog flagship book plan (50 prompts + cover + SEO). IN PROGRESS.

## How to resume
### Re-rank niches anytime (uses saved Apify pulls):
```
python3 scripts/rank_niches.py
```
### Pull fresh/again for a keyword (Apify token pool in .env, auto-rotates):
```
python3 scripts/apify_research.py top10 "<keyword>" > data/niches/apify/<key>.json
```
### Continue producing the frog book (currently at Phase 3 plan-review):
```
/kdp-create-book   (or resume: generate_images.py --plan output/cottagecore_frogs/plan.json --count 50)
```
### Start the next niche book:
Pick from TOP5; recommended order: Frogs (now) → Haunted Bookshop (by Aug 5) → National Parks → Fishing series → Dark Romance.

## Important caveats (don't forget)
- Opp uses averages → single mega-seller inflates it; seasonal niches read low off-season (re-pull Halloween/Christmas in Sept).
- Always re-pull a niche's exact keyword right before producing (sub-angles shift weekly).
- Apify = the hard-data source; Amazon blocks WebFetch, so WebSearch alone = LOW_CONFIDENCE.
