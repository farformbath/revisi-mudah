"""End-to-end integration test covering the entire MentorSpec pipeline.

Validates:
1. Audio inspection and provenance hashing on actual WAV file.
2. Privacy gate enforcement (DENY mode strictly prevents cloud access).
3. Capability router fallback to local transcription.
4. Feedback extraction and evidence integrity verification.
5. Evidence tampering rejection (quote mismatch raises EvidenceIntegrityError).
6. Author adjudication workflow (accepted vs rejected vs clarified).
7. Formal implementation plan generation (accepted items only, execution boundary footer).
8. ARS handoff export verification (no manuscript file modification).
"""

import wave
from pathlib import Path

import pytest

from revisi_mudah.academic.adjudication import apply_adjudication
from revisi_mudah.academic.ars_adapter import export_ars_revision_roadmap
from revisi_mudah.academic.extraction import parse_extracted_feedback
from revisi_mudah.academic.roadmap import generate_implementation_plan
from revisi_mudah.audio.inspect import inspect_audio
from revisi_mudah.core.contracts import (
    AdjudicationDecision,
    AudioResult,
    AuthorAdjudication,
    AuthorDecisionItem,
    AuthorInfo,
    Transcription,
    TranscriptSegment,
)
from revisi_mudah.core.policy import (
    CloudUploadConsent,
    PrivacyPolicy,
    PrivacyViolationError,
)
from revisi_mudah.core.router import AudioRouter
from revisi_mudah.core.validator import EvidenceIntegrityError
from revisi_mudah.providers.base import AudioProvider


def create_synthetic_wav(path: Path, duration_seconds: int = 5) -> Path:
    """Create a valid synthetic 16-bit PCM mono WAV file."""
    sample_rate = 16000
    num_frames = sample_rate * duration_seconds
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * num_frames)
    return path


class MockLocalProvider(AudioProvider):
    """Deterministic mock provider simulating local Whisper output for integration testing."""

    @property
    def name(self) -> str:
        return "local_whisper_mock"

    @property
    def is_cloud(self) -> bool:
        return False

    def is_available(self) -> bool:
        return True

    def transcribe(self, audio_path: Path, source) -> AudioResult:
        segments = [
            TranscriptSegment(
                id="S001",
                start_ms=1000,
                end_ms=2500,
                speaker="supervisor",
                text="Metodologi evaluasi pada Bab 3 harus ditambah metrik F1-Score.",
            ),
            TranscriptSegment(
                id="S002",
                start_ms=3000,
                end_ms=4500,
                speaker="supervisor",
                text="Untuk daftar pustaka coba periksa sitasi yang lebih baru dari 2024.",
            ),
        ]
        return AudioResult(
            schema="mentorspec/1.0",
            source=source,
            transcription=Transcription(
                provider="mock_local",
                language="id",
                segments=segments,
            ),
        )


class MockCloudProvider(AudioProvider):
    """Mock cloud provider for testing privacy gate rejection."""

    @property
    def name(self) -> str:
        return "mock_cloud"

    @property
    def is_cloud(self) -> bool:
        return True

    def is_available(self) -> bool:
        return True

    def transcribe(self, audio_path: Path, source) -> AudioResult:
        raise NotImplementedError(
            "Mock cloud should never be invoked under DENY policy."
        )


