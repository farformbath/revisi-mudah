"""Unit tests for AudioRouter provider resolution and deduplication."""

from revisi_mudah.core.router import AudioRouter


def test_router_shares_gemini_provider_instance():
    router = AudioRouter()
    assert "cloud_stt" in router.providers
    assert "gemini_audio" in router.providers
    assert router.providers["cloud_stt"] is router.providers["gemini_audio"]
