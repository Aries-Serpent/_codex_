"""Security-focused tests for PatternLearner pattern IDs."""

import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent / "src"))

from pattern_learner import PatternLearner


def test_pattern_id_length_and_format():
    """Ensure SHA-256-based IDs follow expected format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        learner = PatternLearner(kb_path=Path(tmpdir))
        pattern_id = learner._generate_pattern_id("failure", "cause")

        assert pattern_id.startswith("pattern_")
        suffix = pattern_id.split("_", 1)[1]
        assert len(suffix) == learner.SHA256_PREFIX_LENGTH
        assert all(ch in "0123456789abcdef" for ch in suffix)


def test_pattern_id_changes_when_content_changes():
    """Ensure different inputs yield different IDs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        learner = PatternLearner(kb_path=Path(tmpdir))
        first = learner._generate_pattern_id("failure", "cause")
        second = learner._generate_pattern_id("failure", "different")

        assert first != second


def test_legacy_lookup_resolves_pattern():
    """Ensure legacy MD5 IDs resolve to the migrated pattern."""
    with tempfile.TemporaryDirectory() as tmpdir:
        learner = PatternLearner(kb_path=Path(tmpdir))
        pattern_id = learner._generate_pattern_id("legacy", "cause")
        legacy_id = learner._legacy_pattern_id("legacy", "cause")
        learner._update_or_create_pattern(
            {
                "pattern_id": pattern_id,
                "failure_type": "legacy",
                "root_cause": "cause",
                "common_symptoms": [],
                "occurrences": 1,
            }
        )

        learner.patterns[pattern_id].legacy_ids.append(legacy_id)
        resolved = learner._resolve_pattern_id(legacy_id)
        assert resolved == pattern_id
