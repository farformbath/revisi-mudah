"""Local-first speech recognition provider via whisper.cpp (GGML) or faster-whisper."""

from __future__ import annotations

import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from revisi_mudah.core.contracts import (
    AudioResult,
    AudioSource,
    Transcription,
    TranscriptSegment,
)
from revisi_mudah.providers.base import AudioProvider


class WhisperExecutionError(RuntimeError):
    """Raised when whisper-cli subprocess returns a non-zero exit code."""


class WhisperOutputError(RuntimeError):
    """Raised when whisper-cli fails to generate expected valid JSON output."""


class LocalWhisperProvider(AudioProvider):
    """
    Local offline speech recognition using whisper.cpp (GGML) or faster-whisper.
    Zero cloud data transmission, zero API keys required.
    """

    def __init__(
        self, binary_path: str = "whisper-cli", model_path: str = "models/ggml-base.bin"
    ):
        self.binary_path = binary_path
        self.model_path = model_path

    @property
    def name(self) -> str:
        return "local_whisper"

    @property
    def is_cloud(self) -> bool:
        return False

    def is_available(self) -> bool:
        """Check if whisper-cli binary or faster_whisper python package is present."""
        if shutil.which(self.binary_path) is not None:
            return True
        try:
            import faster_whisper  # noqa: F401

            return True
        except ImportError:
            return False

    def transcribe(self, audio_path: Path, source: AudioSource) -> AudioResult:
        """Transcribe audio locally and construct AudioResult."""
        if not audio_path.is_file():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        segments: list[TranscriptSegment] = []

        # Try faster-whisper if installed
        try:
            from faster_whisper import WhisperModel

            model = WhisperModel("base", device="cpu", compute_type="int8")
            raw_segments, info = model.transcribe(str(audio_path), language="id")

            for idx, s in enumerate(raw_segments, start=1):
                start_ms = int(s.start * 1000)
                end_ms = int(s.end * 1000)
                # Ensure end_ms > start_ms
                if end_ms <= start_ms:
                    end_ms = start_ms + 1000

                conf = None
                if hasattr(s, "avg_logprob") and s.avg_logprob is not None:
                    try:
                        conf = round(float(min(1.0, max(0.0, math.exp(s.avg_logprob)))), 4)
                    except (OverflowError, ValueError):
                        conf = None

                seg = TranscriptSegment(
                    id=f"S{idx:03d}",
                    start_ms=start_ms,
                    end_ms=end_ms,
                    speaker=None,
                    text=s.text.strip(),
                    confidence=conf,
                )
                segments.append(seg)

            lang = info.language if info and hasattr(info, "language") else "id"
            transcription = Transcription(
                provider="faster-whisper",
                model="base",
                language=lang,
                segments=segments,
            )
            return AudioResult(
                schema="mentorspec/1.0", source=source, transcription=transcription
            )
        except ImportError:
            pass

        # Try whisper-cli binary (whisper.cpp)
        cli_bin = shutil.which(self.binary_path)
        if cli_bin is not None:
            with tempfile.TemporaryDirectory(prefix="revisi-mudah-whisper-") as tmp_dir:
                output_prefix = Path(tmp_dir) / "transcript"
                cmd = [
                    cli_bin,
                    "-m",
                    str(self.model_path),
                    "-f",
                    str(audio_path),
                    "-oj",
                    "-of",
                    str(output_prefix),
                    "-l",
                    "id",
                ]
                res = subprocess.run(cmd, capture_output=True, text=True, check=False)
                if res.returncode != 0:
                    raise WhisperExecutionError(
                        f"whisper-cli failed (exit code {res.returncode}): {res.stderr.strip()}"
                    )

                output_json_path = output_prefix.with_suffix(".json")
                if not output_json_path.is_file():
                    raise WhisperOutputError(
                        f"whisper-cli completed without expected JSON output: {output_json_path}"
                    )

                try:
                    with open(output_json_path, encoding="utf-8") as f:
                        data = json.load(f)
                except Exception as e:
                    raise WhisperOutputError(
                        f"Failed to parse whisper-cli JSON output: {e}"
                    ) from e

                raw_segs = data.get("transcription", [])
                for idx, item in enumerate(raw_segs, start=1):
                    start_ms = item.get("offsets", {}).get("from", 0)
                    end_ms = item.get("offsets", {}).get("to", start_ms + 1000)
                    seg = TranscriptSegment(
                        id=f"S{idx:03d}",
                        start_ms=start_ms,
                        end_ms=end_ms,
                        speaker=None,
                        text=item.get("text", "").strip(),
                        confidence=None,
                    )
                    segments.append(seg)

                transcription = Transcription(
                    provider="whisper.cpp",
                    model=Path(self.model_path).name,
                    language="id",
                    segments=segments,
                )
                return AudioResult(
                    schema="mentorspec/1.0",
                    source=source,
                    transcription=transcription,
                )

        raise RuntimeError(
            "Local Whisper provider is not configured. "
            "Please install faster-whisper ('uv add faster-whisper') or provide a compiled whisper.cpp binary."
        )
