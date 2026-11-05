"""Semantic and schema validators for MentorSpec 1.0."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jsonschema

from revisi_mudah.core.contracts import (
    AdjudicationDecision,
    AudioResult,
    AuthorAdjudication,
    MentorFeedback,
)


class ValidationError(Exception):
    """Base exception for all MentorSpec validation errors."""


class SemanticValidationError(ValidationError):
    """Raised when semantic integrity rules (e.g. timestamps, bounds) are violated."""


class EvidenceIntegrityError(ValidationError):
    """Raised when feedback quotes do not exist in the referenced transcript segment."""


def _normalize_text(s: str) -> str:
    """Normalize whitespace and lowercase for forgiving substring matching."""
    return re.sub(r"\s+", " ", s.strip().lower())


def get_schemas_dir() -> Path:
    """Resolve schemas directory relative to package or project root."""
    # Try local package location or parent repo root
    current = Path(__file__).resolve()
    for parent in [current.parent.parent.parent.parent, current.parent.parent.parent]:
        candidate = parent / "schemas"
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("Could not locate Revisi Mudah schemas directory.")


def validate_against_json_schema(data: dict[str, Any], schema_name: str) -> None:
    """Validate a dictionary directly against a MentorSpec JSON Schema."""
    schemas_dir = get_schemas_dir()
    schema_path = schemas_dir / schema_name
    if not schema_path.is_file():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_dict = json.load(f)

    try:
        jsonschema.validate(instance=data, schema=schema_dict)
    except jsonschema.exceptions.ValidationError as e:
        raise ValidationError(
            f"JSON Schema validation failed for {schema_name}: {e.message}"
        ) from e


def validate_audio_result(audio: AudioResult) -> None:
    """
    Enforce semantic rules on AudioResult:
    1. start_ms >= 0
    2. end_ms > start_ms
    3. Segments are sorted chronologically by start_ms
    4. end_ms does not exceed total duration_ms (when duration_ms > 0)
    5. Segment IDs are strictly unique
    """
    seen_ids = set()
    prev_start = -1

    for idx, seg in enumerate(audio.transcription.segments):
        # 1. Unique IDs
        if seg.id in seen_ids:
            raise SemanticValidationError(
                f"Duplicate segment ID: '{seg.id}' at index {idx}."
            )
        seen_ids.add(seg.id)

        # 2. Positive & proper interval
        if seg.start_ms < 0:
            raise SemanticValidationError(
                f"Segment '{seg.id}' has negative start_ms: {seg.start_ms}."
            )
        if seg.end_ms <= seg.start_ms:
            raise SemanticValidationError(
                f"Segment '{seg.id}' end_ms ({seg.end_ms}) must be strictly greater than start_ms ({seg.start_ms})."
            )

        # 3. Chronological sorting
        if seg.start_ms < prev_start:
            raise SemanticValidationError(
                f"Segments out of chronological order at '{seg.id}': start_ms {seg.start_ms} < previous {prev_start}."
            )
        prev_start = seg.start_ms

        # 4. Duration boundary
        if audio.source.duration_ms > 0 and seg.end_ms > audio.source.duration_ms:
            raise SemanticValidationError(
                f"Segment '{seg.id}' end_ms ({seg.end_ms}) exceeds audio duration ({audio.source.duration_ms})."
            )


def validate_feedback_integrity(feedback: MentorFeedback, audio: AudioResult) -> None:
    """
    Enforce evidence integrity:
    1. Source ref matches audio SHA-256 digest
    2. Unique feedback IDs
    3. Every evidence segment_id exists in transcript
    4. Every quote is verifiably present in the referenced segment text
    """
    if feedback.source_ref.lower() != audio.source.sha256.lower():
        raise EvidenceIntegrityError(
            f"Feedback source_ref '{feedback.source_ref}' does not match audio SHA-256 '{audio.source.sha256}'."
        )

    # Build segment map
    segment_map = {seg.id: seg for seg in audio.transcription.segments}
    seen_fids = set()

    for item in feedback.feedback_items:
        if item.id in seen_fids:
            raise SemanticValidationError(f"Duplicate feedback ID: '{item.id}'.")
        seen_fids.add(item.id)

        for ev in item.evidence:
            if ev.segment_id not in segment_map:
                raise EvidenceIntegrityError(
                    f"Feedback '{item.id}' references non-existent segment '{ev.segment_id}'."
                )

            target_segment = segment_map[ev.segment_id]
            norm_quote = _normalize_text(ev.quote)
            norm_seg_text = _normalize_text(target_segment.text)

            if norm_quote not in norm_seg_text:
                raise EvidenceIntegrityError(
                    f"Evidence integrity failed in '{item.id}': quote '{ev.quote}' "
                    f"is not found verbatim in segment '{ev.segment_id}' text: '{target_segment.text}'."
                )


def validate_adjudication(
    adjudication: AuthorAdjudication, feedback: MentorFeedback
) -> None:
    """
    Enforce adjudication integrity:
    1. Source ref matches feedback source ref
    2. Unique decision per feedback ID
    3. Every decision maps to a valid feedback item
    4. 'clarified' decisions must supply clarified_action or author_notes
    """
    if adjudication.source_ref.lower() != feedback.source_ref.lower():
        raise SemanticValidationError(
            f"Adjudication source_ref '{adjudication.source_ref}' does not match feedback source_ref '{feedback.source_ref}'."
        )

    feedback_ids = {item.id for item in feedback.feedback_items}
    seen_decisions = set()

    for d in adjudication.decisions:
        if d.feedback_id in seen_decisions:
            raise SemanticValidationError(
                f"Multiple adjudication decisions for feedback ID '{d.feedback_id}'."
            )
        seen_decisions.add(d.feedback_id)

        if d.feedback_id not in feedback_ids:
            raise SemanticValidationError(
                f"Adjudication references unknown feedback ID '{d.feedback_id}'."
            )

        if d.decision == AdjudicationDecision.CLARIFIED:
            has_action = bool(d.clarified_action and d.clarified_action.strip())
            has_notes = bool(d.author_notes and d.author_notes.strip())
            if not (has_action or has_notes):
                raise SemanticValidationError(
                    f"Decision for '{d.feedback_id}' is 'clarified', but neither clarified_action nor author_notes was provided."
                )
