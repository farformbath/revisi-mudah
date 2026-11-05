# Revisi Mudah

**Dari rekaman bimbingan menjadi rencana revisi yang terstruktur.**  
*Audio-to-Academic Implementation Planning System*

Revisi Mudah adalah sistem AI yang membantu mahasiswa mengubah rekaman bimbingan akademik menjadi transkrip bertimestamp, feedback berbasis bukti, dan rencana implementasi revisi yang berada sepenuhnya di bawah kendali penulis. Revisi Mudah tidak melakukan pengeditan skripsi secara otomatis.

---

## 🎯 Key Capabilities

- **Universal Capability Router:** Mengalirkan audio secara cerdas antara Whisper lokal (GGML / CTranslate2), model native multimodal, dan cloud STT.
- **Strict Privacy & Consent Gate:** Zero silent cloud uploads. Mendukung mode `ask`, `allow`, dan `deny` (100% lokal offline).
- **Verbatim Acoustic Evidence:** Rekaman audio asli adalah sumber kebenaran akustik. Transkrip dan timestamp milidetik disimpan secara permanen.
- **Evidence Integrity Verification:** Setiap kutipan (*quote*) diverifikasi secara semantik dan wajib ada di segmen transkrip sebelum diterima.
- **Mandatory Author Adjudication:** AI hanya mengekstrak kandidat (`needs_author_review`); hanya mahasiswa (penulis) yang berwenang menyetujui tugas revisi.
- **Hard Execution Boundary:** Hanya menghasilkan rencana revisi (*planning only*). Dilarang mengedit file naskah skripsi atau membuat patch otomatis.
- **Dual Interface:** Typer CLI (`revisi-mudah`) + Python MCP Server (`revisi-mudah-mcp`) + Agent Skill (`revisi-mudah`).
- **Academic Research Skills (ARS) Compatibility:** Mengekspor dokumen serah-terima (*handoff*) yang kompatibel dengan protokol ARS #670.
- **Backward Compatibility:** Menyediakan alias transisi `mentorspec` dan `mentorspec-mcp`.

---

## 🔬 Research & Ecosystem Context

Revisi Mudah dirancang berdasarkan kebutuhan nyata dalam ekosistem coding agent akademik:
- **Oh My Pi (can1357/oh-my-pi):** Issue #5834 (*Audio/Video Input Modality*), PR #10669 (*Audio/Video Content Integration*), dan PR #16611 (*Audio Transcription Through Audio-Capable Models*).
- **Academic Research Skills (ARS):** Revision Protocol #390 (Scoped Patch) dan Revision Roadmap #670 (Claim & Evidence Boundaries).

---

## 📦 Architecture & Flow

```text
Audio Recording (bimbingan.m4a)
      │
      ▼
Audio Inspector (SHA-256 digest, metadata, duration)
      │
      ▼
Privacy Gate & Capability Router (Local Whisper / Gemini / OMP native)
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
Menggunakan `uv`:
```bash
git clone https://github.com/farformbath/revisi-mudah.git
cd revisi-mudah
uv sync
```

### 2. Inspect Audio Recording (Offline)
```bash
uv run revisi-mudah inspect bimbingan.m4a
```

### 3. Transcribe Audio
```bash
uv run revisi-mudah transcribe bimbingan.m4a -o transcript.json --cloud-consent deny
```

### 4. Connect via MCP Server
Revisi Mudah menyediakan server MCP berbasis stdio (`revisi-mudah-mcp`). Lihat panduan deployment lengkap di [`docs/mcp-deployment.md`](docs/mcp-deployment.md):

- **Oh My Pi (OMP):** `~/.omp/agent/mcp.json` (`"type": "stdio"`)
- **Google Antigravity:** `~/.gemini/config/mcp_config.json`
- **OpenCode:** `opencode.json` (`"type": "local"`, command array)
- **Claude Code & Desktop:** `~/.claude.json` / `.mcp.json` / `claude_desktop_config.json`
- **Cursor:** `.cursor/mcp.json` (`"type": "stdio"`)

*Catatan Windows: Jika client GUI tidak menemukan `uv` di PATH, gunakan path absolut `C:/Users/LOQ/.local/bin/uv.exe`.*

---

## 📋 Canonical Artifacts

| File | Schema | Deskripsi |
|---|---|---|
| `transcript.json` | `schemas/audio-result.schema.json` | Transkrip verbatim dengan timestamp milidetik per segmen |
| `feedback.json` | `schemas/feedback.schema.json` | Arahan dosen yang terikat langsung ke kutipan verbatim |
| `adjudication.json` | `schemas/adjudication.schema.json` | Keputusan penulis (accepted, rejected, clarified) |
| `implementation-plan.md` | Markdown | Rencana implementasi revisi resmi hanya dari tugas yang disetujui |

---

## 🛡️ License
MIT License.
