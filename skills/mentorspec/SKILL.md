---
name: mentorspec
description: "Audio-to-Academic Implementation Planning System. Converts thesis supervision and bimbingan recordings into evidence-grounded revision roadmaps without unauthorized manuscript modification."
category: academic
risk: safe
tags: "[audio, academic, thesis, bimbingan, revision-roadmap, transcription, research-integrity]"
triggers:
  - "bimbingan"
  - "rekaman dosen"
  - "mentorspec"
  - "audio skripsi"
  - "revisi bimbingan"
  - "supervision audio"
---

# MentorSpec — Audio-to-Academic Implementation Planning System

MentorSpec transforms audio recordings of academic supervision (bimbingan skripsi / thesis mentoring) into structured, evidence-grounded implementation plans approved by the author.

## ⚠️ Hard Execution Boundary (Non-Negotiable)

1. **Planning Only:** MentorSpec produces **implementation plans only**. It **NEVER** modifies manuscript files directly, whether through MCP or Agent CLI.
2. **No Automatic Patching:** No LaTeX (`.tex`), Typst (`.typ`), or Word (`.docx`) patches are generated or applied automatically.
3. **Mandatory Author Adjudication:** The author must explicitly accept, reject, or clarify each extracted directive before it enters the implementation plan. LLMs have no authority to approve supervisor feedback on behalf of the author.
4. **Verbatim Preservation:** The original recording is the acoustic source of truth. Raw transcripts and timestamps are preserved immutably.
5. **Privacy Gate:** No audio is uploaded to external cloud services without explicit user consent.

---

## Output Artifacts

MentorSpec generates three canonical artifacts:

| Artifact | Format | Description |
|---|---|---|
| `transcript.json` | JSON (`audio-result.schema.json`) | Verbatim transcript with millisecond timestamps and segment IDs |
| `feedback.json` | JSON (`feedback.schema.json` & `adjudication.schema.json`) | Supervisor directives with evidence anchors and author adjudication decisions |
| `implementation-plan.md` | Markdown | Structured revision plan containing only author-accepted tasks with evidence timestamps |

---

## Workflow

```
bimbingan.m4a
      │
      ▼
1. Audio Inspection & Provenance (SHA-256 digest, metadata, duration)
      │
      ▼
2. Capability Routing & Privacy Gate (Local Whisper / Gemini / OMP native)
      │
      ▼
3. Verbatim Timestamped Transcription (`transcript.json`)
      │
      ▼
4. Academic Feedback Extraction (Categorization into 9 academic domains)
      │
      ▼
5. Author Adjudication (Human-in-the-Loop: Accept / Reject / Clarify)
      │
      ▼
6. Implementation Plan Generation (`implementation-plan.md`)
      │
      ▼
7. Optional ARS Handoff Export (`ars-revision-roadmap.json`)
```

---

## MCP Tools Reference

When running MentorSpec as an MCP server (`mentorspec server`):

- **`audio_inspect(audio_path)`**: Inspects recording metadata (SHA-256, duration, file size, media type).
- **`audio_transcribe(audio_path, cloud_consent)`**: Transcribes audio respecting privacy policy (`ask`, `allow`, or `deny`).
- **`academic_extract_feedback(audio_result_json, raw_llm_json)`**: Validates that all extracted quotes exist verbatim in transcript segments.
- **`academic_adjudicate(feedback_json, adjudication_json)`**: Applies author decisions to feedback items.
- **`academic_build_roadmap(audio_result_json, feedback_json)`**: Generates the formal `implementation-plan.md` for accepted items.
- **`academic_export_ars(audio_result_json, feedback_json)`**: Exports a handoff document compatible with Academic Research Skills (ARS).

---

## Autonomous Agent Instructions

When invoked by a user with an audio recording:
1. First run `audio_inspect` to verify file existence and hash.
2. Check user privacy preferences before transcribing.
3. Transcribe audio to verbatim segments.
4. Extract directives into the 9 categories (`methodology`, `theory`, `data`, `analysis`, `formula`, `citation`, `structure`, `editorial`, `administrative`).
5. Present extracted items to the author for adjudication.
6. Once author decisions are received, generate `implementation-plan.md`.
7. Conclude with the explicit boundary declaration: no manuscript files were modified.
