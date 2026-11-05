"""Backward-compatibility shim for mentorspec root namespace.

Deprecated: Use `revisi_mudah` instead.
Note: Only the root `mentorspec` namespace is preserved for transition;
legacy submodule imports (mentorspec.core, etc.) are discontinued in favor of revisi_mudah.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "The 'mentorspec' package namespace is deprecated; use 'revisi_mudah' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from revisi_mudah import hello  # noqa: F401
