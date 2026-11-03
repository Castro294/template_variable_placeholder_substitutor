"""Public API for template_variable_placeholder_substitutor."""

from .core import (
    MissingKeysError,
    Substitutor,
    substitute,
)

__all__ = [
    "MissingKeysError",
    "Substitutor",
    "substitute",
]
