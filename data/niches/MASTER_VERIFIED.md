# MASTER VERIFIED — niche ranking from REAL Apify data

- **Date:** 2026-06-27 | **Source:** Apify junglee/Amazon-crawler (18 keywords). Raw: `apify/*.json`
- Opp = avg monthly sales(top10) / avg reviews(top10). Recompute: `python3 scripts/rank_niches.py`
- ⚠️ Opp uses AVERAGES → a single mega-seller inflates it (single-winner trap); seasonal niches
  read artificially low off-season (June). Interpretations below correct for these.

## Full ranking (raw)
| Niche | minBSR | avg rev | sales/mo | Opp | Raw verdict | Real read |
|---|---:|---:|---:|---:|---|---|
| cozy_haunted_bookshop | 58,944 | 2 | 26 | 13.2 | BLUE_OCEAN | ✅ open intersection (seasonal, thin data) |
| fly_fishing | **523** | 121 | 484 | 4.0 | MODERATE | ❌ SINGLE-WINNER trap (one BSR-523 book skews it) |
| bass_fishing | 55,566 | **8** | 18 | 2.3 | MODERATE | ✅ low review barrier, modest demand — real lane |
| dark_romance | 19,473 | 32 | 44 | 1.4 | COMPETITIVE | ✅ BookTok trend, real demand, beatable |
| golf_adults | 102,177 | 7 | 9 | 1.3 | WEAK | ❌ low demand |
| self_compassion | 4,816 | 151 | 164 | 1.1 | COMPETITIVE | ⚠ high demand BUT entrenched (avg 151 rev) |
| coloring_through_grief | 50,474 | 19 | 16 | 0.8 | COMPETITIVE | ✅ steady evergreen, modest |
| motorcycle_adults | 4,095 | 191 | 141 | 0.7 | COMPETITIVE | ⚠ demand high, saturated |
| anxiety_relief | **129** | **2417** | 1594 | 0.7 | COMPETITIVE | ❌ HUGE but SATURATED (avg 2417 rev) |
| hunting_men | 17,513 | 74 | 47 | 0.6 | COMPETITIVE | ⚠ moderate, entrenched |
| fishing_for_men | 65,783 | 31 | 18 | 0.6 | COMPETITIVE | ❌ generic = modest (premium angle only) |
| horror_adults | 5,330 | 323 | 172 | 0.5 | COMPETITIVE | ⚠ demand high, saturated |
| birdwatching | 36,793 | 48 | 18 | 0.4 | SATURATED | ❌ low demand vs competition |
| gnome_adults | 1,840 | 628 | 216 | 0.3 | SATURATED | ❌ saturated |
| pet_loss_grief | 690,814 | 3 | 1 | 0.3 | WEAK | ❌ almost NO demand (corrected!) |
| truck_adults | 16,870 | 339 | 33 | 0.1 | SATURATED | ❌ saturated |
| anime_chibi | 186,831 | 70 | 6 | 0.1 | WEAK | ❌ low demand |
| cottagecore_christmas | 1,524,013 | 24 | 1 | 0.04 | WEAK | ⚠ unreadable off-season — re-pull Sep |

## ✅ VERIFIED POTENTIAL NICHES (the shortlist that survives hard data)

### TIER 1 — real openings (do these)
1. **Cozy Haunted Bookshop** (seasonal Q4) — keyword returns general halloween, NO dedicated
   bookshop title → intersection open; halloween sells even off-season. Ship by early Aug.
   *Caveat: thin/seasonal data — strong but validate in-season.*
2. **Bass Fishing** (evergreen) — avg only **8 reviews** in top-10 = very low barrier, modest but
   real demand, 2 books under BSR 100k. The cleanest genuine blue-ocean-ish evergreen lane.
3. **Dark Romance coloring** (evergreen/trend) — BookTok-driven, real demand (44 sales/mo),
   moderate competition (32 rev). Rising aesthetic the big brands haven't locked.

### TIER 2 — steady but modest / enter only via sharp sub-angle
4. **Coloring Through Grief** — steady evergreen, modest (16/mo, 19 rev). Emotional loyalty.
5. **Self-Compassion** — strong demand (164/mo) BUT entrenched (151 rev) → only with a fresh angle.

### ❌ AVOID
- **Saturated (huge demand, huge reviews — suicide head-on):** anxiety_relief (2417 rev!),
  horror, motorcycle, gnome, truck, self-compassion head-on.
- **Single-winner trap:** fly_fishing (one BSR-523 book owns it).
- **Low demand:** pet_loss (corrected — almost none), golf, birdwatching, anime_chibi,
  fishing_for_men (generic).
- **Unreadable now:** cottagecore_christmas (re-pull Sep-Oct).

## Key corrections vs the old WebSearch research (now deleted)
- "fishing for men" HOT 7.5 → really COMPETITIVE/modest. Use bass-fishing or premium species angle.
- "pet loss grief" assumed open → actually almost zero demand.
- "anxiety relief" assumed enter-able → massively saturated (2417 avg reviews).
- Halloween-bookshop intersection → CONFIRMED open.

## Next
- Produce TIER-1: Bass Fishing (evergreen, now) + Cozy Haunted Bookshop (Q4, by Aug 5).
- Before each volume, pull its exact keyword to confirm (sub-angles shift fast).
- Re-pull all seasonal niches in Sept for true in-season reads.
