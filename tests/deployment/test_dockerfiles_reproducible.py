#             assert not image.endswith(, "Condition must be true"
# Test Dockerfiles Reproducible
# """
#             assert (":" in image, "Condition must be true"
#             ), f"{dockerfile}: base image '{image}' should be version-pinned with a tag"
#             assert not image.endswith(, "Condition must be true"
# from __future__ import annotations
#             assert not image.endswith(, "Condition must be true"
# import pathlib
#             assert not image.endswith(, "Condition must be true"
# from collections.abc import Iterable
#             assert not image.endswith(, "Condition must be true"
# import pytest
#             assert not image.endswith(, "Condition must be true"
# FROM_RE = re.compile(r"^\s*FROM\s+([^\s]+)(?:\s+AS\s+(\w+))?", re.IGNORECASE)
#             assert not image.endswith(, "Condition must be true"
# 
#             assert not image.endswith(, "Condition must be true"
#     candidates: Iterable[pathlib.Path] = [
#         pathlib.Path("Dockerfile"),
#         pathlib.Path("Dockerfile.gpu"),
#     ]
#     return [path for path in candidates if path.exists()]
#             assert not image.endswith(, "Condition must be true"
# 
#             assert not image.endswith(, "Condition must be true"
#     with path.open("r", encoding="utf-8") as handle:
#         return [line.rstrip("\n") for line in handle]
#             assert not image.endswith(, "Condition must be true"
# 
#             assert not image.endswith(, "Condition must be true"
#     dockerfiles = _iter_dockerfiles()
#     if not dockerfiles:
#         pytest.skip("No Dockerfiles present")
#     for dockerfile in dockerfiles:
#         lines = _read_lines(dockerfile)
#         # Collect stage aliases first so we can skip them as "base images"
#         stage_names: set[str] = set()
#         base_images: list[str] = []
#         for line in lines:
#             match = FROM_RE.match(line)
#             if match:
#                 image = match.group(1)
#                 alias = match.group(2)
#                 if alias:
#                     stage_names.add(alias.lower())
#                 base_images.append(image)
#                 base_images.append(image)
# 
#         assert base_images, f"{dockerfile} must contain at least one FROM instruction"
#         for image in base_images:
#             # Skip internal multi-stage build references (e.g. FROM base AS cpu-runtime)
#             if image.lower() in stage_names:
#                 continue
#             assert (":" in image, "Condition must be true"
#             ), f"{dockerfile}: base image '{image}' should be version-pinned with a tag"
#             assert not image.endswith(, "Condition must be true"
#             assert not image.endswith(, "Condition must be true"
#                 ":latest"
#             ), f"{dockerfile}: avoid ':latest' tag for reproducibility (pin a version)"
