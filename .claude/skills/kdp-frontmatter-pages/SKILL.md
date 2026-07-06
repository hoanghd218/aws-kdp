---
name: kdp-frontmatter-pages
description: Replace a KDP coloring book's plain text title / copyright / thank-you pages with illustrated front & back matter (and add a "This Book Belongs To" page). Write personalized image prompts, generate the art with the built-in ChatGPT image_gen tool, then merge into interior.pdf. USE WHEN user says 'tao trang bia trong sach', 'frontmatter pages', 'thay trang thank you', 'title page dep', 'this book belongs to page', 'trang dau cuoi sach', 'decorative interior pages', 'lam trang title va thank you', 'ghep frontmatter', 'illustrated title page', 'personalize thank you page'.
---

# KDP Frontmatter Pages

Turn the ugly plain-text title / copyright / thank-you pages into themed
illustrations that match the book's interior. Always includes a
"This Book Belongs To" page for ALL books (adults and kids alike). Fully automated flow:
**Claude writes the prompts → Claude generates the art with the built-in
ChatGPT `image_gen` tool → Claude merges them into `interior.pdf`.**

> Image generation uses the same built-in `image_gen` tool as the
> `kdp-chatgpt-cover-creator` skill — no external renderer, no manual hand-off.
> (If `image_gen` is unavailable in the current runtime, fall back to writing
> the `.txt` prompts and asking the user to generate `1.png`/`2.png`/`3.png`
> by hand, then resume at Phase 2.)

---

## Phase Routing

| Phase | Trigger | What Claude does |
|-------|---------|------------------|
| **1 — Prompts + Generate** | "generate frontmatter", "lam trang title/thank you", book has no `frontmatter/*.png` yet | Read `plan.json`, write 3 personalized prompts to `output/<theme>/frontmatter/{1,2,3}.txt`, then call the built-in `image_gen` tool to produce `1.png`/`2.png`/`3.png` |
| **2 — Merge** | "ghep lai", "ghep frontmatter vao", `frontmatter/1.png` & `3.png` already exist | Inspect images, run the assembly script, run QC |

Phase 1 normally flows straight into Phase 2 in a single run — generate, then
merge. Stop between phases only if `image_gen` is unavailable (hand-off mode).

Always confirm the **theme_key** (folder under `output/`). If unclear, list
`output/*/plan.json` and ask which book.

---

## Phase 1 — Write the prompts and generate the art

1. Read `output/<theme>/plan.json`. Note: `audience`, `page_size`, `author`,
   `title`, and skim several `page_prompts` + the `cover_prompt` to capture the
   **exact visual style** and any **recurring mascots/objects** (e.g. a kawaii
   teddy bear, balloons, a smiling cake).
2. Load `references/prompt-templates.md` and fill the bracketed slots so the 3
   pages clearly belong to THIS book — same style, same characters, real objects
   from the book mentioned in the thank-you message.
3. Personalize the copy:
   - **Title (1)**: short punchy hero title (not the full 60-char KDP title) +
     genre sub-banner + 3-line subtitle + copyright line.
   - **Belongs To (2)**: ALWAYS generate for every book — adults and kids alike.
     For adults adapt the wording (e.g. "This Book Belongs To" + name line, no
     age field); for kids include the "AGE: ____" line.
   - **Thank You (3)**: warm, theme-specific message + an Amazon-review CTA.
4. Write the three prompts to `output/<theme>/frontmatter/{1,2,3}.txt`
   (create the folder) as a record of what was generated.
5. **Generate the images with the built-in `image_gen` tool** — one call per
   prompt. This is the same ChatGPT image-generation path the
   `kdp-chatgpt-cover-creator` skill uses; do **not** ask the user to make the
   art by hand and do **not** route through `image_providers.py`.
   - Request **square** output for `8.5x8.5` books, **portrait 3:4** for
     `8.5x11` (match `plan.json.page_size`).
   - Spell every word of the baked-in text EXACTLY (title, subtitle, author such
     as `BoBoArt`, thank-you copy) — misspellings are the top reject reason.
   - Save the chosen renders into the book folder:
     - `output/<theme>/frontmatter/1.png` — Title
     - `output/<theme>/frontmatter/2.png` — This Book Belongs To (**always required**)
     - `output/<theme>/frontmatter/3.png` — Thank You
   - If a render comes back garbled or off-style, re-call `image_gen` for just
     that page before moving on.
6. Proceed directly to **Phase 2 — Merge** (no user hand-off needed). Only stop
   and ask the user to generate the PNGs manually if `image_gen` is unavailable
   in this runtime.

**Style is non-negotiable:** square for 8.5x8.5 / portrait 3:4 for 8.5x11;
grayscale (black line + soft gray) on white; text baked in with EXACT wording;
no full-page border/frame. See `references/prompt-templates.md`.

---

## Phase 2 — Merge into the interior

1. **Inspect** `frontmatter/1.png` (and `2.png`, `3.png`) with the Read tool.
   Check: text spelled correctly, grayscale, square/portrait matches trim, art
   not touching edges. If small print is garbled, re-call `image_gen` for that
   page (or, in hand-off mode, ask the user to regenerate it). The script's plain
   copyright page still carries the legal text, so minor garbling on the
   title/thank-you art is only cosmetic.
2. **Run the assembly script** (it backs up the old PDF, upscales the art to
   300 DPI, keeps coloring pages on right-hand pages with blank backs, forces an
   even page count):
   ```bash
   python .claude/skills/kdp-frontmatter-pages/scripts/assemble_frontmatter.py <theme_key>
   ```
   Useful flags: `--size 8.5x11|8.5x8.5`, `--author "Name"`, `--age 3-7`,
   `--no-copyright`.
3. **QC** the result:
   ```bash
   python scripts/pdf_qc.py --pdf output/<theme>/interior.pdf --trim <size> --require-even-pages
   ```
4. **Visually verify** by rendering a few pages (title, copyright, belongs-to,
   first coloring page, last/thank-you) and Reading them. Report GO/NO-GO.

---

## Page order produced

`Title(1.png)` → `Copyright(text)` → `This Book Belongs To(2.png)` →
(blank pad if needed) → coloring pages (right-hand, blank backs) →
`Thank You(3.png)` as the even last page.

---

## Image conventions

| File | Page | Required |
|------|------|----------|
| `frontmatter/1.png` | Title | ✅ |
| `frontmatter/2.png` | This Book Belongs To | ✅ (always — adults + kids) |
| `frontmatter/3.png` | Thank You | ✅ |

Generate at ≥2550px square (or 2550×3300 portrait). The script grayscales +
upscales to the trim's pixel target so print is ≥300 DPI.

---

## Quality criteria (GO checklist)

- [ ] All text spelled correctly and matches book metadata/author
- [ ] Style + recurring characters match the interior pages
- [ ] Grayscale only, white background, no full-page frame
- [ ] Correct orientation for the trim (square vs portrait)
- [ ] `pdf_qc.py` verdict = GO (even pages, trim match)
- [ ] Old interior backed up as `interior_backup_*.pdf`

---

## Scripts

- `scripts/assemble_frontmatter.py` — merge frontmatter images + coloring pages
  into `interior.pdf`. Reads trim/author/age from `plan.json`. Run from repo root.

## References

- `references/prompt-templates.md` — the 3 prompt blueprints + style rules
  (load during Phase 1).
