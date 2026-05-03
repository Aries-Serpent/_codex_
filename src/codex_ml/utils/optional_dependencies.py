"""Helpers for optional dependency error messaging."""

from __future__ import annotations

__all__ = [
    "build_optional_dependency_error",
    "format_optional_dependency_error",
    "raise_optional_dependency_error",
]


def format_optional_dependency_error(package: str, feature: str) -> str:
    """Return a standardised ImportError message for optional packages."""

    return (
        f"{package} is required for {feature}.\n"
        f"Install with: pip install {package}\n"
        "Or install all optional dependencies: pip install -r requirements/dev.txt"
    )


def build_optional_dependency_error(package: str, feature: str) -> ImportError:
    """Construct an ``ImportError`` with standard messaging."""

    return ImportError(format_optional_dependency_error(package, feature))


def raise_optional_dependency_error(package: str, feature: str) -> None:
    """Raise an ImportError describing how to install ``package``."""

    raise build_optional_dependency_error(package, feature)
