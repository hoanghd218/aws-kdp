# Next KDP coloring-book opportunity — 2026-10-11

Market: Amazon.com, English paperback, adult/kids coloring books. Research is a snapshot, not a sales guarantee. The local Apify top-10 files were saved 2026-09-28 and lack an embedded `researched_at` field. Re-pull before committing to production or ad spend; `APIFY_API_TOKEN` is not configured in this environment.

## Candidate comparison

| Query | Relevant / 10 | Usable BSR | Estimated median units/month* | BSR <200k | Median reviews | Median price | Largest seller share* | Assessment |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| horror coloring book for adults | 9 | 7 | 150 | 7 | 99 | $9.99 | 42% | TEST: strongest observed demand, seasonal and IP-sensitive |
| dragon coloring book for adults | 9 | 8 | 43.5 | 4 | 33 | $6.99 | 31% | TEST: evergreen, but overlaps Lunora Press's existing Cozy Dragon Treasures |
| fishing coloring book for kids | 7 | 7 | 12 | 3 | 10 | $9.99 | 43% | WATCH: weaker demand and mixed search intent |

*Modelled from a BSR snapshot by `scripts/rank_niches.py`; not actual orders or live sales. One September snapshot may overstate annual demand for horror.

Local evidence: `data/niches/apify/horror_adults.json`, `dragon_adults.json`, `fishing_for_kids.json`. Ranking script: `scripts/rank_niches.py`.

Representative Amazon listings from the captured top results:

- Horror: [Freak of Horror, B0CFCWW65Z](https://www.amazon.com/dp/B0CFCWW65Z), [Dark Beauty, B0C9KCX1XC](https://www.amazon.com/dp/B0C9KCX1XC), [Horror Stoner, B0FKGNZDSB](https://www.amazon.com/dp/B0FKGNZDSB). Several competing concepts use recognizable movie villains or serial killers. An original-creature book can avoid that rights risk, but the adjacent concept needs a fresh query validation.
- Dragons: [Mythographic Dragonspell, 1250373263](https://www.amazon.com/dp/1250373263), [Dragons Coloring Book, B0CWD9J7FH](https://www.amazon.com/dp/B0CWD9J7FH), [The Garden of Baby Dragons, B0GLXBLW39](https://www.amazon.com/dp/B0GLXBLW39). One direct Amazon page for Dragonspell showed a Books BSR near 60,691 when crawled in October; BSR fluctuates.

## Decision

**First: test the already finished `out/dragon_hoard_treasure` flagship rather than create another near-duplicate dragon book.** Product name: *Cozy Dragon Treasures: Coloring Book for Adults and Teens*. Publish/list only after the user elects to do so; measure impressions, clicks, conversion, royalties, ad cost, reviews, and returns.

**Next genuinely new title to validate: an original adult horror/haunted folklore coloring book.** Proposed content: 60 distinct single-sided scenes in an eerie village, haunted observatory, forest, lighthouse, greenhouse, abandoned theater, and similar settings, with wholly original creatures. Differentiate from the existing cozy Gothic book by a darker horror audience and stronger suspense, while avoiding gore that would narrow buyers. Avoid copyrighted film villains, celebrity likenesses, franchise names, and similar cover cues. Do one flagship, not a series batch. Given the October date, treat 2026 Halloween demand as uncertain; assess year-round demand with a fresh pull and plan the next Halloween season early.

**Economics:** KDP's current US large-trim black-ink rate for 110+ pages is $1 + $0.017/page. For a 125-page, 8.5x11 paperback, estimated print cost is $3.13. At $9.99, standard-distribution royalty is about $2.86 before ads, returns, taxes, and other costs (60% × $9.99 − $3.13). At $8.99, the 50% tier yields about $1.37. Confirm with KDP's calculator at setup.

Sources: [KDP printing cost](https://kdp.amazon.com/en_US/help/topic/G201834340), [KDP print pricing and royalties](https://kdp.amazon.com/en_US/help/topic/G8BKPU9AGVZSF9QF), [KDP content and AI rules](https://kdp.amazon.com/en_US/help/topic/G200672390), [KDP IP rights](https://kdp.amazon.com/help?topicId=A1PQPW247IIYZY).

Confidence: **MEDIUM** for broad niche ranking, **LOW** for any specific new sub-angle until a fresh Amazon top-10 pull confirms relevant demand and competition. Next validation date: before artwork production or paid ads.
