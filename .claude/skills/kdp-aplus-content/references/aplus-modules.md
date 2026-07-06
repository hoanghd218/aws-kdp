# A+ Content — the 5-module pattern

The "From the Publisher" strip below the book description. Up to 5–7 image modules; **all
marketing copy lives INSIDE the images.** This skill builds the proven **kawaii coloring-book
layout** (inspired by Girl Getaway / MinaAru best-seller style): hero → specs → features+friends →
two sample showcases. The look is defined in `kawaii-style.md` — read it first; this file is the
layout + copy spec.

---

## Visual philosophy (learned from top sellers)

The strongest A+ strips share these traits:

1. **Product-first, decoration-second.** Showcase panels let the colored art carry the visual
   weight — sparse sparkle stars on a solid background, nothing more. Scalloped borders and kawaii
   frames belong only on the features/friends module, not on showcase panels.

2. **Bold size hierarchy.** Each showcase panel has ONE large colored image (60%+ width) + TWO
   smaller line-art thumbnails. Never three equal-size images.

3. **Solid bold background colors**, consistent per module type:
   - Hero + Specs: warm golden yellow (e.g. `#F2C84B`) — cheerful, book-cover-adjacent
   - Showcase A + B: solid soft teal (`#6BBFBF`) — premium, calm, makes art pop
   - Features/Friends: soft cream or the book's main accent — softer feel

4. **Colored samples must look FINISHED.** The large image in showcase modules is a full-color
   cel-shaded illustration of a real scene from the book, in the book's actual palette — it
   proves how beautiful a colored page looks. Never AI-generic art.

5. **Less text in showcases.** Modules 04 and 05 carry ZERO baked-in text — the art speaks.
   Only the Specs module (02) has callout labels.

---

## The 5 modules

| id | panel | what it shows | composite real files? |
|----|-------|---------------|------------------------|
| `01_hero` | brand hero | book cover mockup + brand wordmark + big bubble title + subtitle | **cover** |
| `02_specs` | book specs | open-book mockup: single-sided pages + blank-paper backs + dimension labels | **page** |
| `03_features_friends` | features + cast | 4 feature icons (top) + "Meet the Friends" character line-up (bottom) | no |
| `04_sample_showcase_a` | page samples | 1 large COLORED sample (right) + 2 line-art page thumbnails (left) | **pages** |
| `05_sample_showcase_b` | page samples | 1 large COLORED sample (left) + 2 line-art page thumbnails (right) — mirrored layout | **pages** |

Keep the `id` values exactly as above — the append script names files `aplus_<id>.png`.

---

## Per-module spec

### 01_hero — size 970x500 — composite: real cover

**Background:** warm golden yellow (e.g. `#F2C84B`) with tiny scattered 4-point sparkle stars in
cream/white + small plus signs. Sparse, asymmetric. NO outer border frame.

**Layout:**
- **LEFT 45%**: the book's front cover as a standing paperback, 5-degree rightward tilt, soft drop
  shadow. Composite the real `cover.png` / `front_artwork.png` here.
- **RIGHT 55%**: completely open flat golden background reserved for typography only:
  - Brand name in small handwritten marker script (warm brown `#5A4636`) at top
  - Book TITLE in large chunky rounded bubble font, all-caps, dark brown outline with white fill,
    slight playful tilt
  - Subtitle in medium handwritten script below

`copy`: `{ brand, title, subtitle }`.

---

### 02_specs — size 970x600 — composite: real page

**Background:** same warm golden yellow with sparkle stars. NO outer border frame.

**Layout:**
- **LEFT 38%**: front cover composite (same standing-tilted-paperback treatment as hero)
- **RIGHT 57%**: an open-book spread illustration (kawaii style, clean warm-brown outlines, slight
  leftward tilt, soft drop shadow):
  - **Left leaf**: plain white page with handwritten label "Single-sided pages" + curved arrow
    pointing at the blank leaf
  - **Behind the open book**: a second loose sheet peeking out, labeled "Blank Paper" in small
    script
  - **Right leaf**: COMPOSITE PLACEHOLDER for a real `page_NN.png` coloring page
  - **Below the spread**: dashed dimension lines (thin warm-brown, arrowhead end-caps) labeled
    with the trim size from `plan.json.page_size` (e.g. "8.5 inch" side and bottom)

`copy`: `{ size_label, callouts: ["Single-sided pages", "Blank Paper", "<W> x <H> inch"] }`.

---

### 03_features_friends — size 970x600 — composite: no

