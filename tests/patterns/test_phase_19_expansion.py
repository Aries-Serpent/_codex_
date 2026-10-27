"""
Phase 19 Pattern Library Expansion - Validation Tests

Validate the documented P-041 through P-060 catalog contracts.

Confidence and evidence labels are declarations in the documents, not fresh
measurements of production readiness or proof of Phase 19 completion.
"""

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PATTERN_DIR = ROOT / ".codex/patterns"
PATTERN_IDS = tuple(f"P-{i:03}" for i in range(41, 61))


def pattern_path(pattern_id):
    matches = sorted(PATTERN_DIR.glob(f"{pattern_id}_*.md"))
    assert len(matches) == 1, f"{pattern_id}: expected one document, found {matches}"
    return matches[0]


def metadata(content, field):
    matches = re.findall(rf"^\*\*{re.escape(field)}\*\*:[ \t]*(.+?)\s*$", content, re.M)
    assert len(matches) == 1, f"Expected one nonempty {field} declaration"
    return matches[0]


def confidence(pattern_id):
    value = metadata(pattern_path(pattern_id).read_text(encoding="utf-8"), "Confidence")
    assert re.fullmatch(r"(?:0\.\d+|1\.0+)", value), f"{pattern_id}: invalid confidence {value}"
    return float(value)


def section(content, heading):
    match = re.search(rf"^(#{{2,3}}) {re.escape(heading)}\s*$", content, re.M)
    assert match, f"Missing section {heading!r}"
    tail = content[match.end() :]
    end = re.search(rf"^#{{1,{len(match[1])}}} ", tail, re.M)
    body = tail[: end.start()] if end else tail
    assert body.strip(), f"Empty section {heading!r}"
    return body


def validate_document(pattern_id):
    content = pattern_path(pattern_id).read_text(encoding="utf-8")
    assert content.startswith(f"# {pattern_id}:"), f"{pattern_id}: incorrect identity"
    confidence(pattern_id)
    for field in ("Category", "Phase Introduced", "Evidence Source"):
        metadata(content, field)
    success_rate = metadata(content, "Success Rate")
    assert re.fullmatch(r"\d+%", success_rate), f"{pattern_id}: invalid success rate"
    assert 0 <= int(success_rate[:-1]) <= 100
    for heading in (
        "Description",
        "Context",
        "Risk Assessment",
        "Related Patterns",
        "Production Validation",
    ):
        section(content, heading)
    # Both published templates contain explicit outcome criteria. P-042..P-050
    # put these under Implementation Guidance / Success Metrics, not a missing field.
    heading = (
        "Success Criteria"
        if re.search(r"^## Success Criteria$", content, re.M)
        else "Success Metrics"
    )
    criteria = section(content, heading)
    assert (
        len(re.findall(r"^(?:- |✅ )\S", criteria, re.M)) >= 4
    ), f"{pattern_id}: incomplete criteria"
    risk = section(content, "Risk Assessment")
    assert "**Risk**:" in risk and "**Mitigation**:" in risk
    return content


def validate_evidence(pattern_id):
    content = pattern_path(pattern_id).read_text(encoding="utf-8")
    source = metadata(content, "Evidence Source")
    assert re.search(r"Phase (?:17|18)", source), f"{pattern_id}: missing campaign provenance"
    validation = section(content, "Production Validation")
    assert re.search(
        r"Phase (?:17|18)", validation
    ), f"{pattern_id}: missing historical validation attribution"


