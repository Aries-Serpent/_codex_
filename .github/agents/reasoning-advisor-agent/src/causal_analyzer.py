"""Causal Analyzer for Reasoning Advisor Agent"""
from dataclasses import dataclass
from typing import List, Dict, Any
import random

RANDOM_SEED = 50

@dataclass
class CausalRelation:
    cause: str
    effect: str
    confidence: float
    evidence: List[str]

class CausalAnalyzer:
    """Analyze causal relationships in code changes"""
    
    def __init__(self, seed: int = RANDOM_SEED):
        self.seed = seed
        self._rng = random.Random(seed)
        self.relations: List[CausalRelation] = []
        self.initialized = True
    
    def add_relation(self, cause: str, effect: str, confidence: float, evidence: List[str]) -> CausalRelation:
        rel = CausalRelation(cause=cause, effect=effect, confidence=confidence, evidence=evidence)
        self.relations.append(rel)
        return rel
    
    def analyze_impact(self, change: str) -> List[CausalRelation]:
        """Analyze causal impact of a change"""
        return [r for r in self.relations if r.cause == change]
    
    def get_metrics(self) -> Dict[str, Any]:
        return {
            "seed": self.seed,
            "total_relations": len(self.relations),
            "avg_confidence": sum(r.confidence for r in self.relations) / len(self.relations) if self.relations else 0.0,
            "initialized": self.initialized
        }

def create_analyzer(seed: int = RANDOM_SEED) -> CausalAnalyzer:
    return CausalAnalyzer(seed=seed)
