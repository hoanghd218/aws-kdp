---
name: kdp-book-creator
description: Create a KDP coloring book end-to-end (planning, image generation & review, and book assembly) running every step inline — no sub-agents. USE WHEN the user says 'tao sach', 'create coloring book', 'kdp create book', 'build coloring book end to end', 'make a coloring book', 'tao sach to mau', or otherwise asks to produce a complete KDP coloring book from a concept. Trigger even when the user only gives a concept (e.g. "a book about cozy cats") without explicitly naming the pipeline.
user-invocable: true
---

# KDP Book Creator — End-to-End Pipeline (skills only, no agents)

You run the entire pipeline yourself, in one continuous flow. There are **no sub-agents** — every phase is done inline by you, calling other skills where noted. Claude writes ALL prompts and metadata; never call any external LLM API for *writing*.

## Execution Protocol — READ FIRST

- Run ALL phases **in sequence without stopping**, except Phase 1 (interview) and Phase 3 (plan review), which require user input.
- Do **NOT** ask for confirmation between phases. The user invoked the skill — that is the green light.
- After finishing a phase, **immediately proceed to the next phase in the same turn**. No "ready to continue?", no summary-and-stop.
- Between phases, emit ONE short progress sentence (e.g. "Plan done, generating images now"), then continue.
- Stop only when: (a) Phase 8 / Deliver is done, (b) a blocking error you cannot recover from, or (c) Phase 1 / Phase 3 needs user input.

## Pipeline

```
Phase 1: Interview                     (you — pause for user)
Phase 2: Plan Writing                  (you — write prompts + kdp-book-detail skill)
Phase 3: Plan Review                   (you — pause for user)
Phase 4: Images — generate + review    (you — generate_images.py + kdp-image-reviewer criteria + regen loop)
Phase 5: Interior PDF                  (you — build_pdf.py basic interior)
Phase 6: Frontmatter Pages             (you — kdp-frontmatter-pages skill → illustrated pages → rebuilt interior.pdf)
Phase 7: Cover + Preflight             (you — kdp-cover-creator + kdp-cover-checker)
Phase 8: A+ Content                    (you — kdp-aplus-content skill → aplus_content.json + aplus/*.png)
   + Deliver                           (you — present to user)
```

Note: `config.THEMES` auto-discovers any `output/{theme_key}/plan.json` — you do **not** register themes in `config.py` anywhere.

---

## Phase 1: Interview (pause for user)

Use **AskUserQuestion** to collect:

1. **Concept** — e.g. "cozy cats in a cafe". Skip if passed as invocation args.
2. **Audience** — Adults (cozy/cute) or Kids (6–12).
3. **Book size** — 8.5x11 (portrait, default) or 8.5x8.5 (square).
4. **Page count** — recommend 25–30.
5. **Theme key** — snake_case slug; suggest one based on concept.
6. **Author** — first name + last name.

**→ Once answered, IMMEDIATELY proceed to Phase 2. Do not re-confirm the answers.**

---

## Phase 2: Plan Writing

Write the complete plan yourself in one pass — page prompts + cover prompt + SEO metadata.

### 2.1 Read the prompt guide

- Adults → `.claude/skills/kdp-prompt-writer/references/adult-prompt-guide.md`
- Kids   → `.claude/skills/kdp-prompt-writer/references/kids-prompt-guide.md`

### 2.2 Write the cover prompt

Full-color artwork matching the concept. **Never** bake text into the image — title/subtitle are overlaid later by the cover generator.

### 2.3 Write page prompts

SIZE_TAG:
- `8.5x8.5` → `"SQUARE format (1:1 aspect ratio)"`
- `8.5x11`  → `"PORTRAIT orientation (3:4 aspect ratio)"`

**Adults** — every prompt starts with:
```
Black and white line art illustration for an adult coloring book, cute cozy cottagecore aesthetic, medium detail, bold clean outlines, large open shapes for easy coloring, no shading. NO borders, NO frames, NO rectangular boundary lines around the image. White background. {SIZE_TAG}.
```
Structure: Scene / Foreground / Midground / Background. End each prompt with:
```
Clean bold outlines, cozy relaxing cottagecore environment, easy-to-color shapes, adult coloring book page. NO borders or frames.
```
Large stylized shapes only. NO dense micro-patterns. Minimize characters per scene. If 2+ characters, append:
```
IMPORTANT: Each character must have clearly defined, complete body with no overlapping or merged body parts
```
Prefer pet companions over a second human character.

