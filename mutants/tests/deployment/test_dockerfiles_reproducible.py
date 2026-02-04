"""
Test Dockerfiles Reproducible

Test module for dockerfiles reproducible.
"""

from __future__ import annotations

import pathlib
import re
from typing import Iterable, List

import pytest

FROM_RE = re.compile(r"^\s*FROM\s+([^\s]+)", re.IGNORECASE)


def _iter_dockerfiles() -> List[pathlib.Path]:
    candidates: Iterable[pathlib.Path] = [
        pathlib.Path("Dockerfile"),
        pathlib.Path("Dockerfile.gpu"),
    ]
    return [path for path in candidates if path.exists()]


def _read_lines(path: pathlib.Path) -> List[str]:
    with path.open("r", encoding="utf-8") as handle:
        return [line.rstrip("\n") for line in handle]


def test_base_images_are_pinned_and_not_latest():
    dockerfiles = _iter_dockerfiles()
    if not dockerfiles:
        pytest.skip("No Dockerfiles present")

    for dockerfile in dockerfiles:
        lines = _read_lines(dockerfile)
        base_images: List[str] = []
        for line in lines:
            match = FROM_RE.match(line)
            if match:
                base_images.append(match.group(1))

        assert base_images, f"{dockerfile} must contain at least one FROM instruction"
        for image in base_images:
            assert (
                ":" in image
            ), f"{dockerfile}: base image '{image}' should be version-pinned with a tag"
            assert not image.endswith(
                ":latest"
            ), f"{dockerfile}: avoid ':latest' tag for reproducibility (pin a version)"
