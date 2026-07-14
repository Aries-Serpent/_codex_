"""
Root Cause Inference Engine - Phase 4E Planset 011

Implements backward-chaining root cause inference with probabilistic causal graphs.
Traces anomalies to upstream causes with multi-hop causal chains (5+ levels deep).

Components:
  - CausalGraph: Probabilistic DAG of system dependencies with edge weights
  - BackwardChainer: Multi-hop causal chain tracing with confidence scoring
  - RootCauseInference: End-to-end root cause identification

Target: >80% root cause identification success rate, <1s latency
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict
import heapq

import numpy as np

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class CausalLink:
    """
    Link in causal graph representing cause → effect relationship.
    
    Attributes:
        source: Source metric/system
        target: Target metric/system
        conditional_probability: P(effect | cause) - likelihood cause produces effect
        learned_from_count: Number of historical occurrences
        successful_predictions: How many times this link predicted correctly
        last_updated: When this link was last validated
    """
    source: str
    target: str
    conditional_probability: float  # 0-1
    learned_from_count: int = 0
    successful_predictions: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def accuracy(self) -> float:
        """Calculate prediction accuracy for this link"""
        if self.learned_from_count == 0:
            return self.conditional_probability
        return self.successful_predictions / max(self.learned_from_count, 1)
    
    def confidence(self) -> float:
        """Confidence in this link's probability estimate"""
        # More observations = higher confidence
        return min(self.learned_from_count / 100.0, 1.0)


@dataclass
class CausalPath:
    """Path from root cause to anomaly"""
    path: List[CausalLink]  # Links in path
    total_probability: float  # P(effect | root cause)
    confidence: float  # Confidence in this path
    
    def depth(self) -> int:
        """Number of hops in this path"""
        return len(self.path)


@dataclass
class RootCauseInference:
    """Inferred root cause of an anomaly"""
    root_cause: str
    anomaly_id: str
    confidence: float  # 0-1
    causal_path: Optional[CausalPath]
    alternative_causes: List[Tuple[str, float]] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    inferred_at: datetime = field(default_factory=datetime.utcnow)
    
    def explanation(self) -> str:
        """Generate human-readable explanation"""
        if self.causal_path:
            path_str = " → ".join([link.source for link in self.causal_path.path] + 
                                 [self.causal_path.path[-1].target] if self.causal_path.path else [self.root_cause])
            return f"{self.root_cause} caused {self.anomaly_id} (confidence: {self.confidence:.1%}). Causal path: {path_str}"
        return f"{self.root_cause} likely caused {self.anomaly_id} (confidence: {self.confidence:.1%})"


# ============================================================================
# CAUSAL GRAPH
# ============================================================================