**Kids** — bold thick clean outlines, single centered subject filling most of the page, NO shading/gradients/borders/frames, simple enough for crayons and markers. SIZE_TAG must be included.

**All audiences:** ensure variety across settings, activities, moods, and poses. Do not repeat the same scene twice.

### 2.4 SEO metadata via kdp-book-detail skill

Invoke:
```
Skill: kdp-book-detail
args:  "Concept: {concept}, Audience: {audience}, Author: {author_first_name} {author_last_name}, Page count: {page_count}, Page size: {page_size}"
```
Collect: Title, Subtitle, Description (HTML), 7 Backend Keywords, 2 BISAC Categories, Reading Age. If the skill fails twice, write the metadata yourself following best-seller Amazon patterns.

### 2.5 Write `output/{theme_key}/plan.json` (fully filled — no empty strings)

```json
{
  "theme_key": "{theme_key}",
  "concept": "{concept}",
  "audience": "{audience}",
  "page_size": "{page_size}",
  "title": "...",
  "subtitle": "...",
  "description": "...",
  "keywords": ["...", "..."],
  "categories": ["...", "..."],
  "reading_age": "...",
  "author": { "first_name": "{author_first_name}", "last_name": "{author_last_name}" },
  "cover_prompt": "...",
  "back_cover_prompt": "...",
  "page_prompts": ["...", "..."]
}
```
Validate it parses as JSON. Also write `output/{theme_key}/prompts.txt` — one prompt per line, in page order.

**`cover_prompt` + `back_cover_prompt`** feed the cover skill — write both in the detailed "ads-marketing" format:
- **`cover_prompt` (front):** `Use case: ads-marketing.` Bake **all** text into the art — title, subtitle, two short taglines, author spelled letter-by-letter. State panel shape from `page_size` (square 1:1 for 8.5×8.5, portrait 3:4 for 8.5×11). All text inside safe margins; no barcode/watermark/mockup.
- **`back_cover_prompt` (back):** `Use case: ads-marketing.` A **2×3 grid of six preview cards — top row 3 fully COLORED, bottom row 3 black-and-white line art**. **Each preview card MUST match the book's page shape — for a square 8.5×8.5 book every card is a SQUARE (1:1) card; for an 8.5×11 book every card is a PORTRAIT (3:4) card.** Say the card shape explicitly in the prompt (e.g. "six equal SQUARE preview cards in a 2×3 grid, each card 1:1") — image models default to tall rectangular cards otherwise. Same size, evenly spaced, surrounded by on-theme decorations. No title/author text, no barcode box, no blank white rectangle (barcode stamped by code).

### 2.6 Write frontmatter prompts + the external render queue (`image_prompts.json`)

So the whole book — cover, the illustrated front/back matter, AND every coloring page — can be generated in one pass in an external tool, write the frontmatter prompts now (not only in Phase 6) and bundle everything into a render queue.

1. **Write the 3 frontmatter prompts** to `output/{theme_key}/frontmatter/{1,2,3}.txt` using the blueprints in `.claude/skills/kdp-frontmatter-pages/references/prompt-templates.md`, personalized to THIS book (same style/characters as the page prompts; adults omit the "AGE:" line). `1.txt` = Title, `2.txt` = This Book Belongs To, `3.txt` = Thank You. Match orientation to `page_size` (SQUARE for 8.5×8.5, PORTRAIT 3:4 for 8.5×11) and spell the author + all baked-in text exactly.
2. **Build the render queue:**
   ```bash
   python scripts/build_image_prompts.py {theme_key}
   ```
   This writes `output/{theme_key}/image_prompts.json` — a flat `[{prompt, size, filename}]` list in book order: `front_artwork.png`, `back_artwork.png`, `frontmatter/1.png` (Title), `frontmatter/2.png` (Belongs-To), `images/page_01.png … page_NN.png`, `frontmatter/3.png` (Thank You). `size` is the aspect ratio (`1:1` for square, `3:4` for portrait). Re-run this script any time `plan.json` or a frontmatter `.txt` changes.

The user can render every item externally and drop the PNGs back at the listed `filename` paths; the pipeline (Phase 4 image gen) is then skippable. If you DO auto-generate via Phase 4 instead, `image_prompts.json` still serves as the canonical prompt manifest.

