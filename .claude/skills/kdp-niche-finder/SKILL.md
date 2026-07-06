---
name: kdp-niche-finder
description: >-
  Find PROFITABLE, low-competition KDP coloring-book niches using REAL Amazon data (Apify
  top-10 BSR/reviews/price) and a deterministic Opportunity Score — not vibes. Sweeps many
  candidate keywords, computes Opp = demand/competition for each, corrects for the common
  traps (single-winner inflation, off-season seasonal reads, low-demand floors), and returns a
  ranked, evidence-backed shortlist of money niches plus a 5-10 book series for each. USE THIS
  whenever the user wants to find/research/validate KDP or coloring-book niches, asks "what
  book should I make", "find a niche", "is this niche worth it", "tim ngach", "ngach kiem tien",
  "research niche", "blue ocean niche", wants to AVOID saturated markets, or wants to verify a
  niche idea with hard Amazon numbers. Prefer this over guessing from WebSearch — Amazon blocks
  direct page fetches, so Apify is the only reliable hard-data source here.
---

# KDP Niche Finder — hard-data niche research

Find coloring-book (and low-content) niches that actually make money: **real demand, beatable
competition, margin headroom.** Every verdict traces to an Apify top-10 pull + a deterministic
score — never a guess. WebSearch can suggest candidates, but it routinely *overrates* niches
(e.g. "fishing for men" looks hot but real BSR shows modest demand). Only Apify numbers decide.

## The one metric that matters: Opportunity Score

```
Opp = avg monthly sales (top-10)  /  avg review count (top-10)
```
- **Numerator = DEMAND** — are people actually buying? (from BSR → sales table)
- **Denominator = COMPETITION BARRIER** — have rivals locked it with reviews?
- High Opp = real demand AND nobody has cemented dominance = a lane you can break into.

| Opp | Meaning |
|-----|---------|
| ≥ 5 | 🌊 BLUE_OCEAN — prioritize |
| 2–5 | 🌤 MODERATE |
| 0.5–2 | COMPETITIVE |
| < 0.5 | SATURATED — avoid |

**Opp never stands alone.** Three traps make the raw number lie — always sanity-check (see
`Reading the numbers` below): single mega-seller inflation, off-season seasonal collapse, and a
low-demand floor where Opp is high only because reviews are ~0 (nobody competing *or* buying).

## Workflow

### Step 0 — Confirm Apify is live (token pool)
The hard data comes from `scripts/apify_research.py` (Apify `junglee/Amazon-crawler`). It reads
`APIFY_API_TOKEN` from `.env`, which may be a **comma-separated pool** — the script auto-rotates
to the next token on HTTP 401/402/403 ("Monthly usage hard limit exceeded"). Quick check:

```bash
python3 scripts/apify_research.py top10 "frog coloring book for adults" | head -5
```
If it prints JSON → live. If all tokens 403 → tell the user Apify credit is exhausted; they must
top up or add another token to the comma list in `.env`. Do NOT silently fall back to WebSearch
guesses and present them as hard data — say clearly the result is LOW_CONFIDENCE if you must.

### Step 1 — Build the candidate keyword list
You need a list of `key,keyword` pairs to sweep. Sources, in order of value:
1. **The user's ideas** — whatever niches they want validated.
2. **Category brainstorm** — for a theme (e.g. "male hobbies", "cottagecore", "mental health"),
   enumerate 8-15 concrete long-tail keywords + audience. Favor SPECIFIC long-tail
   ("bass fishing coloring book") over generic heads ("coloring book") — heads are always
   saturated; the money is in the specific intersection a brand hasn't filled.
3. **Sub-angles of a winner** — once a niche scores well, sweep its species/style/occasion
   variants to build a 5-10 book SERIES (e.g. fishing → bass, deep-sea, trout, kayak, ice…).

Keep keys snake_case; they become the saved filenames.

### Step 2 — Sweep the keywords (pull real top-10)
Use the bundled helper — it pulls each keyword (skipping ones already cached), saving each to
`data/niches/apify/<key>.json`:

```bash
python3 .claude/skills/kdp-niche-finder/scripts/niche_sweep.py \
  "bass_fishing=bass fishing coloring book" \
  "deep_sea_fishing=deep sea fishing coloring book" \
  "frog_adults=frog coloring book for adults"
```
Each pull takes ~30-60s. For a large list (10+), **run it in the background** (`run_in_background`)
and continue once it completes — don't block. Re-running is cheap (cached pulls are skipped), so
it's safe to resume after an interruption. Conserve Apify credits: only pull what you'll use, and
reuse the saved JSONs (they persist in `data/niches/apify/`).

