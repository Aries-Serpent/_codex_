"""Central definition of the codex package version."""

__all__ = ["__version__"]

# NOTE: Keep in sync with the version published in the distribution metadata.
# The ``pyproject.toml`` configuration reads this value via
# ``tool.setuptools.dynamic`` so wheels and sdists always embed the same number.
__version__ = "0.1.0"
