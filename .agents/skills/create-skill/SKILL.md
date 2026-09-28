---
name: create-skill
description: Create or update reusable Codex skills with valid SKILL.md metadata, optional scripts, references, assets, and UI metadata. Use when the user asks to create, convert, migrate, improve, or validate a skill for Codex.
---

# Create a Codex Skill

Create repository skills in `.agents/skills/<skill-name>/` or personal skills in `~/.agents/skills/<skill-name>/`.

## Workflow

1. Understand concrete trigger phrases, inputs, outputs, and failure cases.
2. Choose a lowercase hyphen-case name under 64 characters.
3. Plan only reusable content:
   - `SKILL.md` for core instructions
   - `scripts/` for deterministic repeated operations
   - `references/` for detailed guidance loaded only when needed
   - `assets/` for templates and output resources
   - `agents/openai.yaml` for optional UI metadata
4. Write YAML frontmatter with only `name` and `description`. Put all trigger guidance in the description.
5. Write concise imperative instructions. Keep `SKILL.md` under 500 lines when practical and link directly to needed references.
6. Do not add README, changelog, installation guide, or duplicate documentation.
7. Test bundled scripts on representative safe inputs.
8. Run the Codex skill validator and fix every error.
9. Show invocation with `$skill-name`. Codex may also trigger the skill implicitly from its description.

## Minimal template

```markdown
---
name: skill-name
description: Explain what the skill does and exactly when Codex should use it.
---

# Skill Name

Follow the task-specific workflow here.
```

Codex discovers repository skills from `.agents/skills` between the current directory and repository root. If a change is not visible automatically, restart Codex.
