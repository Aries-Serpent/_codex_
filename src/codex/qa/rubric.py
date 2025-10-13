"""Offline QA rubric definition and scoring utilities."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class RubricCriterion(BaseModel):
    """A single evaluation criterion in a QA rubric."""

    id: str
    description: str
    max_score: float


class QARubric(BaseModel):
    """A QA rubric composed of multiple criteria."""

    name: str
    criteria: list[RubricCriterion] = Field(default_factory=list)


def load_rubric(path: Path) -> QARubric:
    """Load a QA rubric definition from CSV or JSON."""

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
    """Generate a JSONL score file for the provided rubric."""

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
                except ValueError:
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")
