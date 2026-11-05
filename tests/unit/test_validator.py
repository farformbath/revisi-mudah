"""Unit tests for semantic and evidence integrity validation."""

import pytest

from revisi_mudah.core.contracts import (
    AudioResult,
    AudioSource,
    AuthorAdjudication,
    AuthorDecisionItem,
    AuthorInfo,
    EvidenceAnchor,
    FeedbackCategory,
    FeedbackItem,
    FeedbackType,
    MentorFeedback,
    Transcription,
    TranscriptSegment,
)
from revisi_mudah.core.validator import (
    EvidenceIntegrityError,
    SemanticValidationError,
    validate_adjudication,
    validate_audio_result,
    validate_feedback_integrity,
)


def make_sample_audio_result(
    duration_ms: int = 60000,
    segments: list | None = None,
) -> AudioResult:
    if segments is None:
        segments = [
            TranscriptSegment(
                id="S001",
                start_ms=1000,
                end_ms=5000,
                text="Metodologi penelitian harus diperbaiki dan diperjelas.",
            ),
            TranscriptSegment(
                id="S002",
                start_ms=6000,
                end_ms=10000,
                text="Minggu depan langsung daftar sidang saja.",
            ),
        ]

    source = AudioSource(
        file="bimbingan.m4a",
        sha256="a" * 64,
        duration_ms=duration_ms,
        file_size_bytes=5000000,
        media_type="audio/mp4",
    )
    transcription = Transcription(
        provider="whisper.cpp",
        segments=segments,
    )
    return AudioResult(source=source, transcription=transcription)


def test_validate_audio_result_success():
    audio = make_sample_audio_result()
    validate_audio_result(audio)  # Should not raise


def test_validate_audio_result_negative_timestamp():
    # Construct without Pydantic schema validation to test semantic validator
    segments = [
        TranscriptSegment.model_construct(
            id="S001", start_ms=-500, end_ms=4000, text="Invalid"
        ),
    ]
    audio = make_sample_audio_result(segments=segments)
    with pytest.raises(SemanticValidationError, match="negative start_ms"):
        validate_audio_result(audio)


def test_validate_audio_result_end_before_start():
    segments = [
        TranscriptSegment(id="S001", start_ms=5000, end_ms=4000, text="Invalid"),
    ]
    audio = make_sample_audio_result(segments=segments)
    with pytest.raises(
        SemanticValidationError, match="must be strictly greater than start_ms"
    ):
        validate_audio_result(audio)


def test_validate_audio_result_out_of_order():
    segments = [
        TranscriptSegment(id="S001", start_ms=10000, end_ms=12000, text="First"),
        TranscriptSegment(
            id="S002", start_ms=8000, end_ms=9000, text="Second (out of order)"
        ),
    ]
    audio = make_sample_audio_result(segments=segments)
    with pytest.raises(SemanticValidationError, match="out of chronological order"):
        validate_audio_result(audio)


def test_validate_audio_result_exceeds_duration():
    segments = [
        TranscriptSegment(id="S001", start_ms=1000, end_ms=70000, text="Too long"),
    ]
    audio = make_sample_audio_result(duration_ms=60000, segments=segments)
    with pytest.raises(SemanticValidationError, match="exceeds audio duration"):
        validate_audio_result(audio)


def test_validate_audio_result_duplicate_segment_id():
    segments = [
        TranscriptSegment(id="S001", start_ms=1000, end_ms=2000, text="A"),
        TranscriptSegment(id="S001", start_ms=3000, end_ms=4000, text="B"),
    ]
    audio = make_sample_audio_result(segments=segments)
    with pytest.raises(SemanticValidationError, match="Duplicate segment ID"):
        validate_audio_result(audio)


def test_evidence_integrity_success():
    audio = make_sample_audio_result()
    feedback = MentorFeedback(
        source_ref="a" * 64,
        feedback_items=[
            FeedbackItem(
                id="F001",
                category=FeedbackCategory.METHODOLOGY,
                type=FeedbackType.REVISION_REQUEST,
                evidence=[
                    EvidenceAnchor(
                        segment_id="S001",
                        quote="Metodologi penelitian harus diperbaiki",
                    )
                ],
                action="Clarify methodology steps",
            )
        ],
    )
    validate_feedback_integrity(feedback, audio)  # Should pass


def test_evidence_integrity_quote_mismatch_fails():
    audio = make_sample_audio_result()
    feedback = MentorFeedback(
        source_ref="a" * 64,
        feedback_items=[
            FeedbackItem(
                id="F001",
                category=FeedbackCategory.METHODOLOGY,
                type=FeedbackType.REVISION_REQUEST,
                # Quote does NOT exist in S001
                evidence=[
                    EvidenceAnchor(segment_id="S001", quote="Ini rumus salah total")
                ],
                action="Fix formula",
            )
        ],
    )
    with pytest.raises(EvidenceIntegrityError, match="not found verbatim in segment"):
        validate_feedback_integrity(feedback, audio)


def test_adjudication_validation_clarified_requires_notes():
    feedback = MentorFeedback(
        source_ref="a" * 64,
        feedback_items=[
            FeedbackItem(
                id="F001",
                category=FeedbackCategory.METHODOLOGY,
                type=FeedbackType.REVISION_REQUEST,
                evidence=[EvidenceAnchor(segment_id="S001", quote="Metodologi")],
                action="Action",
            )
        ],
    )
    adjudication = AuthorAdjudication(
        source_ref="a" * 64,
        feedback_ref="ref1",
        author=AuthorInfo(adjudicated_at="2026-11-05T00:00:00Z"),
        decisions=[
            AuthorDecisionItem(
                feedback_id="F001",
                decision="clarified",
                author_notes=None,
                clarified_action=None,  # Missing both notes and action!
            )
        ],
    )
    with pytest.raises(
        SemanticValidationError,
        match="neither clarified_action nor author_notes was provided",
    ):
        validate_adjudication(adjudication, feedback)
