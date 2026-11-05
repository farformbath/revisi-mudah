"""Roadmap and Implementation Plan generator for Revisi Mudah."""

from __future__ import annotations

from revisi_mudah.academic.evidence import format_evidence_range
from revisi_mudah.core.contracts import (
    AudioResult,
    FeedbackItem,
    FeedbackStatus,
    MentorFeedback,
)
from revisi_mudah.core.validator import (
    validate_audio_result,
    validate_feedback_integrity,
)


def _infer_expected_outcome(item: FeedbackItem) -> str:
    """Generate professional expected outcome text based on feedback category and action."""
    cat = item.category.value
    if cat == "methodology":
        return "A clearer, rigorous, and internally consistent research methodology."
    elif cat == "data":
        return "Validated datasets and transparent data-handling procedures."
    elif cat == "formula":
        return "Mathematically verified formulas and standardized algorithmic notation."
    elif cat == "analysis":
        return "Accurate comparative interpretation and validated evaluation metrics."
    elif cat == "citation":
        return "Compliant, verified references with active DOIs and current scholarly sources."
    elif cat == "administrative":
        return (
            "Prepared administrative checklist and milestones for defense registration."
        )
    elif cat == "structure":
        return "Cohesive chapter organization adhering to thesis guidelines."
    elif cat == "editorial":
        return "Professional academic tone with corrected terminology and typographical fixes."
    return f"Resolution of supervisor directive regarding {cat}."


def generate_implementation_plan(audio: AudioResult, feedback: MentorFeedback) -> str:
    """
    Generate the formal Academic Revision Implementation Plan markdown.
    Adheres strictly to the MentorSpec execution boundary (planning only).
    """
    validate_audio_result(audio)
    validate_feedback_integrity(feedback, audio)

    # Build segment map for timestamp lookups
    segment_map = {seg.id: seg for seg in audio.transcription.segments}

    # Filter only accepted items
    accepted_items: list[FeedbackItem] = [
        item
        for item in feedback.feedback_items
        if item.status == FeedbackStatus.ACCEPTED
    ]

    lines = [
        "# Academic Revision Implementation Plan",
        f"Source: {audio.source.file}",
        f"Schema: {feedback.schema_version}",
        "Status: Approved by Author",
        "",
    ]

    if not accepted_items:
        lines.append(
            "*(No feedback items have been approved by the author yet. Adjudication required.)*"
        )
        lines.append("")
    else:
        for idx, item in enumerate(accepted_items, start=1):
            category_title = item.category.value.capitalize()
            target_str = ""
            if item.target and item.target.chapter:
                target_str = f" ({item.target.chapter}"
                if item.target.section:
                    target_str += f", {item.target.section}"
                target_str += ")"

            lines.append(f"## {idx}. {category_title}{target_str}")
            lines.append("Priority: High")

            # Determine timestamp range from evidence segments
            evidence_ranges = []
            quotes = []
            for ev in item.evidence:
                if ev.segment_id in segment_map:
                    seg = segment_map[ev.segment_id]
                    evidence_ranges.append(
                        format_evidence_range(seg.start_ms, seg.end_ms)
                    )
                quotes.append(ev.quote)

            evidence_str = (
                ", ".join(evidence_ranges) if evidence_ranges else "Recorded Audio"
            )
            lines.append(f"Source Evidence: {evidence_str}")
            lines.append("Author Decision: Accepted")
            lines.append("")

            lines.append("Supervisor Feedback:")
            for q in quotes:
                lines.append(f'> "{q}"')
            lines.append("")

            lines.append("Implementation Tasks:")
            # Split action into clean bullet points if multi-step or format cleanly
            action_steps = [s.strip() for s in item.action.split("\n") if s.strip()]
            for step in action_steps:
                if step.startswith(("- ", "* ")):
                    lines.append(step)
                else:
                    lines.append(f"- {step}")
            lines.append("")

            outcome = _infer_expected_outcome(item)
            lines.append("Expected Outcome:")
            lines.append(outcome)
            lines.append("")
            lines.append("---")
            lines.append("")

    # Mandatory Execution Boundary per specification
    lines.extend(
        [
            "## Execution Boundary",
            "This document is an implementation plan only.",
            "- No manuscript files were modified.",
            "- No LaTeX or Typst patches were generated.",
            "- No automatic revision was executed.",
            "- All implementation tasks remain under the author's control.",
        ]
    )

    return "\n".join(lines)
