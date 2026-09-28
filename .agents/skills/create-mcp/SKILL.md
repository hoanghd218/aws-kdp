---
name: create-mcp
description: Add, configure, troubleshoot, or build MCP servers for Codex. Use when the user asks to connect an MCP integration, configure an STDIO or Streamable HTTP server, add tools or data to Codex, or build a custom MCP server.
---

# Create or Configure a Codex MCP Server

Use Codex MCP configuration, not Claude Code settings.

## Choose the task

- Configure an existing server when a command or HTTP endpoint already exists.
- Build a server when the user needs custom tools or resources.
- Prefer an installed plugin or existing MCP integration when it already covers the request.

## Configuration scope

- Personal: `~/.codex/config.toml`
- Project: `.codex/config.toml` for trusted projects

The desktop app, Codex CLI, and IDE extension share this configuration on the same host.

## Configure an existing server

1. Confirm transport: STDIO or Streamable HTTP.
2. Inspect existing config and preserve unrelated sections.
3. Add a uniquely named `[mcp_servers.<name>]` table.
4. Keep credentials in environment variables. Never commit tokens.
5. Restart Codex after changes and inspect `/mcp` status.
6. Exercise one harmless tool or resource to verify the connection.

Examples:

```toml
[mcp_servers.local_tools]
command = "npx"
args = ["-y", "@example/mcp-server"]

[mcp_servers.remote_docs]
url = "https://example.com/mcp"
bearer_token_env_var = "EXAMPLE_MCP_TOKEN"
```

## Build a custom server

1. Define a small tool surface with explicit inputs, outputs, errors, and side effects.
2. Use JSON Schema with useful field descriptions and strict validation.
3. Return concise structured results; paginate or filter large payloads.
4. Put cross-tool constraints and rate limits in the server `instructions` field.
5. Add authentication, timeouts, logging, and secret redaction before production use.
6. Test initialization, tool discovery, successful calls, invalid inputs, and upstream failures.
7. Configure the finished server in Codex and verify through `/mcp`.

Do not modify global configuration without explicit user authorization when a project-scoped configuration is sufficient.
