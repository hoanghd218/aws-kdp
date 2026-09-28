---
name: create-hook
description: Create or update Codex lifecycle hooks in hooks.json or config.toml. Use when the user asks to automate actions before or after tool use, at session start or end, on prompts, compaction, permission requests, subagent events, or when a turn stops.
---

# Create a Codex Hook

Create deterministic lifecycle automation for Codex.

## Locations

- Project JSON: `.codex/hooks.json`
- Project inline config: `.codex/config.toml`
- Personal JSON: `~/.codex/hooks.json`
- Personal inline config: `~/.codex/config.toml`

Prefer one representation per config layer. Project hooks run only for trusted projects, and new or changed command hooks require trust review.

## Supported events

Use the event that most narrowly matches the request: `SessionStart`, `SessionEnd`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `UserPromptSubmit`, `PreCompact`, `PostCompact`, `SubagentStart`, `SubagentStop`, or `Stop`.

## Workflow

1. Clarify the trigger, matcher, handler behavior, timeout, and failure policy.
2. Inspect existing `.codex/hooks.json` and `.codex/config.toml`; preserve unrelated hooks.
3. Prefer a command hook for deterministic checks. Keep scripts in `.codex/hooks/` for project scope.
4. Use explicit executable paths and quote paths safely.
5. Avoid secrets in hook definitions and avoid destructive side effects.
6. Validate JSON/TOML and run the handler directly with representative input when safe.
7. Tell the user to review/trust the hook with `/hooks` if required.

## Minimal JSON example

```json
{
  "description": "Project lifecycle hooks",
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .codex/hooks/post_tool_check.py",
            "timeout": 10,
            "statusMessage": "Checking tool result"
          }
        ]
      }
    ]
  }
}
```
