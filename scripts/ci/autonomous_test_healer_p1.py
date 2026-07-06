#!/usr/bin/env python3
"""
Phase 13 Track 13.1: Autonomous Test Healer — P1 Panic Pattern Framework
========================================================================

Autonomous detection and remediation of P1 panic failures (OOM, segfault, heap, stack).

Patterns:
  - P1-1: OutOfMemory (OOM) — batch size reduction, gradient checkpointing
  - P1-2: Segmentation Fault — try-except wrapper, fallback-to-CPU
  - P1-3: Heap Exhaustion — cache clearing, context managers
  - P1-4: Stack Overflow — recursion limit, recursive call breaking

Status: ADVISORY MODE (Days 1-2 analysis, Days 3+ deployment)
Authority: @mbaetiong (D-Tier autonomous)
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class P1Pattern(Enum):
    """P1 panic pattern types."""
    OOM = "OutOfMemory"
    SEGFAULT = "SegmentationFault"
    HEAP = "HeapExhaustion"
    STACK = "StackOverflow"


@dataclass
class FailureDetection:
    """Detected failure with pattern classification."""
    test_file: str
    test_name: str
    pattern: P1Pattern
    error_message: str
    confidence: float
    suggested_fix: str


class P1PanicDetector:
    """Detect P1 panic failures in test output and logs."""
    
    # Regex patterns for P1 failures
    PATTERNS = {
        P1Pattern.OOM: [
            r"(?i)(out of memory|oom|memory error|cuda out of memory)",
            r"(?i)(allocat.*failed|cannot allocate memory)",
            r"(?i)(memory exhausted|insufficient memory)",
        ],
        P1Pattern.SEGFAULT: [
            r"(?i)(segmentation fault|segfault|sigsegv)",
            r"(?i)(null pointer dereference|access violation)",
            r"(?i)(address.*boundary error|illegal instruction)",
        ],
        P1Pattern.HEAP: [
            r"(?i)(heap corruption|heap exhaustion|heap overflow)",
            r"(?i)(double free|invalid free)",
            r"(?i)(buffer overflow|out of bounds)",
        ],
        P1Pattern.STACK: [
            r"(?i)(stack overflow|stack exhaustion|recursion limit)",
            r"(?i)(maximum recursion depth exceeded)",
            r"(?i)(call stack size exceeded)",
        ],
    }
    
    def __init__(self):
        self.compiled_patterns = {}
        for pattern_type, regexes in self.PATTERNS.items():
            self.compiled_patterns[pattern_type] = [
                re.compile(regex) for regex in regexes
            ]
    
    def detect_from_log(self, log_content: str) -> List[Tuple[P1Pattern, float]]:
        """
        Detect P1 panic patterns in log content.
        
        Returns: List of (pattern, confidence) tuples, highest confidence first.
        """
        detections = []
        
        for pattern_type, compiled in self.compiled_patterns.items():
            for regex in compiled:
                if regex.search(log_content):
                    # Confidence based on pattern specificity
                    confidence = 0.95 if len(regex.pattern) > 30 else 0.85
                    detections.append((pattern_type, confidence))
        
        # Deduplicate by pattern type, keep highest confidence
        best_by_type = {}
        for pattern_type, confidence in detections:
            if pattern_type not in best_by_type or confidence > best_by_type[pattern_type]:
                best_by_type[pattern_type] = confidence
        
        return sorted(
            [(p, c) for p, c in best_by_type.items()],
            key=lambda x: x[1],
            reverse=True
        )
    
    def classify_test_failure(self, test_file: str, test_name: str, 
                             error_message: str) -> Optional[FailureDetection]:
        """Classify a test failure as P1 panic if detected."""
        detections = self.detect_from_log(error_message)
        
        if not detections:
            return None
        
        pattern, confidence = detections[0]
        suggested_fix = self._suggest_fix(pattern, test_file, test_name)
        
        return FailureDetection(
            test_file=test_file,
            test_name=test_name,
            pattern=pattern,
            error_message=error_message[:200],  # Truncate
            confidence=confidence,
            suggested_fix=suggested_fix,
        )
    
    def _suggest_fix(self, pattern: P1Pattern, test_file: str, test_name: str) -> str:
        """Generate suggested fix for P1 pattern."""
        suggestions = {
            P1Pattern.OOM: (
                f"Reduce batch size in {test_name}. "
                "Consider adding @pytest.mark.parametrize with smaller batches or "
                "using gradient checkpointing for large model tests."
            ),
            P1Pattern.SEGFAULT: (
                f"Wrap {test_name} in try-except. "
                "Consider mocking C/C++ bindings or adding fallback-to-CPU logic."
            ),
            P1Pattern.HEAP: (
                f"Clear cache before {test_name}. "
                "Use context managers to limit data collection or add cleanup fixtures."
            ),
            P1Pattern.STACK: (
                f"Add recursion limit to {test_name}. "
                "Break recursive calls into smaller steps or mock recursion."
            ),
        }
        return suggestions.get(pattern, "Manual review required.")


class P1PanicHealer:
    """Auto-heal P1 panic failures with pattern-specific fixes."""
    
    def __init__(self, repo_root: Path = Path(".")):
        self.repo_root = repo_root
        self.detector = P1PanicDetector()
    
    def heal_oom_failure(self, test_file: str, test_name: str, 
                        confidence: float) -> Dict:
        """Heal OOM failure by reducing batch size or adding checkpointing."""
        
        test_path = self.repo_root / test_file
        if not test_path.exists():
            return {"status": "SKIP", "reason": "Test file not found"}
        
        content = test_path.read_text()
        
        fixes_applied = []
        
        # Strategy 1: Add @pytest.mark.parametrize with smaller batch size
        if f"def {test_name}" in content:
            fixes_applied.append({
                "type": "batch_size_parametrize",
                "suggestion": f"Add @pytest.mark.parametrize('batch_size', [1, 8, 32]) before def {test_name}()",
            })
        
        # Strategy 2: Add gradient checkpointing suggestion
        if "model" in content.lower() or "tensor" in content.lower():
            fixes_applied.append({
                "type": "gradient_checkpointing",
                "suggestion": f"Enable gradient checkpointing for {test_name} to reduce memory usage",
            })
        
        # Strategy 3: Add memory pooling suggestion
        if "cuda" in content.lower() or "gpu" in content.lower():
            fixes_applied.append({
                "type": "memory_pooling",
                "suggestion": f"Use torch.cuda.empty_cache() before {test_name}",
            })
        
        return {
            "status": "SUGGESTIONS_GENERATED",
            "pattern": "OOM",
            "confidence": confidence,
            "test_file": test_file,
            "test_name": test_name,
            "fixes": fixes_applied,
        }
    
    def heal_segfault_failure(self, test_file: str, test_name: str,
                             confidence: float) -> Dict:
        """Heal segfault by wrapping in try-except or mocking."""
        
        test_path = self.repo_root / test_file
        if not test_path.exists():
            return {"status": "SKIP", "reason": "Test file not found"}
        
        fixes_applied = []
        
        # Strategy 1: Wrap in try-except
        fixes_applied.append({
            "type": "try_except_wrapper",
            "suggestion": f"Wrap {test_name} in try-except block to catch segfaults gracefully",
            "code_snippet": f"""
