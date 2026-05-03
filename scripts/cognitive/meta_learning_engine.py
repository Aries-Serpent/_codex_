#!/usr/bin/env python3
"""
Meta Learning Engine

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/cognitive/meta_learning_engine.py [options]

    Examples:
    $ python scripts/cognitive/meta_learning_engine.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""



import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class Pattern:
    """Represents a learned pattern that can be shared across agents"""
    pattern_id: str
    pattern_type: str  # "code", "decision", "optimization", "failure"
    source_agent: int
    context: Dict[str, Any]
    effectiveness: float  # 0.0 to 1.0
    usage_count: int = 0
    last_used: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "source_agent": self.source_agent,
            "context": self.context,
            "effectiveness": self.effectiveness,
            "usage_count": self.usage_count,
            "last_used": self.last_used,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pattern':
        return cls(**data)


@dataclass
class KnowledgeTransfer:
    """Record of a knowledge transfer between agents"""
    transfer_id: str
    source_agent: int
    target_agent: int
    pattern_id: str
    timestamp: str
    success: bool
    efficiency_gain: Optional[float] = None


class SharedMemory:
    """Centralized knowledge store for all agents"""

    def __init__(self, memory_path: Path):
        self.memory_path = memory_path
        self.memory_path.mkdir(parents=True, exist_ok=True)

        self.data_dir = self.memory_path / "data"
        self.metadata_dir = self.memory_path / "metadata"
        self.index_file = self.memory_path / "index.json"

        self.data_dir.mkdir(exist_ok=True)
        self.metadata_dir.mkdir(exist_ok=True)

        self.index: Dict[str, Dict[str, Any]] = self._load_index()

    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        """Load memory index from disk"""
        if self.index_file.exists():
            with open(self.index_file) as f:
                return json.load(f)
        return {}

    def _save_index(self):
        """Save memory index to disk"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def store(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Store data with metadata, return unique ID"""
        # Generate unique ID from data hash
        data_str = json.dumps(data, sort_keys=True)
        data_id = hashlib.sha256(data_str.encode()).hexdigest()[:16]

        # Store data
        data_file = self.data_dir / f"{data_id}.json"
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)

        # Store metadata
        metadata_file = self.metadata_dir / f"{data_id}.json"
        metadata["stored_at"] = datetime.now().isoformat()
        metadata["data_id"] = data_id
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Update index
        self.index[data_id] = {
            "data_file": str(data_file),
            "metadata_file": str(metadata_file),
            **metadata
        }
        self._save_index()

        return data_id

    def retrieve(self, data_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve data by ID"""
        if data_id not in self.index:
            return None

        data_file = Path(self.index[data_id]["data_file"])
        if not data_file.exists():
            return None

        with open(data_file) as f:
            return json.load(f)

    def get_metadata(self, data_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata by ID"""
        if data_id not in self.index:
            return None

        metadata_file = Path(self.index[data_id]["metadata_file"])
        if not metadata_file.exists():
            return None

        with open(metadata_file) as f:
            return json.load(f)

    def search(self, query: Dict[str, Any]) -> List[str]:
        """Search for data IDs matching query criteria"""
        matches = []

        for data_id, entry in self.index.items():
            match = True
            for key, value in query.items():
                if key not in entry or entry[key] != value:
                    match = False
                    break

            if match:
                matches.append(data_id)

        return matches


class PatternLibrary:
    """Library of successful patterns with similarity detection"""

    def __init__(self, library_path: Path):
        self.library_path = library_path
        self.library_path.mkdir(parents=True, exist_ok=True)

        self.patterns_file = self.library_path / "patterns.json"
        self.patterns: Dict[str, Pattern] = self._load_patterns()

    def _load_patterns(self) -> Dict[str, Pattern]:
        """Load patterns from disk"""
        if self.patterns_file.exists():
            with open(self.patterns_file) as f:
                data = json.load(f)
                return {pid: Pattern.from_dict(p) for pid, p in data.items()}
        return {}

    def _save_patterns(self):
        """Save patterns to disk"""
        data = {pid: p.to_dict() for pid, p in self.patterns.items()}
        with open(self.patterns_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_pattern(self, pattern: Pattern) -> str:
        """Add pattern to library"""
        self.patterns[pattern.pattern_id] = pattern
        self._save_patterns()
        return pattern.pattern_id

    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Retrieve pattern by ID"""
        return self.patterns.get(pattern_id)

    def update_pattern_usage(self, pattern_id: str):
        """Update pattern usage statistics"""
        if pattern_id in self.patterns:
            self.patterns[pattern_id].usage_count += 1
            self.patterns[pattern_id].last_used = datetime.now().isoformat()
            self._save_patterns()

    def find_similar_patterns(self, pattern: Pattern, threshold: float = 0.7) -> List[Pattern]:
        """Find patterns similar to the given pattern"""
        similar = []

        # Simple similarity based on type and context keys
        for p in self.patterns.values():
            if p.pattern_id == pattern.pattern_id:
                continue

            if p.pattern_type != pattern.pattern_type:
                continue

            # Calculate context overlap
            context_keys1 = set(pattern.context.keys())
            context_keys2 = set(p.context.keys())

            if not context_keys1 or not context_keys2:
                continue

            overlap = len(context_keys1 & context_keys2)
            union = len(context_keys1 | context_keys2)
            similarity = overlap / union if union > 0 else 0

            if similarity >= threshold:
                similar.append(p)

        return similar

    def get_top_patterns(self, pattern_type: Optional[str] = None, limit: int = 10) -> List[Pattern]:
        """Get top patterns by effectiveness"""
        patterns = list(self.patterns.values())

        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type == pattern_type]

        patterns.sort(key=lambda p: (p.effectiveness, p.usage_count), reverse=True)
        return patterns[:limit]


class MetaLearningEngine:
    """Main meta-learning engine coordinating knowledge transfer and pattern reuse"""

    # V10 Agent definitions (seeds 46-55)
    AGENTS = {
        1: "Emergent Intelligence",
        2: "Performance Monitor",
        3: "Documentation",
        4: "CI Optimizer",
        5: "Reasoning Advisor",
        6: "Ecosystem Coordinator",
        7: "Research Lead",
        8: "ML Engineering",
        9: "DevOps Lead",
        10: "UX Research"
    }

    def __init__(self, shared_memory_path: Path, pattern_library_path: Path):
        self.shared_memory = SharedMemory(shared_memory_path)
        self.pattern_library = PatternLibrary(pattern_library_path)

        self.transfers_log = shared_memory_path / "transfers.json"
        self.transfers: List[KnowledgeTransfer] = self._load_transfers()

        self.metrics = {
            "total_patterns": 0,
            "total_transfers": 0,
            "successful_transfers": 0,
            "average_efficiency_gain": 0.0,
            "pattern_reuse_rate": 0.0
        }

    def _load_transfers(self) -> List[KnowledgeTransfer]:
        """Load transfer history"""
        if self.transfers_log.exists():
            with open(self.transfers_log) as f:
                data = json.load(f)
                return [KnowledgeTransfer(**t) for t in data]
        return []

    def _save_transfers(self):
        """Save transfer history"""
        data = [vars(t) for t in self.transfers]
        with open(self.transfers_log, 'w') as f:
            json.dump(data, f, indent=2)

    def transfer_knowledge(
        self,
        source_agent: int,
        target_agent: int,
        pattern: Pattern
    ) -> Dict[str, Any]:
        """Transfer learned pattern from source to target agent"""

        # Validate agents
        if source_agent not in self.AGENTS or target_agent not in self.AGENTS:
            return {"status": "error", "message": "Invalid agent ID"}

        # Store pattern in shared memory
        pattern_data = pattern.to_dict()
        metadata = {
            "source_agent": source_agent,
            "target_agent": target_agent,
            "pattern_type": pattern.pattern_type,
            "transfer_timestamp": datetime.now().isoformat()
        }

        pattern_id = self.shared_memory.store(pattern_data, metadata)

        # Add to pattern library
        self.pattern_library.add_pattern(pattern)

        # Record transfer
        transfer = KnowledgeTransfer(
            transfer_id=hashlib.sha256(f"{source_agent}{target_agent}{pattern_id}".encode()).hexdigest()[:12],
            source_agent=source_agent,
            target_agent=target_agent,
            pattern_id=pattern_id,
            timestamp=datetime.now().isoformat(),
            success=True
        )

        self.transfers.append(transfer)
        self._save_transfers()

        print(f"✅ Knowledge transferred: {self.AGENTS[source_agent]} → {self.AGENTS[target_agent]}")
        print(f"   Pattern: {pattern.pattern_type} (effectiveness: {pattern.effectiveness:.2%})")

        return {
            "status": "success",
            "pattern_id": pattern_id,
            "transfer_id": transfer.transfer_id
        }

    def optimize_reuse(self) -> Dict[str, Any]:
        """Identify and consolidate reusable patterns across agents"""
        print("🔄 Optimizing pattern reuse across agents...")

        all_patterns = list(self.pattern_library.patterns.values())
        if not all_patterns:
            return {
                "status": "no_patterns",
                "message": "No patterns available for optimization"
            }

        # Find similar pattern groups
        pattern_groups: List[List[Pattern]] = []
        processed: Set[str] = set()

        for pattern in all_patterns:
            if pattern.pattern_id in processed:
                continue

            similar = self.pattern_library.find_similar_patterns(pattern, threshold=0.6)
            if similar:
                group = [pattern] + similar
                pattern_groups.append(group)
                processed.update(p.pattern_id for p in group)
            else:
                processed.add(pattern.pattern_id)

        # Consolidate similar patterns
        consolidated_count = 0
        for group in pattern_groups:
            if len(group) > 1:
                # Keep the most effective pattern in the group
                best_pattern = max(group, key=lambda p: (p.effectiveness, p.usage_count))

                # Mark others for potential removal or merging
                consolidated_count += len(group) - 1

                print(f"   Consolidated {len(group)} similar patterns into pattern {best_pattern.pattern_id}")

        reduction_percentage = (consolidated_count / len(all_patterns) * 100) if all_patterns else 0

        result = {
            "status": "success",
            "original_count": len(all_patterns),
            "pattern_groups": len(pattern_groups),
            "consolidated_count": consolidated_count,
            "reduction_percentage": reduction_percentage
        }

        print(f"✅ Optimization complete: {reduction_percentage:.1f}% reduction possible")

        return result

    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate meta-learning performance metrics"""
        self.metrics["total_patterns"] = len(self.pattern_library.patterns)
        self.metrics["total_transfers"] = len(self.transfers)
        self.metrics["successful_transfers"] = sum(1 for t in self.transfers if t.success)

        # Calculate efficiency gains
        efficiency_gains = [t.efficiency_gain for t in self.transfers if t.efficiency_gain is not None]
        self.metrics["average_efficiency_gain"] = (
            sum(efficiency_gains) / len(efficiency_gains) if efficiency_gains else 0.0
        )

        # Calculate reuse rate
        if self.metrics["total_patterns"] > 0:
            total_usage = sum(p.usage_count for p in self.pattern_library.patterns.values())
            self.metrics["pattern_reuse_rate"] = total_usage / self.metrics["total_patterns"]

        return self.metrics

    def apply_lessons_to_task(self, task_context: Dict[str, Any], lessons: List[str]) -> Dict[str, Any]:
        """Apply meta-learning lessons to a specific task (e.g., LiceCAP ingestion)"""
        print("\n🧠 Applying meta-learning to task...")

        recommendations = []

        for lesson in lessons:
            # Pattern matching on lessons to generate recommendations
            if "conversion" in lesson.lower() or "wrapping" in lesson.lower():
                # Create a pattern for code conversion
                pattern = Pattern(
                    pattern_id=hashlib.sha256(lesson.encode()).hexdigest()[:12],
                    pattern_type="code_conversion",
                    source_agent=0,  # System-generated
                    context={
                        "task": "external_repo_integration",
                        "lesson": lesson,
                        "applies_to": task_context.get("repo_name", "unknown")
                    },
                    effectiveness=0.85  # Estimated
                )

                self.pattern_library.add_pattern(pattern)
                recommendations.append({
                    "pattern_id": pattern.pattern_id,
                    "recommendation": "Use established conversion patterns for C/C++ to Python wrapping",
                    "tools": ["ctypes", "cffi", "pybind11", "SWIG"]
                })

            elif "plugin" in lesson.lower() or "adapter" in lesson.lower():
                pattern = Pattern(
                    pattern_id=hashlib.sha256(lesson.encode()).hexdigest()[:12],
                    pattern_type="plugin_architecture",
                    source_agent=0,
                    context={
                        "task": "external_repo_integration",
                        "lesson": lesson,
                        "pattern": "adapter"
                    },
                    effectiveness=0.80
                )

                self.pattern_library.add_pattern(pattern)
                recommendations.append({
                    "pattern_id": pattern.pattern_id,
                    "recommendation": "Implement plugin adapter for external tool integration",
                    "template": "Create wrapper class with standardized interface"
                })

            elif "license" in lesson.lower():
                pattern = Pattern(
                    pattern_id=hashlib.sha256(lesson.encode()).hexdigest()[:12],
                    pattern_type="compliance_check",
                    source_agent=0,
                    context={
                        "task": "external_repo_integration",
                        "lesson": lesson,
                        "category": "legal"
                    },
                    effectiveness=1.0  # Critical
                )

                self.pattern_library.add_pattern(pattern)
                recommendations.append({
                    "pattern_id": pattern.pattern_id,
                    "recommendation": "Ensure license compatibility before integration",
                    "action": "Review GPL requirements if applicable"
                })

        print(f"✅ Generated {len(recommendations)} recommendations from {len(lessons)} lessons")

        return {
            "status": "success",
            "task": task_context,
            "lessons_applied": len(lessons),
            "recommendations": recommendations,
            "patterns_created": len(recommendations)
        }


def main():
    parser = argparse.ArgumentParser(description="Meta-Learning Engine for Cognitive Brain")
    parser.add_argument("--mode", choices=["transfer", "optimize", "apply", "metrics"], required=True,
                      help="Operation mode")
    parser.add_argument("--source-agent", type=int, choices=range(1, 11),
                      help="Source agent ID for transfer mode")
    parser.add_argument("--target-agent", type=int, choices=range(1, 11),
                      help="Target agent ID for transfer mode")
    parser.add_argument("--pattern-type", help="Pattern type for transfer")
    parser.add_argument("--lessons-file", help="JSON file with lessons learned for apply mode")
    parser.add_argument("--shared-memory", default="cognitive/shared_memory",
                      help="Shared memory directory")
    parser.add_argument("--pattern-library", default="cognitive/patterns",
                      help="Pattern library directory")

    args = parser.parse_args()

    # Initialize engine
    engine = MetaLearningEngine(
        Path(args.shared_memory),
        Path(args.pattern_library)
    )

    if args.mode == "transfer":
        if not args.source_agent or not args.target_agent:
            print("Error: --source-agent and --target-agent required for transfer mode")
            return 1

        # Create example pattern for transfer
        pattern = Pattern(
            pattern_id=hashlib.sha256(f"pattern_{datetime.now()}".encode()).hexdigest()[:12],
            pattern_type=args.pattern_type or "optimization",
            source_agent=args.source_agent,
            context={"example": True, "timestamp": datetime.now().isoformat()},
            effectiveness=0.85
        )

        result = engine.transfer_knowledge(args.source_agent, args.target_agent, pattern)
        print(json.dumps(result, indent=2))

    elif args.mode == "optimize":
        result = engine.optimize_reuse()
        print(json.dumps(result, indent=2))

    elif args.mode == "apply":
        if not args.lessons_file:
            print("Error: --lessons-file required for apply mode")
            return 1

        with open(args.lessons_file) as f:
            data = json.load(f)

        lessons = data.get("lessons_learned", [])
        task_context = {k: v for k, v in data.items() if k != "lessons_learned"}

        result = engine.apply_lessons_to_task(task_context, lessons)
        print(json.dumps(result, indent=2))

    elif args.mode == "metrics":
        metrics = engine.calculate_metrics()
        print(json.dumps(metrics, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
