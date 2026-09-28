---
name: kdp-batch-planner
description: Turn multiple coloring-book idea briefs into complete production plans with niche-validation status, content architecture, polished front matter, text-free imagegen artwork prompts, SEO metadata, and unique page prompts. Use for batch planning ideas without generating images.
---

# KDP Batch Planner

Scan `ideas/*.md`, show the candidate list and validation status, and get one approval for which ideas to plan plus shared author/trim/page-count settings.

For each selected idea, apply `$kdp-prompt-writer` in full. A valid batch plan includes:

- commercial evidence or an explicit `discovery_only/user_skipped` warning;
- buyer promise, style bible, 4–6 section content arc, and duplication matrix;
- polished, book-specific front-matter copy;
- text-free built-in imagegen prompts for cover, back cover, title art, optional ownership art, and closing art;
- one unique structured interior prompt per page;
- complete, truthful metadata and author;
- `page_count == page_prompts == duplication_matrix`, 7 keywords, and valid JSON.

Save `output/<theme>/plan.json` and `prompts.txt`. Review all plans with the user before moving idea files to `ideas/done/`.

Planning does not authorize image generation. Do not call image APIs or built-in imagegen in this skill. Do not batch-plan a full series as production-ready until its flagship has live validation data.
