"""Verification of backward compatibility shims for mentorspec namespace."""

import pytest


def test_legacy_import_emits_deprecation_warning():
    with pytest.deprecated_call():
        import mentorspec  # noqa: F401
