# Revisi Mudah — Multi-Client MCP Deployment Guide

This guide provides verified, client-specific configuration payloads for deploying the **Revisi Mudah** MCP Server (`revisi-mudah-mcp`) across Agent CLI and GUI harnesses.

---

## 1. Oh My Pi (OMP)
OMP accepts `mcpServers` at the root JSON object, requires `"type": "stdio"`, and expects string `command` with an array of `args`.

- **User Scope:** `~/.omp/agent/mcp.json` (`C:/Users/LOQ/.omp/agent/mcp.json`)
- **Project Scope:** `.omp/mcp.json`

```json
{
  "$schema": "https://raw.githubusercontent.com/can1357/oh-my-pi/main/packages/coding-agent/src/config/mcp-schema.json",
  "mcpServers": {
    "revisi-mudah": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/LOQ/revisi-mudah",
        "run",
        "revisi-mudah-mcp"
      ]
    }
  }
}
```

---

## 2. Google Antigravity
Antigravity places `mcpServers` directly at the root JSON level.

- **Global CLI Scope:** `~/.gemini/config/mcp_config.json`
- **Workspace Scope:** `.agents/mcp_config.json`

```json
{
  "mcpServers": {
    "revisi-mudah": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/LOQ/revisi-mudah",
        "run",
        "revisi-mudah-mcp"
      ]
    }
  }
}
```

---

## 3. OpenCode
OpenCode uses the root property `mcp` with the server identifier directly as the key (no intermediate `servers` key), `"type": "local"`, and an array for `command`.

- **Configuration File:** `opencode.json` or `opencode.jsonc`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "revisi-mudah": {
      "type": "local",
      "command": [
        "uv",
        "--directory",
        "C:/Users/LOQ/revisi-mudah",
        "run",
        "revisi-mudah-mcp"
      ],
      "enabled": true
    }
  }
}
```

---

## 4. Claude Code & Claude Desktop

Claude Code supports three distinct scopes:
1. **User Scope (`~/.claude.json`):** Located at root `mcpServers`. Available across all projects for this user.
2. **Local Scope (`~/.claude.json`):** Configured inside `projects[project_path].mcpServers`. Private to your machine for that specific project.
3. **Project Scope (`.mcp.json`):** Committed in the project root directory and shared via Git.
   *Note: Project-scoped MCP servers can prompt for interactive author approval when first accessed.*

### Configuration Format (Claude Desktop & Claude Code):
```json
{
  "mcpServers": {
    "revisi-mudah": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/LOQ/revisi-mudah",
        "run",
        "revisi-mudah-mcp"
      ]
    }
  }
}
```

---

## 5. Cursor
Cursor requires `"type": "stdio"` for stdio-based servers in `.cursor/mcp.json`.

- **Workspace Scope:** `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "revisi-mudah": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/LOQ/revisi-mudah",
        "run",
        "revisi-mudah-mcp"
      ]
    }
  }
}
```

---

## ⚠️ Repository Working Directory & Windows Path Fallback

### Repository Path:
The repository is deployed at `C:/Users/LOQ/revisi-mudah`. All MCP configurations reflect this active path.

### Executable Fallback:
If a GUI client cannot find `uv` in its environment PATH, substitute `"uv"` with the verified absolute binary path:
- Windows default: `"C:/Users/LOQ/.local/bin/uv.exe"` (or escaped `"C:\\Users\\LOQ\\.local\\bin\\uv.exe"`).

---

## 6. Deployment Verification Tiers

Revisi Mudah maintains three formal tiers of deployment verification:

1. **Configuration Verified:** File path, root JSON schema, client-specific runner type (`stdio` vs `local`), and argument structures match official client documentation. All 5 configurations above are Configuration Verified.
2. **Tool Test Verified:** Internal tool calls and subprocess stdio JSON-RPC handshakes pass automated tests (`test_mcp_tools.py` and `test_mcp_protocol_smoke.py`). All 6 tools are verified advertised.
3. **Client Runtime Verified:** The external client process actively spawns the Revisi Mudah server, completes the MCP handshake, and surfaces all 6 registered tools in its client palette during an interactive session.
