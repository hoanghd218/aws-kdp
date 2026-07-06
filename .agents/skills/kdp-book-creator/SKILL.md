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
- Stop only when: (a) Phase 5 delivered, (b) a blocking error you cannot recover from, or (c) Phase 1 / Phase 3 needs user input.

## Pipeline

```
Phase 1: Interview                     (you — pause for user)
Phase 2: Plan Writing                  (you — write prompts + kdp-book-detail skill)
Phase 3: Plan Review                   (you — pause for user)
Phase 4: Images — generate + review    (you — generate_images.py + kdp-image-reviewer criteria + regen loop)
Phase 5: Assembly + Preflight          (you — build_pdf.py + kdp-cover-creator + kdp-cover-checker)
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
  "page_prompts": ["...", "..."]
}
```
Validate it parses as JSON. Also write `output/{theme_key}/prompts.txt` — one prompt per line, in page order.

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

## Phase 5: Assembly + Preflight + Deliver (inline)

### 5.1 Build interior PDF
```bash
python build_pdf.py --theme {theme_key} --title "{title}" --subtitle "{subtitle}" --author "{author_first_name} {author_last_name}"
```
`--author` is required (KDP needs the author on title + copyright pages to match the cover). Verify `output/{theme_key}/interior.pdf` exists, > 1 MB.

### 5.2 Cover via kdp-cover-creator skill
```
Skill: kdp-cover-creator
args:  "--theme {theme_key} --author \"{author_first_name} {author_last_name}\" --size {page_size} --renderer ai33"
```
Verify `cover.png` and `cover.pdf` exist (> 500 KB). For `8.5x8.5`, confirm cover height ≈ 8.75" (not 11.25").

### 5.3 Preflight via kdp-cover-checker skill + manual checks
```
Skill: kdp-cover-checker
args:  "output/{theme_key}/cover.pdf"
```
Then manually verify: metadata consistency (title/author match across title page, copyright, cover, spine); interior even page count + correct page size; spine text only if ≥ 79 pages; barcode area clean; 300 DPI; no banned terms ("spiral bound", "leather bound", "hard bound", "calendar") and no promo claims ("best seller", "#1", "guaranteed", "award-winning") in plan.json.

### 5.4 Fix simple failures yourself
Rerun `build_pdf.py` with corrected flags, rerun cover with correct `--size`, or edit `plan.json` to remove banned terms (then rebuild PDF so the title page matches). Keep fixes conservative — don't hand-edit PDFs. Only escalate if a fix needs user input.

### 5.5 Deliver

```
BOOK COMPLETE!

Interior PDF: output/{theme_key}/interior.pdf
Cover:        output/{theme_key}/cover.pdf   (+ cover.png)
Plan:         output/{theme_key}/plan.json
  - Title:    {title}
  - Keywords: {keywords}

KDP PRE-FLIGHT: {pass/fail summary}
{Unresolved-pages list from Phase 4, if any — label "manual review recommended"}

NEXT STEPS
1. kdp.amazon.com → New Paperback
2. Upload interior.pdf + cover.pdf (not PNG)
3. Trim: {page_size}, No bleed
4. Copy title / description / 7 keywords / 2 categories / reading age from plan.json

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

Don't stop the chain on soft failures — retry inline. Only surface blockers that genuinely need user input.

## Rules

- **Never** call any external LLM API for *writing* prompts or metadata — Claude writes everything.
- Continue in the same turn after each phase. Do not end your turn waiting for a nudge.
- Only 2 user pauses in the whole pipeline: Phase 1 (interview) and Phase 3 (plan review).
- For multiple books, use `kdp-batch-planner` (ideas → plans) then `kdp-batch-assembler` (plans → books).
