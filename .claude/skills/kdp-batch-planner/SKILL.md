---
name: kdp-batch-planner
description: "Batch-plan KDP coloring books from the ideas folder. Scans ideas/*.md and writes one complete plan (page prompts + cover prompt + SEO metadata) per idea — inline, no sub-agents. USE WHEN user says 'plan all ideas', 'batch plan', 'create plans from ideas', 'plan ideas folder', 'lap ke hoach sach', 'plan tat ca'."
user-invocable: true
---

# KDP Batch Planner — One Plan Per Idea (skills only, no agents)

You scan the `ideas/` folder and write a complete plan for each idea yourself, one after another. No image generation, no PDF — planning only. There are **no sub-agents**; you do every plan inline.

## Step 1: Scan Ideas Folder

Read all `ideas/*.md` files (skip `ideas/done/`). For each file, extract from frontmatter: `topic`, `audience`, `style`, `season`, `score`. From the body, extract `Page count` (Suggested Approach) and `Key themes`. List all found ideas with their scores.

## Step 2: Interview User

Use AskUserQuestion to gather shared settings:

1. **Which ideas to process?** Show the list (default: all)
2. **Author name**: First + Last for all books
3. **Book size**: 8.5x11 (portrait, default) or 8.5x8.5 (square) — or per-idea
4. **Default page count**: Use each idea's suggested count, or override all?

## Step 3: Write Each Plan (inline, sequentially)

For EACH selected idea, do the following yourself (Claude writes all prompts — never call an external AI API for prompts):

### 3.1 Derive theme_key
Strip ONLY the leading number prefix and its underscore from the filename, e.g. `19_lavender_dreams` → `lavender_dreams`, `05_4th_july_patriotic` → `4th_july_patriotic`. Create `output/{theme_key}/`.

### 3.2 Write cover prompt + page prompts
Read the prompt guide for reference:
- Adults: `.claude/skills/kdp-prompt-writer/references/adult-prompt-guide.md`
- Kids: `.claude/skills/kdp-prompt-writer/references/kids-prompt-guide.md`

Cover prompt: full-color, matching style/aesthetic, DO NOT bake text into the image.

SIZE_TAG: `"SQUARE format (1:1 aspect ratio)"` for 8.5x8.5, `"PORTRAIT orientation (3:4 aspect ratio)"` for 8.5x11.

**Adults** — start each prompt with:
```
Black and white line art illustration for an adult coloring book, {style} aesthetic, medium detail, bold clean outlines, large open shapes for easy coloring, no shading. NO borders, NO frames, NO rectangular boundary lines around the image. White background. {SIZE_TAG}.
```
Structure each with Scene / Foreground / Midground / Background. End with:
```
Clean bold outlines, {style} environment, easy-to-color shapes, adult coloring book page. NO borders or frames.
```
Large stylized shapes, NO dense micro-patterns. Minimize characters; if 2+, append: `IMPORTANT: Each character must have clearly defined, complete body with no overlapping or merged body parts`. Prefer pet companions over a second human.

**Kids** — bold thick clean outlines (ages 6–12), single centered subject filling most of the page, NO shading/gradients/borders/frames, simple for crayons/markers. Include SIZE_TAG.

Ensure variety (settings, activities, moods, poses); use "Key themes" for scene inspiration.

### 3.3 Write draft plan.json
Save `output/{theme_key}/plan.json` with `theme_key`, `concept` (=topic), `audience`, `page_size`, `cover_prompt`, `back_cover_prompt`, `page_prompts`, and `author`. Leave `title`/`subtitle`/`description`/`keywords` empty for now. Also write `output/{theme_key}/prompts.txt` (one prompt per line).

Write `cover_prompt` + `back_cover_prompt` in the "ads-marketing" format used by `kdp-chatgpt-cover-creator`: front bakes all text into the art (title/subtitle/taglines/author, panel shape from `page_size`); back is a 2×3 grid of six preview cards — **top row 3 fully colored, bottom row 3 line art, cards matching the book shape (square cards for a square 8.5×8.5 book)** — no barcode box. (See the kdp-prompt-writer Step 6 notes.)

### 3.4 SEO metadata via kdp-book-detail skill
```
Skill: kdp-book-detail
args:  "Plan: output/{theme_key}/plan.json, Author: {author_first_name} {author_last_name}, Audience: {audience}"
```
Then update plan.json with `title`, `subtitle`, `description`, `keywords` (7), `categories`, `reading_age`. If the skill fails twice, write the metadata yourself.

### 3.5 Verify
Re-read plan.json: title/subtitle not empty, keywords has 7, page_prompts has the right count, cover_prompt and back_cover_prompt not empty, author present, valid JSON. Confirm `output/{theme_key}/bookinfo.md` exists (created by kdp-book-detail). Do NOT move the idea file yet.

## Step 4: Review All Plans with User

Present a summary table:
```
| # | Theme Key | Title | Audience | Pages | Status |
|---|-----------|-------|----------|-------|--------|
```
For each plan show Title & Subtitle, 7 Keywords, 2 sample page prompts. Ask: "Approve all plans? Or which need changes?" If changes, edit the specific plan.json directly.

After approval, for each approved plan move its idea file to done:
```bash
mv ideas/{idea_filename} ideas/done/{idea_filename}
```
Do NOT move rejected ideas. (No `config.py` edits needed — `THEMES` auto-discovers `output/{theme_key}/plan.json`.)

## Error Handling

| Error | Action |
|-------|--------|
| One idea fails to plan | Report it, continue with the others |
| Idea file missing fields | Use sensible defaults (30 pages, 8.5x11, adults) |
| kdp-book-detail fails | Retry once, then leave metadata empty and flag to user |

## Rules

- NEVER use Gemini/AI API for writing prompts — Claude writes ALL prompts.
- Process ideas inline, one at a time, end to end — no sub-agents.
- Move processed ideas to `ideas/done/` only after the user approves their plan.
