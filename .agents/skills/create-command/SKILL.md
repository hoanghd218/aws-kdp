---
name: create-command
description: Turn a repeated workflow or requested slash-command shortcut into a reusable Codex skill or custom prompt. Use when the user asks to create a command, slash command, quick action, shortcut, or reusable prompt for Codex.
---

# Create a Codex Command Workflow

Codex built-in slash commands are product-defined. For user-defined workflows, create a skill under `.agents/skills/`; enabled skills appear in the command picker and can be invoked with `$skill-name`. If the current Codex surface explicitly supports custom prompts, use its `/prompts:<name>` mechanism only when the user asks for a prompt rather than a skill.

## Workflow

1. Ask or infer the repeated action, inputs, expected output, tools, and safety boundaries.
2. Prefer a skill when the workflow needs instructions, scripts, references, implicit triggering, or repository sharing.
3. Use lowercase hyphen-case and create `.agents/skills/<name>/SKILL.md`.
4. Put only `name` and `description` in frontmatter. Front-load trigger phrases in `description`.
5. Write imperative instructions. Use `$ARGUMENTS` only if the target custom-prompt surface documents it; do not copy Claude Code `argument-hint` or `allowed-tools` fields.
6. Add scripts or references only when they improve repeatability.
7. Validate with the Codex skill validator and show an invocation example: `$<name> ...`.

## Minimal template

```markdown
---
name: workflow-name
description: Perform a specific repeatable workflow. Use when the user asks to ...
---

# Workflow Name

1. Inspect the relevant inputs.
2. Perform the workflow.
3. Verify the result.
4. Report changed files and checks.
```

Do not attempt to override or add product-owned slash commands such as `/status`, `/model`, or `/review`.