**→ IMMEDIATELY Read `output/{theme_key}/plan.json` and go to Phase 3.**

---

## Phase 3: Plan Review (pause for user)

Present to the user:
- Title + Subtitle
- Description (HTML, show raw — it's short)
- 7 Keywords, 2 Categories, Reading Age
- 3–5 sample page prompts

Ask: *"Duyệt để tiếp tục generate images, hoặc cần sửa gì?"*

If changes: edit `plan.json` directly with the Edit tool, re-present the delta, loop until approved.

**→ Once approved, IMMEDIATELY proceed to Phase 4.**

---

## Phase 4: Images — generate + review + regen (inline)

### 4.1 Generate
```bash
python generate_images.py --plan output/{theme_key}/plan.json --count {page_count}
```
The script auto-handles page size, parallel workers, and retries. `--start N` skips existing pages, so reruns are resumable.

### 4.2 Verify files
```bash
ls -la output/{theme_key}/images/
```
Confirm every `page_01.png` … `page_{page_count:02d}.png` exists and is non-empty. For gaps, re-run `generate_images.py --start N --count 1` (N = missing page index − 1), up to 2 attempts per page.

### 4.3 Review every image
Open each image with the Read tool (Claude vision). Batch Reads ~5 at a time. Score each page **PASS / WARN / REDO** using the criteria in the `kdp-image-reviewer` skill:

**CRITICAL (any one ⇒ REDO):** not line art (color/photos/heavy shading); borders/frames/rectangular boundary; AI anatomy errors (missing limbs, extra fingers, merged characters); mirror/reflection duplicate; clothing without a person; gibberish text; body horror; ghost/faint duplicate.

**Quality (multiple ⇒ REDO; one minor ⇒ WARN):** lines too thin/broken; too cluttered or too sparse; dense micro-patterns (adults); not single-subject-centered (kids); blurry/distorted; subject doesn't match prompt.

### 4.4 Regenerate REDO pages
For each REDO page XX: `rm output/{theme_key}/images/page_XX.png`, then `python generate_images.py --plan output/{theme_key}/plan.json --start {XX-1} --count 1`, re-review. Retry ONCE more (max 2 regen attempts/page). If still bad, mark **WARN** ("unresolved after 2 regens") and move on.

Keep PASS/WARN/REDO-resolved/REDO-unresolved counts. If > 30% of pages are unresolved REDOs, pause and ask the user: ship as-is, or regenerate the whole set with a stronger prompt?

**→ Otherwise IMMEDIATELY proceed to Phase 5.**

---

## Phase 5: Interior PDF (inline)

### 5.1 Build basic interior PDF
```bash
python build_pdf.py --theme {theme_key} --title "{title}" --subtitle "{subtitle}" --author "{author_first_name} {author_last_name}"
```
`--author` is required (KDP needs the author on title + copyright pages to match the cover). Verify `output/{theme_key}/interior.pdf` exists, > 1 MB.

**→ IMMEDIATELY proceed to Phase 6.**

---

## Phase 6: Frontmatter Pages (inline)

Invoke the `kdp-frontmatter-pages` skill:
```
Skill: kdp-frontmatter-pages
args:  "{theme_key}"
```

The skill reads `plan.json`, writes 3 personalized illustrated page prompts, generates the art with the built-in `image_gen` tool, and runs `assemble_frontmatter.py` to replace the plain title/copyright/thank-you pages — rebuilding `interior.pdf` in-place. Fully automated; no user pause needed.

After the skill completes, verify:
- `output/{theme_key}/frontmatter/1.png` (Title), `2.png` (Belongs To), `3.png` (Thank You) all exist
- `output/{theme_key}/interior.pdf` is updated (mtime newer than Phase 5 build)

If the skill reports that `image_gen` is unavailable: write the 3 prompts yourself from the templates in `kdp-frontmatter-pages/references/prompt-templates.md`, ask the user to generate the PNGs manually, then run `python .claude/skills/kdp-frontmatter-pages/scripts/assemble_frontmatter.py {theme_key}` once the PNGs are in place.

**→ IMMEDIATELY proceed to Phase 7.**

---

## Phase 7: Cover + Preflight (inline)

### 7.1 Cover via kdp-cover-creator skill
```
Skill: kdp-cover-creator
args:  "--theme {theme_key} --author \"{author_first_name} {author_last_name}\" --size {page_size} --renderer ai33"
```
Verify `cover.png` and `cover.pdf` exist (> 500 KB). For `8.5x8.5`, confirm cover height ≈ 8.75" (not 11.25").

