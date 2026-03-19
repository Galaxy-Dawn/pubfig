"""Helpers for backward-compatible public API parameter aliases."""

from __future__ import annotations

import warnings
from typing import Sequence, TypeVar

T = TypeVar("T")


def _normalize_sequence(value: Sequence[str]) -> list[str]:
    return [str(item) for item in value]


def resolve_sequence_alias(
    primary: Sequence[str] | None,
    legacy: Sequence[str] | None,
    *,
    primary_name: str,
    legacy_name: str,
) -> list[str] | None:
    """Resolve a preferred sequence parameter with one backward-compatible alias."""
    if primary is None:
        if legacy is None:
            return None
        warnings.warn(
            f"`{legacy_name}` is deprecated and will be removed in a future release; use `{primary_name}` instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        return _normalize_sequence(legacy)
    if legacy is None:
        return _normalize_sequence(primary)

    primary_list = _normalize_sequence(primary)
    legacy_list = _normalize_sequence(legacy)
    if primary_list != legacy_list:
        raise ValueError(
            f"{primary_name} and {legacy_name} are both provided but different; please pass only one."
        )
    return primary_list


def resolve_scalar_alias(
    primary: T | None,
    legacy: T | None,
    *,
    primary_name: str,
    legacy_name: str,
    legacy_default: T | None = None,
) -> T | None:
    """Resolve a preferred scalar parameter with one backward-compatible alias."""
    if primary is None:
        if legacy is not None and legacy != legacy_default:
            warnings.warn(
                f"`{legacy_name}` is deprecated and will be removed in a future release; "
                f"use `{primary_name}` instead.",
                DeprecationWarning,
                stacklevel=3,
            )
        return legacy
    if legacy is None or legacy == legacy_default:
        return primary
    if primary != legacy:
        raise ValueError(f"{primary_name} and {legacy_name} are both provided but different; please pass only one.")
    return primary
