"""Semantic and schema validators for MentorSpec 1.0."""

from __future__ import annotations

import json
import warnings
from importlib.resources import files
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


TIMESTAMP_END_TOLERANCE_MS: int = 250


def _normalize_text(s: str) -> str:
    """Normalize whitespace and lowercase for forgiving substring matching."""
    return " ".join(s.strip().lower().split())


def get_schemas_dir() -> Path:
    """Resolve the single canonical schemas directory located inside the package."""
    pkg_schemas = Path(__file__).resolve().parent.parent / "schemas"
    if pkg_schemas.is_dir():
        return pkg_schemas
    raise FileNotFoundError(
        f"Could not locate package schemas directory at {pkg_schemas}"
    )


def load_json_schema(schema_name: str) -> dict[str, Any]:
    """Load a schema dictionary using importlib.resources with fallback to source tree."""
    try:
        schema_resource = (
            files("revisi_mudah").joinpath("schemas").joinpath(schema_name)
        )
        if schema_resource.is_file():
            return json.loads(schema_resource.read_text(encoding="utf-8"))
    except (TypeError, ModuleNotFoundError, FileNotFoundError):
        pass

    schemas_dir = get_schemas_dir()
    schema_path = schemas_dir / schema_name
    if not schema_path.is_file():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, encoding="utf-8") as f:
        return json.load(f)


def validate_against_json_schema(data: dict[str, Any], schema_name: str) -> None:
    """Validate a dictionary directly against a MentorSpec JSON Schema."""
    schema_dict = load_json_schema(schema_name)
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

        # 4. Duration boundary check with final-segment tolerance
        if audio.source.duration_ms > 0:
            is_final_segment = idx == len(audio.transcription.segments) - 1
            overflow = seg.end_ms - audio.source.duration_ms

            if overflow > 0:
                if not is_final_segment:
                    raise SemanticValidationError(
                        f"Non-final segment '{seg.id}' end_ms ({seg.end_ms}) exceeds audio duration ({audio.source.duration_ms})."
                    )
                if overflow > TIMESTAMP_END_TOLERANCE_MS:
                    raise SemanticValidationError(
                        f"Final segment '{seg.id}' end_ms ({seg.end_ms}) exceeds audio duration "
                        f"({audio.source.duration_ms}) by {overflow}ms, exceeding the {TIMESTAMP_END_TOLERANCE_MS}ms tolerance."
                    )
                # Small overshoot within tolerance on final segment: clamp to duration_ms
                clamped_end = max(seg.start_ms + 1, audio.source.duration_ms)
                warnings.warn(
                    f"Normalizing final segment '{seg.id}' end_ms from {seg.end_ms} to {clamped_end} "
                    f"(clamped within {TIMESTAMP_END_TOLERANCE_MS}ms tolerance).",
                    UserWarning,
                    stacklevel=2,
                )
                seg.end_ms = clamped_end


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
