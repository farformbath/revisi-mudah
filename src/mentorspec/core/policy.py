"""Privacy policy and user consent gating for MentorSpec."""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class CloudUploadConsent(str, Enum):
    ASK = "ask"
    ALLOW = "allow"
    DENY = "deny"


class PrivacyPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cloud_upload: CloudUploadConsent = Field(
        default=CloudUploadConsent.ASK,
        description="Policy for uploading audio to cloud APIs ('ask', 'allow', 'deny').",
    )
    default_provider: str = Field(
        default="auto",
        description="Default provider or 'auto' for capability-based resolution.",
    )
    provider_order: list[str] = Field(
        default_factory=lambda: ["omp_native", "cloud_stt", "local_whisper"],
        description="Priority order for audio transcription providers.",
    )
    require_consent_for_cloud: bool = Field(
        default=True,
        description="Enforce user consent prompt when cloud_upload is 'ask'.",
    )
    preserve_original_audio: bool = Field(default=True)
    preserve_verbatim_transcript: bool = Field(default=True)
    preserve_timestamps: bool = Field(default=True)


class PrivacyViolationError(Exception):
    """Raised when an attempt is made to use cloud services under a deny policy."""


def evaluate_cloud_permission(
    policy: PrivacyPolicy,
    prompt_callback: Callable[[str], bool] | None = None,
    provider_name: str = "cloud_provider",
) -> bool:
    """
    Evaluate whether sending data to a cloud provider is permitted under the active policy.

    - DENY: Always raises PrivacyViolationError.
    - ALLOW: Returns True.
    - ASK: Calls prompt_callback if provided; if not provided or declined, returns False.
    """
    if policy.cloud_upload == CloudUploadConsent.DENY:
        raise PrivacyViolationError(
            f"Cloud upload is explicitly DENIED by policy. Cannot use provider '{provider_name}'."
        )

    if policy.cloud_upload == CloudUploadConsent.ALLOW:
        return True

    # CloudUploadConsent.ASK
    if prompt_callback is not None:
        message = (
            f"MentorSpec requests permission to upload audio to external cloud provider '{provider_name}'. "
            "Do you consent?"
        )
        approved = prompt_callback(message)
        return bool(approved)

    # Non-interactive without explicit approval defaults to denying cloud upload
    return False
