"""Smoke tests for MentorSpec MCP tools."""

from revisi_mudah.mcp.tools import (
    tool_academic_adjudicate,
    tool_academic_build_roadmap,
    tool_academic_export_ars,
    tool_academic_extract_feedback,
    tool_audio_inspect,
)


def test_mcp_tools_pipeline(tmp_path):
    # 1. Create a mock audio file
    fake_audio = tmp_path / "bimbingan_test.m4a"
    fake_audio.write_bytes(b"dummy audio data for testing")

    # 2. Test inspect tool
    inspect_res = tool_audio_inspect(str(fake_audio))
    assert inspect_res["file"] == "bimbingan_test.m4a"
    assert len(inspect_res["sha256"]) == 64

    # 3. Test extract feedback tool
    audio_result = {
        "schema": "mentorspec/1.0",
        "source": inspect_res,
        "transcription": {
            "provider": "test",
            "language": "id",
            "segments": [
                {
                    "id": "S001",
                    "start_ms": 1000,
                    "end_ms": 5000,
                    "text": "Metodologi evaluasi perlu diperbaiki.",
                }
            ],
        },
    }

    raw_llm_json = """
    {
      "feedback_items": [
        {
          "id": "F001",
          "category": "methodology",
          "type": "revision_request",
          "evidence": [
            {
              "segment_id": "S001",
              "quote": "Metodologi evaluasi perlu diperbaiki."
            }
          ],
          "target": {"chapter": "BAB III", "section": "3.4"},
          "action": "Tambahkan metrik evaluasi F1-Score dan AUC-ROC.",
          "ambiguity": null,
          "status": "needs_author_review"
        }
      ]
    }
    """
    feedback_res = tool_academic_extract_feedback(audio_result, raw_llm_json)
    assert len(feedback_res["feedback_items"]) == 1
    assert feedback_res["feedback_items"][0]["status"] == "needs_author_review"

    # 4. Test adjudicate tool
    adjudication_data = {
        "schema": "mentorspec/1.0",
        "source_ref": inspect_res["sha256"],
        "feedback_ref": "FB-001",
        "author": {"name": "Far", "adjudicated_at": "2026-11-05T12:00:00Z"},
        "decisions": [
            {
                "feedback_id": "F001",
                "decision": "accepted",
                "author_notes": "Setuju dengan dosen",
            }
        ],
    }
    adjudicated_fb = tool_academic_adjudicate(feedback_res, adjudication_data)
    assert adjudicated_fb["feedback_items"][0]["status"] == "accepted"

    # 5. Test build roadmap tool
    roadmap_md = tool_academic_build_roadmap(audio_result, adjudicated_fb)
    assert "# Academic Revision Implementation Plan" in roadmap_md
    assert "F1-Score dan AUC-ROC" in roadmap_md
    assert "## Execution Boundary" in roadmap_md

    # 6. Test ARS export tool
    ars_data = tool_academic_export_ars(audio_result, adjudicated_fb)
    assert ars_data["schema"] == "ars/revision-roadmap/1.0"
    assert len(ars_data["revision_tasks"]) == 1
    assert ars_data["handoff_boundary"]["manuscript_modified"] is False
