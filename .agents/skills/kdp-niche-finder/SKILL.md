---
name: kdp-niche-finder
description: Discover and validate profitable KDP coloring-book niches with fresh Amazon top-result data, relevance filtering, robust demand/competition statistics, seasonality and IP checks, and a flagship-first launch gate. Use for niche research, market validation, low-competition ideas, or deciding what coloring book to make.
---

# KDP Niche Finder

Separate discovery from validation. Web search can generate candidate ideas; only fresh Amazon evidence may approve production.

## Why the old score is insufficient

Do not approve a niche from `average monthly sales / average reviews` alone. A single bestseller, an irrelevant search result, missing reviews, or stale seasonal data can create a false blue-ocean verdict.

The canonical V2 gate uses:

- result relevance ratio;
- number of usable BSR and review observations;
- median monthly sales, not only the mean;
- demand depth (`<100k` and `<200k` BSR counts);
- median reviews;
- winner concentration (largest estimated seller share);
- cache age, seasonality, economics, content scalability, and IP risk.

`Opportunity V2 = median monthly sales × demand-depth factor / sqrt(median reviews + 1)` is a ranking aid, never a standalone verdict.

## Workflow

### 1. Build specific candidates

Start from user ideas, Amazon shopper language, adjacent sub-angles, and upcoming seasonal demand. Prefer a concrete topic × audience × style/use case. Generic head terms waste data pulls.

Discovery claims from blogs, Pinterest, Etsy, social media, or web search remain `DISCOVERY_ONLY` until Amazon validation.

### 2. Pull fresh Amazon evidence

Check Apify access:

```bash
python3 scripts/apify_research.py top10 "frog coloring book for adults" >/dev/null
```

Sweep only candidates the user could act on:

```bash
python3 .agents/skills/kdp-niche-finder/scripts/niche_sweep.py \
  "frog_adults=frog coloring book for adults" \
  "deep_sea_fishing=deep sea fishing coloring book"
```

New pulls include `researched_at`. Never fabricate Amazon BSR, review, price, title, ASIN, or publisher data. If the pull fails, mark the result `LOW_CONFIDENCE` and do not approve production.

### 3. Rank with conservative gates

```bash
python3 scripts/rank_niches.py
python3 scripts/rank_niches.py --json > data/niches/latest_ranked.json
```

Default freshness is 30 days; seasonal or fast-moving terms should be repulled closer to production, ideally within 7 days.

### 4. Interpret verdicts

| Verdict | Meaning | Action |
|---|---|---|
| `BLUE_OCEAN` | Fresh, relevant, deep demand, beatable median reviews, no dominant outlier | Eligible for deeper validation |
| `PROMISING` | Some demand depth and reachable competition | Validate economics and differentiation |
| `COMPETITIVE` | Demand exists but barrier is meaningful | Enter only with a strong product/ads angle |
| `SINGLE_WINNER` | One listing drives the apparent demand | Do not infer a healthy niche |
| `IRRELEVANT_RESULTS` | Amazon query drift; results do not match the intended book | Rewrite keyword and repull |
| `WEAK_DEMAND` | Too few meaningful sellers or low median sales | Avoid or reposition |
| `RESEARCH_MORE` | Thin/missing evidence | Repull or inspect products manually |
| `REFRESH_DATA` | Cache too old | Repull before deciding |

No automated verdict replaces manual review of titles/ASINs.

### 5. Complete the production gate

Before marking a niche `GO`, verify:

1. At least 8 top results captured.
2. At least 60% are dedicated, relevant coloring books for the intended audience.
3. At least 5 usable BSR observations and 5 review observations.
4. At least two genuinely selling relevant books, not one outlier.
5. Median demand is viable and price supports printing cost, royalty, and ads.
6. Search intent is not split across kids/adults or coloring/activity/fiction products.
7. Seasonality is evaluated in the correct window.
8. At least 30 genuinely distinct page concepts exist without duplication.
9. A clear cover/content gap exists versus the relevant top competitors.
10. Title, keywords, visual motifs, and concept pass IP/trademark screening.

### 6. Save an evidence packet

Save a markdown or JSON packet under `data/niches/` containing:

- query and research timestamp;
- relevant competitor table with ASIN/source URLs;
- V2 metrics, verdict, confidence, and flags;
- market gap and differentiation hypothesis;
- rough unit economics and ads assumptions;
- seasonality and IP notes;
- `GO`, `TEST`, or `NO_GO` decision;
- next validation date.

## Launch rule

Produce one flagship first. A high research score is a hypothesis, not proof of conversion. Do not batch a 5–10 book series until the flagship has enough live data to evaluate impressions, click-through rate, conversion, organic sales, ad spend, and returns/reviews.

## Output summary

```text
NICHE VALIDATION — <keyword> (<date>)
Data confidence: HIGH | MEDIUM | LOW
Relevant results: X/10 | usable BSR: X | usable reviews: X
Median sales/mo: X | <200k depth: X | median reviews: X | winner share: X%
Verdict: ... | Production decision: GO | TEST | NO_GO
Gap: ...
Risks: ...
Next: produce one flagship with $kdp-book-creator, or repull/reposition.
```

## References

- `references/opportunity-score.md` explains the approximate BSR conversion and legacy score.
- `scripts/apify_research.py` pulls Amazon data.
- `scripts/rank_niches.py` implements the V2 relevance/freshness/robust-statistics gate.
