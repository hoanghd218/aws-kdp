#!/usr/bin/env python3
"""Rank cached Amazon niche pulls with conservative, relevance-aware gates.

V2 deliberately avoids a single ``average sales / average reviews`` verdict.
It filters irrelevant search results, uses medians, measures demand depth and
winner concentration, and refuses to approve stale or thin evidence.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DIR = Path(__file__).resolve().parent.parent / "data" / "niches" / "apify"

GENERIC = {
    "a", "an", "and", "book", "books", "color", "coloring", "colour", "colouring",
    "page", "pages", "for", "the", "of", "with", "adult", "adults", "grown", "ups",
    "kid", "kids", "child", "children", "men", "women", "teen", "teens", "bold", "easy",
}
SYNONYMS = {"bookshop": "bookstore", "shop": "store", "ocean": "sea"}


def bsr_to_monthly_sales(bsr: int | None) -> float:
    if not bsr or bsr <= 0:
        return 0.0
    for threshold, daily in [
        (100, 900), (1_000, 160), (5_000, 45), (10_000, 17), (25_000, 9),
        (50_000, 5), (100_000, 2.5), (200_000, 1.2), (500_000, 0.4),
        (1_000_000, 0.12),
    ]:
        if bsr <= threshold:
            return daily * 30
    return 0.9


def _stem(word: str) -> str:
    word = SYNONYMS.get(word, word)
    if word.endswith("ies") and len(word) > 4:
        word = word[:-3] + "y"
    for suffix in ("ing", "ers", "er", "ed", "es", "s", "y"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            word = word[: -len(suffix)]
            break
    return word


def _tokens(text: str) -> list[str]:
    return [_stem(token) for token in re.findall(r"[a-z0-9]+", text.lower())]


def _audience(text: str) -> str | None:
    tokens = set(_tokens(text))
    adult = bool(tokens & {"adult", "adults", "grown", "women", "men", "teen", "teens"})
    kids = bool(tokens & {"kid", "kids", "child", "children", "toddler", "preschool"})
    if adult and not kids:
        return "adults"
    if kids and not adult:
        return "kids"
    return None


def title_is_relevant(keyword: str, title: str) -> bool:
    title_tokens = set(_tokens(title))
    query_tokens = _tokens(keyword)
    core = [token for token in query_tokens if token not in {_stem(x) for x in GENERIC}]
    if "color" not in title_tokens:
        return False
    required = max(1, math.ceil(len(set(core)) * 0.67)) if core else 0
    matched = sum(1 for token in set(core) if token in title_tokens)
    query_audience = _audience(keyword)
    title_audience = _audience(title)
    audience_ok = not query_audience or not title_audience or query_audience == title_audience
    return matched >= required and audience_ok


def _extract_bsr(item: dict[str, Any]) -> int | None:
    for key in ("bestsellerRanks", "bestsellersRank", "bsr", "bestSellersRank"):
        value = item.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            match = re.search(r"[\d,]+", value)
            if match:
                return int(match.group(0).replace(",", ""))
        if isinstance(value, list):
            for entry in value:
                if isinstance(entry, dict) and str(entry.get("category", "")).lower() == "books":
                    try:
                        return int(str(entry.get("rank", "")).replace(",", "").replace("#", ""))
                    except ValueError:
                        pass
            if value and isinstance(value[0], dict):
                try:
                    return int(str(value[0].get("rank", "")).replace(",", "").replace("#", ""))
                except ValueError:
                    pass
    return None


def _number(item: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = item.get(key)
        if isinstance(value, dict):
            value = value.get("value") or value.get("amount")
        if value is None:
            continue
        try:
            return float(str(value).replace("$", "").replace(",", "").strip())
        except ValueError:
            continue
    return None


def normalized_products(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw = data.get("raw_products") or []
    if raw:
        return [
            {
                "title": str(item.get("title") or ""),
                "asin": item.get("asin"),
                "bsr": _extract_bsr(item),
                "reviews": _number(item, "reviewsCount", "reviews"),
                "price": _number(item, "price", "priceValue", "listPrice"),
            }
            for item in raw[:10]
        ]

    # Legacy cache fallback. New pulls preserve per-product alignment in raw_products.
    titles = data.get("top10_titles") or []
    bsr = data.get("top10_bsr") or []
    reviews = data.get("top10_reviews") or []
    prices = data.get("top10_prices") or []
    count = max(len(titles), len(bsr), len(reviews), len(prices))
    return [
        {
            "title": titles[i] if i < len(titles) else "",
            "asin": None,
            "bsr": bsr[i] if i < len(bsr) else None,
            "reviews": reviews[i] if i < len(reviews) else None,
            "price": prices[i] if i < len(prices) else None,
        }
        for i in range(min(10, count))
    ]


def cache_age_days(path: Path, data: dict[str, Any]) -> int:
    value = data.get("researched_at") or data.get("fetched_at")
    if value:
        try:
            when = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            return max(0, (datetime.now(timezone.utc) - when).days)
        except ValueError:
            pass
    return max(0, (datetime.now(timezone.utc) - datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)).days)


def evaluate(path: Path, max_age_days: int) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    keyword = str(data.get("primary_keyword") or path.stem.replace("_", " "))
    products = normalized_products(data)
    relevant = [p for p in products if title_is_relevant(keyword, p["title"])]
    measured = [p for p in relevant if p["bsr"]]
    reviews = [p["reviews"] for p in relevant if p["reviews"] is not None]
    prices = [p["price"] for p in relevant if p["price"] and p["price"] > 0]
    sales = [bsr_to_monthly_sales(p["bsr"]) for p in measured]
    age = cache_age_days(path, data)

    median_sales = statistics.median(sales) if sales else 0.0
    mean_sales = statistics.mean(sales) if sales else 0.0
    median_reviews = statistics.median(reviews) if reviews else 0.0
    under100k = sum(1 for p in measured if p["bsr"] < 100_000)
    under200k = sum(1 for p in measured if p["bsr"] < 200_000)
    winner_share = max(sales) / sum(sales) if sales and sum(sales) else 0.0
    depth_factor = min(1.0, under200k / 3.0)
    robust_opp = median_sales * depth_factor / math.sqrt(median_reviews + 1)
    relevance_ratio = len(relevant) / len(products) if products else 0.0

    flags: list[str] = []
    if age > max_age_days:
        verdict = "REFRESH_DATA"
        flags.append(f"cache_{age}d")
    elif len(products) < 8 or len(measured) < 5 or len(reviews) < 5:
        verdict = "RESEARCH_MORE"
        flags.append("thin_evidence")
    elif relevance_ratio < 0.60:
        verdict = "IRRELEVANT_RESULTS"
        flags.append("query_drift")
    elif median_sales < 6 or under200k < 2:
        verdict = "WEAK_DEMAND"
    elif winner_share > 0.55:
        verdict = "SINGLE_WINNER"
        flags.append("outlier_dominates")
    elif median_reviews >= 250:
        verdict = "SATURATED"
    elif median_sales >= 15 and under200k >= 3 and median_reviews <= 100 and robust_opp >= 2:
        verdict = "BLUE_OCEAN"
    elif median_sales >= 6 and under200k >= 2 and median_reviews <= 150:
        verdict = "PROMISING"
    else:
        verdict = "COMPETITIVE"

    return {
        "niche": path.stem,
        "keyword": keyword,
        "cache_age_days": age,
        "results": len(products),
        "relevant_results": len(relevant),
        "relevance_ratio": relevance_ratio,
        "measured_bsr": len(measured),
        "review_observations": len(reviews),
        "median_monthly_sales": median_sales,
        "mean_monthly_sales": mean_sales,
        "median_reviews": median_reviews,
        "median_price": statistics.median(prices) if prices else 0.0,
        "under_100k": under100k,
        "under_200k": under200k,
        "winner_share": winner_share,
        "opportunity_v2": robust_opp,
        "verdict": verdict,
        "flags": flags,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-age-days", type=int, default=30)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    rows = [row for path in sorted(DIR.glob("*.json")) if (row := evaluate(path, args.max_age_days))]
    priority = {"BLUE_OCEAN": 0, "PROMISING": 1, "COMPETITIVE": 2}
    rows.sort(key=lambda row: (priority.get(row["verdict"], 9), -row["opportunity_v2"]))

    if args.json:
        print(json.dumps(rows, indent=2))
        return 0

    print(f"{'niche':<23}{'rel':>6}{'med/mo':>8}{'<200k':>7}{'medrev':>8}{'win%':>7}{'OppV2':>8}  verdict")
    print("-" * 104)
    for row in rows:
        print(
            f"{row['niche']:<23}{row['relevant_results']:>2}/{row['results']:<3}"
            f"{row['median_monthly_sales']:>8.1f}{row['under_200k']:>7}"
            f"{row['median_reviews']:>8.0f}{row['winner_share']:>7.0%}"
            f"{row['opportunity_v2']:>8.2f}  {row['verdict']}"
        )
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    print(f"\n{len(rows)} niches ranked with V2 gates. Verdicts: {counts}")
    print("Approval requires fresh data, >=60% relevant results, >=5 BSR/review observations, and demand depth.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
