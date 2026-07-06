#!/usr/bin/env python3
"""Rank niches from Apify top10 pulls in data/niches/apify/*.json by real Opportunity Score.

Opp = avg monthly sales(top10) / avg reviews(top10).  Uses the niche-hunter BSR->sales table.
Usage: python3 scripts/rank_niches.py
"""
import json, glob, os

DIR = os.path.join(os.path.dirname(__file__), "..", "data", "niches", "apify")

def bsr_to_sales(b):
    if not b or b <= 0: return 0.0
    for thr, s in [(100,900),(1000,160),(5000,45),(10000,17),(25000,9),(50000,5),
                   (100000,2.5),(200000,1.2),(500000,0.4),(1000000,0.12)]:
        if b <= thr: return s
    return 0.03

def verdict(opp, mo):
    if mo < 12:  base = "WEAK/low-demand"
    elif opp >= 5:   base = "BLUE_OCEAN"
    elif opp >= 2:   base = "MODERATE"
    elif opp >= 0.5: base = "COMPETITIVE"
    else:            base = "SATURATED"
    return base

rows = []
for path in sorted(glob.glob(os.path.join(DIR, "*.json"))):
    name = os.path.basename(path)[:-5]
    try:
        d = json.load(open(path))
    except Exception:
        continue
    bsr = [x for x in d.get("top10_bsr", []) if x]
    rev = d.get("top10_reviews", []) or []
    px  = [x for x in d.get("top10_prices", []) if x]
    if not bsr:
        continue
    sales = [bsr_to_sales(b) for b in bsr]
    mo = sum(sales)/len(sales)*30
    avg_rev = sum(rev)/len(rev) if rev else 0
    opp = mo/avg_rev if avg_rev > 0 else mo
    rows.append({
        "niche": name, "kw": d.get("primary_keyword",""),
        "avg_bsr": sum(bsr)//len(bsr), "min_bsr": min(bsr),
        "under100k": sum(1 for b in bsr if b < 100000),
        "avg_rev": avg_rev, "avg_px": (sum(px)/len(px) if px else 0),
        "mo_sales": mo, "opp": opp, "verdict": verdict(opp, mo),
    })

rows.sort(key=lambda r: r["opp"], reverse=True)
print(f"{'niche':<22}{'avgBSR':>9}{'minBSR':>9}{'<100k':>6}{'rev':>6}{'$':>6}{'sales/mo':>9}{'Opp':>7}  verdict")
print("-"*92)
for r in rows:
    print(f"{r['niche']:<22}{r['avg_bsr']:>9}{r['min_bsr']:>9}{r['under100k']:>6}"
          f"{r['avg_rev']:>6.0f}{r['avg_px']:>6.1f}{r['mo_sales']:>9.1f}{r['opp']:>7.2f}  {r['verdict']}")
print(f"\n{len(rows)} niches ranked.  (mo<12 => WEAK regardless of Opp; off-season seasonal niches read low)")
