"""Unit tests for audio inspector and provenance hashing."""

from pathlib import Path

from mentorspec.audio.inspect import compute_sha256, detect_media_type, inspect_audio


def test_compute_sha256(tmp_path: Path):
    sample_file = tmp_path / "test_audio.wav"
    sample_file.write_bytes(
        b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00"
    )

    digest = compute_sha256(sample_file)
    assert len(digest) == 64
    assert digest == digest.lower()


def test_detect_media_type():
    assert detect_media_type(Path("bimbingan.m4a")) == "audio/mp4"
    assert detect_media_type(Path("bimbingan.mp3")) == "audio/mpeg"
    assert detect_media_type(Path("bimbingan.wav")) == "audio/wav"
    assert detect_media_type(Path("bimbingan.flac")) == "audio/flac"


def test_inspect_audio_relative_file_sanitization(tmp_path: Path):
    audio_path = tmp_path / "deep" / "nested" / "session_recording.m4a"
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    audio_path.write_bytes(b"fake audio data" * 100)

    source = inspect_audio(audio_path)
    # The file field must be purely relative, no directory path leak!
    assert source.file == "session_recording.m4a"
    assert "/" not in source.file
    assert "\\" not in source.file
    assert source.file_size_bytes == 1500
    assert len(source.sha256) == 64
