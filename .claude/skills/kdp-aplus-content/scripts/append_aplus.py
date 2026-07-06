#!/usr/bin/env python3
"""Append A+ Content module image prompts into a book's image_prompts.json.

Reads  output/{theme_key}/aplus_content.json  (written by the kdp-aplus-content skill)
and pushes one render item per module into  output/{theme_key}/image_prompts.json.
Each module renders at its own "size" (the hero is a wide banner); modules without a
"size" fall back to the standard KDP A+ size 970x600. Idempotent: strips any prior
aplus_* items first. Creates image_prompts.json if it does not exist yet.

Usage:
    python3 .claude/skills/kdp-aplus-content/scripts/append_aplus.py <theme_key>
"""
import json
import os
import sys

A_PLUS_SIZE = "970x600"  # default when a module omits "size"


def main():
    if len(sys.argv) < 2:
        print("Usage: append_aplus.py <theme_key>")
        sys.exit(1)

    theme = sys.argv[1]
    base = os.path.join("output", theme)
    aplus_path = os.path.join(base, "aplus_content.json")
    queue_path = os.path.join(base, "image_prompts.json")

    if not os.path.isdir(base):
        print(f"Error: book folder not found: {base}")
        sys.exit(1)
    if not os.path.exists(aplus_path):
        print(f"Error: {aplus_path} not found. Write aplus_content.json first.")
        sys.exit(1)

    modules = json.load(open(aplus_path, encoding="utf-8")).get("modules", [])
    if not modules:
        print(f"Error: no 'modules' in {aplus_path}")
        sys.exit(1)

    if os.path.exists(queue_path):
        items = json.load(open(queue_path, encoding="utf-8"))
    else:
        items = []

    # idempotent: drop previously appended A+ items
    items = [it for it in items if not str(it.get("filename", "")).startswith("aplus_")]

    for m in modules:
        mid = m.get("id")
        if not mid:
            continue
        items.append({
            "prompt": m.get("image_prompt", ""),
            "size": m.get("size") or A_PLUS_SIZE,
            "filename": f"aplus_{mid}.png",
        })

    json.dump(items, open(queue_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    aplus_items = [it for it in items if str(it["filename"]).startswith("aplus_")]
    other = len(items) - len(aplus_items)
    print(f"Updated {queue_path}")
    print(f"  {other} existing items + {len(aplus_items)} A+ modules:")
    for it in aplus_items:
        print(f"    {it['filename']}  ({it['size']})")


if __name__ == "__main__":
    main()
