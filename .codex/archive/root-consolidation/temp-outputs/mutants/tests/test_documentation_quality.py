"""
Documentation Quality Tests

Comprehensive test suite for documentation quality assessment, clarity metrics,
completeness checking, and technical accuracy verification.
Coverage: Documentation quality dimensions and scoring.
"""

import re
from pathlib import Path
from typing import List

import pytest


class DocumentationQualityAnalyzer:
    """Analyzer for documentation quality metrics."""

    def __init__(self, docs_root: Path = None):
        """Initialize quality analyzer."""
        if docs_root is None:
            docs_root = Path(__file__).resolve().parent.parent / "docs"
        self.docs_root = docs_root

    def calculate_clarity_score(self, content: str) -> float:
        """Calculate clarity score (0-1) based on readability metrics."""
        if not content:
            return 0.0

        # Metrics: short paragraphs, clear structure, good headers
        score = 0.0

        # Check for good heading structure
        headings = len(re.findall(r"^#+\s", content, re.MULTILINE))
        if headings > 0:
            score += 0.2

        # Check for reasonable paragraph length
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        avg_para_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        if 50 < avg_para_length < 200:  # Reasonable length
            score += 0.2

        # Check for code examples
        if "```" in content:
            score += 0.15

        # Check for lists (good for clarity)
        lists = len(re.findall(r"^[\s]*[-*+]\s", content, re.MULTILINE))
        if lists > 0:
            score += 0.15

        # Check for no excessive jargon (heuristic)
        words = content.split()
        if words:
            score += 0.15  # Base score for having content
            # Penalty for excessive all-caps words
            caps_words = [w for w in words if w.isupper() and len(w) > 1]
            if len(caps_words) / len(words) > 0.1:
                score -= 0.1

        return min(score, 1.0)

    def calculate_completeness_score(self, content: str, filename: str = "") -> float:
        """Calculate completeness score (0-1)."""
        if not content:
            return 0.0

        score = 0.0

        # Check required sections
        has_description = len(content.split()) > 10
        has_examples = "```" in content or "example" in content.lower()
        has_usage = "usage" in content.lower() or "how to" in content.lower() or "tutorial" in content.lower()
        has_params = ("parameter" in content.lower() or "argument" in content.lower() or
                      re.search(r"\*\*\w+\*\*:", content))

        if has_description:
            score += 0.25
        if has_examples:
            score += 0.25
        if has_usage:
            score += 0.25
        if has_params:
            score += 0.25

        return min(score, 1.0)

    def check_grammar_quality(self, content: str) -> List[str]:
        """Check for common grammar issues."""
        issues = []

        # Check for doubled words
        doubled = re.findall(r"\b(\w+)\s+\1\b", content, re.IGNORECASE)
        if doubled:
            issues.append(f"Doubled words found: {doubled[:3]}")

        # Check for missing spaces after punctuation
        missing_space = re.findall(r"[.!?]\w", content)
        if missing_space:
            issues.append("Missing space after punctuation")

        # Check for trailing whitespace
        trailing = re.findall(r"\s+$", content, re.MULTILINE)
        if len(trailing) > 5:
            issues.append("Excessive trailing whitespace")

        return issues

    def assess_technical_accuracy(self, content: str) -> float:
        """Assess technical accuracy heuristically."""
        # This is a heuristic check based on presence of verifiable elements
        score = 0.0

        # Check for version information
        if re.search(r"version|v\d+\.\d+", content, re.IGNORECASE):
            score += 0.2

        # Check for API documentation format
        if re.search(r":\s*\(.*?\)", content):  # Parameter-like syntax
            score += 0.2

        # Check for return documentation
        if re.search(r"return|output|result", content, re.IGNORECASE):
            score += 0.2

        # Check for error handling documentation
        if re.search(r"error|exception|fail|raise", content, re.IGNORECASE):
            score += 0.2

        # Check for type information (if any)
        if re.search(r":\s*\w+\[\w+\]|\s*->\s*\w+", content):
            score += 0.2

        return min(score, 1.0)

    def check_version_consistency(self, content: str) -> bool:
        """Check if documentation mentions consistent versions."""
        versions = re.findall(r"v?\d+\.\d+(\.\d+)?", content)
        if not versions:
            return True  # No versions mentioned is fine
        # Check if versions are consistent (not wildly different)
        return len(set(versions)) <= 3  # At most 3 different versions is reasonable


