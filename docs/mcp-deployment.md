# MentorSpec Multi-Client MCP Deployment Guide

This guide provides verified, syntactically exact configuration payloads for deploying MentorSpec across different Agent CLI and GUI harnesses.

---

## 1. Oh My Pi (OMP)
OMP accepts `mcpServers` at the root object and requires `"type": "stdio"`.

- **User Scope:** `~/.omp/agent/mcp.json` (`C:/Users/LOQ/.omp/agent/mcp.json`)
- **Project Scope:** `.omp/mcp.json`

```json
{
  "$schema": "https://raw.githubusercontent.com/can1357/oh-my-pi/main/packages/coding-agent/src/config/mcp-schema.json",
  "mcpServers": {
    "mentorspec": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/LOQ/mentorspec",
        "run",
        "mentorspec-mcp"
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
    "mentorspec": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/LOQ/mentorspec",
        "run",
        "mentorspec-mcp"
      ]
    }
  }
}
```

---

## 3. OpenCode
OpenCode uses the root property `mcp` with the server name as direct sub-key (no intermediate `servers` key), `"type": "local"`, and an array for `command`.

- **Configuration File:** `opencode.json` or `opencode.jsonc`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "mentorspec": {
      "type": "local",
      "command": [
        "uv",
        "--directory",
        "C:/Users/LOQ/mentorspec",
        "run",
        "mentorspec-mcp"
      ],
      "enabled": true
    }
  }
}
```

---

## 4. Claude Code & Claude Desktop
- **Claude Desktop:** `claude_desktop_config.json`
- **Claude Code (User Scope):** `~/.claude.json`
- **Claude Code (Project Scope):** `.mcp.json`

```json
{
  "mcpServers": {
    "mentorspec": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/LOQ/mentorspec",
        "run",
        "mentorspec-mcp"
      ]
    }
  }
}
```

---

## 5. Cursor
- **Workspace Scope:** `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "mentorspec": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/LOQ/mentorspec",
        "run",
        "mentorspec-mcp"
      ]
    }
  }
}
```

---

## ⚠️ Windows Path Fallback
If a GUI client fails to resolve `uv` in its environment PATH, substitute `"uv"` with the absolute binary path obtained via `where.exe uv`:

Windows default:
`"C:/Users/LOQ/.local/bin/uv.exe"` (or with escaped backslashes `"C:\\Users\\LOQ\\.local\\bin\\uv.exe"`).

---

## 6. Deployment Verification Tiers
MentorSpec distinguishes three formal tiers of deployment verification:
1. **Configuration Verified:** File path, root JSON schema, client-specific runner type (`stdio` vs `local`), and argument structures match official client documentation. All 5 configurations above are Configuration Verified.
2. **Tool Test Verified:** Internal tool calls and data schemas pass automated headless tests (`test_mcp_tools.py` in test suite).
3. **Client Runtime Verified:** The external client process actively spawns the MentorSpec server, completes the MCP handshake, and surfaces all 6 registered tools in its client palette. This tier is evaluated during the live interactive pilot.
