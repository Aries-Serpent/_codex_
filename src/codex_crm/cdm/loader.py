"""Helpers for loading the CRM Customer Data Model (CDM)."""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Union

try:  # pragma: no cover - optional dependency
    import pandas as pd
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal installs
    pd = None  # type: ignore[assignment]

if TYPE_CHECKING:  # pragma: no cover - imported for typing only
    import pandas

TableType = Union["pandas.DataFrame", list[dict[str, str]]]

_CDM_RELATIVE_PATH = Path("config") / "cdm"


def _iter_candidate_roots() -> list[Path]:
    """Return candidate project roots ordered by likelihood.

    When running from a source checkout we expect ``src/codex_crm/cdm/loader.py``
    so climbing three levels from ``__file__`` lands at the repository root. When
    the package is installed, the files typically live under
    ``site-packages/codex_crm``. In that case the configuration payload may be a
    package resource and the ``config`` folder can sit directly under the
    package root or one of its parents. We therefore probe a small set of
    sensible ancestors.
    """

    here = Path(__file__).resolve()
    candidates: list[Path] = []

    try:
        repo_root = here.parents[3]
    except IndexError:
        repo_root = None
    else:
        candidates.append(repo_root)

    package_root = here.parent.parent
    candidates.append(package_root)

    # In an installed environment the package usually lives in site-packages or
    # dist-packages. Walking back to the directory that contains that folder is
    # often where project-level resources are copied to. We also include all
    # ancestors to cover editable installs or custom layouts.
    for ancestor in package_root.parents:
        candidates.append(ancestor)

    # Preserve order but deduplicate.
    deduped: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate
        if resolved in seen:
            continue
        deduped.append(resolved)
        seen.add(resolved)

    return deduped


def _locate_cdm_dir() -> Path:
    """Locate the directory that contains the CDM CSV files."""

    searched: list[Path] = []
    for root in _iter_candidate_roots():
        candidate = root / _CDM_RELATIVE_PATH
        searched.append(candidate)
        if candidate.is_dir():
            return candidate

        # Some installation layouts store the data directly under the package
        # root (``codex_crm/cdm`` vs ``codex_crm/config/cdm``). Detect this by
        # checking for the ``cdm`` directory alongside the loader.
        alternate = root / "cdm"
        searched.append(alternate)
        if alternate.is_dir():
            return alternate

    raise FileNotFoundError(
        "Unable to locate the CRM CDM directory. Looked in: "
        + ", ".join(str(path) for path in searched)
    )


def _read_csv(csv_path: Path) -> TableType:
    if pd is not None:
        return pd.read_csv(csv_path)

    with csv_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


@lru_cache(maxsize=1)
def load_cdm() -> dict[str, TableType]:
    """Load all CSV tables from the CDM folder."""

    cdm_dir = _locate_cdm_dir()
    tables: dict[str, TableType] = {}
    for csv_path in sorted(cdm_dir.glob("*.csv")):
        tables[csv_path.stem] = _read_csv(csv_path)

    if not tables:
        raise FileNotFoundError(f"No CDM CSV files were found in {cdm_dir}")

    return tables
