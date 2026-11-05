"""Deterministic tool implementations for MentorSpec MCP server."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mentorspec.academic.adjudication import apply_adjudication
from mentorspec.academic.ars_adapter import export_ars_revision_roadmap
from mentorspec.academic.extraction import parse_extracted_feedback
from mentorspec.academic.roadmap import generate_implementation_plan
from mentorspec.audio.inspect import inspect_audio
from mentorspec.core.contracts import AudioResult, AuthorAdjudication, MentorFeedback
from mentorspec.core.policy import CloudUploadConsent, PrivacyPolicy
from mentorspec.core.router import AudioRouter


def tool_audio_inspect(audio_path: str) -> dict[str, Any]:
    """Inspect local audio file and return its provenance metadata and SHA-256 digest."""
    path = Path(audio_path).resolve()
    source = inspect_audio(path)
    return source.model_dump()


def tool_audio_transcribe(
    audio_path: str, cloud_consent: str = "ask"
) -> dict[str, Any]:
    """
    Transcribe audio file through the capability router respecting privacy policies.
    cloud_consent can be 'ask', 'allow', or 'deny'.
    """
    path = Path(audio_path).resolve()
    consent_enum = CloudUploadConsent(cloud_consent.lower())
    policy = PrivacyPolicy(cloud_upload=consent_enum)
    router = AudioRouter(policy=policy)

    audio_result = router.process_audio(path)
    return audio_result.model_dump(by_alias=True)


def tool_academic_extract_feedback(
    audio_result_data: str | dict[str, Any], raw_llm_json: str
) -> dict[str, Any]:
    """
    Parse and validate LLM-extracted supervisor feedback against the audio transcript.
    Enforces evidence integrity (quotes must exist in referenced segments).
    """
    if isinstance(audio_result_data, str):
        audio_dict = json.loads(audio_result_data)
    else:
        audio_dict = audio_result_data

    audio = AudioResult.model_validate(audio_dict)
    feedback = parse_extracted_feedback(raw_llm_json, audio)
    return feedback.model_dump(by_alias=True)


def tool_academic_adjudicate(
    feedback_data: str | dict[str, Any],
    adjudication_data: str | dict[str, Any],
) -> dict[str, Any]:
    """
    Apply author adjudication (accepted, rejected, clarified) to feedback items.
    """
    if isinstance(feedback_data, str):
        fb_dict = json.loads(feedback_data)
    else:
        fb_dict = feedback_data

    if isinstance(adjudication_data, str):
        adj_dict = json.loads(adjudication_data)
    else:
        adj_dict = adjudication_data

    feedback = MentorFeedback.model_validate(fb_dict)
    adjudication = AuthorAdjudication.model_validate(adj_dict)

    updated_feedback = apply_adjudication(feedback, adjudication)
    return updated_feedback.model_dump(by_alias=True)


def tool_academic_build_roadmap(
    audio_result_data: str | dict[str, Any],
    feedback_data: str | dict[str, Any],
) -> str:
    """
    Generate markdown Academic Revision Implementation Plan for accepted feedback items only.
    Contains strict execution boundaries (no file mutation).
    """
    if isinstance(audio_result_data, str):
        audio_dict = json.loads(audio_result_data)
    else:
        audio_dict = audio_result_data

    if isinstance(feedback_data, str):
        fb_dict = json.loads(feedback_data)
    else:
        fb_dict = feedback_data

    audio = AudioResult.model_validate(audio_dict)
    feedback = MentorFeedback.model_validate(fb_dict)

    return generate_implementation_plan(audio, feedback)


def tool_academic_export_ars(
    audio_result_data: str | dict[str, Any],
    feedback_data: str | dict[str, Any],
) -> dict[str, Any]:
    """
    Export accepted feedback into an ARS-compatible Revision Roadmap handoff structure.
    Does NOT execute revision mode or alter any thesis files.
    """
    if isinstance(audio_result_data, str):
        audio_dict = json.loads(audio_result_data)
    else:
        audio_dict = audio_result_data

    if isinstance(feedback_data, str):
        fb_dict = json.loads(feedback_data)
    else:
        fb_dict = feedback_data

    audio = AudioResult.model_validate(audio_dict)
    feedback = MentorFeedback.model_validate(fb_dict)

    return export_ars_revision_roadmap(audio, feedback)
