"""Self-replicating solar factory simulation — research toolkit."""

from .sim import Factory, CONFIG, ResourceType, Recipe, ModuleSpec

__version__ = "1.1.0"
__all__ = [
    "Factory",
    "CONFIG",
    "ResourceType",
    "Recipe",
    "ModuleSpec",
    "api",
    "__version__",
]


def __getattr__(name: str):
    if name == "api":
        from . import api as _api
        return _api
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
