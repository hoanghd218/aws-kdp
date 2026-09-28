---
name: create-agent
description: Create or update project-scoped or personal custom Codex subagents. Use when the user asks to create an agent, specialist, autonomous worker, reviewer, explorer, or reusable delegated role for Codex.
---

# Create a Codex Agent

Create a focused custom agent as a standalone TOML file.

## Workflow

1. Determine the agent's single responsibility, expected inputs, output shape, and whether it may edit files.
2. Choose scope:
   - Project: `.codex/agents/<agent-name>.toml`
   - Personal: `~/.codex/agents/<agent-name>.toml`
3. Inspect existing config and agents before editing. Preserve unrelated settings.
4. Use a lowercase snake_case `name`; keep the filename close to the name.
5. Write the three required fields:

```toml
name = "reviewer"
description = "Review changes for correctness, security risks, regressions, and missing tests."
developer_instructions = """
Review like an owner. Lead with concrete findings and file references.
Do not modify files unless the parent explicitly requests fixes.
"""
```

6. Add optional settings only when justified: `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, or `skills.config`.
7. Use `sandbox_mode = "read-only"` for research and review agents unless edits are required.
8. Validate TOML syntax and report the created path plus an example invocation prompt.

## Orchestration guidance

- Delegate only concrete, bounded work that can run independently.
- Keep write-heavy agents from editing overlapping files concurrently.
- Tell the parent whether to wait for all agents and what each agent must return.
- Subagents inherit the parent permission mode; do not imply they can bypass approvals.

## Quality checklist

- Narrow responsibility and clear trigger
- Required TOML fields present
- No secrets or machine-specific credentials
- Minimum necessary permissions
- Concrete output contract
- TOML parses successfully