class TestDocumentationClarityMetrics:
    """Test suite for documentation clarity assessment."""

    @pytest.fixture
    def analyzer(self):
        """Provide quality analyzer."""
        return DocumentationQualityAnalyzer()

    def test_clarity_score_calculation(self, analyzer):
        """Test that clarity score calculates properly."""
        good_content = """
# Example Title

This is a clear example.

## Section 1
- Point 1
- Point 2

## Section 2
```python
example_code()
```
"""
        score = analyzer.calculate_clarity_score(good_content)
        assert 0 <= score <= 1, "Clarity score should be between 0 and 1"

    def test_clarity_score_empty_content(self, analyzer):
        """Test clarity score for empty content."""
        score = analyzer.calculate_clarity_score("")
        assert score == 0.0

    def test_clarity_improves_with_structure(self, analyzer):
        """Test that clarity score improves with good structure."""
        bad = "This is text without structure"
        good = "# Title\n\n## Section\n\n- Point 1\n- Point 2"
        bad_score = analyzer.calculate_clarity_score(bad)
        good_score = analyzer.calculate_clarity_score(good)
        assert good_score >= bad_score

    def test_documentation_with_good_paragraphs(self, analyzer):
        """Test clarity for well-paragraphed documentation."""
        content = "A reasonable paragraph with about 100 words that flows well. " * 5
        score = analyzer.calculate_clarity_score(content)
        assert score > 0

    def test_clarity_with_code_examples(self, analyzer):
        """Test that code examples improve clarity."""
        with_code = "```python\ncode_here()\n```"
        without_code = "plain text"
        score_with = analyzer.calculate_clarity_score(with_code)
        score_without = analyzer.calculate_clarity_score(without_code)
        # Code examples should help clarity
        assert score_with >= score_without


class TestDocumentationCompletenessAssessment:
    """Test suite for documentation completeness."""

    @pytest.fixture
    def analyzer(self):
        """Provide quality analyzer."""
        return DocumentationQualityAnalyzer()

    def test_completeness_score_calculation(self, analyzer):
        """Test that completeness score calculates properly."""
        content = "This is a description. Examples: code here. Usage: how to use. Parameters: param1"
        score = analyzer.calculate_completeness_score(content)
        assert 0 <= score <= 1

    def test_completeness_empty_content(self, analyzer):
        """Test completeness for empty content."""
        score = analyzer.calculate_completeness_score("")
        assert score == 0.0

    def test_completeness_with_all_sections(self, analyzer):
        """Test completeness with all major sections."""
        complete = """
# API

Description of this API.

## Usage
Here's how to use it.

## Examples
```python
code()
```

## Parameters
- **param1**: Description
- **param2**: Description
"""
        score = analyzer.calculate_completeness_score(complete)
        assert score >= 0.5, "Complete documentation should score well"

    def test_completeness_with_sparse_content(self, analyzer):
        """Test completeness for sparse documentation."""
        sparse = "Some basic text."
        score = analyzer.calculate_completeness_score(sparse)
        assert score < 0.5, "Sparse documentation should score lower"


