"""Pydantic data contracts for Revisi Mudah v1.0."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FeedbackCategory(str, Enum):
    METHODOLOGY = "methodology"
    THEORY = "theory"
    DATA = "data"
    ANALYSIS = "analysis"
    FORMULA = "formula"
    CITATION = "citation"
    STRUCTURE = "structure"
    EDITORIAL = "editorial"
    ADMINISTRATIVE = "administrative"


class FeedbackType(str, Enum):
    REVISION_REQUEST = "revision_request"
    QUESTION = "question"
    SUGGESTION = "suggestion"
    APPROVAL = "approval"
    ADMINISTRATIVE_INSTRUCTION = "administrative_instruction"
    DECISION = "decision"
    DEADLINE = "deadline"


class FeedbackStatus(str, Enum):
    NEEDS_AUTHOR_REVIEW = "needs_author_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CLARIFIED = "clarified"


class AdjudicationDecision(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CLARIFIED = "clarified"


# ==============================================================================
# Audio Result Models
# ==============================================================================


class AudioSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file: str = Field(
        ..., description="Relative audio filename, without directory paths."
    )
    sha256: str = Field(
        ...,
        pattern=r"^[a-f0-9]{64}$",
        description="64-character lowercase SHA-256 hash.",
    )
    duration_ms: int = Field(..., ge=0, description="Duration in milliseconds.")
    file_size_bytes: int = Field(..., ge=0, description="File size in bytes.")
    media_type: str = Field(
        ..., pattern=r"^audio/.+", description="MIME type, e.g. audio/mp4."
    )

    @field_validator("file")
    @classmethod
    def validate_relative_filename(cls, v: str) -> str:
        if "/" in v or "\\" in v:
            raise ValueError(
                f"File name must be relative and contain no path separators: {v}"
            )
        return v


class TranscriptSegment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        ..., pattern=r"^S[0-9]+$", description="Segment identifier, e.g. S001."
    )
    start_ms: int = Field(..., ge=0, description="Start time in milliseconds.")
    end_ms: int = Field(..., ge=0, description="End time in milliseconds.")
    speaker: str | None = Field(
        default=None, description="Speaker name/label, or None."
    )
    text: str = Field(..., description="Verbatim text.")
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class Transcription(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str
    model: str | None = "unknown"
    language: str = "id"
    segments: list[TranscriptSegment] = Field(default_factory=list)


class AudioResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(default="mentorspec/1.0", alias="schema")
    source: AudioSource
    transcription: Transcription


# ==============================================================================
# Feedback Models
# ==============================================================================


class EvidenceAnchor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    segment_id: str = Field(..., pattern=r"^S[0-9]+$")
    quote: str = Field(
        ..., min_length=1, description="Verbatim quote from the segment."
    )


class TargetLocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chapter: str | None = None
    section: str | None = None


class FeedbackItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., pattern=r"^F[0-9]+$")
    category: FeedbackCategory
    type: FeedbackType
    evidence: list[EvidenceAnchor] = Field(..., min_length=1)
    target: TargetLocation | None = None
    action: str = Field(..., min_length=1)
    ambiguity: str | None = None
    status: FeedbackStatus = Field(default=FeedbackStatus.NEEDS_AUTHOR_REVIEW)


class ExtractionMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")

    extractor_model: str | None = None
    extracted_at: str | None = None


class MentorFeedback(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(default="mentorspec/1.0", alias="schema")
    source_ref: str = Field(..., pattern=r"^[a-f0-9]{64}$")
    extraction_metadata: ExtractionMetadata | None = None
    feedback_items: list[FeedbackItem] = Field(default_factory=list)


# ==============================================================================
# Adjudication Models
# ==============================================================================


class AuthorInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    adjudicated_at: str


class AuthorDecisionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    feedback_id: str = Field(..., pattern=r"^F[0-9]+$")
    decision: AdjudicationDecision
    author_notes: str | None = None
    clarified_action: str | None = None


class AuthorAdjudication(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(default="mentorspec/1.0", alias="schema")
    source_ref: str = Field(..., pattern=r"^[a-f0-9]{64}$")
    feedback_ref: str
    author: AuthorInfo
    decisions: list[AuthorDecisionItem] = Field(..., min_length=1)
