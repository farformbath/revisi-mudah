"""Regression tests for robust JSON extraction from language model outputs."""

import pytest

from revisi_mudah.academic.extraction import extract_json_payload


def test_extract_json_raw():
    raw = '{"feedback_items": [{"id": "F001"}]}'
    result = extract_json_payload(raw)
    assert result == {"feedback_items": [{"id": "F001"}]}


def test_extract_json_fenced_markdown():
    fenced = """```json
    {
      "feedback_items": [{"id": "F001"}]
    }
    ```"""
    result = extract_json_payload(fenced)
    assert "feedback_items" in result
    assert result["feedback_items"][0]["id"] == "F001"


def test_extract_json_preamble_and_postamble():
    content = """Sure! Here is the structured supervisor feedback you requested:

    ```json
    {
      "feedback_items": [{"id": "F001", "action": "Add F1 metric"}]
    }
    ```

    Please let me know if you need any adjustments!"""
    result = extract_json_payload(content)
    assert result["feedback_items"][0]["action"] == "Add F1 metric"


def test_extract_json_unfenced_with_preamble():
    content = 'Note from model: {"feedback_items": [{"id": "F001"}]} done.'
    result = extract_json_payload(content)
    assert result["feedback_items"][0]["id"] == "F001"


def test_extract_json_handles_curly_braces_in_strings():
    content = '{"feedback_items": [{"id": "F001", "action": "Use template {variable_name} in section 3."}]}'
    result = extract_json_payload(content)
    assert (
        result["feedback_items"][0]["action"]
        == "Use template {variable_name} in section 3."
    )


def test_extract_json_rejects_empty():
    with pytest.raises(ValueError, match="Received empty or whitespace-only response"):
        extract_json_payload("")
    with pytest.raises(ValueError, match="Received empty or whitespace-only response"):
        extract_json_payload("   \n\t  ")


def test_extract_json_rejects_truncated():
    truncated = '{"feedback_items": [{"id": "F001", "action": "Incomplete'
    with pytest.raises(ValueError, match="No valid JSON object found"):
        extract_json_payload(truncated)


def test_extract_json_rejects_ambiguous_multiple_roots():
    ambiguous = (
        '{"feedback_items": [{"id": "F001"}]} and {"feedback_items": [{"id": "F002"}]}'
    )
    with pytest.raises(
        ValueError, match="Ambiguous response: multiple root JSON objects found"
    ):
        extract_json_payload(ambiguous)
