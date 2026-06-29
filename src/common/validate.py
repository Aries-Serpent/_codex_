"""
Validate Module

This module provides functionality for validate.

Usage:
    from common.validate import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import csv
import logging
import shutil
import site
import sys
from importlib import import_module
from pathlib import Path

# Ensure the installed Great Expectations package takes precedence over
# the repository-local configuration directory of the same name.
for _site_path in site.getsitepackages():
    if _site_path in sys.path:
        sys.path.remove(_site_path)
    sys.path.insert(0, _site_path)

try:
    gx = import_module("great_expectations")
except ImportError:
    gx = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


def _ensure_docs_out() -> Path:
    out = Path(".codex") / "ge_docs"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _fallback_validate(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                type(exc).__name__
                logger.debug("ValueError: <ERROR_TYPE>")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def run_clean_checkpoint(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if gx is None or not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        type(e).__name__
        logger.debug("AttributeError: <ERROR_TYPE>")
        logger.warning("AttributeError: <ERROR_TYPE>", exc_info=True)
        try:
            success_flag = results["success"]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out
