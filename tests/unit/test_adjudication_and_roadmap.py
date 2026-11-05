"""Unit tests for author adjudication, roadmap generation, and ARS handoff adapter."""

from revisi_mudah.academic.adjudication import (
    apply_adjudication,
    extract_adjudicated_subsets,
)
from revisi_mudah.academic.ars_adapter import export_ars_revision_roadmap
from revisi_mudah.academic.roadmap import generate_implementation_plan
from revisi_mudah.core.contracts import (
    AdjudicationDecision,
    AudioResult,
    AudioSource,
    AuthorAdjudication,
    AuthorDecisionItem,
    AuthorInfo,
    EvidenceAnchor,
    FeedbackCategory,
    FeedbackItem,
    FeedbackStatus,
    FeedbackType,
    MentorFeedback,
    TargetLocation,
    Transcription,
    TranscriptSegment,
)


def make_test_environment():
    source = AudioSource(
        file="bimbingan.m4a",
        sha256="b" * 64,
        duration_ms=120000,
        file_size_bytes=1000000,
        media_type="audio/mp4",
    )
    segments = [
        TranscriptSegment(
            id="S001",
            start_ms=10000,
            end_ms=25000,
            text="Metodologi penelitian perlu diperjelas.",
        ),
        TranscriptSegment(
            id="S002",
            start_ms=30000,
            end_ms=45000,
            text="Grafik pada Bab IV kurang terbaca.",
        ),
        TranscriptSegment(
            id="S003",
            start_ms=50000,
            end_ms=60000,
            text="Minggu depan langsung daftar sidang.",
        ),
    ]
    audio = AudioResult(
        source=source, transcription=Transcription(provider="test", segments=segments)
    )

    feedback = MentorFeedback(
        source_ref="b" * 64,
        feedback_items=[
            FeedbackItem(
                id="F001",
                category=FeedbackCategory.METHODOLOGY,
                type=FeedbackType.REVISION_REQUEST,
                evidence=[
                    EvidenceAnchor(
                        segment_id="S001",
                        quote="Metodologi penelitian perlu diperjelas.",
                    )
                ],
                target=TargetLocation(chapter="BAB III"),
                action="Perjelas tahapan metodologi",
            ),
            FeedbackItem(
                id="F002",
                category=FeedbackCategory.ANALYSIS,
                type=FeedbackType.REVISION_REQUEST,
                evidence=[
                    EvidenceAnchor(
                        segment_id="S002", quote="Grafik pada Bab IV kurang terbaca."
                    )
                ],
                target=TargetLocation(chapter="BAB IV"),
                action="Perbaiki kontras dan resolusi grafik",
            ),
            FeedbackItem(
                id="F003",
                category=FeedbackCategory.ADMINISTRATIVE,
                type=FeedbackType.DEADLINE,
                evidence=[
                    EvidenceAnchor(
                        segment_id="S003", quote="Minggu depan langsung daftar sidang."
                    )
                ],
                action="Siapkan berkas pendaftaran sidang",
            ),
        ],
    )
    return audio, feedback


def test_adjudication_updates_status():
    _audio, feedback = make_test_environment()

    adjudication = AuthorAdjudication(
        source_ref="b" * 64,
        feedback_ref="FB-1",
        author=AuthorInfo(name="Student", adjudicated_at="2026-11-05T12:00:00Z"),
        decisions=[
            AuthorDecisionItem(
                feedback_id="F001", decision=AdjudicationDecision.ACCEPTED
            ),
            AuthorDecisionItem(
                feedback_id="F002",
                decision=AdjudicationDecision.REJECTED,
                author_notes="Dosen setuju pakai tabel.",
            ),
            AuthorDecisionItem(
                feedback_id="F003",
                decision=AdjudicationDecision.CLARIFIED,
                clarified_action="Daftar sidang setelah Bab 4 direview sekali lagi.",
            ),
        ],
    )

    updated = apply_adjudication(feedback, adjudication)
    accepted, rejected, pending = extract_adjudicated_subsets(updated)

    assert len(accepted) == 1
    assert accepted[0].id == "F001"
    assert accepted[0].status == FeedbackStatus.ACCEPTED

    assert len(rejected) == 1
    assert rejected[0].id == "F002"
    assert rejected[0].status == FeedbackStatus.REJECTED

    assert len(pending) == 1
    assert pending[0].id == "F003"
    assert pending[0].status == FeedbackStatus.CLARIFIED
    assert pending[0].action == "Daftar sidang setelah Bab 4 direview sekali lagi."


def test_roadmap_includes_only_accepted_tasks_with_execution_boundary():
    audio, feedback = make_test_environment()

    # Adjudicate: only F001 accepted
    adjudication = AuthorAdjudication(
        source_ref="b" * 64,
        feedback_ref="FB-1",
        author=AuthorInfo(name="Student", adjudicated_at="2026-11-05T12:00:00Z"),
        decisions=[
            AuthorDecisionItem(
                feedback_id="F001", decision=AdjudicationDecision.ACCEPTED
            ),
            AuthorDecisionItem(
                feedback_id="F002", decision=AdjudicationDecision.REJECTED
            ),
            AuthorDecisionItem(
                feedback_id="F003", decision=AdjudicationDecision.REJECTED
            ),
        ],
    )
    adjudicated_feedback = apply_adjudication(feedback, adjudication)

    plan_md = generate_implementation_plan(audio, adjudicated_feedback)

    # Verifications
    assert "# Academic Revision Implementation Plan" in plan_md
    assert "Status: Approved by Author" in plan_md
    assert "Methodology" in plan_md
    assert "F001" not in plan_md or "Methodology" in plan_md
    # F002 and F003 should NOT appear as accepted tasks
    assert "Grafik pada Bab IV kurang terbaca" not in plan_md

    # Execution Boundary MUST be present
    assert "## Execution Boundary" in plan_md
    assert "This document is an implementation plan only." in plan_md
    assert "No manuscript files were modified." in plan_md
    assert "No LaTeX or Typst patches were generated." in plan_md
    assert "No automatic revision was executed." in plan_md


def test_ars_adapter_export():
    audio, feedback = make_test_environment()
    adjudication = AuthorAdjudication(
        source_ref="b" * 64,
        feedback_ref="FB-1",
        author=AuthorInfo(adjudicated_at="2026-11-05T12:00:00Z"),
        decisions=[
            AuthorDecisionItem(
                feedback_id="F001", decision=AdjudicationDecision.ACCEPTED
            ),
            AuthorDecisionItem(
                feedback_id="F002", decision=AdjudicationDecision.REJECTED
            ),
            AuthorDecisionItem(
                feedback_id="F003", decision=AdjudicationDecision.REJECTED
            ),
        ],
    )
    adjudicated_feedback = apply_adjudication(feedback, adjudication)

    ars_payload = export_ars_revision_roadmap(audio, adjudicated_feedback)

    assert ars_payload["schema"] == "ars/revision-roadmap/1.0"
    assert ars_payload["adjudication_status"] == "author_approved"
    assert ars_payload["handoff_boundary"]["manuscript_modified"] is False
    assert ars_payload["handoff_boundary"]["patches_generated"] is False
    assert len(ars_payload["revision_tasks"]) == 1
    assert ars_payload["revision_tasks"][0]["task_id"] == "F001"
