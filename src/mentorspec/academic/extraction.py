"""LLM prompt templates and parser for Academic Feedback extraction."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from mentorspec.core.contracts import (
    AudioResult,
    EvidenceAnchor,
    ExtractionMetadata,
    FeedbackCategory,
    FeedbackItem,
    FeedbackStatus,
    FeedbackType,
    MentorFeedback,
    TargetLocation,
)
from mentorspec.core.validator import validate_feedback_integrity

EXTRACTION_SYSTEM_PROMPT = """You are an Academic Research Auditor. Your role is to analyze a timestamped transcript of a thesis supervision/mentoring session (bimbingan skripsi) and extract structured supervisor feedback.

### RULES:
1. Every feedback item must be tied to VERBATIM quote(s) found directly in the transcript segments.
2. Status MUST ALWAYS be 'needs_author_review'. You have NO authority to approve or reject feedback on behalf of the author.
3. Classify each directive into one of the following Categories:
   - methodology (research methods, validation, procedures)
   - theory (theoretical framework, background concepts)
   - data (datasets, variables, cleaning, sampling)
   - analysis (interpretation of results, metrics, benchmarks)
   - formula (mathematical formulas, algorithmic equations)
   - citation (references, literature currency, DOIs)
   - structure (chapter organization, subchapters)
   - editorial (academic phrasing, formatting, typographical corrections)
   - administrative (deadlines, defense registration requirements)
4. Classify each directive into one of the following Types:
   - revision_request, question, suggestion, approval, administrative_instruction, decision, deadline
5. If a supervisor's intent has multiple interpretations or lacks specific chapter/section targets, explicitly document the 'ambiguity'.

### OUTPUT FORMAT:
Return ONLY a valid JSON object matching this structure:
{
  "feedback_items": [
    {
      "id": "F001",
      "category": "methodology",
      "type": "revision_request",
      "evidence": [
        {
          "segment_id": "S001",
          "quote": "verbatim text matching the segment exactly"
        }
      ],
      "target": {
        "chapter": "BAB III",
        "section": null
      },
      "action": "Concrete, actionable description of what to revise.",
      "ambiguity": null,
      "status": "needs_author_review"
    }
  ]
}
"""


def build_extraction_user_prompt(audio: AudioResult) -> str:
    """Format transcript segments into a structured user prompt for extraction."""
    lines = [
        f"Audio Source: {audio.source.file} (Duration: {audio.source.duration_ms} ms)",
        "Language: " + audio.transcription.language,
        "",
        "--- VERBATIM TRANSCRIPT SEGMENTS ---",
    ]
    for seg in audio.transcription.segments:
        speaker_tag = f"[{seg.speaker}] " if seg.speaker else ""
        lines.append(
            f"[{seg.id}] ({seg.start_ms}ms - {seg.end_ms}ms) {speaker_tag}{seg.text}"
        )

    lines.append("--- END TRANSCRIPT ---")
    lines.append(
        "\nExtract supervisor feedback according to your instructions. Output JSON only."
    )
    return "\n".join(lines)


def parse_extracted_feedback(
    raw_json_str: str,
    audio: AudioResult,
    extractor_model: str = "unknown",
) -> MentorFeedback:
    """
    Parse LLM extraction output into a validated MentorFeedback object.
    Enforces that status is 'needs_author_review'.
    """
    # Clean potential markdown code blocks
    cleaned = raw_json_str.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("\n", 1)[0]
        cleaned = cleaned.strip()

    data = json.loads(cleaned)
    raw_items = data.get("feedback_items", [])

    items: list[FeedbackItem] = []
    for item_data in raw_items:
        evidence_list = [
            EvidenceAnchor(segment_id=ev["segment_id"], quote=ev["quote"])
            for ev in item_data.get("evidence", [])
        ]

        target_data = item_data.get("target")
        target = (
            TargetLocation(
                chapter=target_data.get("chapter"),
                section=target_data.get("section"),
            )
            if target_data
            else None
        )

        item = FeedbackItem(
            id=item_data["id"],
            category=FeedbackCategory(item_data["category"]),
            type=FeedbackType(item_data["type"]),
            evidence=evidence_list,
            target=target,
            action=item_data["action"],
            ambiguity=item_data.get("ambiguity"),
            # Iron rule: Always starts at needs_author_review
            status=FeedbackStatus.NEEDS_AUTHOR_REVIEW,
        )
        items.append(item)

    metadata = ExtractionMetadata(
        extractor_model=extractor_model,
        extracted_at=datetime.now(UTC).isoformat(),
    )

    feedback = MentorFeedback(
        schema="mentorspec/1.0",
        source_ref=audio.source.sha256,
        extraction_metadata=metadata,
        feedback_items=items,
    )

    # Validate evidence integrity
    validate_feedback_integrity(feedback, audio)
    return feedback
