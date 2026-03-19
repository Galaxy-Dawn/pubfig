"""Bar plot functions (Matplotlib).

This module re-exports the public bar-related plotting functions. Implementations
live in private modules to keep individual files small and maintainable.
"""

from __future__ import annotations

from ._bar_scatter import bar_scatter
from ._bar_simple import bar
from ._bar_stacked import stacked_bar

__all__ = ["bar", "bar_scatter", "stacked_bar"]

