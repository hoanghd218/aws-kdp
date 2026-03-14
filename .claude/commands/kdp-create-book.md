---
description: Create a KDP coloring book end-to-end (interview → prompts → images → PDF → cover)
argument-hint: [concept description]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(python:*), Bash(ls:*), Bash(mkdir:*), Skill, Agent, AskUserQuestion
---

# KDP Coloring Book Creator

You are orchestrating the full pipeline to create a KDP-ready coloring book.

## If $ARGUMENTS is provided:
Use it as the book concept. Skip to Phase 2.

## If no arguments:
Start with Phase 1.

---

## Phase 1: Interview

Ask the user these questions (use AskUserQuestion):

1. **Concept**: What's the book about? (e.g., "cozy cats in a café", "cute dinosaurs")
2. **Audience**: Adults (cozy/cute style) or Kids (ages 6-12)?
3. **Pages**: How many coloring pages? (recommend 25-30)
4. **Theme key**: Suggest a snake_case name based on concept (e.g., `cozy_cat_cafe`)
5. **Author name**: For the cover

---

## Phase 2: Plan & Write Prompts

Use the `kdp-prompt-writer` skill to:
- Generate SEO title, subtitle, description, 7 keywords
- Write cover prompt
- Write all page prompts (20-30)
- Save plan JSON to `plans/{theme_key}_plan.json`
- Save prompts to `prompts/{theme_key}.txt`

**IMPORTANT**: Claude writes ALL prompts. Do NOT use Gemini for prompt generation.

Pass the concept, audience, page count, and theme key to the skill.

---

## Phase 3: Review Plan with User

Present the plan summary:
- Title & subtitle
- Description & keywords
- 3-5 sample page prompts

Ask user to approve or request changes.

---

## Phase 4: Generate Images

Use the `kdp-image-generator` skill to:
- Generate all coloring page images from the plan
- Uses Gemini Nano Banana Pro (the ONLY step that calls Gemini API)

```bash
python generate_images.py --plan plans/{theme_key}_plan.json --count {pages}
```

---

## Phase 5: Review Images

Use the `kdp-image-reviewer` skill to:
- Check generated images for quality
- Identify pages needing regeneration
- Regenerate any failed pages

---

## Phase 6: Build Book

Use the `kdp-book-builder` skill to:
- Register theme in config.py (if needed)
- Build KDP-ready PDF interior
- Generate the full cover (front + spine + back)

---

## Phase 7: Deliver

Present final deliverables:
- Interior PDF: `output/books/{theme_key}_coloring_book.pdf`
- Cover: `covers/{theme_key}_cover.png`
- Plan: `plans/{theme_key}_plan.json`

Remind user about KDP upload steps.
