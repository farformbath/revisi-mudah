"""Unit tests for privacy policies and cloud consent gates."""

import pytest

from revisi_mudah.core.policy import (
    CloudUploadConsent,
    PrivacyPolicy,
    PrivacyViolationError,
    evaluate_cloud_permission,
)


def test_policy_deny_strictly_blocks_cloud():
    policy = PrivacyPolicy(cloud_upload=CloudUploadConsent.DENY)
    with pytest.raises(PrivacyViolationError, match="explicitly DENIED"):
        evaluate_cloud_permission(policy, provider_name="gemini")


def test_policy_allow_permits_cloud():
    policy = PrivacyPolicy(cloud_upload=CloudUploadConsent.ALLOW)
    assert evaluate_cloud_permission(policy, provider_name="gemini") is True


def test_policy_ask_with_approval():
    policy = PrivacyPolicy(cloud_upload=CloudUploadConsent.ASK)
    prompt_called = False

    def mock_prompt(msg: str) -> bool:
        nonlocal prompt_called
        prompt_called = True
        return True

    assert (
        evaluate_cloud_permission(
            policy, prompt_callback=mock_prompt, provider_name="gemini"
        )
        is True
    )
    assert prompt_called is True


def test_policy_ask_with_rejection():
    policy = PrivacyPolicy(cloud_upload=CloudUploadConsent.ASK)

    def mock_prompt(msg: str) -> bool:
        return False

    assert (
        evaluate_cloud_permission(
            policy, prompt_callback=mock_prompt, provider_name="gemini"
        )
        is False
    )


def test_policy_ask_non_interactive_defaults_to_false():
    policy = PrivacyPolicy(cloud_upload=CloudUploadConsent.ASK)
    # No callback provided in non-interactive environment
    assert (
        evaluate_cloud_permission(policy, prompt_callback=None, provider_name="gemini")
        is False
    )


def test_policy_rejects_false_preservation():
    with pytest.raises(ValueError, match="is not supported"):
        PrivacyPolicy(preserve_original_audio=False)
    with pytest.raises(ValueError, match="is not supported"):
        PrivacyPolicy(preserve_verbatim_transcript=False)
    with pytest.raises(ValueError, match="is not supported"):
        PrivacyPolicy(preserve_timestamps=False)