### Step 3 — Rank by real Opportunity Score
```bash
python3 scripts/rank_niches.py
```
This reads every `data/niches/apify/*.json`, computes avg/min BSR, est. monthly sales (BSR→sales
table baked in), avg reviews, avg price, and **Opp**, then prints a ranked table with a verdict
per niche. It also flags `mo<12 ⇒ WEAK/low-demand` regardless of Opp (the low-demand floor).

### Step 4 — Read the numbers (apply judgment, don't trust raw Opp)
For each high-Opp niche, open its `data/niches/apify/<key>.json` and check `top10_titles` +
`top10_bsr` + `top10_reviews` to catch the three traps:

- **Single-winner trap.** If `min_bsr` is tiny (e.g. 523) but `avg_bsr` is in the millions, ONE
  dominant book is carrying the whole average → not a real opening. (Saw this on fly_fishing.)
- **Seasonal off-season collapse.** Halloween/Christmas niches pulled in June read near-dead
  (BSR in the millions) because it's off-peak — you CANNOT judge a seasonal niche off-season.
  Re-pull ~2-3 months before the season, or judge on supply/competition alone. Conversely, a
  seasonal niche that still ranks live off-season is a STRONG signal.
- **Low-demand-floor / empty Opp.** Very high Opp driven by `avg reviews ≈ 0` can mean "nobody
  has cemented it" (good) OR "nobody's buying" (bad). Cross-check the numerator: is anything
  actually selling (a book under BSR ~100k)? If not, it's low-demand, not blue ocean. Also watch
  the inverse: a keyword that returns GENERAL results (e.g. "halloween bookstore" returns generic
  halloween) means no dedicated competitor exists yet — the intersection is genuinely OPEN.

Also weight **demand vs competition together**: a niche with 173 sales/mo at 24 reviews beats one
with 8 reviews but 6 sales/mo — both are "low competition" but only the first has real money.

### Step 5 — Deliver + save
Write a ranked shortlist to `data/niches/` (markdown). For the top picks, recommend a 5-10 book
**series** (each volume a distinct sub-angle/keyword so they don't cannibalize). Save raw pulls
stay in `data/niches/apify/`. Optionally scaffold per-book briefs under
`data/niches/production/<NN>-<niche>/` (README + one brief per volume) so work resumes later.

## Output format

```
🎯 NICHE FINDER — <topic/keywords swept>  (N niches, real Apify data)

RANKED (by Opp, judgment-corrected)
| # | niche | demand/mo | avg reviews | Opp | verdict | note (trap?) |
...

✅ POTENTIAL NICHES (survive the traps)
 1. <niche> — <why: demand × low competition, one-line>
 ...
❌ AVOID — saturated: <list (huge reviews)> | low-demand: <list> | single-winner: <list>

SERIES for the top pick (5-10 books, distinct sub-angles): <list of volumes + keywords>

NEXT: re-pull the exact keyword right before producing (sub-angles shift weekly); seasonal
niches need an in-season re-pull. Then /kdp-create-book "<flagship concept>".
```

## Rules
- NEVER fabricate BSR/reviews/price. Only report what the Apify pull returns; if Apify is down,
  say so and mark anything from WebSearch as LOW_CONFIDENCE.
- ALWAYS sanity-check raw Opp against the three traps before calling something a winner — a
  pure-number BLUE_OCEAN that's actually a single-winner or off-season read is worse than useless.
- Prefer SPECIFIC long-tail keywords; generic head terms ("coloring book for adults") are always
  saturated and waste a pull.
- For a SERIES, each volume must be a genuinely different sub-angle (species/style/occasion) — KDP
  forbids duplicate content and near-identical books cannibalize each other.
- Validate the FLAGSHIP (vol 1) with real sales before batch-producing the rest of a series.
- Conserve Apify credits: reuse cached `data/niches/apify/*.json`; only pull keywords you'll act on.
- Re-pull a niche's exact keyword right before producing it — niches shift week to week.

## Reference
- `references/opportunity-score.md` — the BSR→sales table, full math, and worked trap examples.
- Core scripts (in the repo, not the skill): `scripts/apify_research.py` (token-pool puller),
  `scripts/rank_niches.py` (ranker). The skill's `scripts/niche_sweep.py` wraps the puller for
  batch lists.
