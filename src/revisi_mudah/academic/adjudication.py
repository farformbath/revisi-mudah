"""Author adjudication application logic."""

from __future__ import annotations

from revisi_mudah.core.contracts import (
    AdjudicationDecision,
    AuthorAdjudication,
    FeedbackItem,
    FeedbackStatus,
    MentorFeedback,
)
from revisi_mudah.core.validator import validate_adjudication


def apply_adjudication(
    feedback: MentorFeedback, adjudication: AuthorAdjudication
) -> MentorFeedback:
    """
    Apply an AuthorAdjudication onto a MentorFeedback artifact.
    Updates each feedback item status to accepted, rejected, or clarified.
    """
    validate_adjudication(adjudication, feedback)

    decision_map = {d.feedback_id: d for d in adjudication.decisions}
    updated_items: list[FeedbackItem] = []

    for item in feedback.feedback_items:
        if item.id in decision_map:
            d = decision_map[item.id]
            if d.decision == AdjudicationDecision.ACCEPTED:
                new_status = FeedbackStatus.ACCEPTED
                action = item.action
            elif d.decision == AdjudicationDecision.REJECTED:
                new_status = FeedbackStatus.REJECTED
                action = item.action
            else:  # CLARIFIED
                new_status = FeedbackStatus.CLARIFIED
                action = d.clarified_action if d.clarified_action else item.action

            ambiguity = (
                f"Author note: {d.author_notes}" if d.author_notes else item.ambiguity
            )

            updated_item = FeedbackItem(
                id=item.id,
                category=item.category,
                type=item.type,
                evidence=item.evidence,
                target=item.target,
                action=action,
                ambiguity=ambiguity,
                status=new_status,
            )
            updated_items.append(updated_item)
        else:
            updated_items.append(item)

    return MentorFeedback(
        schema=feedback.schema_version,
        source_ref=feedback.source_ref,
        extraction_metadata=feedback.extraction_metadata,
        feedback_items=updated_items,
    )


def extract_adjudicated_subsets(
    feedback: MentorFeedback,
) -> tuple[list[FeedbackItem], list[FeedbackItem], list[FeedbackItem]]:
    """
    Separate feedback items into (accepted, rejected, unadjudicated_or_clarified).
    Only accepted items are eligible for implementation plan inclusion.
    """
    accepted: list[FeedbackItem] = []
    rejected: list[FeedbackItem] = []
    pending_or_clarified: list[FeedbackItem] = []

    for item in feedback.feedback_items:
        if item.status == FeedbackStatus.ACCEPTED:
            accepted.append(item)
        elif item.status == FeedbackStatus.REJECTED:
            rejected.append(item)
        else:
            pending_or_clarified.append(item)

    return accepted, rejected, pending_or_clarified
