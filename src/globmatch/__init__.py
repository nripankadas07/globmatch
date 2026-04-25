"""Public API for the globmatch package.

All pattern matching is implemented in :mod:`globmatch._core`; this
module only re-exports the stable entry points so callers can write
``from globmatch import match, filter_names, compile, GlobError``.
"""

from ._core import (
    CompiledGlob,
    GlobError,
    compile,
    filter_names,
    match,
    translate,
)

__all__ = [
    "CompiledGlob",
    "GlobError",
    "compile",
    "filter_names",
    "match",
    "translate",
]

__version__ = "0.1.0"
