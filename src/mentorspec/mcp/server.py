"""MentorSpec MCP Server implementation using Python MCP SDK."""

from __future__ import annotations

import asyncio
from typing import Any

from mcp.server.mcpserver import MCPServer

from mentorspec.mcp.tools import (
    tool_academic_adjudicate,
    tool_academic_build_roadmap,
    tool_academic_export_ars,
    tool_academic_extract_feedback,
    tool_audio_inspect,
    tool_audio_transcribe,
)

server = MCPServer("mentorspec")


@server.tool(name="audio_inspect")
def audio_inspect(audio_path: str) -> dict[str, Any]:
    """Inspect local audio file and return provenance metadata (SHA-256, duration, size, media_type)."""
    return tool_audio_inspect(audio_path)


@server.tool(name="audio_transcribe")
def audio_transcribe(audio_path: str, cloud_consent: str = "ask") -> dict[str, Any]:
    """
    Transcribe audio file through capability router with privacy gating.
    cloud_consent can be 'ask', 'allow', or 'deny'.
    """
    return tool_audio_transcribe(audio_path, cloud_consent)


@server.tool(name="academic_extract_feedback")
def academic_extract_feedback(
    audio_result_json: str, raw_llm_json: str
) -> dict[str, Any]:
    """
    Parse and validate LLM-extracted supervisor feedback against verbatim audio transcript.
    Enforces evidence integrity (quotes must exist in referenced segments).
    """
    return tool_academic_extract_feedback(audio_result_json, raw_llm_json)


@server.tool(name="academic_adjudicate")
def academic_adjudicate(feedback_json: str, adjudication_json: str) -> dict[str, Any]:
    """
    Apply author decisions (accepted, rejected, clarified) to extracted feedback items.
    """
    return tool_academic_adjudicate(feedback_json, adjudication_json)


@server.tool(name="academic_build_roadmap")
def academic_build_roadmap(audio_result_json: str, feedback_json: str) -> str:
    """
    Generate markdown Academic Revision Implementation Plan for author-accepted feedback items.
    Strictly read-only; does not modify any manuscript files.
    """
    return tool_academic_build_roadmap(audio_result_json, feedback_json)


@server.tool(name="academic_export_ars")
def academic_export_ars(audio_result_json: str, feedback_json: str) -> dict[str, Any]:
    """
    Export accepted feedback into an ARS-compatible Revision Roadmap handoff structure.
    Does not execute revision mode or alter any thesis files.
    """
    return tool_academic_export_ars(audio_result_json, feedback_json)


def main() -> None:
    """Entry point for running the stdio MCP server."""
    asyncio.run(server.run_stdio_async())


if __name__ == "__main__":
    main()
