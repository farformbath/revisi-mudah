"""Contract tests validating against JSON Schema definitions."""

import pytest

from mentorspec.core.validator import ValidationError, validate_against_json_schema


def test_audio_result_schema_valid():
    valid_data = {
        "schema": "mentorspec/1.0",
        "source": {
            "file": "bimbingan.m4a",
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "duration_ms": 3600000,
            "file_size_bytes": 12500000,
            "media_type": "audio/mp4",
        },
        "transcription": {
            "provider": "whisper.cpp",
            "model": "ggml-base.bin",
            "language": "id",
            "segments": [
                {
                    "id": "S001",
                    "start_ms": 120000,
                    "end_ms": 136000,
                    "speaker": "supervisor_1",
                    "text": "Metodologi penelitian perlu diperjelas.",
                    "confidence": 0.95,
                }
            ],
        },
    }
    validate_against_json_schema(valid_data, "audio-result.schema.json")


def test_audio_result_schema_rejects_absolute_path():
    invalid_data = {
        "schema": "mentorspec/1.0",
        "source": {
            "file": "C:/Users/LOQ/bimbingan.m4a",  # Path separator forbidden
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "duration_ms": 3600000,
            "file_size_bytes": 12500000,
            "media_type": "audio/mp4",
        },
        "transcription": {"provider": "whisper.cpp", "language": "id", "segments": []},
    }
    with pytest.raises(ValidationError):
        validate_against_json_schema(invalid_data, "audio-result.schema.json")


def test_feedback_schema_valid():
    valid_data = {
        "schema": "mentorspec/1.0",
        "source_ref": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "feedback_items": [
            {
                "id": "F001",
                "category": "methodology",
                "type": "revision_request",
                "evidence": [
                    {
                        "segment_id": "S001",
                        "quote": "Metodologi penelitian perlu diperjelas.",
                    }
                ],
                "target": {"chapter": "BAB III", "section": "3.2"},
                "action": "Clarify research methodology steps.",
                "ambiguity": None,
                "status": "needs_author_review",
            }
        ],
    }
    validate_against_json_schema(valid_data, "feedback.schema.json")


def test_adjudication_schema_valid():
    valid_data = {
        "schema": "mentorspec/1.0",
        "source_ref": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "feedback_ref": "FB-20261105",
        "author": {"name": "Student Author", "adjudicated_at": "2026-11-05T12:00:00Z"},
        "decisions": [
            {
                "feedback_id": "F001",
                "decision": "accepted",
                "author_notes": "Will clarify in section 3.2.",
            }
        ],
    }
    validate_against_json_schema(valid_data, "adjudication.schema.json")