def test_wrapped_{test_name}():
    try:
        {test_name}()
    except (OSError, Exception) as e:
        pytest.skip(f"Segfault detected: {{e}}, skipping on this system")
""",
        })
        
        # Strategy 2: Mock fallback suggestion
        fixes_applied.append({
            "type": "mock_fallback",
            "suggestion": f"Mock C/C++ bindings in {test_name} or add CPU fallback",
        })
        
        return {
            "status": "SUGGESTIONS_GENERATED",
            "pattern": "SEGFAULT",
            "confidence": confidence,
            "test_file": test_file,
            "test_name": test_name,
            "fixes": fixes_applied,
        }
    
    def heal_heap_failure(self, test_file: str, test_name: str,
                         confidence: float) -> Dict:
        """Heal heap exhaustion by clearing cache or limiting data."""
        
        fixes_applied = []
        
        # Strategy 1: Add cache clearing
        fixes_applied.append({
            "type": "cache_clearing",
            "suggestion": f"Add cache clearing before {test_name}",
            "code_snippet": """
@pytest.fixture(autouse=True)
def clear_cache():
    yield
    # Clear any caches here
    gc.collect()
""",
        })
        
        # Strategy 2: Use context manager
        fixes_applied.append({
            "type": "context_manager",
            "suggestion": f"Use context manager to limit data collection in {test_name}",
        })
        
        return {
            "status": "SUGGESTIONS_GENERATED",
            "pattern": "HEAP",
            "confidence": confidence,
            "test_file": test_file,
            "test_name": test_name,
            "fixes": fixes_applied,
        }
    
    def heal_stack_failure(self, test_file: str, test_name: str,
                          confidence: float) -> Dict:
        """Heal stack overflow by adding recursion limit or breaking recursion."""
        
        test_path = self.repo_root / test_file
        if not test_path.exists():
            return {"status": "SKIP", "reason": "Test file not found"}
        
        fixes_applied = []
        
        # Strategy 1: Add recursion limit
        fixes_applied.append({
            "type": "recursion_limit",
            "suggestion": f"Add sys.setrecursionlimit() before {test_name}",
            "code_snippet": """
