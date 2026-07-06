# A+ Content — the 7-module pattern (Bold & Easy best-sellers)

## What A+ Content is
Amazon's "From the Publisher" strip below the book description — a series of image
modules. **All marketing copy lives INSIDE the images.** KDP gives you up to 5–7 modules.
Top Bold & Easy sellers (e.g. Coco Wyo "Simple Art") win by showing real interior pages,
keeping text short, and including one fully-colored sample.

## KDP A+ image specs (hard rules)
- **Width: 970 px** (the standard module width). Most modules → **970 × 600 px** (≈ 16:10).
- **≥ 300 DPI**, JPG or PNG, **≤ 5 MB** per image.
- No external links, no phone/email, no price/shipping claims, no time-sensitive wording
  ("new", "best seller", "#1"), no other brands' trademarks, no customer-review quotes.
- If a renderer only accepts aspect ratios, use **16:10** then resize to 970 px wide.

## Copywriting rules
- One headline + at most 3 short bullets/captions per module. Big, scannable.
- Reference what's ACTUALLY inside (real scenes, real page count, real trim size).
- Weave 1–2 of the book's top keywords in naturally — never keyword-stuff.
- Match the book's voice: cozy = warm/gentle, kids = playful, anime = bold/energetic.
- Every `image_prompt` must reserve clear empty space (a cream/solid panel) for the copy.

## Composite vs pure-AI
Three modules look best built by **compositing real `page_NN.png` files** (don't let AI
fake book pages): `inside_grid`, `single_sided`, `before_after`. The other four
(`hero`, `bold_easy`, `perfect_for`, `series_cta`) the renderer can draw standalone.
Still write a self-contained `image_prompt` for all 7 so they're generatable.

## The 7 modules

| id | type | purpose | composite? |
|----|------|---------|-----------|
| `01_hero` | full-width banner | brand + one-line hook + a few page thumbnails | optional |
| `02_inside_grid` | image grid | 4–6 real interior pages — prove the line-art style | **yes** |
| `03_bold_easy` | feature close-up | zoom on thick outlines + 3 benefit bullets | optional |
| `04_single_sided` | feature | single-sided / paper / trim-size selling points | **yes** |
| `05_perfect_for` | 3-column icons | stress relief / gift / easy-for-everyone | no |
| `06_before_after` | transformation | blank line-art vs fully-colored sample | **yes** |
| `07_series_cta` | brand close | series tie-in + warm closing invitation | no |

## aplus_content.json shape

```json
{
  "book": "<title>",
  "brand": "<brand/author>",
  "note": "Each module = ONE 970x600 image. 'copy' = text baked into the image. 'image_prompt' = background art; composite real pages where noted.",
  "modules": [
    {
      "id": "01_hero",
      "type": "full-width banner",
      "copy": { "headline": "...", "subhead": "...", "footer": "..." },
      "image_prompt": "... 970x600 ... reserve a panel for the headline ...",
      "composite": false
    }
    // ... 6 more, ids exactly: 02_inside_grid, 03_bold_easy, 04_single_sided,
    //     05_perfect_for, 06_before_after, 07_series_cta
  ]
}
```

`copy` fields vary by module type — use `headline`, `subhead`, `caption`, `bullets` (array),
`columns` (array of {title,text}), `footer` as the layout needs. Keep `id` values exactly as
above so the append script names files `aplus_<id>.png`.

## Theme adaptation cheatsheet
- **Palette**: reuse the colors named in the book's own `cover_prompt`.
- **Scenes**: skim `page_prompts` and name the real categories in `02`/`hero` captions.
- **Audience**: adults → calm/premium; kids 6-12 → bright/fun, mention "for kids ages 6-12";
  anime → dynamic, mention fandom.
- **Numbers**: pull page count from `len(page_prompts)` and trim from `page_size`.
