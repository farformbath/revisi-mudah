"""CLI interface for MentorSpec using Typer."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from mentorspec.audio.inspect import inspect_audio
from mentorspec.core.policy import CloudUploadConsent, PrivacyPolicy
from mentorspec.core.router import AudioRouter
from mentorspec.mcp.server import main as run_mcp_server

app = typer.Typer(
    name="mentorspec",
    help="MentorSpec — Audio-to-Academic Implementation Planning System.",
    add_completion=False,
)
console = Console()


@app.command()
def inspect(
    audio_path: Path = typer.Argument(
        ..., help="Path to audio recording (.m4a, .mp3, .wav)"
    ),
):
    """Inspect an audio recording: calculate SHA-256 and extract metadata without cloud upload."""
    if not audio_path.is_file():
        console.print(f"[red]Error:[/red] File not found: {audio_path}")
        raise typer.Exit(1)

    source = inspect_audio(audio_path)
    console.print("[green]Provenance & Audio Metadata:[/green]")
    console.print_json(data=source.model_dump())


@app.command()
def transcribe(
    audio_path: Path = typer.Argument(..., help="Path to audio recording"),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Path to save transcript.json"
    ),
    cloud_consent: str = typer.Option(
        "ask", "--cloud-consent", help="'ask', 'allow', or 'deny'"
    ),
):
    """Transcribe audio into a verbatim, timestamped transcript (AudioResult)."""
    if not audio_path.is_file():
        console.print(f"[red]Error:[/red] File not found: {audio_path}")
        raise typer.Exit(1)

    policy = PrivacyPolicy(cloud_upload=CloudUploadConsent(cloud_consent.lower()))

    def consent_prompt(msg: str) -> bool:
        return typer.confirm(
            f"\n[bold yellow]PRIVACY NOTICE:[/bold yellow] {msg}", default=False
        )

    router = AudioRouter(policy=policy)
    try:
        audio_result = router.process_audio(audio_path, consent_callback=consent_prompt)
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]Transcription failed:[/red] {e}")
        raise typer.Exit(1)

    data = audio_result.model_dump(by_alias=True)
    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        console.print(f"[green]Saved transcript to:[/green] {output}")
    else:
        console.print_json(data=data)


@app.command()
def server():
    """Run the MentorSpec MCP Server via stdio."""
    run_mcp_server()


def main():
    app()


if __name__ == "__main__":
    main()