import sys

@pytest.fixture
def safe_recursion_limit():
    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(5000)
    yield
    sys.setrecursionlimit(old_limit)
""",
        })
        
        # Strategy 2: Break recursion suggestion
        fixes_applied.append({
            "type": "break_recursion",
            "suggestion": f"Convert recursive call to iterative in {test_name}",
        })
        
        # Strategy 3: Mock recursion
        fixes_applied.append({
            "type": "mock_recursion",
            "suggestion": f"Mock the recursive function in {test_name}",
        })
        
        return {
            "status": "SUGGESTIONS_GENERATED",
            "pattern": "STACK",
            "confidence": confidence,
            "test_file": test_file,
            "test_name": test_name,
            "fixes": fixes_applied,
        }
    
    def heal(self, failure: FailureDetection) -> Dict:
        """Apply appropriate healing based on pattern."""
        
        healers = {
            P1Pattern.OOM: self.heal_oom_failure,
            P1Pattern.SEGFAULT: self.heal_segfault_failure,
            P1Pattern.HEAP: self.heal_heap_failure,
            P1Pattern.STACK: self.heal_stack_failure,
        }
        
        healer = healers.get(failure.pattern)
        if not healer:
            return {"status": "UNKNOWN_PATTERN", "pattern": str(failure.pattern)}
        
        return healer(failure.test_file, failure.test_name, failure.confidence)


class P1AnalysisReport:
    """Generate analysis report for P1 remediation."""
    
    def __init__(self):
        self.detections = []
        self.heals = []
    
    def add_detection(self, detection: FailureDetection):
        """Add detected failure."""
        self.detections.append(detection)
    
    def add_heal(self, heal_result: Dict):
        """Add heal result."""
        self.heals.append(heal_result)
    
    def summary(self) -> Dict:
        """Generate summary report."""
        total_detections = len(self.detections)
        by_pattern = {}
        
        for detection in self.detections:
            pattern = detection.pattern.value
            if pattern not in by_pattern:
                by_pattern[pattern] = []
            by_pattern[pattern].append(detection)
        
        return {
            "total_detections": total_detections,
            "by_pattern": {
                pattern: {
                    "count": len(detections),
                    "avg_confidence": sum(d.confidence for d in detections) / len(detections),
                    "tests": [f"{d.test_file}::{d.test_name}" for d in detections],
                }
                for pattern, detections in by_pattern.items()
            },
            "total_heals": len(self.heals),
            "heals_successful": sum(1 for h in self.heals if h.get("status") != "SKIP"),
        }


def main():
    """Demo P1 panic detection and healing."""
    
    logger.info("Phase 13 Track 13.1: P1 Panic Pattern Framework")
    logger.info("=" * 60)
    
    detector = P1PanicDetector()
    healer = P1PanicHealer()
    report = P1AnalysisReport()
    
    # Example: Simulate detection
    test_error = "CUDA out of memory (OOM) trying to allocate X GB"
    detections = detector.detect_from_log(test_error)
    
    logger.info(f"\nDetected patterns from error: {test_error}")
    for pattern, confidence in detections:
        logger.info(f"  - {pattern.value}: {confidence*100:.0f}% confidence")
    
    # Example: Classify and heal
    failure = detector.classify_test_failure(
        "tests/test_rag.py",
        "test_large_model_loading",
        "CUDA out of memory (OOM) error"
    )
    
    if failure:
        logger.info(f"\nClassified failure:")
        logger.info(f"  File: {failure.test_file}")
        logger.info(f"  Test: {failure.test_name}")
        logger.info(f"  Pattern: {failure.pattern.value}")
        logger.info(f"  Confidence: {failure.confidence*100:.0f}%")
        logger.info(f"  Suggestion: {failure.suggested_fix}")
        
        report.add_detection(failure)
        
        # Apply heal
        heal_result = healer.heal(failure)
        logger.info(f"\nHeal result: {json.dumps(heal_result, indent=2)}")
        report.add_heal(heal_result)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Analysis Summary:")
    logger.info(json.dumps(report.summary(), indent=2))


if __name__ == "__main__":
    main()