class CausalGraph:
    """
    Probabilistic directed acyclic graph (DAG) of system dependencies.
    
    Edges have weights representing conditional probabilities.
    Learns from historical correlations and updates dynamically.
    
    Target: 100+ nodes, 300+ edges
    """
    
    # Initial system dependency structure (seed the graph)
    INITIAL_STRUCTURE = {
        # CI/CD failures can cause
        "ci_cd.build_failure": ["performance.latency_spike", "coverage.regression", "security.policy_violation"],
        "ci_cd.timeout": ["performance.latency_spike", "coverage.regression"],
        "ci_cd.deploy_failure": ["performance.cpu_spike"],
        
        # Performance issues can cause
        "performance.latency_spike": ["coverage.regression", "security.timeout", "rag.retrieval_failure"],
        "performance.memory_spike": ["coverage.regression", "rag.timeout"],
        "performance.cpu_spike": ["rag.retrieval_failure", "auth.token_failure"],
        "performance.throughput_drop": ["coverage.regression"],
        
        # Auth issues can cause
        "auth.token_failure": ["performance.latency_spike", "rag.retrieval_failure"],
        "auth.rate_limit": ["rag.retrieval_failure", "performance.latency_spike"],
        
        # RAG failures can cause
        "rag.retrieval_failure": ["performance.latency_spike", "coverage.regression"],
        "rag.timeout": ["performance.latency_spike"],
        "rag.embedding_failure": ["coverage.regression"],
        
        # Coverage issues can cause
        "coverage.regression": ["ci_cd.build_failure", "security.policy_violation"],
        
        # Security issues can cause
        "security.vulnerability": ["ci_cd.build_failure", "coverage.regression"],
        "security.policy_violation": ["ci_cd.build_failure"],
    }
    
    def __init__(self):
        """Initialize causal graph"""
        self.links: Dict[Tuple[str, str], CausalLink] = {}
        self.nodes: Set[str] = set()
        self.reverse_links: Dict[str, Set[str]] = defaultdict(set)  # target -> sources
        
        # Seed graph with initial structure
        for source, targets in self.INITIAL_STRUCTURE.items():
            self.nodes.add(source)
            for target in targets:
                self.nodes.add(target)
                # Initialize with moderate probability
                key = (source, target)
                self.links[key] = CausalLink(
                    source=source,
                    target=target,
                    conditional_probability=0.6
                )
                self.reverse_links[target].add(source)
    
    def add_link(self, 
                source: str, 
                target: str, 
                probability: float = 0.5) -> None:
        """Add or update causal link"""
        self.nodes.add(source)
        self.nodes.add(target)
        
        key = (source, target)
        if key in self.links:
            link = self.links[key]
            # Update with exponential smoothing
            alpha = 0.1
            link.conditional_probability = (
                alpha * probability + 
                (1 - alpha) * link.conditional_probability
            )
        else:
            link = CausalLink(
                source=source,
                target=target,
                conditional_probability=probability
            )
            self.links[key] = link
        
        self.reverse_links[target].add(source)
    
    def learn_from_correlation(self, 
                              source: str, 
                              target: str, 
                              success: bool = True) -> None:
        """Learn from a correlation event"""
        self.add_link(source, target)
        
        key = (source, target)
        link = self.links[key]
        link.learned_from_count += 1
        
        if success:
            link.successful_predictions += 1
        
        # Adjust probability based on accuracy
        accuracy = link.accuracy()
        link.conditional_probability = accuracy
    
    def get_upstream_causes(self, effect: str) -> List[str]:
        """Get all potential causes for an effect"""
        return list(self.reverse_links.get(effect, []))
    
    def get_downstream_effects(self, cause: str) -> List[str]:
        """Get all potential effects of a cause"""
        return [link.target for link in self.links.values() 
                if link.source == cause]
    
    def get_path_probability(self, path: CausalPath) -> float:
        """Calculate probability of a causal path"""
        if not path.path:
            return 1.0
        
        # Multiply probabilities along path
        prob = 1.0
        for link in path.path:
            prob *= link.conditional_probability
        
        return prob
    
    def stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        return {
            "nodes": len(self.nodes),
            "edges": len(self.links),
            "avg_out_degree": len(self.links) / max(len(self.nodes), 1),
            "learned_links": sum(1 for link in self.links.values() 
                               if link.learned_from_count > 0),
            "total_observations": sum(link.learned_from_count 
                                     for link in self.links.values()),
        }


# ============================================================================
# BACKWARD CHAINER
# ============================================================================


