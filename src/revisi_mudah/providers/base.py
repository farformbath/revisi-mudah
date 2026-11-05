"""Abstract base class for audio transcription providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from revisi_mudah.core.contracts import AudioResult, AudioSource


class AudioProvider(ABC):
    """Abstract interface for all audio transcription backends."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider identifier."""

    @property
    @abstractmethod
    def is_cloud(self) -> bool:
        """Whether this provider transmits audio data to an external cloud service."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider dependencies and credentials are functional."""

    @abstractmethod
    def transcribe(self, audio_path: Path, source: AudioSource) -> AudioResult:
        """
        Transcribe an audio file into an AudioResult contract.
        Must preserve verbatim text and timestamps.
        """
