"""Evidence mapping and timestamp formatting utilities."""

from __future__ import annotations

import re

from revisi_mudah.core.contracts import TranscriptSegment


def ms_to_timestamp(ms: int) -> str:
    """Convert millisecond timestamp to HH:MM:SS format."""
    total_seconds = max(0, ms // 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_evidence_range(start_ms: int, end_ms: int) -> str:
    """Format start and end milliseconds as a human-readable range, e.g. 00:12:30–00:12:46."""
    return f"{ms_to_timestamp(start_ms)}–{ms_to_timestamp(end_ms)}"


def find_matching_segment(
    quote: str, segments: list[TranscriptSegment]
) -> tuple[str, int, int] | None:
    """
    Search for a verbatim quote across a list of segments.
    Returns (segment_id, start_ms, end_ms) if found, or None.
    """
    norm_quote = re.sub(r"\s+", " ", quote.strip().lower())
    for seg in segments:
        norm_text = re.sub(r"\s+", " ", seg.text.strip().lower())
        if norm_quote in norm_text:
            return seg.id, seg.start_ms, seg.end_ms
    return None
