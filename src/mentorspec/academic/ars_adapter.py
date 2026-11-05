"""Handoff adapter for Academic Research Skills (ARS).

Per MentorSpec architectural boundary:
This adapter exports a handoff document only.
It does NOT execute ARS Revision Mode #390 and does NOT modify any manuscript files.
"""

from __future__ import annotations

from typing import Any

from mentorspec.core.contracts import (
    AudioResult,
    FeedbackItem,
    FeedbackStatus,
    MentorFeedback,
)
from mentorspec.core.validator import validate_audio_result, validate_feedback_integrity


def export_ars_revision_roadmap(
    audio: AudioResult, feedback: MentorFeedback
) -> dict[str, Any]:
    """
    Export an approved MentorSpec feedback set to an ARS-compatible Revision Roadmap data structure.
    Only items with status 'accepted' are exported.
    """
    validate_audio_result(audio)
    validate_feedback_integrity(feedback, audio)

    accepted_items: list[FeedbackItem] = [
        item
        for item in feedback.feedback_items
        if item.status == FeedbackStatus.ACCEPTED
    ]

    tasks = []
    for item in accepted_items:
        quotes = [ev.quote for ev in item.evidence]
        tasks.append(
            {
                "task_id": item.id,
                "category": item.category.value,
                "type": item.type.value,
                "target": {
                    "chapter": item.target.chapter if item.target else None,
                    "section": item.target.section if item.target else None,
                },
                "supervisor_feedback": quotes,
                "action": item.action,
                "author_decision": "accepted",
                "ars_obligation": "mandatory"
                if item.type.value in ["revision_request", "decision"]
                else "advisory",
            }
        )

    return {
        "schema": "ars/revision-roadmap/1.0",
        "provenance": {
            "source_type": "mentorspec_audio_distillation",
            "source_audio_file": audio.source.file,
            "source_audio_sha256": audio.source.sha256,
            "mentorspec_version": "mentorspec/1.0",
        },
        "adjudication_status": "author_approved",
        "handoff_boundary": {
            "execution_mode": "manual_or_ars_external",
            "manuscript_modified": False,
            "patches_generated": False,
        },
        "revision_tasks": tasks,
    }
