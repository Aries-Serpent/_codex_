"""
Rubric Module

This module provides functionality for rubric.

Usage:
    from qa.rubric import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import ast
import logging

logger = logging.getLogger(__name__)


import csv  # noqa: E402
import json  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

from pydantic import BaseModel, Field  # noqa: E402


class RubricCriterion(BaseModel):
    """A single evaluation criterion in a QA rubric."""

    id: str
    description: str
    max_score: float


class QARubric(BaseModel):
    """A QA rubric composed of multiple criteria."""

    name: str = "default"
    criteria: list[RubricCriterion] = Field(default_factory=list)

    @staticmethod
    def _clamp_score(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def score_code_quality(self, code: Any) -> float:
        if not isinstance(code, str):
            raise TypeError("code must be a string")
        if not code.strip():
            return 0.0

        tree = ast.parse(code)
        score = 0.5
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                score += 0.1
            if isinstance(node, (ast.Return, ast.Assign, ast.AnnAssign)):
                score += 0.05
        return self._clamp_score(score)

    def score_test_coverage(self, coverage_data: dict[str, Any]) -> float:
        if not isinstance(coverage_data, dict):
            raise TypeError("coverage_data must be a mapping")
        covered = coverage_data.get("covered")
        total = coverage_data.get("total")
        if not isinstance(covered, (int, float)) or not isinstance(total, (int, float)):
            return 0.0
        if total <= 0:
            return 0.0
        return self._clamp_score(covered / total)

    def score_documentation(self, code: Any) -> float:
        if not isinstance(code, str):
            raise TypeError("code must be a string")
        if not code.strip():
            return 0.0

        tree = ast.parse(code)
        docstrings = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and ast.get_docstring(node, clean=False)
        )
        return self._clamp_score(0.5 + (0.1 * docstrings))

    def aggregate_scores(self, scores: dict[str, Any]) -> float:
        if not isinstance(scores, dict):
            raise TypeError("scores must be a mapping")
        numeric = [float(value) for value in scores.values() if isinstance(value, (int, float))]
        if not numeric:
            return 0.0
        return self._clamp_score(sum(numeric) / len(numeric))

    def evaluate(self, code: Any, threshold: float = 0.5) -> float:
        score = self.aggregate_scores(
            {
                "code_quality": self.score_code_quality(code),
                "documentation": self.score_documentation(code),
            }
        )
        return score if score >= threshold else 0.0


def load_rubric(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def generate_scores(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    type(e).__name__
                    logger.debug("ValueError: <ERROR_TYPE>")
                    logger.warning("ValueError: <ERROR_TYPE>", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")
