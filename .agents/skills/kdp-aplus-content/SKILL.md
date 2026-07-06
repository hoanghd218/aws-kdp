---
name: kdp-aplus-content
description: Generate Amazon KDP A+ Content ("From the Publisher") modules tailored to a coloring book's theme. Produces aplus_content.json (module copy + 970x600 image prompts) and appends the A+ image prompts into the book's image_prompts.json. USE WHEN user says 'tao content A+', 'create A+ content', 'kdp a plus', 'from the publisher', 'a+ modules', 'lam content a+', 'enhanced brand content', 'tao a+ cho sach', 'add a+ content', 'make a+ for book'.
---

# KDP A+ Content Generator

Turn a finished (or planned) coloring book into a 7-module **A+ Content** set — the "From the Publisher" image strip that sells the book below the description. Each module is ONE image; the marketing copy is baked INTO that image at layout time.

This skill writes the **theme-aware copy + image prompts**; a script does the mechanical append into the book's image-generation queue.

---

## Inputs

Works off an existing book under `output/{theme_key}/`:
- `plan.json` — title, subtitle, audience, page_size, brand/author, keywords, page_prompts (required)
- `image_prompts.json` — the cover + page render queue (optional; created if missing)

If the user names a book ("A+ for cozy_cottage") use that theme_key. If they don't, list `output/*/plan.json` and ask which book.

---

## Process

### Step 1 — Read the book
Load `output/{theme_key}/plan.json`. Pull: `title`, `subtitle`, `audience`, `page_size`, `brand`/`author`, `keywords`, and skim `page_prompts` to learn the actual scene mix (e.g. cottages / gardens / critters). The A+ copy MUST reference what's really inside — never generic filler.

### Step 2 — Write the 7 modules
Open `references/aplus-modules.md` for the canonical pattern, KDP specs, and copywriting rules. Write `output/{theme_key}/aplus_content.json` with all 7 modules. For each module fill:
- `copy` — the exact text that goes in the image (headline, bullets, captions). Match the book's tone (cozy = warm & gentle; kids = playful; anime = bold/energetic).
- `image_prompt` — a **self-contained** prompt the renderer can draw directly, in the book's palette, with clear empty space reserved for the copy. Mark which modules look best with **real page composites**.

Use the book's real numbers (page count, trim size) and its top keywords woven naturally into headlines/bullets.

### Step 3 — Append to the render queue
Run the script to push the 7 A+ image prompts into `image_prompts.json` at **970x600**:

```bash
python3 .claude/skills/kdp-aplus-content/scripts/append_aplus.py <theme_key>
```

It is idempotent (strips any prior `aplus_*` items first) and creates `image_prompts.json` if absent. It prints the final queue summary.

### Step 4 — Report
Tell the user: the 7 modules created, which 3 need real-page composites (`inside_grid`, `single_sided`, `before_after`), and that `size` is `970x600` (use `16:10` if their renderer only takes ratios). Point them to `aplus_content.json` for the copy to type during layout.

---

## Output

**Type:** book asset
**Location:** `output/{theme_key}/`
**Files produced / updated:**
- `aplus_content.json` — 7 modules, copy + image prompts (NEW)
- `image_prompts.json` — A+ prompts appended at 970x600 (UPDATED)

---

## Quality Criteria

GOOD A+ content:
- Copy names what's ACTUALLY in this book (real scenes, real page count, real trim size)
- Mostly imagery; text is short, large, scannable — one headline + ≤3 bullets per module
- Consistent palette pulled from the book's own cover/theme
- Reserves clear empty space in each prompt for the copy overlay
- Flags the 3 composite-with-real-pages modules instead of letting AI fake book pages
- 970px wide, 300 DPI, ≤5 MB per module (KDP hard limits)

BAD A+ content:
- Generic "relax and unwind" copy that fits any book
- Walls of text baked into the image
- Mismatched colors module-to-module
- Inventing features the book doesn't have

---

## References

- `references/aplus-modules.md` — the 7-module pattern, KDP A+ specs, copywriting rules

## Scripts

- `scripts/append_aplus.py` — append A+ prompts into `image_prompts.json`. Run: `python3 .claude/skills/kdp-aplus-content/scripts/append_aplus.py <theme_key>`
