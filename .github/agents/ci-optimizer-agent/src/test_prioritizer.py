"""
Test Prioritizer for CI Optimizer Agent
Optimizes test execution order for faster feedback
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import random

RANDOM_SEED = 49

@dataclass
class TestInfo:
    """Test information"""
    name: str
    duration_ms: float
    failure_rate: float
    last_failure: Optional[str]
    priority_score: float = 0.0

class TestPrioritizer:
    """Prioritize test execution order"""
    
    def __init__(self, seed: int = RANDOM_SEED):
        self.seed = seed
        self._rng = random.Random(seed)
        self.tests: List[TestInfo] = []
        self.execution_history: List[Dict[str, Any]] = []
        self.initialized = True
    
    def add_test(self, name: str, duration_ms: float, failure_rate: float, 
                 last_failure: Optional[str] = None) -> TestInfo:
        """Add test to prioritizer"""
        test = TestInfo(
            name=name,
            duration_ms=duration_ms,
            failure_rate=failure_rate,
            last_failure=last_failure
        )
        test.priority_score = self._calculate_priority(test)
        self.tests.append(test)
        return test
    
    def _calculate_priority(self, test: TestInfo) -> float:
        """Calculate test priority score"""
        # Higher priority = run first
        # Factors: failure rate (40%), recency (30%), speed (30%)
        failure_score = test.failure_rate * 0.4
        recency_score = 0.3 if test.last_failure else 0.0
        speed_score = (1.0 - min(test.duration_ms / 10000, 1.0)) * 0.3
        return failure_score + recency_score + speed_score
    
    def get_prioritized_order(self) -> List[TestInfo]:
        """Get tests in prioritized order"""
        return sorted(self.tests, key=lambda t: t.priority_score, reverse=True)
    
    def optimize_for_time(self, max_time_ms: float) -> List[TestInfo]:
        """Select tests that fit within time budget"""
        prioritized = self.get_prioritized_order()
        selected = []
        total_time = 0.0
        
        for test in prioritized:
            if total_time + test.duration_ms <= max_time_ms:
                selected.append(test)
                total_time += test.duration_ms
        
        return selected
    
    def record_execution(self, test_name: str, passed: bool, duration_ms: float):
        """Record test execution result"""
        self.execution_history.append({
            "test": test_name,
            "passed": passed,
            "duration_ms": duration_ms
        })
        
        # Update test info
        for test in self.tests:
            if test.name == test_name:
                if not passed:
                    test.last_failure = "recent"
                    test.failure_rate = min(test.failure_rate + 0.1, 1.0)
                test.priority_score = self._calculate_priority(test)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get prioritizer metrics"""
        return {
            "seed": self.seed,
            "total_tests": len(self.tests),
            "execution_history_size": len(self.execution_history),
            "avg_priority": sum(t.priority_score for t in self.tests) / len(self.tests) if self.tests else 0.0,
            "initialized": self.initialized
        }

def create_prioritizer(seed: int = RANDOM_SEED) -> TestPrioritizer:
    """Factory function"""
    return TestPrioritizer(seed=seed)
