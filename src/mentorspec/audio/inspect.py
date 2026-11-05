"""Audio file inspection and provenance hashing."""

from __future__ import annotations

import hashlib
import mimetypes
from pathlib import Path

try:
    import mutagen
except ImportError:
    mutagen = None

from mentorspec.core.contracts import AudioSource


def compute_sha256(path: Path) -> str:
    """Calculate 64-character lowercase hexadecimal SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


def detect_media_type(path: Path) -> str:
    """Detect MIME type from file extension or content."""
    suffix = path.suffix.lower()
    ext_map = {
        ".m4a": "audio/mp4",
        ".mp4": "audio/mp4",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
        ".webm": "audio/webm",
        ".aac": "audio/aac",
    }
    if suffix in ext_map:
        return ext_map[suffix]

    mime, _ = mimetypes.guess_type(path.name)
    if mime and mime.startswith("audio/"):
        return mime
    return "audio/octet-stream"


def get_audio_duration_ms(path: Path) -> int:
    """Extract audio duration in milliseconds using wave or mutagen."""
    # Try standard library wave module first if it's a WAV file
    if path.suffix.lower() == ".wav":
        try:
            import wave

            with wave.open(str(path), "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                if rate > 0:
                    return int((frames / float(rate)) * 1000)
        except (OSError, wave.Error):
            pass

    if mutagen is not None:
        try:
            audio_info = mutagen.File(str(path))
            if (
                audio_info
                and audio_info.info
                and getattr(audio_info.info, "length", None) is not None
            ):
                return int(audio_info.info.length * 1000)
        except (OSError, AttributeError, ValueError):
            return 0
    return 0


def inspect_audio(file_path: str | Path) -> AudioSource:
    """
    Inspect an audio file on disk and construct an AudioSource contract.
    Ensures relative filename to prevent local system path leaks.
    """
    path = Path(file_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Audio file does not exist: {file_path}")

    file_size = path.stat().st_size
    sha256 = compute_sha256(path)
    media_type = detect_media_type(path)
    duration_ms = get_audio_duration_ms(path)
    clean_filename = path.name

    return AudioSource(
        file=clean_filename,
        sha256=sha256,
        duration_ms=duration_ms,
        file_size_bytes=file_size,
        media_type=media_type,
    )
