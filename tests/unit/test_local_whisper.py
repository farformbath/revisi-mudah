"""Unit tests for LocalWhisperProvider output resolution and error handling."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from revisi_mudah.core.contracts import AudioSource
from revisi_mudah.providers.local_whisper import (
    LocalWhisperProvider,
    WhisperExecutionError,
    WhisperOutputError,
)


@pytest.fixture
def mock_source():
    return AudioSource(
        file="sample.wav",
        sha256="c" * 64,
        duration_ms=5000,
        file_size_bytes=1000,
        media_type="audio/wav",
    )


def test_whisper_cli_success(tmp_path: Path, mock_source):
    fake_audio = tmp_path / "sample.wav"
    fake_audio.write_bytes(b"dummy")

    provider = LocalWhisperProvider(
        binary_path="mock-whisper-cli", model_path="model.bin"
    )

    def mock_subprocess_run(cmd, capture_output=True, text=True, check=False):
        # cmd has -of <output_prefix>
        of_idx = cmd.index("-of")
        output_prefix = Path(cmd[of_idx + 1])
        output_json = output_prefix.with_suffix(".json")
        output_json.write_text(
            json.dumps(
                {
                    "transcription": [
                        {
                            "offsets": {"from": 100, "to": 2500},
                            "text": "Metodologi evaluasi bab 3.",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        return MagicMock(returncode=0, stdout="", stderr="")

    with (
        patch("shutil.which", return_value="/bin/mock-whisper-cli"),
        patch("subprocess.run", side_effect=mock_subprocess_run),
    ):
        result = provider.transcribe(fake_audio, mock_source)
        assert result.transcription.provider == "whisper.cpp"
        assert len(result.transcription.segments) == 1
        assert result.transcription.segments[0].text == "Metodologi evaluasi bab 3."
        assert result.transcription.segments[0].start_ms == 100
        assert result.transcription.segments[0].end_ms == 2500


def test_whisper_cli_execution_failure(tmp_path: Path, mock_source):
    fake_audio = tmp_path / "sample.wav"
    fake_audio.write_bytes(b"dummy")

    provider = LocalWhisperProvider(
        binary_path="mock-whisper-cli", model_path="model.bin"
    )

    with (
        patch("shutil.which", return_value="/bin/mock-whisper-cli"),
        patch(
            "subprocess.run",
            return_value=MagicMock(returncode=1, stderr="CUDA out of memory"),
        ),
        pytest.raises(WhisperExecutionError, match="CUDA out of memory"),
    ):
        provider.transcribe(fake_audio, mock_source)


def test_whisper_cli_missing_output(tmp_path: Path, mock_source):
    fake_audio = tmp_path / "sample.wav"
    fake_audio.write_bytes(b"dummy")

    provider = LocalWhisperProvider(
        binary_path="mock-whisper-cli", model_path="model.bin"
    )

    # Subprocess succeeds but doesn't produce output JSON
    with (
        patch("shutil.which", return_value="/bin/mock-whisper-cli"),
        patch("subprocess.run", return_value=MagicMock(returncode=0, stderr="")),
        pytest.raises(WhisperOutputError, match="without expected JSON output"),
    ):
        provider.transcribe(fake_audio, mock_source)
