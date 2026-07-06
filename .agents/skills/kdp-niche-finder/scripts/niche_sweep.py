#!/usr/bin/env python3
"""Batch-pull Apify top-10 for many keywords, then print the ranked Opportunity table.

Usage (from repo root):
    python3 .claude/skills/kdp-niche-finder/scripts/niche_sweep.py \
        "bass_fishing=bass fishing coloring book" \
        "frog_adults=frog coloring book for adults"

Each arg is "key=keyword". Pulls are saved to data/niches/apify/<key>.json (idempotent: a valid
cached pull is skipped, so re-running after an interruption is cheap and safe). After pulling, it
runs scripts/rank_niches.py to print the ranked table. Apify token rotation is handled by
scripts/apify_research.py (comma-separated APIFY_API_TOKEN pool in .env).
"""
import os, sys, subprocess, json

REPO = subprocess.run(["git","rev-parse","--show-toplevel"], capture_output=True, text=True).stdout.strip() \
       or os.getcwd()
APIFY = os.path.join(REPO, "scripts", "apify_research.py")
RANK  = os.path.join(REPO, "scripts", "rank_niches.py")
OUTDIR = os.path.join(REPO, "data", "niches", "apify")
os.makedirs(OUTDIR, exist_ok=True)

def valid(path):
    try:
        with open(path) as f:
            return f.read(1) == "{" and bool(json.load(open(path)).get("top10_bsr"))
    except Exception:
        return False

pairs = []
for a in sys.argv[1:]:
    if "=" not in a:
        print(f"skip bad arg (need key=keyword): {a}"); continue
    k, kw = a.split("=", 1)
    pairs.append((k.strip(), kw.strip()))

if not pairs:
    print(__doc__); sys.exit(1)

for k, kw in pairs:
    out = os.path.join(OUTDIR, f"{k}.json")
    if valid(out):
        print(f"skip {k} (cached)"); continue
    print(f"pull {k} : {kw}")
    with open(out, "w") as fo:
        r = subprocess.run([sys.executable, APIFY, "top10", kw], stdout=fo,
                           stderr=subprocess.PIPE, text=True)
    print("  OK" if valid(out) else f"  FAIL: {r.stderr.strip()[:200]}")

print("\n" + "="*70)
subprocess.run([sys.executable, RANK])