class TestPhase19PatternExpansion:
    """Test suite for Phase 19 pattern library expansion (P-041 through P-060)"""

    PATTERN_DIR = PATTERN_DIR
    CONFIDENCE_THRESHOLD = 0.89  # Minimum confidence for new patterns

    @pytest.mark.parametrize(
        "pattern_id,expected_confidence",
        [
            ("P-041", 0.92),  # Model Versioning & Rollback
            ("P-042", 0.93),  # A/B Testing Infrastructure
            ("P-043", 0.91),  # Model Quantization
            ("P-044", 0.90),  # ML Pipeline Monitoring
            ("P-045", 0.89),  # Federated ML Updates
            ("P-046", 0.93),  # Blue-Green Deployment
            ("P-047", 0.92),  # Canary Release Rollout
            ("P-048", 0.91),  # Stability Monitoring
            ("P-049", 0.93),  # Automated Rollback
            ("P-050", 0.90),  # Incident Response
            ("P-051", 0.92),  # DAG Orchestration
            ("P-052", 0.91),  # Config Drift
            ("P-053", 0.89),  # Self-Service Automation
            ("P-054", 0.90),  # Multi-Environment
            ("P-055", 0.92),  # Health Check Integration
            ("P-056", 0.90),  # Trace Correlation
            ("P-057", 0.89),  # Log Aggregation
            ("P-058", 0.91),  # Metrics Aggregation
            ("P-059", 0.92),  # Anomaly Detection
            ("P-060", 0.91),  # Critical Path Analysis
        ],
    )
    def test_pattern_confidence_score(self, pattern_id, expected_confidence):
        """Verify each pattern has target confidence score"""
        assert (
            expected_confidence >= self.CONFIDENCE_THRESHOLD
        ), f"{pattern_id}: Confidence {expected_confidence} below threshold {self.CONFIDENCE_THRESHOLD}"
        assert confidence(pattern_id) == pytest.approx(
            expected_confidence
        ), f"{pattern_id}: declared confidence differs from catalog contract"

    @pytest.mark.parametrize(
        "pattern_id",
        [
            "P-041",
            "P-042",
            "P-043",
            "P-044",
            "P-045",
            "P-046",
            "P-047",
            "P-048",
            "P-049",
            "P-050",
            "P-051",
            "P-052",
            "P-053",
            "P-054",
            "P-055",
            "P-056",
            "P-057",
            "P-058",
            "P-059",
            "P-060",
        ],
    )
    def test_pattern_file_exists(self, pattern_id):
        """Verify pattern documentation file exists"""
        assert pattern_path(pattern_id).is_file()

    @pytest.mark.parametrize(
        "pattern_id",
        [
            "P-041",
            "P-042",
            "P-043",
            "P-044",
            "P-045",
            "P-046",
            "P-047",
            "P-048",
            "P-049",
            "P-050",
            "P-051",
            "P-052",
            "P-053",
            "P-054",
            "P-055",
            "P-056",
            "P-057",
            "P-058",
            "P-059",
            "P-060",
        ],
    )
    def test_pattern_documentation_completeness(self, pattern_id):
        """Verify pattern has required documentation sections"""
        validate_document(pattern_id)

    @pytest.mark.parametrize(
        "pattern_id,category",
        [
            ("P-041", "ML Deployment"),
            ("P-042", "ML Deployment"),
            ("P-043", "ML Deployment"),
            ("P-044", "ML Deployment"),
            ("P-045", "ML Deployment"),
            ("P-046", "Production Release"),
            ("P-047", "Production Release"),
            ("P-048", "Production Release"),
            ("P-049", "Production Release"),
            ("P-050", "Production Release"),
            ("P-051", "Advanced Automation"),
            ("P-052", "Advanced Automation"),
            ("P-053", "Advanced Automation"),
            ("P-054", "Advanced Automation"),
            ("P-055", "Advanced Automation"),
            ("P-056", "Observability"),
            ("P-057", "Observability"),
            ("P-058", "Observability"),
            ("P-059", "Observability"),
            ("P-060", "Observability"),
        ],
    )
    def test_pattern_category_classification(self, pattern_id, category):
        """Verify pattern has correct category classification"""
        content = pattern_path(pattern_id).read_text(encoding="utf-8")
        assert (
            metadata(content, "Category") == category
        ), f"{pattern_id}: Expected category '{category}' not found in documentation"

    def test_total_pattern_count(self):
        """Verify 20 new patterns added (P-041 through P-060)"""
        paths = [pattern_path(pattern_id) for pattern_id in PATTERN_IDS]
        assert len(set(paths)) == 20
        assert paths[0].name.startswith("P-041_")
        assert paths[-1].name.startswith("P-060_")

    def test_pattern_library_average_confidence(self):
        """Verify pattern library average confidence ≥0.90"""
        new_confidences = [confidence(pattern_id) for pattern_id in PATTERN_IDS]

        avg_confidence = sum(new_confidences) / len(new_confidences)
        assert avg_confidence >= 0.90, f"Average confidence {avg_confidence:.3f} below target 0.90"

        # Verify all individual patterns meet minimum threshold
        for conf in new_confidences:
            assert conf >= 0.89, f"Pattern confidence {conf} below minimum 0.89"

    def test_evidence_based_patterns(self):
        """Verify all patterns are evidence-based from Phase 17-18"""
        for pattern_id in PATTERN_IDS:
            validate_evidence(pattern_id)

    def test_no_breaking_changes_to_existing_patterns(self):
        """Verify new patterns don't break existing P-001 to P-040"""
        old_paths = [pattern_path(f"P-{i:03}") for i in range(1, 41)]
        new_paths = [pattern_path(pattern_id) for pattern_id in PATTERN_IDS]
        assert len(set(old_paths)) == 40
        assert set(old_paths).isdisjoint(new_paths)

    def test_pattern_cross_references(self):
        """Verify new patterns cross-reference related patterns appropriately"""
        # P-041 should reference related patterns like P-046, P-049, P-055
        p041 = pattern_path("P-041").read_text()
        assert "P-046" in p041 or "P-049" in p041, "P-041 missing expected cross-references"

        # P-046 should reference related patterns like P-047
        p046 = pattern_path("P-046").read_text()
        assert (
            "P-047" in p046 or "rollback" in p046.lower()
        ), "P-046 missing expected cross-references"
        for pattern_id in PATTERN_IDS:
            content = pattern_path(pattern_id).read_text()
            refs = re.findall(r"P-\d{3}", section(content, "Related Patterns"))
            assert refs, f"{pattern_id}: missing related pattern IDs"
            for ref in refs:
                assert pattern_path(ref).is_file()

    def test_validation_test_coverage(self):
        """Verify validation test coverage for all 20 new patterns"""
        tree = ast.parse(Path(__file__).read_text())
        expected = {
            "test_pattern_confidence_score",
            "test_pattern_file_exists",
            "test_pattern_documentation_completeness",
            "test_pattern_category_classification",
        }
        checked = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in expected:
                decorator = node.decorator_list[0]
                rows = ast.literal_eval(decorator.args[1])
                ids = {row[0] if isinstance(row, tuple) else row for row in rows}
                assert ids == set(PATTERN_IDS), node.name
                checked.add(node.name)
        assert checked == expected