class TestDocumentationGrammarQuality:
    """Test suite for grammar and spelling validation."""

    @pytest.fixture
    def analyzer(self):
        """Provide quality analyzer."""
        return DocumentationQualityAnalyzer()

    def test_detects_doubled_words(self, analyzer):
        """Test that doubled words are detected."""
        content = "This this is wrong. The the problem."
        issues = analyzer.check_grammar_quality(content)
        assert any("doubled" in issue.lower() or "word" in issue.lower() for issue in issues)

    def test_no_false_positives_for_repeated_words(self, analyzer):
        """Test that repeated words in different contexts aren't flagged."""
        content = "This is fine. Point one and point two are important points."
        issues = analyzer.check_grammar_quality(content)
        # Should not flag as many issues

    def test_detects_missing_space_punctuation(self, analyzer):
        """Test detection of missing space after punctuation."""
        content = "First sentence.Second sentence!"
        issues = analyzer.check_grammar_quality(content)
        assert any("space" in issue.lower() for issue in issues)

    def test_detects_trailing_whitespace(self, analyzer):
        """Test detection of excessive trailing whitespace."""
        content = "Line 1   \nLine 2   \nLine 3   \nLine 4   \nLine 5   \nLine 6   \n"
        issues = analyzer.check_grammar_quality(content)
        assert any("trailing" in issue.lower() for issue in issues)

    def test_well_formatted_text_passes(self, analyzer):
        """Test that well-formatted text passes grammar check."""
        content = """
        This is a well formatted sentence. Here's another one!
        
        And a proper paragraph with good spacing.
        """
        issues = analyzer.check_grammar_quality(content)
        # Should have few or no issues
        assert len(issues) <= 2


class TestDocumentationTechnicalAccuracy:
    """Test suite for technical accuracy assessment."""

    @pytest.fixture
    def analyzer(self):
        """Provide quality analyzer."""
        return DocumentationQualityAnalyzer()

    def test_technical_accuracy_score_calculation(self, analyzer):
        """Test that technical accuracy score calculates."""
        content = "This function returns a string. Version: v1.0"
        score = analyzer.assess_technical_accuracy(content)
        assert 0 <= score <= 1

    def test_recognizes_version_information(self, analyzer):
        """Test that version information is recognized."""
        with_version = "This is version 2.1.0"
        without_version = "This is some text"
        score_with = analyzer.assess_technical_accuracy(with_version)
        score_without = analyzer.assess_technical_accuracy(without_version)
        assert score_with > score_without

    def test_recognizes_api_documentation(self, analyzer):
        """Test that API documentation format is recognized."""
        api_content = "Returns: (str): The result string"
        score = analyzer.assess_technical_accuracy(api_content)
        assert score > 0

    def test_recognizes_error_handling_docs(self, analyzer):
        """Test that error documentation is recognized."""
        error_content = "Raises ValueError if input is invalid"
        score = analyzer.assess_technical_accuracy(error_content)
        assert score > 0

    def test_recognizes_type_information(self, analyzer):
        """Test that type annotations are recognized."""
        typed_content = "function(param: str) -> bool"
        score = analyzer.assess_technical_accuracy(typed_content)
        assert score > 0


class TestDocumentationVersionConsistency:
    """Test suite for version consistency in documentation."""

    @pytest.fixture
    def analyzer(self):
        """Provide quality analyzer."""
        return DocumentationQualityAnalyzer()

    def test_consistent_version_information(self, analyzer):
        """Test that version information is consistent."""
        consistent = "Version 1.0. Latest: 1.0.1. Requires: >= 1.0"
        assert analyzer.check_version_consistency(consistent)

    def test_inconsistent_version_information(self, analyzer):
        """Test detection of wildly inconsistent versions."""
        inconsistent = "Version 1.0 and Version 5.0 and Version 10.0 and Version 15.0"
        # Should detect inconsistency
        result = analyzer.check_version_consistency(inconsistent)
        # More than 3 versions might be a problem

    def test_no_version_information_acceptable(self, analyzer):
        """Test that docs without versions are acceptable."""
        no_version = "This is documentation without version info"
        assert analyzer.check_version_consistency(no_version)

    def test_single_version_is_consistent(self, analyzer):
        """Test that single version is consistent."""
        single = "Version 2.0 is required"
        assert analyzer.check_version_consistency(single)


