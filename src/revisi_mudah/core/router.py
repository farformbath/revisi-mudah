"""Universal Audio Capability Router with privacy gating and fallback resolution."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from revisi_mudah.audio.inspect import inspect_audio
from revisi_mudah.core.contracts import AudioResult
from revisi_mudah.core.policy import PrivacyPolicy, evaluate_cloud_permission
from revisi_mudah.core.validator import validate_audio_result
from revisi_mudah.providers.base import AudioProvider
from revisi_mudah.providers.gemini import GeminiAudioProvider
from revisi_mudah.providers.local_whisper import LocalWhisperProvider
from revisi_mudah.providers.omp_native import OmpNativeAudioProvider


class AudioRouter:
    """Dispatches audio transcription to the optimal available provider under privacy policy."""

    def __init__(self, policy: PrivacyPolicy | None = None):
        self.policy = policy or PrivacyPolicy()
        gemini_provider = GeminiAudioProvider()
        self.providers: dict[str, AudioProvider] = {
            "omp_native": OmpNativeAudioProvider(),
            "cloud_stt": gemini_provider,
            "gemini_audio": gemini_provider,
            "local_whisper": LocalWhisperProvider(),
        }

    def register_provider(self, name: str, provider: AudioProvider) -> None:
        """Register a custom or external audio provider."""
        self.providers[name] = provider

    def resolve_provider(
        self,
        consent_callback: Callable[[str], bool] | None = None,
    ) -> AudioProvider:
        """Resolve the highest-priority provider permitted by capability and privacy policy."""
        # Check providers in priority order defined by policy
        for provider_key in self.policy.provider_order:
            if provider_key not in self.providers:
                continue

            candidate = self.providers[provider_key]
            if not candidate.is_available():
                continue

            if candidate.is_cloud:
                permitted = evaluate_cloud_permission(
                    self.policy,
                    prompt_callback=consent_callback,
                    provider_name=candidate.name,
                )
                if not permitted:
                    continue

            return candidate

        # If no preferred provider worked, check local_whisper fallback
        local_cand = self.providers.get("local_whisper")
        if local_cand and local_cand.is_available():
            return local_cand

        raise RuntimeError(
            "No eligible audio transcription provider available. "
            "Under the current privacy policy, no cloud providers were authorized "
            "and local Whisper is not configured."
        )

    def process_audio(
        self,
        audio_path: str | Path,
        consent_callback: Callable[[str], bool] | None = None,
    ) -> AudioResult:
        """Inspect, route, transcribe, and validate audio into an AudioResult contract."""
        path = Path(audio_path).resolve()
        source = inspect_audio(path)
        provider = self.resolve_provider(consent_callback=consent_callback)

        audio_result = provider.transcribe(path, source)
        validate_audio_result(audio_result)
        return audio_result
