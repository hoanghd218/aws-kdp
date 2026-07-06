# Apify REAL-DATA Analysis — flagship keywords (HARD data)

- **Date:** 2026-06-27 | **Source:** Apify junglee/Amazon-crawler (token pool restored)
- Raw pulls saved in `data/niches/apify/*.json`. This REPLACES the earlier WebSearch
  LOW_CONFIDENCE guesses for these 4 keywords.
- BSR→sales table from niche-hunter. Opportunity = avg monthly sales(top10) / avg reviews(top10).

## Results

| Niche (keyword) | avg BSR | min BSR | avg reviews | avg $ | mo.sales/bk | **Opp** | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| cozy_haunted_bookshop (`halloween bookstore coloring book`) | 572k | 58,944 | **2.0** | $10.52 | 26.3 | **13.2** | 🌊 BLUE_OCEAN* |
| coloring_through_grief (`grief coloring book for adults`) | 674k | 50,474 | 19.1 | $8.39 | 15.7 | 0.82 | COMPETITIVE (steady evergreen) |
| fishing_for_men (`fishing coloring book for men`) | 1.04M | 65,783 | 30.8 | $10.00 | 17.9 | 0.58 | COMPETITIVE — **NOT the HOT 7.5 WebSearch claimed** |
| cottagecore_christmas (`cottagecore christmas coloring book`) | 3.7M | 1.52M | 23.7 | $8.59 | 0.9 | 0.04 | ⚠ unreadable OFF-SEASON (June) |

## What the hard data corrected (vs WebSearch ranking)

### 🎣 Fishing for men — DOWNGRADED (HOT 7.5 → COMPETITIVE)
- Real demand is MODEST: only 2/10 under BSR 100k; most rank 350k–2.7M = few sales.
- Low competition (avg 30 reviews) but ALSO low demand → Opp 0.58, not blue ocean.
- The ONE book that sells well: *Fantastic Game Fish of North America* — BSR 65k, 144 pages,
  **$14.99**, educational species guide. → the winning angle is **premium/educational/detailed**,
  NOT generic "fishing for men". Generic = modest.

### 🎃 Halloween bookshop — CONFIRMED OPEN (but read Opp 13 cautiously)
- The keyword `halloween bookstore coloring book` returned GENERAL halloween books, NOT one
  dedicated bookstore title → **the bookshop intersection is genuinely empty** (key finding).
- General halloween sells even in June off-season (BSR 58k–264k on 0-review books) → real
  category demand; in-season (Sep-Oct) these surge.
- avg reviews 2.0 → very thin review barrier. Opp 13.2 is inflated by off-season + obscure
  low-review titles, but the direction is right: **differentiated halloween-bookshop = open lane.**
- ⚠ Earlier we saw the cute/cozy-halloween HEAD term IS locked by Coco Wyo ("Spooky Cutie" #1).
  So win via the bookshop/vintage-gothic angle, not generic cozy-halloween.

### 🕊 Grief / self-compassion — CONFIRMED steady evergreen (real, modest)
- Genuinely relevant results, real audience. Best: *Grief in Color* journal BSR 50k/84 rev;
  *Remember Grief is Love* 151k/16 rev. Moderate competition (avg 19 rev), Opp 0.82.
- Many affirmation books already exist; OPEN sub-angles NOT in top-10: **pet-loss grief**,
  **child/pregnancy loss**, **Christian grief** (one present). Evergreen + emotional loyalty =
  the steadiest real pick of the four.

### 🎄 Cottagecore Christmas — UNREADABLE off-season
- ALL competitors BSR 1.5M–5.6M because it's JUNE (Christmas maximally off-peak). A 224-review
  book ranks 4.5M off-season → June data CANNOT judge a Q4 seasonal niche.
- Supply is moderate (Cozy Christmas Nooks, Cottagecore Christmas, Cozy Christmas Cottage b&e).
- **Action:** re-pull in Sept-Oct, OR treat as a known seasonal and decide on supply alone.
- ⚠ Same off-season caveat technically applies to halloween — but halloween still showed live
  ranks now, which is the stronger signal.

## Revised recommendation (hard-data driven)

| Priority | Pick | Why (real data) | Caveat |
|---|---|---|---|
| **1 steady evergreen** | **Grief / Self-Compassion** (differentiate: pet-loss or child-loss) | Only confirmed real evergreen demand + emotional loyalty; Opp 0.82; open sub-angles | Modest volume, sensitive content |
| **2 seasonal Q4** | **Halloween Bookshop / Vintage-Gothic** | Intersection empty; category demand live even off-season | Validate in-season; ship by early Aug |
| **3 reposition** | **Fishing — premium species/educational** ($12.99+, 100+ pg) | Generic modest, but premium angle (Game Fish 144pg $14.99) sells | NOT generic "for men" |
| **4 defer** | Cottagecore Christmas | seasonal, supply moderate | June data unreadable — re-pull Sep |

## Method note / credits
- Token pool now live (2 keys, auto-rotate on 403 — see scripts/apify_research.py).
- Only 4 flagship keywords pulled (conserve credits). Sub-angle keywords (bass fishing, pet-loss
  grief, haunted library, etc.) NOT yet pulled — do before committing each volume.