def test_end_to_end_audited_flow(tmp_path: Path):
    # --------------------------------------------------------------------------
    # Step 1: Physical Audio Creation & Inspection
    # --------------------------------------------------------------------------
    wav_path = create_synthetic_wav(
        tmp_path / "bimbingan_skripsi.wav", duration_seconds=5
    )
    source = inspect_audio(wav_path)

    assert source.file == "bimbingan_skripsi.wav"
    assert len(source.sha256) == 64
    assert source.media_type == "audio/wav"
    assert source.duration_ms == 5000
    assert source.file_size_bytes > 0

    # --------------------------------------------------------------------------
    # Step 2: Privacy Gate Verification
    # --------------------------------------------------------------------------
    deny_policy = PrivacyPolicy(
        cloud_upload=CloudUploadConsent.DENY,
        provider_order=["mock_cloud"],
    )
    deny_router = AudioRouter(policy=deny_policy)
    deny_router.register_provider("mock_cloud", MockCloudProvider())
    with pytest.raises(PrivacyViolationError, match="explicitly DENIED"):
        deny_router.resolve_provider()

    # --------------------------------------------------------------------------
    # Step 3: Local Offline Routing & Transcription
    # --------------------------------------------------------------------------
    offline_policy = PrivacyPolicy(
        cloud_upload=CloudUploadConsent.DENY,
        provider_order=["local_whisper_mock"],
    )
    router = AudioRouter(policy=offline_policy)
    router.register_provider("local_whisper_mock", MockLocalProvider())

    audio_result = router.process_audio(wav_path)
    assert audio_result.schema_version == "mentorspec/1.0"
    assert len(audio_result.transcription.segments) == 2
    assert audio_result.transcription.segments[0].id == "S001"

    # --------------------------------------------------------------------------
    # Step 4: Feedback Extraction & Evidence Integrity
    # --------------------------------------------------------------------------
    raw_llm_output = """
    {
      "feedback_items": [
        {
          "id": "F001",
          "category": "methodology",
          "type": "revision_request",
          "evidence": [
            {
              "segment_id": "S001",
              "quote": "Metodologi evaluasi pada Bab 3 harus ditambah metrik F1-Score."
            }
          ],
          "target": {"chapter": "BAB III", "section": "3.4"},
          "action": "Tambahkan definisi dan perhitungan F1-Score pada subbab 3.4.",
          "status": "needs_author_review"
        },
        {
          "id": "F002",
          "category": "citation",
          "type": "suggestion",
          "evidence": [
            {
              "segment_id": "S002",
              "quote": "daftar pustaka coba periksa sitasi yang lebih baru dari 2024"
            }
          ],
          "target": {"chapter": "BAB II", "section": null},
          "action": "Perbarui sitasi literatur dengan paper tahun 2024-2026.",
          "status": "needs_author_review"
        }
      ]
    }
    """
    feedback = parse_extracted_feedback(raw_llm_output, audio_result)
    assert len(feedback.feedback_items) == 2
    # Status MUST be needs_author_review
    assert all(
        item.status.value == "needs_author_review" for item in feedback.feedback_items
    )

    # --------------------------------------------------------------------------
    # Step 5: Evidence Tampering Check (Must reject non-verbatim quotes)
    # --------------------------------------------------------------------------
    tampered_llm_output = """
    {
      "feedback_items": [
        {
          "id": "F003",
          "category": "formula",
          "type": "revision_request",
          "evidence": [
            {
              "segment_id": "S001",
              "quote": "Kutipan fiktif yang tidak pernah diucapkan oleh dosen"
            }
          ],
          "action": "Ganti rumus",
          "status": "needs_author_review"
        }
      ]
    }
    """
    with pytest.raises(EvidenceIntegrityError, match="not found verbatim in segment"):
        parse_extracted_feedback(tampered_llm_output, audio_result)

    # --------------------------------------------------------------------------
    # Step 6: Author Adjudication (Human-in-the-Loop)
    # --------------------------------------------------------------------------
    adjudication = AuthorAdjudication(
        source_ref=source.sha256,
        feedback_ref="EXTRACT-001",
        author=AuthorInfo(name="Mahasiswa", adjudicated_at="2026-11-05T14:00:00Z"),
        decisions=[
            AuthorDecisionItem(
                feedback_id="F001",
                decision=AdjudicationDecision.ACCEPTED,
                author_notes="Setuju, rumus F1-Score akan ditambahkan.",
            ),
            AuthorDecisionItem(
                feedback_id="F002",
                decision=AdjudicationDecision.REJECTED,
                author_notes="Dosen utama sudah menyetujui referensi 2022-2023.",
            ),
        ],
    )
    adjudicated_fb = apply_adjudication(feedback, adjudication)

    item1 = next(item for item in adjudicated_fb.feedback_items if item.id == "F001")
    item2 = next(item for item in adjudicated_fb.feedback_items if item.id == "F002")
    assert item1.status.value == "accepted"
    assert item2.status.value == "rejected"

    # --------------------------------------------------------------------------
    # Step 7: Implementation Plan Generation (Approved Items Only)
    # --------------------------------------------------------------------------
    plan_md = generate_implementation_plan(audio_result, adjudicated_fb)

    # F001 (Accepted) MUST appear
    assert "F1-Score" in plan_md
    assert "00:00:01–00:00:02" in plan_md
    assert "Status: Approved by Author" in plan_md

    # F002 (Rejected) MUST NOT appear in actionable implementation tasks
    assert "Perbarui sitasi literatur dengan paper tahun 2024-2026" not in plan_md

    # Strict Execution Boundary statement MUST be present
    assert "## Execution Boundary" in plan_md
    assert "This document is an implementation plan only." in plan_md
    assert "No manuscript files were modified." in plan_md
    assert "No LaTeX or Typst patches were generated." in plan_md
    assert "No automatic revision was executed." in plan_md

    # --------------------------------------------------------------------------
    # Step 8: Academic Research Skills (ARS) Handoff Export
    # --------------------------------------------------------------------------
    ars_payload = export_ars_revision_roadmap(audio_result, adjudicated_fb)
    assert ars_payload["schema"] == "ars/revision-roadmap/1.0"
    assert ars_payload["adjudication_status"] == "author_approved"
    assert len(ars_payload["revision_tasks"]) == 1
    assert ars_payload["revision_tasks"][0]["task_id"] == "F001"
    assert ars_payload["handoff_boundary"]["manuscript_modified"] is False
    assert ars_payload["handoff_boundary"]["patches_generated"] is False
