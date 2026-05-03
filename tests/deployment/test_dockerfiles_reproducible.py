"""
Test Dockerfiles Reproducible

Test module for dockerfiles reproducible.
"""

from __future__ import annotations

import pathlib
import re
from collections.abc import Iterable

import pytest

FROM_RE = re.compile(r"^\s*FROM\s+([^\s]+)(?:\s+AS\s+(\w+))?", re.IGNORECASE)


def _iter_dockerfiles() -> list[pathlib.Path]:
    candidates: Iterable[pathlib.Path] = [
        pathlib.Path("Dockerfile"),
        pathlib.Path("Dockerfile.gpu"),
    ]
    return [path for path in candidates if path.exists()]


def _read_lines(path: pathlib.Path) -> list[str]:
    with path.open("r", encoding="utf-8") as handle:
        return [line.rstrip("\n") for line in handle]


def test_base_images_are_pinned_and_not_latest():
    dockerfiles = _iter_dockerfiles()
    if not dockerfiles:
        pytest.skip("No Dockerfiles present")

    for dockerfile in dockerfiles:
        lines = _read_lines(dockerfile)

        # Collect stage aliases first so we can skip them as "base images"
        stage_names: set[str] = set()
        base_images: list[str] = []
        for line in lines:
            match = FROM_RE.match(line)
            if match:
                image = match.group(1)
                alias = match.group(2)
                if alias:
                    stage_names.add(alias.lower())
                base_images.append(image)

        assert base_images, f"{dockerfile} must contain at least one FROM instruction"
        for image in base_images:
            # Skip internal multi-stage build references (e.g. FROM base AS cpu-runtime)
            if image.lower() in stage_names:
                continue
            assert (
                ":" in image
            ), f"{dockerfile}: base image '{image}' should be version-pinned with a tag"
            assert not image.endswith(
                ":latest"
            ), f"{dockerfile}: avoid ':latest' tag for reproducibility (pin a version)"
