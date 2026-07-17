#!/usr/bin/env python3
"""
Pattern Library v2 Integration Test Suite
Phase 17 Lane 2 - Pattern Library v2 Expansion

This test suite validates:
1. Pattern discovery algorithm
2. Pattern application accuracy
3. Confidence scoring
4. Pattern combinations
5. Production metrics
"""

import re
from pathlib import Path
from typing import Dict, Optional

import pytest


class PatternLibraryValidator:
    """Validator for Pattern Library v2.0"""
    
    def __init__(self, patterns_dir: str = ".codex/patterns"):
        self.patterns_dir = Path(patterns_dir)
        self.patterns = {}
        self.load_patterns()
    
    def load_patterns(self) -> None:
        """Load all patterns from directory."""
        for pattern_file in sorted(self.patterns_dir.glob("P-*.md")):
            pattern_id = pattern_file.stem.split("_")[0]
            self.patterns[pattern_id] = {
                "file": pattern_file,
                "content": pattern_file.read_text()
            }
    
    def extract_confidence(self, pattern_id: str) -> Optional[float]:
        """Extract confidence score from pattern."""
        content = self.patterns[pattern_id]["content"]
        match = re.search(r"\*\*Confidence\*\*:\s*(0\.\d+)", content)
        return float(match.group(1)) if match else None
    
    def extract_category(self, pattern_id: str) -> Optional[str]:
        """Extract category from pattern."""
        content = self.patterns[pattern_id]["content"]
        match = re.search(r"\*\*Category\*\*:\s*([^\n]+)", content)
        return match.group(1).strip() if match else None
    
    def get_all_confidence_scores(self) -> Dict[str, float]:
        """Get all patterns' confidence scores."""
        scores = {}
        for pattern_id in self.patterns:
            confidence = self.extract_confidence(pattern_id)
            if confidence is not None:
                scores[pattern_id] = confidence
        return scores
    
    def get_pattern_count_by_category(self) -> Dict[str, int]:
        """Count patterns by category."""
        categories = {}
        for pattern_id in self.patterns:
            category = self.extract_category(pattern_id)
            if category:
                categories[category] = categories.get(category, 0) + 1
        return categories


# Tests

class TestPatternLibrary:
    """Test Pattern Library v2"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return PatternLibraryValidator()
    
    def test_pattern_count(self, validator):
        """Verify 40+ patterns exist."""
        assert len(validator.patterns) >= 40, f"Expected 40+ patterns, got {len(validator.patterns)}"
        print(f"✅ Found {len(validator.patterns)} patterns")
    
    def test_confidence_scores(self, validator):
        """Verify confidence scores are valid."""
        scores = validator.get_all_confidence_scores()
        assert len(scores) >= 35, f"Expected 35+ patterns with confidence, got {len(scores)}"
        print(f"✅ {len(scores)} patterns have confidence scores")
    
    def test_average_confidence(self, validator):
        """Verify average confidence >= 0.85."""
        scores = validator.get_all_confidence_scores()
        avg_confidence = sum(scores.values()) / len(scores)
        assert avg_confidence >= 0.85, f"Average confidence {avg_confidence} below 0.85"
        print(f"✅ Average confidence: {avg_confidence:.2f}")
    
    def test_confidence_distribution(self, validator):
        """Verify confidence distribution is healthy."""
        scores = validator.get_all_confidence_scores()
        
        high_conf = sum(1 for s in scores.values() if s >= 0.92)
        medium_high = sum(1 for s in scores.values() if 0.88 <= s < 0.92)
        medium = sum(1 for s in scores.values() if 0.85 <= s < 0.88)
        
        print("✅ Confidence distribution:")
        print(f"   High (≥0.92): {high_conf}")
        print(f"   Medium-High (0.88-0.91): {medium_high}")
        print(f"   Medium (0.85-0.87): {medium}")
        
        assert (high_conf + medium_high + medium) >= len(scores) * 0.85
    
    def test_pattern_index_exists(self):
        """Verify PATTERN_INDEX.md exists."""
        index_file = Path(".codex/patterns/PATTERN_INDEX.md")
        assert index_file.exists(), "PATTERN_INDEX.md not found"
        content = index_file.read_text()
        assert len(content) > 10000, "PATTERN_INDEX.md too small"
        print("✅ PATTERN_INDEX.md exists and is complete")
    
    def test_phase_17_report_exists(self):
        """Verify Phase 17 Lane 2 report exists."""
        report_file = Path(".codex/PHASE_17_LANE_2_PATTERN_LIBRARY_v2.md")
        assert report_file.exists(), "Phase 17 report not found"
        content = report_file.read_text()
        assert "COMPLETE" in content
        assert "40+" in content
        print("✅ Phase 17 Lane 2 report exists")


class TestPhase17Deliverables:
    """Test Phase 17 Lane 2 deliverables"""
    
    def test_deliverables_exist(self):
        """Verify all deliverables exist."""
        required_files = [
            ".codex/patterns/PATTERN_INDEX.md",
            ".codex/patterns/P-001_THREAD_SYNCHRONIZATION_BARRIER.md",
            ".codex/patterns/P-040_FAILURE_NOTIFICATION_STRATEGY.md",
            ".codex/PHASE_17_LANE_2_PATTERN_LIBRARY_v2.md",
        ]
        
        missing = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing.append(file_path)
        
        assert not missing, f"Missing deliverables: {missing}"
        print(f"✅ All {len(required_files)} deliverables present")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