### 7.2 Preflight via kdp-cover-checker skill + manual checks
```
Skill: kdp-cover-checker
args:  "output/{theme_key}/cover.pdf"
```
Then manually verify: metadata consistency (title/author match across title page, copyright, cover, spine); interior even page count + correct page size; spine text only if ≥ 79 pages; barcode area clean; 300 DPI; no banned terms ("spiral bound", "leather bound", "hard bound", "calendar") and no promo claims ("best seller", "#1", "guaranteed", "award-winning") in plan.json.

### 7.3 Fix simple failures yourself
Rerun `build_pdf.py` with corrected flags, rerun cover with correct `--size`, or edit `plan.json` to remove banned terms (then rebuild PDF so the title page matches). Keep fixes conservative — don't hand-edit PDFs. Only escalate if a fix needs user input.

**→ IMMEDIATELY proceed to Phase 8.**

---

## Phase 8: A+ Content (inline)

Invoke the `kdp-aplus-content` skill:
```
Skill: kdp-aplus-content
args:  "{theme_key}"
```

The skill reads `plan.json` + `page_prompts`, writes `aplus_content.json` (5 kawaii modules: hero, specs, features/friends, two sample showcases), then generates the 5 images with the chatgpt renderer to `output/{theme_key}/aplus/aplus_<id>.png`.

After the skill completes, verify:
- `output/{theme_key}/aplus_content.json` exists
- `output/{theme_key}/aplus/` contains 5 PNG files (`aplus_01_hero.png` … `aplus_05_sample_showcase_b.png`)

If the renderer fails: the skill will write `aplus_content.json` with the prompts — inform the user the images need manual generation and point them to the prompts file.

**→ IMMEDIATELY proceed to Deliver.**

---

## Deliver

```
BOOK COMPLETE!

Interior PDF:   output/{theme_key}/interior.pdf
Cover:          output/{theme_key}/cover.pdf   (+ cover.png)
Frontmatter:    output/{theme_key}/frontmatter/   (1.png Title / 2.png Belongs-To / 3.png Thank-You)
A+ Content:     output/{theme_key}/aplus/         (5 kawaii modules)
                output/{theme_key}/aplus_content.json  (copy text for KDP A+ layout)
Plan:           output/{theme_key}/plan.json
  - Title:    {title}
  - Keywords: {keywords}

KDP PRE-FLIGHT: {pass/fail summary}
{Unresolved-pages list from Phase 4, if any — label "manual review recommended"}

NEXT STEPS
1. kdp.amazon.com → New Paperback
2. Upload interior.pdf + cover.pdf (not PNG)
3. Trim: {page_size}, No bleed
4. Copy title / description / 7 keywords / 2 categories / reading age from plan.json
5. KDP A+ Content → upload 5 images from aplus/ and copy text from aplus_content.json

NOTE: KDP limits 10 titles / format / week.
```

---

## Error Handling

| Failure | Recovery |
|---|---|
| kdp-book-detail fails | Write the metadata yourself, continue. |
| Image generation API fails | Retry once. If > 30% unresolved, pause and ask user. |
| build_pdf.py fails | Check images exist + plan.json valid; fix and retry. |
| Cover fails | Check renderer key in `.env`; retry once. |
| kdp-frontmatter-pages: image_gen unavailable | Write prompts to frontmatter/*.txt, ask user to generate PNGs, then run assemble_frontmatter.py. |
| kdp-aplus-content: renderer fails | aplus_content.json is still written; inform user images need manual render. |

Don't stop the chain on soft failures — retry inline. Only surface blockers that genuinely need user input.

## Rules

- **Never** call any external LLM API for *writing* prompts or metadata — Claude writes everything.
- Continue in the same turn after each phase. Do not end your turn waiting for a nudge.
- Only 2 user pauses in the whole pipeline: Phase 1 (interview) and Phase 3 (plan review).
- For multiple books, use `kdp-batch-planner` (ideas → plans) then `kdp-batch-assembler` (plans → books).
