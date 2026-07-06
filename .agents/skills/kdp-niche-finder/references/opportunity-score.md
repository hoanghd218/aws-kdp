# Opportunity Score — math, table, and worked trap examples

## Formula
```
Opp = avg_monthly_sales(top10) / avg_reviews(top10)
avg_monthly_sales = mean( bsr_to_daily_sales(BSR_i) ) * 30
```

## BSR → daily sales (US paperback, mid estimate)
Aggregated from Publisher Rocket / KDSPY / Book Bolt community data. Baked into
`scripts/rank_niches.py`.

| BSR band | sales/day |
|----------|-----------|
| 1–100 | 900 |
| 101–1,000 | 160 |
| 1,001–5,000 | 45 |
| 5,001–10,000 | 17 |
| 10,001–25,000 | 9 |
| 25,001–50,000 | 5 |
| 50,001–100,000 | 2.5 |
| 100,001–200,000 | 1.2 |
| 200,001–500,000 | 0.4 |
| 500,001–1,000,000 | 0.12 |
| > 1,000,000 | 0.03 |

## Verdict thresholds
- Opp ≥ 5 → 🌊 BLUE_OCEAN
- 2–5 → 🌤 MODERATE
- 0.5–2 → COMPETITIVE
- < 0.5 → SATURATED
- Override: monthly sales < ~12 → WEAK/low-demand regardless of Opp.

## The three traps (real examples from the 2026-06 sweep)

### 1. Single-winner inflation
`fly_fishing`: min BSR **523**, avg BSR 1.7M, avg reviews 121, Opp 4.0.
One book ranks #523 (huge) and drags the average sales way up; the other 9 are near-dead and the
winner has 121 reviews = entrenched. Raw Opp says MODERATE; reality is "one publisher owns it."
→ When `min_bsr` ≪ `avg_bsr` by orders of magnitude, distrust the Opp.

### 2. Off-season seasonal collapse
`cottagecore_christmas` pulled in June: avg BSR 3.7M, Opp 0.04 → looks dead. It isn't — Christmas
is maximally off-peak in June, so every competitor ranks in the millions. You cannot score a
seasonal niche off-season. Re-pull ~Sept-Oct, or judge on supply/competition alone.
Inverse signal: `cozy_haunted_bookshop` still showed live ranks (BSR 58k) in June off-season →
unusually strong; in-season it will surge.

### 3. Low-demand floor / empty Opp
`pet_loss_grief`: min BSR 690k, avg reviews 3, Opp 0.34. The near-zero reviews are not "open lane"
— nobody's buying (no book under BSR 100k). Versus `cozy_haunted_bookshop` (reviews 2 but a book
at BSR 58k selling) = genuinely open. The discriminator is the NUMERATOR: is anything selling?

## Demand-weighting beats pure Opp
Compare two "low competition" niches:
- `frog_adults`: 173 sales/mo, 24 reviews, Opp 7.28 ← real money
- `crappie_fishing`: 10 sales/mo, 7 reviews, Opp 1.44 ← low barrier but thin money
Both beatable, but the first has ~17× the demand. Rank by demand × low-competition, not Opp alone.

## Saturated-but-tempting (high demand, but suicide head-on)
High monthly sales with avg reviews in the hundreds/thousands = locked. Avoid head-on; only enter
via a sharp untaken sub-angle. Examples from the sweep: anxiety_relief (avg 2417 reviews),
catfish (663), gnome (628), tattoo (470), bigfoot (366), truck (339), horror (323), witchy (308).