**Background:** soft cream `#FBF3E4` (or book's lightest accent). A hand-drawn wavy scalloped
deckle border in the book's accent color — only module that uses this frame. Sparse pastel doodles.

**Layout (3 horizontal zones):**
- **Top 38%**: 4 evenly spaced icon-caption columns. Each column: one kawaii chibi icon (pastel
  colors, warm-brown outline) + caption below in marker script. Standard captions:
  `Easy to Color` / `<N> Unique Scenes / No repeats` / `Cozy & Relaxing / For Adults` /
  `Mindful / Stress Relief` (replace "For Adults" with "For Kids Ages 6-12" for kids books).
  Use real page count for N.
- **Middle divider**: big bubble-font headline centered: **"Meet the Friends"**, flanked by sparkle
  stars.
- **Bottom 45%**: 4–6 full-color kawaii chibi characters in a horizontal line on a ground stroke.
  Each has a name-tag label below in handwritten script. Characters MUST be real recurring animals
  from the book's `page_prompts` — see "Deriving the friends" below.

`copy`: `{ features: [{icon_hint, caption}], headline: "Meet the Friends", friends: [...] }`.

---

### 04_sample_showcase_a — size 970x600 — composite: pages

**Background:** solid soft teal (e.g. `#6BBFBF`) with tiny scattered 4-point sparkle stars and
plus signs in white/cream. Sparse. NO outer border frame.

**Layout:**
- **LEFT 32%**: TWO small square page-thumbnail cards in a slight cascade (top +5°, bottom -4°,
  slightly overlapping). Each has a thin white border frame (polaroid style) + soft drop shadow.
  COMPOSITE PLACEHOLDER — mark for real `page_NN.png` line-art pages.
- **RIGHT 63%**: ONE large fully rendered full-color kawaii illustration of a real scene from the
  book — the colored version of the first or most iconic reading scene. Draw completely (not a
  placeholder), in the book's actual palette, cel-shaded flat pastel style. Surround with a thick
  colored border frame (book's accent color, 8px) like a premium photo card + soft drop shadow.
  NO text baked in.

The colored sample must describe a SPECIFIC scene from `page_prompts[0]` or another iconic page,
with exact palette colors named. "Cozy reading nook scene" is too vague — name the character,
location, props, and colors.

---

### 05_sample_showcase_b — size 970x600 — composite: pages

**Background:** same soft teal as module 04 — the two panels read as a matched pair.

**Layout:** MIRRORED from 04:
- **LEFT 63%**: ONE large fully rendered full-color kawaii illustration — a DIFFERENT scene from
  the book (not the same as module 04). Same treatment: full color, real palette, cel-shaded,
  thick border frame in a different accent color, soft drop shadow. NO text.
- **RIGHT 32%**: TWO small square line-art thumbnail cards, different pages from module 04, same
  polaroid treatment + composite placeholders.

---

## Deriving the "friends" (module 03)

Skim `page_prompts` for recurring cast. Pick the **4–6 most frequent** animals/characters.
Example: a book with "cat" in 10 pages, "bunny" in 5, "bear" in 5, "fox" in 4, "owl" in 3,
"hedgehog" in 2 → use Cat, Bunny, Bear, Fox, Owl, Hedgehog.

If the book has no recurring characters (flowers/mandalas/patterns), swap for 4–6 signature
**motifs** and rename the headline to "What's Inside" (e.g. a teacup, a bouquet, a lantern, a
butterfly).

---

## aplus_content.json shape

```json
{
  "book": "<title>",
  "brand": "<brand>",
  "palette": ["#FBF3E4", "#F0C4B8", "#BFD3A8", "#5A4636"],
  "note": "...",
  "modules": [
    {
      "id": "01_hero",
      "size": "970x500",
      "composite": "cover",
      "copy": { "brand": "...", "title": "...", "subtitle": "..." },
      "image_prompt": "..."
    }
    // 02_specs, 03_features_friends, 04_sample_showcase_a, 05_sample_showcase_b
  ]
}
```

`composite` values: `false`, `"cover"`, `"page"`, `"pages"`.  
Default size is `970x600`; hero uses `970x500`.

---

## Theme adaptation cheatsheet

- **Background colors**: always golden yellow for hero/specs, teal for showcases. Adjust the teal
  hue slightly to match the book's palette (e.g. sage-teal for nature books, blue-teal for ocean).
- **Colored samples**: describe a specific scene from `page_prompts`, with named palette colors.
  Never write "a cozy reading scene" — name character, location, props, colors.
- **Numbers**: page count from `len(page_prompts)`, trim from `page_size`.
- **Audience**: adults → cozy/calm wording; kids 6-12 → replace "For Adults" with "For Kids
  Ages 6-12" in features; kids → bouncy voice in copy.
- **Showcase border color**: use a different accent from the palette for each showcase panel (04 vs
  05 get different colored frames so they're visually distinct at a glance).
