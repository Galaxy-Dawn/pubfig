"""Optional dependency checks."""

from importlib.util import find_spec


def _is_available(name: str) -> bool:
    return find_spec(name) is not None


def _require(name: str, extra: str) -> None:
    if not _is_available(name):
        raise ImportError(
            f"{name} is required for this feature. "
            f"Install it with: pip install pubfig[{extra}]"
        )
