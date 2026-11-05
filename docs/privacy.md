# Revisi Mudah Privacy & Data Protection Specification

## 1. Principles
Thesis supervision recordings frequently contain sensitive academic IP, unreleased research findings, institutional discussions, and personal evaluations. Revisi Mudah enforces a zero-silent-upload architecture.

## 2. Policy Modes
- `deny`: Strictly forbids any network transmission of audio bytes. Only local providers (e.g., local Whisper.cpp) can execute.
- `ask` (Default): Requests explicit confirmation from the user prior to initiating any cloud API call. In non-interactive contexts, defaults to denying cloud access.
- `allow`: Permits cloud upload to configured and implemented cloud providers (e.g. Gemini).

## 3. Metadata Sanitization
Audio file provenance records only the base filename (e.g., `bimbingan.m4a`) and strictly strips local absolute paths (e.g., `C:/Users/...`) to prevent workstation information disclosure in exported artifacts.

## 4. Agent CLI Boundary & Transcript Privacy
- **Audio Provider Boundary:** `--cloud-consent deny` strictly guarantees that no audio bytes are transmitted to any cloud speech-to-text service. Audio transcription executes 100% locally on the host machine.
- **Harness & LLM Reasoning Boundary:** Once `transcript.json` is generated, if an Agent CLI (such as Claude Code, OpenCode, or OMP) is configured to use a remote cloud model (e.g. Claude 3.7 or Gemini Cloud), the Agent CLI itself may transmit transcript text to its model provider during feedback extraction.
- **True Offline Assurance:** To achieve a completely offline, air-gapped revision planning workflow, users must pair `--cloud-consent deny` with a locally hosted LLM runner (e.g. Ollama or local Llama.cpp) within their agent harness.

## 5. Storage and Data Retention Policy
- Original audio, verbatim transcript, dan timestamp dipertahankan sebagai evidence.
- Revisi Mudah v1.0 tidak melakukan penghapusan otomatis atau perubahan terhadap artefak tersebut.
- Kebijakan aplikasi ini mencegah penghapusan otomatis oleh perangkat lunak Revisi Mudah; ini bukan merupakan jaminan penyimpanan fisik tamper-proof di level filesystem atau sistem operasi.
