"""Backward-compatibility shim for mentorspec namespace.

Deprecated: Use `revisi_mudah` instead.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "The 'mentorspec' package namespace is deprecated; use 'revisi_mudah' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from revisi_mudah import hello  # noqa: F401
