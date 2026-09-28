---
name: kdp-batch-assembler
description: Finish multiple already-approved KDP coloring-book plans one book at a time with built-in imagegen generation, full visual review, polished front matter, PDF assembly, imagegen cover composition, and preflight. Use for batch build or completing all planned books.
---

# KDP Batch Assembler

Scan `output/*/plan.json` and classify each book as missing images, missing review, missing interior, missing cover, or complete. Present the queue and get one approval for the selected books.

Process sequentially so every built-in imagegen result can be inspected and saved to the correct project path. For each selected book, run the relevant phases of `$kdp-book-creator`:

1. Validate the plan schema, approved niche status, style bible, page count, unique prompt count, and polished front-matter copy.
2. Use `$kdp-image-generator` for missing pages; one built-in imagegen call per distinct asset.
3. Use `$kdp-image-reviewer` on every page and target only failed pages for regeneration.
4. Generate text-free front-matter art, compose exact copy, and assemble the interior.
5. Generate text-free front/back cover art with built-in imagegen, then code-compose the wrap.
6. Run PDF, cover, metadata, AI-disclosure, and KDP preflight checks.

Never use `generate_images.py` or `generate_cover.py` unless the user explicitly chooses the legacy provider/API path. Never silently skip visual review. If one book fails, report it and continue; do not mark it complete.

Batch completion means every book has `interior.pdf`, `cover.pdf`, `cover.png`, `plan.json`, a visual review summary, and a preflight verdict. A planned series still follows flagship-first validation; do not produce all volumes merely because plans exist.
