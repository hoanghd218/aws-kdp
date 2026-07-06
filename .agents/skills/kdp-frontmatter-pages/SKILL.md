---
name: kdp-frontmatter-pages
description: Replace a KDP coloring book's plain text title / copyright / thank-you pages with illustrated front and back matter, add an optional "This Book Belongs To" page, auto-generate the page images with the configured IMAGE_RENDERER, and merge them into interior.pdf. USE WHEN user says 'tao trang bia trong sach', 'frontmatter pages', 'thay trang thank you', 'title page dep', 'this book belongs to page', 'trang dau cuoi sach', 'decorative interior pages', 'lam trang title va thank you', 'ghep frontmatter', 'illustrated title page', 'personalize thank you page', 'generate frontmatter images', 'tu tao anh frontmatter', 'tao anh trang dau cuoi'.
---

# KDP Frontmatter Pages

Turn the ugly plain-text title / copyright / thank-you pages into themed
illustrations that match the book's interior, and optionally add a cute
"This Book Belongs To" page. Default flow:
**Codex writes the prompts → Codex generates the PNGs with the configured image
renderer → Codex merges them into `interior.pdf` → Codex runs QC.**

Fall back to human-in-the-loop only when image generation is unavailable
(missing `.env` keys, quota/provider failure) or generated text is visibly wrong.

---

## Phase Routing

| Phase | Trigger | What Codex does |
|-------|---------|------------------|
| **1 — Prompts** | "generate frontmatter prompts", "lam prompt trang title/thank you", book has no `frontmatter/*.txt` yet | Read `plan.json`, write personalized prompts to `output/<theme>/frontmatter/1.txt`,`2.txt`,`3.txt` |
| **2 — Generate images** | "generate frontmatter images", "tu tao anh frontmatter", prompts exist but PNGs are missing | Run the image generation script to create `1.png`, optional `2.png`, and `3.png` |
| **3 — Merge** | "ghep lai", "ghep frontmatter vao", `frontmatter/1.png` & `3.png` now exist | Inspect images, run the assembly script, run QC |

Always confirm the **theme_key** (folder under `output/`). If unclear, list
`output/*/plan.json` and ask which book.

---

## Phase 1 — Write the prompts

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
   - **Belongs To (2)**: only for kids books; skip for pure adult books.
   - **Thank You (3)**: warm, theme-specific message + an Amazon-review CTA.
4. Write prompts to `output/<theme>/frontmatter/{1,2,3}.txt` (create the
   folder). For adult books, skip `2.txt` unless the user explicitly wants an
   ownership/dedication page.

**Style is non-negotiable:** square for 8.5x8.5 / portrait 3:4 for 8.5x11;
grayscale (black line + soft gray) on white; text baked in with EXACT wording;
no full-page border/frame. See `references/prompt-templates.md`.

---

## Phase 2 — Generate frontmatter images

Run from the repo root:

```bash
python3 .agents/skills/kdp-frontmatter-pages/scripts/generate_frontmatter_images.py <theme_key>
```

Useful flags:

```bash
python3 .agents/skills/kdp-frontmatter-pages/scripts/generate_frontmatter_images.py <theme_key> --pages 1,3
python3 .agents/skills/kdp-frontmatter-pages/scripts/generate_frontmatter_images.py <theme_key> --renderer nanopic
python3 .agents/skills/kdp-frontmatter-pages/scripts/generate_frontmatter_images.py <theme_key> --overwrite
```

The script reads `IMAGE_RENDERER` from `.env` (same provider stack as
`scripts/generate_images.py`), loads `frontmatter/*.txt`, generates PNGs into
the same folder, converts to grayscale, fits to the book trim size, and saves at
300 DPI.

If the provider fails or credentials are missing, keep the `.txt` files and tell
the user to generate/save:

- `1.png` = Title
- `2.png` = This Book Belongs To, optional
- `3.png` = Thank You

## Phase 3 — Merge into the interior

1. **Inspect** `frontmatter/1.png` (and `2.png`, `3.png`) with the Read tool.
   Check: text spelled correctly, grayscale, square/portrait matches trim, art
   not touching edges. If small print is garbled, ask the user to regenerate
   that page (the script's plain copyright page still carries the legal text, so
   minor garbling on title/thank-you art is only cosmetic).
2. **Run the assembly script** (it backs up the old PDF, upscales the art to
   300 DPI, keeps coloring pages on right-hand pages with blank backs, forces an
   even page count):
   ```bash
   python3 .agents/skills/kdp-frontmatter-pages/scripts/assemble_frontmatter.py <theme_key>
   ```
   Useful flags: `--size 8.5x11|8.5x8.5`, `--author "Name"`, `--age 3-7`,
   `--no-copyright`.
3. **QC** the result:
   ```bash
   python3 scripts/pdf_qc.py --pdf output/<theme>/interior.pdf --trim <size> --require-even-pages
   ```
4. **Visually verify** by rendering a few pages (title, copyright, belongs-to,
   first coloring page, last/thank-you) and Reading them. Report GO/NO-GO.

---

## Page order produced

`Title(1.png)` → `Copyright(text)` → `This Book Belongs To(2.png, if present)` →
(blank pad if needed) → coloring pages (right-hand, blank backs) →
`Thank You(3.png)` as the even last page.

---

## Image conventions

| File | Page | Required |
|------|------|----------|
| `frontmatter/1.png` | Title | ✅ |
| `frontmatter/2.png` | This Book Belongs To | optional (omit → page skipped) |
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

- `scripts/generate_frontmatter_images.py` — generate `frontmatter/*.png` from
  the prompt text files using the configured image renderer.
- `scripts/assemble_frontmatter.py` — merge frontmatter images + coloring pages
  into `interior.pdf`. Reads trim/author/age from `plan.json`. Run from repo root.

## References

- `references/prompt-templates.md` — the 3 prompt blueprints + style rules
  (load during Phase 1).
