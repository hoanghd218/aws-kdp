---
name: kdp-batch-assembler
description: "Batch-assemble KDP coloring books after planning is done. Scans output/ folders, finds books with plan.json but no interior.pdf, then generates images, reviews, and builds PDF + cover for each — inline, no sub-agents. USE WHEN user says 'batch build', 'batch assemble', 'dong goi sach', 'build all books', 'assemble all books', 'continue batch', 'dong goi tat ca'."
user-invocable: true
---

# KDP Batch Assembler — Finish Every Planned Book (skills only, no agents)

You scan `output/` folders, find books that are planned (have `plan.json`) but not fully assembled (missing `interior.pdf` or `cover.pdf`), then complete each one yourself, one at a time. There are **no sub-agents** — every book is processed inline.

## Step 1: Scan Output Folders

For each `output/*/`:
1. Skip if no `plan.json`.
2. Read `plan.json`: `theme_key`, `title`, `audience`, `page_size`, `page_prompts` count, `author`.
3. Determine status by which files exist:

| Status | Condition |
|--------|-----------|
| **COMPLETE** | `interior.pdf` AND `cover.pdf` both exist (skip) |
| **NEEDS_ASSEMBLY** | Images complete but missing `interior.pdf` or `cover.pdf` |
| **NEEDS_REVIEW** | Image count < expected (partial generation) |
| **NEEDS_IMAGES** | `images/` empty or missing |

Count images: `ls output/{theme_key}/images/page_*.png 2>/dev/null | wc -l`; expected = length of `page_prompts`.

Present incomplete books:
```
| # | Theme Key | Title | Status | Images | Expected | Missing |
|---|-----------|-------|--------|--------|----------|---------|
```

## Step 2: Interview User

Use AskUserQuestion:
1. **Which books to process?** (default: all incomplete)
2. **Skip review?** (default: no — always review)

## Step 3: Process Each Book (inline, sequentially)

For each selected book, run only the phases its status needs:
- **NEEDS_IMAGES**: 3.1 → 3.2 → 3.3 → 3.4
- **NEEDS_REVIEW**: 3.1 (resume missing) → 3.2 → 3.3 → 3.4
- **NEEDS_ASSEMBLY**: 3.3 → 3.4 (skip image gen & review)

### 3.1 Generate images
```bash
python generate_images.py --plan output/{theme_key}/plan.json --count {page_count}
```
Auto-handles page size, parallel workers, retries, and skips existing images. Then verify:
```bash
ls output/{theme_key}/images/page_*.png | wc -l
find output/{theme_key}/images/ -name "page_*.png" -empty
```
Confirm `page_01` … `page_{page_count:02d}` all exist and are non-empty.

### 3.2 Review & auto-regenerate
Read each `page_XX.png` (Read tool, batch ~5). Score PASS / WARN / REDO using the `kdp-image-reviewer` criteria:

**CRITICAL (any ⇒ REDO):** not line art; borders/frames; AI anatomy errors (missing limbs, extra fingers, merged characters); mirror/reflection duplicate; clothing without a person; gibberish text; body horror; ghost/faint duplicate.
**Quality (multiple ⇒ REDO, one minor ⇒ WARN):** lines too thin/broken; too cluttered/sparse; dense micro-patterns (adults); not single-subject-centered (kids); blurry/distorted; subject mismatch.

For each REDO page XX: `rm output/{theme_key}/images/page_XX.png`, then `python generate_images.py --plan output/{theme_key}/plan.json --start {XX-1} --count 1`, re-review. Max 2 regen attempts/page; if still bad, mark WARN and move on.

### 3.3 Build PDF + cover
```bash
python build_pdf.py --theme {theme_key} --author "{author_first_name} {author_last_name}"
```
Verify `interior.pdf` exists (> 1 MB). Then the cover:
```
Skill: kdp-cover-creator
args:  "--theme {theme_key} --author \"{author_first_name} {author_last_name}\" --size {page_size} --renderer ai33"
```
Verify `cover.png` and `cover.pdf` exist (> 500 KB). (No `config.py` edits — `THEMES` auto-discovers `plan.json`.)

### 3.4 KDP pre-flight
Run `kdp-cover-checker` on `output/{theme_key}/cover.pdf`, then verify: metadata consistency (title/author across title page, copyright, cover); copyright year 2026; interior even page count + correct page size; spine text only if ≥ 79 pages; barcode area clean; no banned terms / promo claims in plan.json. Fix simple issues yourself (rerun with corrected flags); escalate only if a fix needs user input.

## Step 4: Summary Report

```
BATCH ASSEMBLY COMPLETE!

| # | Theme Key | Title | Status | Interior PDF | Cover PDF |
|---|-----------|-------|--------|-------------|-----------|

Summary: X of Y books assembled successfully
Failed: <reasons>

NEXT STEPS:
1. Review any FAILED books manually
2. Upload completed books to kdp.amazon.com
3. KDP limits 10 titles per format per week
```

## Error Handling

| Error | Action |
|-------|--------|
| One book fails | Report it, continue with the others |
| plan.json missing required fields | Skip book, report to user |
| Image generation fails repeatedly | After retries per page, skip that page and report |
| PDF build fails | Check images exist + plan.json valid, report error |
| Cover fails | Check renderer keys in `.env`, retry once, report |

## Rules

- Process books inline, one at a time, end to end — no sub-agents.
- Always verify plan.json has required fields before assembling.
- If a book fails, do NOT mark it complete.
- NEVER skip image review unless the user explicitly requests it.
- Always run the KDP pre-flight check.
