---
name: kdp-prompt-writer
description: "Analyze a coloring-book concept and write the complete production plan: market-aware metadata, style bible, content arc, polished front matter, text-free imagegen cover/frontmatter prompts, and unique interior page prompts. Use for book planning, page prompts, metadata, or plan.json creation and revision."
---

# KDP Prompt Writer

Codex writes all plan text directly. Do not call another model for prompt or metadata writing.

## Workflow

1. Read the adult or kids guide in `references/`.
2. Confirm concept, differentiating angle, audience/age, trim, unique coloring-page count, author, and avoid list.
3. If commercial viability matters, require the saved `$kdp-niche-finder` evidence or clearly mark validation as skipped/low confidence.
4. Define the product and content architecture before individual prompts.
5. Write exact metadata and editorial copy.
6. Write structured imagegen prompts and validate uniqueness.
7. Save valid JSON plus one-prompt-per-line text.

## Content architecture

Create:

- `buyer_promise`: what experience/result the buyer receives;
- `style_bible`: stable subject traits, medium, line weight, detail density, composition rules, cover palette, and forbidden elements;
- 4–6 `sections` with a progression in setting, activity, mood, or difficulty;
- `duplication_matrix`: one row per page with subject, action, setting, pose/camera, hero props, and section.

No two pages may reuse the same subject + action + setting. Avoid padding the count with near-duplicates.

## Metadata

- Title/subtitle must read naturally and match the book exactly; never keyword-stuff or use unsupported promotional claims.
- Description must state only real production facts: actual unique illustrations, trim, single-sided layout, audience, style, and featured subjects.
- Supply 7 nonduplicative backend keyword phrases and relevant categories.
- Coloring books are generally not low-content under Amazon's current definition; do not mark them low-content by default.

## Polished front matter

Write book-specific copy, not templates that could fit any topic:

```json
"front_matter": {
  "title_kicker": "short promise",
  "ownership_heading": "kids only",
  "closing_heading": "theme-specific headline",
  "closing_message": "2–3 sentences referencing concrete book scenes, mood, or achievement",
  "review_request": "one neutral request for an honest Amazon review"
}
```

Do not use “Thank you for being here,” “Made with love,” “Share and tag us on Amazon,” or requests for a positive/five-star review.

## Imagegen prompt structure

Use the imagegen shared schema where helpful:

```text
Use case: illustration-story
Asset type: Amazon KDP coloring-book interior page
Primary request: <distinct scene>
Scene/backdrop: <setting>
Subject: <subject + invariant traits>
Style/medium: black-and-white line art, <style bible>
Composition/framing: <SQUARE 1:1 or PORTRAIT 3:4>, safe no-bleed margin
Constraints: bold clean closed outlines; white background; easy-to-color open regions; exact subject count
Avoid: color, gray fill, shading, gradient, border, frame, text, letters, numbers, signature, watermark, mockup, cropped subject, merged anatomy
```

Adult pages may use coherent layered scenes but must avoid micro-pattern clutter. Kids pages should use one dominant centered subject and age-appropriate open shapes. Multiple characters must be separated with complete visible anatomy.

Cover/frontmatter prompts use artwork only:

- cover use case: `ads-marketing`;
- frontmatter use case: `illustration-story`;
- require intentional negative space for code-rendered text;
- forbid every word, letter, number, barcode, ISBN, QR code, logo, placeholder box, and mockup.

## Required plan fields

```json
{
  "theme_key": "...",
  "concept": "...",
  "audience": "adults|kids",
  "age_range": "...",
  "page_size": "8.5x8.5|8.5x11",
  "page_count": 36,
  "title": "...",
  "subtitle": "...",
  "description": "...",
  "keywords": ["..."],
  "categories": ["...", "..."],
  "reading_age": "...",
  "author": {"first_name": "...", "last_name": "..."},
  "ai_disclosure": {"interior_images": "ai_generated", "cover_artwork": "ai_generated"},
  "niche_validation": {},
  "content_strategy": {
    "buyer_promise": "...",
    "style_bible": {},
    "sections": [],
    "duplication_matrix": []
  },
  "front_matter": {},
  "frontmatter_art_prompts": {"title": "...", "belongs_to": null, "closing": "..."},
  "cover_prompt": "text-free front artwork",
  "back_cover_prompt": "text-free back artwork",
  "page_prompts": ["..."]
}
```

Require `page_count == len(page_prompts) == len(duplication_matrix)`, 7 keywords, no empty production fields, and valid JSON. Save to `output/<theme>/plan.json` and `output/<theme>/prompts.txt`.