class BackwardChainer:
    """
    Backward-chaining root cause inference engine.
    
    Traces anomalies to upstream causes using breadth-first search.
    Finds multi-hop causal chains (5+ levels deep).
    
    Target: >80% success rate, <1s latency
    """
    
    def __init__(self, 
                causal_graph: CausalGraph,
                max_depth: int = 5,
                confidence_threshold: float = 0.3):
        """
        Initialize backward chainer.
        
        Args:
            causal_graph: Causal graph to reason about
            max_depth: Maximum chain depth to explore
            confidence_threshold: Minimum confidence to include in search
        """
        self.graph = causal_graph
        self.max_depth = max_depth
        self.confidence_threshold = confidence_threshold
    
    def find_root_causes(self, 
                        anomaly: str, 
                        lookback_anomalies: Optional[List[str]] = None) -> List[RootCauseInference]:
        """
        Find root causes of an anomaly using backward chaining.
        
        Args:
            anomaly: Anomaly to find root cause for
            lookback_anomalies: Recent anomalies in system (for validation)
        
        Returns:
            List of root cause inferences, ranked by confidence
        """
        # BFS to find upstream causes
        queue: List[Tuple[str, int, List[CausalLink], float]] = [
            (anomaly, 0, [], 1.0)  # (node, depth, path, confidence)
        ]
        
        visited: Set[str] = set()
        all_paths: List[CausalPath] = []
        found_root = False
        
        while queue:
            current, depth, path, conf = queue.pop(0)
            
            if current in visited and depth > 0:  # Allow revisit at different depths
                continue
            visited.add(current)
            
            # Get upstream causes
            upstream = self.graph.get_upstream_causes(current)
            
            if not upstream or depth >= self.max_depth:
                # No upstream causes OR reached max depth - this is a potential root
                if path or depth == 0:
                    # Include paths of any depth, including zero-hop (direct anomaly as root)
                    all_paths.append(CausalPath(
                        path=path,
                        total_probability=conf if path else 1.0,
                        confidence=min(conf if path else 0.5, 1.0)
                    ))
                    if path:
                        found_root = True
                continue
            
            # Add upstream nodes to queue
            for cause in upstream:
                key = (cause, current)
                if key in self.graph.links:
                    link = self.graph.links[key]
                    new_conf = conf * link.conditional_probability
                    
                    if new_conf >= self.confidence_threshold:
                        queue.append((cause, depth + 1, path + [link], new_conf))
        
        # Sort paths by confidence (higher first)
        all_paths.sort(key=lambda p: p.confidence, reverse=True)
        
        # Convert paths to root cause inferences
        inferences: List[RootCauseInference] = []
        root_causes_seen: Set[str] = set()
        
        for path in all_paths[:10]:  # Top 10 paths
            if path.path:  # Only include paths with actual links
                root_cause = path.path[0].source
                
                if root_cause not in root_causes_seen:
                    confidence = min(path.confidence, 1.0)
                    
                    inference = RootCauseInference(
                        root_cause=root_cause,
                        anomaly_id=anomaly,
                        confidence=confidence,
                        causal_path=path,
                        evidence={
                            "path_length": path.depth(),
                            "path_probability": path.total_probability,
                        }
                    )
                    inferences.append(inference)
                    root_causes_seen.add(root_cause)
        
        return inferences
    
    def explain_chain(self, path: CausalPath) -> str:
        """Generate human-readable explanation of causal chain"""
        if not path.path:
            return "No causal path found"
        
        chain = []
        for link in path.path:
            chain.append(f"{link.source} (p={link.conditional_probability:.2f})")
        chain.append(path.path[-1].target)
        
        return " → ".join(chain)


# ============================================================================
# ROOT CAUSE ENGINE (Orchestrator)
# ============================================================================


class RootCauseEngine:
    """
    Orchestrates causal graph and backward chainer for root cause inference.
    
    Single entry point for root cause identification.
    """
    
    def __init__(self, 
                max_depth: int = 5,
                confidence_threshold: float = 0.3):
        """Initialize root cause engine"""
        self.causal_graph = CausalGraph()
        self.chainer = BackwardChainer(
            self.causal_graph,
            max_depth=max_depth,
            confidence_threshold=confidence_threshold
        )
    
    def infer_root_cause(self, 
                        anomaly: str,
                        related_anomalies: Optional[List[str]] = None) -> Optional[RootCauseInference]:
        """
        Infer root cause of an anomaly.
        
        Args:
            anomaly: Anomaly identifier
            related_anomalies: Other related anomalies for context
        
        Returns:
            Most likely root cause inference, or None if no root cause found
        """
        inferences = self.chainer.find_root_causes(anomaly, related_anomalies)
        
        if inferences:
            return inferences[0]  # Return highest confidence
        
        return None
    
    def infer_multiple_causes(self, 
                             anomaly: str,
                             top_n: int = 5) -> List[RootCauseInference]:
        """Get top N possible root causes"""
        return self.chainer.find_root_causes(anomaly)[:top_n]
    
    def learn_from_incident(self,
                           root_cause: str,
                           anomaly: str,
                           success: bool = True) -> None:
        """Learn from resolved incident"""
        self.causal_graph.learn_from_correlation(root_cause, anomaly, success)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return self.causal_graph.stats()
