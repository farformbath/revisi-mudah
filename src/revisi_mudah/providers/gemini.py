"""Google Gemini native multimodal audio provider."""

from __future__ import annotations

import json
import os
from pathlib import Path

from revisi_mudah.core.contracts import (
    AudioResult,
    AudioSource,
    Transcription,
    TranscriptSegment,
)
from revisi_mudah.providers.base import AudioProvider


class GeminiAudioProvider(AudioProvider):
    """Google Gemini multimodal audio provider (native audio understanding)."""

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name

    @property
    def name(self) -> str:
        return "gemini_audio"

    @property
    def is_cloud(self) -> bool:
        return True

    def is_available(self) -> bool:
        """Check if GEMINI_API_KEY or GOOGLE_API_KEY is configured in the environment."""
        return bool(
            os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        )

    def transcribe(self, audio_path: Path, source: AudioSource) -> AudioResult:
        """Upload audio via Google GenAI Files API and retrieve structured transcript."""
        if not self.is_available():
            raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY is not set.")

        try:
            from google import genai

            client = genai.Client()

            # Upload audio file
            uploaded = client.files.upload(file=str(audio_path))

            prompt = (
                "Transcribe this academic bimbingan session verbatim in Indonesian. "
                "Output ONLY a valid JSON object matching this structure:\n"
                "{\n"
                '  "language": "id",\n'
                '  "segments": [\n'
                '    {"id": "S001", "start_ms": 0, "end_ms": 4500, "speaker": "supervisor", "text": "..."}\n'
                "  ]\n"
                "}"
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=[uploaded, prompt],
            )

            # Cleanup uploaded file from Google server
            try:
                client.files.delete(name=uploaded.name)
            except (OSError, RuntimeError):
                pass

            cleaned = response.text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                if cleaned.endswith("```"):
                    cleaned = cleaned.rsplit("\n", 1)[0]
                cleaned = cleaned.strip()

            data = json.loads(cleaned)
            segments: list[TranscriptSegment] = [
                TranscriptSegment(
                    id=s["id"],
                    start_ms=s["start_ms"],
                    end_ms=s["end_ms"],
                    speaker=s.get("speaker"),
                    text=s["text"],
                    confidence=s.get("confidence"),
                )
                for s in data.get("segments", [])
            ]

            transcription = Transcription(
                provider="gemini_audio",
                model=self.model_name,
                language=data.get("language", "id"),
                segments=segments,
            )
            return AudioResult(
                schema="mentorspec/1.0", source=source, transcription=transcription
            )

        except ImportError:
            raise RuntimeError(
                "google-genai package is not installed. Run 'uv add google-genai'."
            )
