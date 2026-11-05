"""Oh My Pi (OMP) native multimodal audio interface adapter.

Per architectural specification:
This adapter is prepared as an interface for upstream OMP PR #16611 / Issue #5834.
It does NOT attempt unauthorized snooping into OMP's internal agent.db auth store.
When native multimodal audio transport is officially merged into OMP stable runtime,
this adapter connects directly to that channel.
"""

from __future__ import annotations

import os
from pathlib import Path

from mentorspec.core.contracts import AudioResult, AudioSource
from mentorspec.providers.base import AudioProvider


class OmpNativeAudioProvider(AudioProvider):
    """Interface adapter for Oh My Pi native multimodal audio pipeline."""

    @property
    def name(self) -> str:
        return "omp_native"

    @property
    def is_cloud(self) -> bool:
        return False

    def is_available(self) -> bool:
        """
        Check if the runtime environment exports the official OMP native audio transport socket/hook.
        Returns False until PR #16611 is merged and available in the active runtime.
        """
        return bool(
            os.environ.get("OMP_NATIVE_AUDIO_ENABLED", "").lower() in ["1", "true"]
        )

    def transcribe(self, audio_path: Path, source: AudioSource) -> AudioResult:
        if not self.is_available():
            raise NotImplementedError(
                "OMP Native Audio is not yet active in this runtime environment. "
                "Tracking upstream: can1357/oh-my-pi PR #16611 and Issue #5834. "
                "Use 'local_whisper' or configured cloud STT instead."
            )
        raise NotImplementedError("OMP native audio transport hook is not initialized.")
