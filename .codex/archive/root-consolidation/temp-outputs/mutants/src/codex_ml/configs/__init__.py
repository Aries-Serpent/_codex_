"""Packaged Hydra configuration defaults for Codex ML."""

from importlib import resources as _resources
from pathlib import Path as _Path

__all__ = ("get_config_path",)


def get_config_path() -> str:
    """Return the filesystem path to the packaged Hydra configuration directory."""
    with _resources.as_file(_resources.files(__name__)) as path:
        return str(_Path(path))
