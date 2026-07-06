---
name: kdp-aplus-content
description: Generate Amazon KDP A+ Content ("From the Publisher") in the proven kawaii coloring-book style (Girl Getaway / MinaAru best-seller look) — a 5-module strip: brand hero, book specs, feature icons + "Meet the Friends" character line-up, and two page-sample showcases. Layout pattern: warm golden background for hero/specs, solid teal for showcases (1 large colored sample + 2 line-art thumbnails each). Produces aplus_content.json (baked-in copy + full kawaii image prompts) and appends the A+ prompts into the book's image_prompts.json. USE WHEN user says 'tao content A+', 'create A+ content', 'kdp a plus', 'from the publisher', 'a+ modules', 'lam content a+', 'enhanced brand content', 'tao a+ cho sach', 'add a+ content', 'make a+ for book', 'meet the friends', 'aplus kawaii'.
---

# KDP A+ Content Generator (kawaii style)

Turn a finished or planned coloring book into a **5-module A+ Content strip** — the
"From the Publisher" images that sell the book below the description. The target look is the
best-selling **kawaii coloring-book** style (Girl Getaway / MinaAru): product-first layout with
minimal decoration, bold background colors, and a dominant large colored sample in each showcase
panel. Key pattern: warm golden yellow background for hero + specs; solid teal background for the
two sample showcases; scalloped kawaii frame ONLY on the features/friends module.

Each module is ONE image; marketing copy is baked INTO the image at layout time. This skill
writes the **theme-aware copy + full kawaii image prompts**; a script does the mechanical append
into the book's render queue. The art is rendered later by the repo's normal image pipeline.

---

## Inputs

Works off an existing book under `output/{theme_key}/`:
- `plan.json` — `title`, `subtitle`, `audience`, `page_size`, `author`/`brand`, `keywords`,
  `cover_prompt`, `page_prompts` (required).
- `cover.png` / `front_artwork.png` — the cover, composited into the hero (optional).
- `images/page_NN.png` — interior pages, composited into specs + sample modules (optional).
- `image_prompts.json` — the render queue (optional; created if missing).

If the user names a book ("A+ for farm_animals_cute_adult") use that theme_key. Otherwise list
`output/*/plan.json` and ask which book.

`author` may be a dict `{first_name, last_name}` or a string — render it as `"First Last"` for the
brand wordmark.

---

## Process

### Step 1 — Read the book
Load `output/{theme_key}/plan.json`. Pull `title`, `subtitle`, `audience`, `page_size`,
`author`/`brand`, `keywords`, `cover_prompt`, and **skim every `page_prompts` entry** to learn:
- the real **scene mix** (what's actually inside), and
- the **recurring characters / motifs** for the "Meet the Friends" line-up.

The A+ copy MUST reference what's really in this book — real scenes, real page count
(`len(page_prompts)`), real trim (`page_size`). Never generic filler.

### Step 2 — Lock the style, then write the 5 modules
Read **`references/kawaii-style.md`** (the visual DNA — borders, doodles, fonts, mascot, palette)
and **`references/aplus-modules.md`** (the 5-module layout + per-module copy spec). Decide ONE
palette pulled from `cover_prompt` and carry it across all modules.

Write `output/{theme_key}/aplus_content.json` with all 5 modules:
`01_hero`, `02_specs`, `03_features_friends`, `04_sample_showcase_a`, `05_sample_showcase_b`.

For each module fill:
- `copy` — the exact text baked into the image (keys per the module spec). Match the book's tone.
- `image_prompt` — a **self-contained kawaii panel** the renderer can draw directly: cream
  scalloped border, the book palette, the right composition, and **clear empty space reserved for
  the copy**. Carry every style pillar from `kawaii-style.md` into the wording.
- `size` — `970x500` for the hero banner, `970x600` for the rest.
- `composite` — `false` / `"cover"` / `"page"` / `"pages"`: which real files to drop in at layout.

Use the book's real numbers and weave 1–2 top keywords naturally into headlines — never stuff.

### Step 3 — Generate the A+ images

**Option A — generate directly** (preferred, uses `chatgpt` renderer via local proxy):
```bash
python3 scripts/generate_aplus_images.py <theme_key> [--renderer chatgpt|ai33|nanopic]
```
Reads `aplus_content.json`, calls the renderer for each module, crops/resizes to exact A+ pixel
size (`970x500` hero, `970x600` rest), and saves to `output/{theme_key}/aplus/aplus_<id>.png`.
Default renderer is `chatgpt`. Modules with `"composite"` set still generate the AI background —
the user composites the real cover/page on top afterwards.

**Option B — append to render queue** (for batch / external tool flows):
```bash
python3 .claude/skills/kdp-aplus-content/scripts/append_aplus.py <theme_key>
```
Pushes the 5 prompts into `image_prompts.json` at their sizes. Idempotent.

### Step 4 — Report
Tell the user: the 5 images generated to `output/{theme_key}/aplus/`, which need **real
cover/page composites** on top (`01_hero` ← composite real cover; `02_specs`/`04`/`05` ←
composite real pages as thumbnails), and point them to `aplus_content.json` for the copy to
type into KDP A+ layout.

---

## Output

**Type:** book asset · **Location:** `output/{theme_key}/`
- `aplus_content.json` — 5 kawaii modules, copy + image prompts (NEW)
- `aplus/aplus_<id>.png` — 5 rendered A+ images at exact KDP size (NEW, via `generate_aplus_images.py`)
- `image_prompts.json` — A+ prompts appended at their sizes (UPDATED, via `append_aplus.py`)

---

## Quality Criteria

GOOD A+ content:
- Looks like ONE branded kawaii set — same palette, same cream wavy borders, same fonts across all 5.
- Copy names what's ACTUALLY inside (real scenes, real page count, real trim size).
- "Meet the Friends" shows THIS book's real recurring characters (or its signature motifs).
- Mostly imagery; text is short, big, scannable — one headline + ≤3 captions per module.
- Reserves clear empty space in each prompt for the baked-in copy.
- Flags the cover/page-composite modules instead of letting AI fake the cover or book pages.
- **970 px wide** (exact), ≤ 5 MB, PNG/JPG. A+ images are screen-only — DPI metadata is irrelevant; KDP does not check it.

BAD A+ content:
- Generic "relax and unwind" copy that fits any book; invented features.
- Walls of text baked into the image; mismatched colors module-to-module.
- A hard rectangular border instead of the soft hand-drawn kawaii frame.
- Fake "characters" that never appear in the book.

---

## References
- `references/kawaii-style.md` — the kawaii visual DNA (read FIRST). Borders, doodles, fonts, mascot, palette, KDP rules.
- `references/aplus-modules.md` — the 5-module layout, per-module copy spec, aplus_content.json shape.

## Scripts
- `scripts/append_aplus.py` — append A+ prompts into `image_prompts.json` (batch/external render flow). Run: `python3 .claude/skills/kdp-aplus-content/scripts/append_aplus.py <theme_key>`
- `scripts/generate_aplus_images.py` — generate A+ images directly with chatgpt renderer, save to `aplus/`. Run: `python3 scripts/generate_aplus_images.py <theme_key> [--renderer chatgpt|ai33|nanopic]`
