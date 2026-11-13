"""
Test suite for the QA rubric module (``codex.qa.rubric``).

Tests cover:
- Rubric model construction and validation
- Loading rubrics from CSV and JSON
- Score generation (per-criterion scores and totals)
- Edge cases and error handling
"""

import json

import pytest
from codex.qa.rubric import (
    QARubric,
    RubricCriterion,
    generate_scores,
    load_rubric,
)
from pydantic import ValidationError


@pytest.fixture
def rubric() -> QARubric:
    return QARubric(
        name="quality",
        criteria=[
            RubricCriterion(id="code_quality", description="Code quality", max_score=5),
            RubricCriterion(id="documentation", description="Docs", max_score=3),
        ],
    )


class TestQARubricInitialization:
    """Test QARubric construction."""

    def test_rubric_creation(self):
        rubric = QARubric(name="empty")
        assert rubric.name == "empty"
        assert rubric.criteria == []

    def test_rubric_requires_name(self):
        with pytest.raises(ValidationError):
            QARubric()

    def test_rubric_with_custom_criteria(self, rubric):
        assert [c.id for c in rubric.criteria] == ["code_quality", "documentation"]
        assert rubric.criteria[0].max_score == 5.0

    def test_criterion_requires_fields(self):
        with pytest.raises(ValidationError):
            RubricCriterion(id="x", description="missing max score")


class TestLoadRubric:
    """Test loading rubric definitions."""

    def test_load_csv(self, tmp_path):
        path = tmp_path / "my_rubric.csv"
        path.write_text(
            "id,description,max_score\n code_quality , Quality ,5\ndocumentation,Docs,\n",
            encoding="utf-8",
        )
        rubric = load_rubric(path)
        assert rubric.name == "my_rubric"
        assert [(c.id, c.description, c.max_score) for c in rubric.criteria] == [
            ("code_quality", "Quality", 5.0),
            ("documentation", "Docs", 0.0),
        ]

    def test_load_json(self, tmp_path, rubric):
        path = tmp_path / "rubric.json"
        path.write_text(rubric.model_dump_json(), encoding="utf-8")
        assert load_rubric(path) == rubric

    def test_load_invalid_json_raises(self, tmp_path):
        path = tmp_path / "rubric.json"
        path.write_text("this is not json {", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            load_rubric(path)


class TestGenerateScores:
    """Test score generation."""

    def _run(self, tmp_path, rubric, csv_text):
        src = tmp_path / "input.csv"
        src.write_text(csv_text, encoding="utf-8")
        out = tmp_path / "scores.jsonl"
        generate_scores(src, rubric, out)
        return [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]

    def test_scores_and_totals(self, tmp_path, rubric):
        rows = self._run(
            tmp_path,
            rubric,
            "id,code_quality,documentation\nr1,4,2.5\nr2,1,0\n",
        )
        assert rows == [
            {"id": "r1", "scores": {"code_quality": 4.0, "documentation": 2.5}, "total_score": 6.5},
            {"id": "r2", "scores": {"code_quality": 1.0, "documentation": 0.0}, "total_score": 1.0},
        ]

    def test_missing_and_invalid_values(self, tmp_path, rubric):
        rows = self._run(
            tmp_path,
            rubric,
            "record_id,code_quality,documentation\nr1,,abc\n",
        )
        assert rows == [
            {
                "id": "r1",
                "scores": {"code_quality": None, "documentation": None},
                "total_score": 0.0,
            }
        ]

    def test_empty_input(self, tmp_path, rubric):
        assert self._run(tmp_path, rubric, "id,code_quality\n") == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
