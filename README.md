# MentorSpec

**Universal Audio-to-Academic Implementation Planning System**  
*An agent-native audio intelligence system that converts academic supervision recordings into evidence-grounded revision roadmaps.*

---

## 🎯 Key Capabilities

- **Universal Capability Router:** Dynamically routes audio between local Whisper (GGML), native multimodal models, and cloud STT.
- **Strict Privacy & Consent Gate:** Zero silent cloud uploads. Supports `ask`, `allow`, and `deny` (100% offline local) modes.
- **Verbatim Acoustic Evidence:** Original recording is the acoustic source of truth. Transcripts with millisecond timestamps are permanently preserved.
- **Evidence Integrity Verification:** Every extracted directive is validated against transcript segment text before acceptance.
- **Mandatory Author Adjudication:** AI extracts candidates (`needs_author_review`); only the student author has the authority to accept tasks.
- **Hard Execution Boundary:** Produces implementation plans only. Does not alter manuscript files or execute unsupervised patches.
- **Dual Interface:** Full Typer CLI (`mentorspec`) + Python MCP Server (`mentorspec-mcp`) + Agent Skill (`SKILL.md`).
- **Academic Research Skills (ARS) Compatibility:** Exports standard Revision Roadmap handoff payloads conforming to ARS #670.

---

## 🔬 Research & Ecosystem Context

MentorSpec is designed around active needs identified in the agent coding ecosystem:
- **Oh My Pi (can1357/oh-my-pi):** Issue #5834 (*Audio/Video Input Modality*), PR #10669 (*Audio/Video Content Integration*), and PR #16611 (*Audio Transcription Through Audio-Capable Models*).
- **Academic Research Skills (ARS):** Revision Protocol #390 (Scoped Patch) and Revision Roadmap #670 (Claim & Evidence Boundaries).

---

## 📦 Architecture & Flow

```
bimbingan.m4a
      │
      ▼
Audio Inspector (SHA-256 digest, metadata, duration)
      │
      ▼
Privacy Gate & Capability Router (Local Whisper / Cloud / Native)
      │
      ▼
Verbatim Transcript (transcript.json)
      │
      ▼
Academic Feedback Extractor (feedback.json)
      │
      ▼
Author Adjudication (Human-in-the-Loop Approval)
      │
      ▼
Implementation Plan (implementation-plan.md)
      │
      ▼
Optional ARS Handoff Export (ars-revision-roadmap.json)
```

---

## 🚀 Quick Start

### 1. Installation
Using `uv`:
```bash
git clone https://github.com/farformbath/mentorspec.git
cd mentorspec
uv sync
```

### 2. Inspect an Audio Recording (Offline)
```bash
uv run mentorspec inspect bimbingan.m4a
```

### 3. Transcribe Audio
```bash
uv run mentorspec transcribe bimbingan.m4a -o transcript.json --cloud-consent ask
```

### 4. Connect via MCP Server
MentorSpec provides standard stdio MCP tools. See [`docs/mcp-deployment.md`](docs/mcp-deployment.md) for verified client-specific configurations:

- **Oh My Pi (OMP):** `~/.omp/agent/mcp.json` or `.omp/mcp.json` (`"type": "stdio"`)
- **Antigravity:** `~/.gemini/config/mcp_config.json` or `.agents/mcp_config.json`
- **OpenCode:** `opencode.json` (`"type": "local"`, command array)
- **Claude Desktop / Claude Code:** `claude_desktop_config.json` / `~/.claude.json` / `.mcp.json`
- **Cursor:** `.cursor/mcp.json`

*Windows Note: If your GUI client cannot locate `uv` in PATH, specify the absolute path (e.g. `C:/Users/LOQ/.local/bin/uv.exe`).*

---

## 📋 Canonical Artifacts

| File | Schema | Purpose |
|---|---|---|
| `transcript.json` | `schemas/audio-result.schema.json` | Verbatim text and timestamps per segment |
| `feedback.json` | `schemas/feedback.schema.json` | Directives linked to verbatim quotes |
| `adjudication.json` | `schemas/adjudication.schema.json` | Human author decisions (accepted, rejected, clarified) |
| `implementation-plan.md` | Markdown | Formatted action plan for accepted tasks only |

---

## 🛡️ License
MIT License.