class TestPatternValidation:
    """Integration tests for pattern validation framework"""

    def test_phase_19_expansion_metrics(self):
        """Compute catalog metrics; do not infer campaign completion."""
        metrics = {
            "patterns_created": len({pattern_path(pid) for pid in PATTERN_IDS}),
            "confidence_avg": sum(confidence(pid) for pid in PATTERN_IDS) / len(PATTERN_IDS),
            "min_confidence": min(confidence(pid) for pid in PATTERN_IDS),
            "groups": {metadata(pattern_path(pid).read_text(), "Category") for pid in PATTERN_IDS},
        }

        assert metrics["patterns_created"] >= 15, "Minimum 15 patterns required"
        assert metrics["confidence_avg"] >= 0.90, "Average confidence must be ≥0.90"
        assert metrics["min_confidence"] >= 0.89
        assert metrics["groups"] == {
            "ML Deployment",
            "Production Release",
            "Advanced Automation",
            "Observability",
        }

    def test_pattern_library_integration(self):
        """Verify new patterns integrate with existing library"""
        pattern_index = PATTERN_DIR / "PATTERN_INDEX.md"
        content = pattern_index.read_text()
        for pattern_id in PATTERN_IDS:
            filename = pattern_path(pattern_id).name
            assert re.search(
                rf"\[{pattern_id}\]\({re.escape(filename)}\)", content
            ), f"Pattern index missing canonical link for {pattern_id}"

    def test_complete_documentation_set(self):
        """Verify complete documentation for all new patterns"""
        for pattern_id in PATTERN_IDS:
            validate_document(pattern_id)


class TestPhase19ComplianceGates:
    """Compliance gate tests for Phase 19 expansion"""

    def test_gate_minimum_pattern_count(self):
        """GATE: Minimum 15 patterns required"""
        pattern_files = {pattern_path(pid) for pid in PATTERN_IDS}
        assert len(pattern_files) >= 15, "GATE FAILED: <15 patterns documented"

    def test_gate_average_confidence(self):
        """GATE: Average confidence ≥0.90"""
        confidences = [confidence(pid) for pid in PATTERN_IDS]
        avg = sum(confidences) / len(confidences)
        assert avg >= 0.90, f"GATE FAILED: Confidence {avg:.3f} < 0.90"

    def test_gate_evidence_based(self):
        """GATE: Each document attributes its historical evidence source."""
        for pattern_id in PATTERN_IDS:
            validate_evidence(pattern_id)

    def test_gate_validation_pass_rate(self):
        """GATE: All documents meet schema; pytest, not this test, reports pass rate."""
        for pattern_id in PATTERN_IDS:
            validate_document(pattern_id)

    def test_gate_production_readiness(self):
        """Check documented confidence/provenance, not current production readiness."""
        min_confidence = 0.85
        all_confidences = [confidence(pid) for pid in PATTERN_IDS]
        for pattern_id in PATTERN_IDS:
            validate_evidence(pattern_id)

        below_threshold = [c for c in all_confidences if c < min_confidence]
        assert (
            len(below_threshold) == 0
        ), f"GATE FAILED: {len(below_threshold)} patterns below {min_confidence} confidence"


class TestCatalogContractGuards:
    """Missing records, malformed values and empty criteria must fail."""

    @pytest.mark.parametrize(
        "old,new",
        [
            ("**Confidence**: 0.92", "**Confidence**: not-a-number"),
            ("**Evidence Source**:", "**Removed Field**:"),
            ("## Risk Assessment", "## Removed Risk Section"),
            ("## Success Criteria", "## Removed Criteria Section"),
            ("**Success Rate**: 94%", "**Success Rate**: 194%"),
        ],
    )
    def test_malformed_document_is_rejected(self, tmp_path, monkeypatch, old, new):
        content = pattern_path("P-041").read_text()
        assert old in content
        (tmp_path / "P-041_TEST.md").write_text(content.replace(old, new, 1))
        monkeypatch.setitem(pattern_path.__globals__, "PATTERN_DIR", tmp_path)
        with pytest.raises(AssertionError):
            validate_document("P-041")

    def test_missing_or_duplicate_document_is_rejected(self, tmp_path, monkeypatch):
        monkeypatch.setitem(pattern_path.__globals__, "PATTERN_DIR", tmp_path)
        with pytest.raises(AssertionError):
            pattern_path("P-060")
        for name in ("P-060_FIRST.md", "P-060_DUPLICATE.md"):
            (tmp_path / name).write_text("# duplicate identity")
        with pytest.raises(AssertionError):
            pattern_path("P-060")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