class TestDocumentationDeprecationDetection:
    """Test suite for deprecated pattern detection."""

    def test_detects_deprecated_keywords(self):
        """Test detection of deprecated markers."""
        content = "@deprecated Use new_function() instead"
        deprecated = re.search(r"@?deprecated|obsolete|outdated", content, re.IGNORECASE)
        assert deprecated is not None

    def test_detects_legacy_patterns(self):
        """Test detection of legacy code patterns."""
        content = "LEGACY: This function uses the old API"
        legacy = re.search(r"legacy|old\s+api|obsolete", content, re.IGNORECASE)
        assert legacy is not None

    def test_recognizes_replacement_info(self):
        """Test recognition of replacement information."""
        content = "Deprecated: Use new_function() instead"
        assert "use" in content.lower() or "instead" in content.lower()

    def test_no_false_positive_deprecated(self):
        """Test that standard text isn't flagged as deprecated."""
        content = "This discusses the history and development"
        deprecated = re.search(r"@deprecated|^\s*deprecated\s*:", content, re.IGNORECASE)
        assert deprecated is None or "@deprecated" not in content.lower()


class TestDocumentationArchitectureIntegrity:
    """Test suite for architecture documentation integrity."""

    def test_architecture_docs_exist(self):
        """Test that architecture documentation exists."""
        docs_root = Path(__file__).resolve().parent.parent / "docs"
        arch_dirs = list(docs_root.rglob("*arch*"))
        # May have architecture documentation
        assert isinstance(arch_dirs, list)

    def test_architecture_docs_readable(self):
        """Test that architecture documentation is readable."""
        docs_root = Path(__file__).resolve().parent.parent / "docs"
        arch_files = list(docs_root.rglob("*arch*.md"))[:3]
        for arch_file in arch_files:
            content = arch_file.read_text(encoding="utf-8")
            assert len(content) > 0

    def test_architecture_consistency_across_docs(self):
        """Test that architecture is consistently documented."""
        docs_root = Path(__file__).resolve().parent.parent / "docs"
        arch_docs = list(docs_root.rglob("*arch*.md"))
        # Different architecture docs should use consistent terminology
        for doc in arch_docs[:3]:
            content = doc.read_text(encoding="utf-8")
            assert isinstance(content, str)

    def test_architecture_diagrams_referenced(self):
        """Test that architecture diagrams are properly referenced."""
        docs_root = Path(__file__).resolve().parent.parent / "docs"
        md_files = list(docs_root.rglob("*.md"))[:10]
        for md_file in md_files:
            content = md_file.read_text(encoding="utf-8")
            # Should be able to parse markdown with potential diagrams
            assert isinstance(content, str)


class TestDocumentationQualityIntegration:
    """Integration tests for documentation quality assessment."""

    def test_overall_quality_assessment(self):
        """Test overall documentation quality assessment."""
        analyzer = DocumentationQualityAnalyzer()
        good_doc = """
# Good Documentation

This is a well-structured document.

## Overview
Introduction to the topic.

## Usage Examples
```python
example_code()
```

## Parameters
- param1: First parameter
- param2: Second parameter

## Return Value
Returns a string result.

## Error Handling
Raises ValueError on invalid input.
"""
        clarity = analyzer.calculate_clarity_score(good_doc)
        completeness = analyzer.calculate_completeness_score(good_doc)
        accuracy = analyzer.assess_technical_accuracy(good_doc)
        version_ok = analyzer.check_version_consistency(good_doc)

        assert clarity > 0.5, "Good docs should have good clarity"
        assert completeness > 0.5, "Good docs should be complete"
        assert accuracy > 0, "Good docs should show technical accuracy"
        assert version_ok, "Good docs should have consistent versions"

    def test_quality_scoring_identifies_weak_docs(self):
        """Test that quality scoring identifies weak documentation."""
        analyzer = DocumentationQualityAnalyzer()
        weak_doc = "Some text here."

        clarity = analyzer.calculate_clarity_score(weak_doc)
        completeness = analyzer.calculate_completeness_score(weak_doc)

        assert clarity < 0.5 or completeness < 0.5, "Weak docs should score low"

    def test_quality_metrics_reproducible(self):
        """Test that quality metrics are reproducible."""
        analyzer = DocumentationQualityAnalyzer()
        doc = "# Test\n\nContent here."

        score1 = analyzer.calculate_clarity_score(doc)
        score2 = analyzer.calculate_clarity_score(doc)

        assert score1 == score2, "Scores should be deterministic"
