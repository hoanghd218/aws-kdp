---
description: Create a KDP coloring book end-to-end (interview → prompts → images → PDF → cover)
argument-hint: [concept description]
allowed-tools: Skill, AskUserQuestion, Bash, Read, Write, Edit, Glob, Grep
---

# KDP Coloring Book Creator

Invoke the `kdp-book-creator` skill to run the full book creation pipeline inline (no sub-agents): interview, planning, image generation, image review & auto-regeneration, PDF assembly, and cover creation.

Use the Skill tool with `skill: "kdp-book-creator"`.

If $ARGUMENTS is provided, pass it as the concept:

```
Skill: kdp-book-creator
args:  "Create a KDP coloring book with this concept: $ARGUMENTS"
```

Otherwise invoke the skill with no concept and let it run its Phase 1 interview.
