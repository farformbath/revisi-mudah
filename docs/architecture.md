# MentorSpec Architecture Specification

## 1. Executive Summary
MentorSpec is an agent-native audio intelligence system designed to convert academic thesis supervision recordings into structured, evidence-grounded implementation plans.

## 2. Core Tenets
1. **The Audio is the Ground Truth:** Text transcripts are machine interpretations. Raw transcripts with millisecond timestamps are permanently preserved.
2. **Privacy Gate by Default:** Audio is never uploaded to cloud providers without explicit consent.
3. **No Autonomous Manuscript Alteration:** MentorSpec produces plans, not patches. No thesis files are touched.
4. **Mandatory Human Adjudication:** AI extracts candidates (`needs_author_review`); only the author can accept tasks.

## 3. Data Contracts
- `schemas/audio-result.schema.json`
- `schemas/feedback.schema.json`
- `schemas/adjudication.schema.json`

## 4. Academic Research Skills (ARS) Boundary
MentorSpec provides an optional export layer for ARS (`ars_adapter.py`). It formats accepted tasks into the ARS Revision Roadmap schema. It does not invoke ARS Revision Mode #390 and does not generate diff patches.

## 5. Execution Boundary Verification Protocol
To empirically verify that no thesis files are altered during execution:
1. **Snapshot Pre-Run:** Generate a SHA-256 manifest of the target thesis directory prior to execution:
   ```bash
   # Pre-pilot manifest
   Get-FileHash thesis/* | Out-File pre-pilot-hashes.txt
   ```
2. **Snapshot Post-Run:** Recalculate SHA-256 digests after MentorSpec completes. All digests must remain byte-identical.
3. **Directory Isolation:** The thesis manuscript files should reside outside the MentorSpec output workspace.

## 6. Local Model Format Specifications
- **`whisper.cpp`:** Requires GGML format model binaries (e.g. `ggml-base.bin`).
- **`faster-whisper`:** Requires CTranslate2 format model weights.
- **Terminology Standard:** Use *"Local-only transcription with cloud upload disabled"* for `--cloud-consent deny`. Reserve *"Air-gapped"* strictly for environments with physically/logically isolated network interfaces.
