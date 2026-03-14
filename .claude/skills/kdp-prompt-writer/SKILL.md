---
name: kdp-prompt-writer
description: Analyze concepts and write SEO-optimized prompts for KDP coloring books. Claude writes ALL prompts — no AI generation. USE WHEN user says 'write coloring book prompts', 'create book plan', 'plan coloring book', 'write page prompts', 'kdp prompts', 'coloring book plan', 'write book metadata', 'create kdp plan'.
---

# KDP Prompt Writer

Claude analyzes the book concept and writes everything: SEO metadata, cover prompt, and all interior page prompts. NO AI/Gemini is used for this step — Claude is the expert prompt writer.

---

## When to Use

- User wants to plan a new coloring book
- The `/project:kdp-create-book` command reaches the planning phase
- User wants to write or rewrite prompts for an existing theme

---

## Process

### Step 1: Determine Audience & Load Guidelines

Read the appropriate reference guide:
- **Adults**: Read `references/adult-prompt-guide.md` in this skill directory
- **Kids**: Read `references/kids-prompt-guide.md` in this skill directory

### Step 2: Write SEO Metadata

Generate based on the concept:

**Title** — Catchy, keyword-rich, includes audience indicator
- Adults: e.g., "Whiskers & Warmth: A Cozy Cat Café Coloring Book for Adults"
- Kids: e.g., "Amazing Dinosaurs Coloring Book for Kids Ages 6-12"

**Subtitle** — Descriptive, complementary
- Adults: e.g., "Relaxing Kawaii Scenes with Cute Cats, Warm Drinks & Cozy Interiors"
- Kids: e.g., "Bold & Easy Designs for Creative Kids"

**Description** — 3-5 sentences for Amazon KDP listing. Emphasize:
- Adults: cozy charm, relaxation, stress relief, beautiful scenes
- Kids: fun, creativity, learning, hours of entertainment

**Keywords** — 7 SEO-relevant keywords for Amazon search

### Step 3: Write Cover Prompt

**Adults cover prompt must include:**
- Full-color illustration (NOT black-and-white)
- Warm, premium cozy aesthetic
- Multiple large readable props and decorative elements
- Title and subtitle text reference
- State "Coloring Book for Adults"

**Kids cover prompt must include:**
- Full-color, vibrant cartoon style
- Eye-catching, professional children's book cover art
- DO NOT include any text/letters/words in the generated image
- Bright colors, cheerful composition
- Mention "Coloring Book for Kids Ages 6-12"

### Step 4: Write Page Prompts (20-30)

**For Adults (Cozy & Cute):**
Each prompt describes a complete black-and-white coloring page with:
- "Cute cozy medium-detail" adult aesthetic
- Complete layered scene: foreground + midground + background
- Large, clear decorative shapes — NO dense micro-patterns
- Simplified vegetation (large stylized shapes, wide spacing, no micro-veins)
- Spaced-out background motifs (wallpapers, textiles use big shapes)
- Kawaii character proportions (consistent across pages)
- Cozy environment props: shelves, lamps, cushions, windows, curtains, tables, art, rugs
- Mix of solo scenes and occasional secondary character interactions

**For Kids (Bold & Easy):**
Each prompt describes a single-subject coloring page with:
- PORTRAIT orientation, black-and-white line art only
- Bold, thick, clean outlines for ages 6-12
- Single subject centered, fills most of page
- NO shading, gradients, borders, or frames
- White background
- Cute, friendly, appealing style
- Simple enough for crayons/markers

### Step 5: Ensure Variety

Page prompts must cover diverse scenes/activities:
- Different settings (indoor, outdoor, seasonal)
- Different activities (cooking, reading, playing, sleeping, crafting)
- Different moods (playful, peaceful, cozy, adventurous)
- Main character in different poses/situations
- Some solo, some with secondary characters (adults)

### Step 6: Save Plan

Create the plan JSON file at `plans/{theme_key}_plan.json`:
```json
{
  "theme_key": "the_theme_key",
  "audience": "adults|kids",
  "title": "...",
  "subtitle": "...",
  "description": "...",
  "keywords": ["kw1", "kw2", "kw3", "kw4", "kw5", "kw6", "kw7"],
  "cover_prompt": "...",
  "page_prompts": ["prompt1", "prompt2", ...]
}
```

Also save `prompts/{theme_key}.txt` (one prompt per line).

### Step 7: Register Theme

Add to `config.py` THEMES dict:
```python
"{theme_key}": {
    "name": "{Title}",
    "book_title": "{Full Title}",
    "prompt_file": "prompts/{theme_key}.txt",
},
```

---

## Output

- `plans/{theme_key}_plan.json` — Full plan with metadata + all prompts
- `prompts/{theme_key}.txt` — One prompt per line

---

## Quality Criteria

- Title is SEO-friendly and audience-appropriate
- Description is compelling and marketplace-ready
- 7 diverse, relevant keywords
- Cover prompt matches audience style guidelines
- Every page prompt follows the correct audience guide strictly
- Page prompts are varied (different scenes, activities, settings)
- Characters described consistently across all prompts
- No dense micro-detail instructions in adult prompts
- No shading/gradient instructions in kids prompts

---

## References

- `references/adult-prompt-guide.md` — Cozy & cute adult style (from Hoja 1)
- `references/kids-prompt-guide.md` — Bold & easy kids style
