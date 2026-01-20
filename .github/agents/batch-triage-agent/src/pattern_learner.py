"""
Pattern Learner - Cognitive brain integration for batch triage

Implements pattern storage, retrieval, and learning from triage outcomes.
Stores patterns in cognitive brain and tracks remediation success rates.
"""

import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class FailurePattern:
    """A learned failure pattern."""
    
    pattern_id: str
    failure_type: str
    root_cause: str
    common_symptoms: List[str]
    legacy_ids: List[str] = None
    occurrences: int = 1
    first_seen: str = ""
    last_seen: str = ""
    success_rate: float = 0.0
    avg_resolution_time_hours: Optional[float] = None
    recommended_actions: List[str] = None
    
    def __post_init__(self):
        if not self.first_seen:
            self.first_seen = datetime.now().isoformat()
        if not self.last_seen:
            self.last_seen = datetime.now().isoformat()
        if self.recommended_actions is None:
            self.recommended_actions = []
        if self.legacy_ids is None:
            self.legacy_ids = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class PatternLearner:
    """
    Learns from triage outcomes and stores patterns in cognitive brain.
    
    Capabilities:
    - Pattern extraction and storage
    - Remediation success tracking
    - Historical context retrieval
    - Pattern expiry management
    """

    # Use 32 hex chars (128 bits) of SHA-256 to minimize birthday-collision risk
    # for potentially large numbers of learned patterns.
    SHA256_PREFIX_LENGTH = 32
    
    def __init__(
        self,
        kb_path: Path = Path(".codex/cognitive_brain"),
        pattern_expiry_days: int = 90,
        min_occurrences: int = 3,
    ):
        """
        Initialize the pattern learner.
        
        Args:
            kb_path: Path to cognitive brain knowledge base
            pattern_expiry_days: Days before patterns expire
            min_occurrences: Minimum occurrences before pattern is considered stable
        """
        self.kb_path = kb_path
        self.patterns_dir = kb_path / "patterns" / "ci_failures"
        self.metrics_dir = Path(".codex/metrics")
        self.remediations_db = self.patterns_dir / "remediations.jsonl"
        
        # Configuration
        self.pattern_expiry_days = pattern_expiry_days
        self.min_occurrences = min_occurrences
        
        # Create directories
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache
        self.patterns: Dict[str, FailurePattern] = {}
        self._pattern_id_cache: Dict[str, str] = {}
        self._legacy_id_map: Dict[str, str] = {}
        self._migration_map_path = self.patterns_dir / "pattern_id_migration.json"
        self._load_id_migration_map()
        self._load_patterns()

    def _load_id_migration_map(self) -> None:
        """Load legacy ID mappings from migration output."""
        if not self._migration_map_path.exists():
            return
        try:
            with open(self._migration_map_path, "r") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning(f"Failed to load migration map: {exc}")
            return
        mappings = data.get("mappings", data)
        if isinstance(mappings, dict):
            self._legacy_id_map.update(mappings)
    
    def _load_patterns(self) -> None:
        """Load existing patterns from storage."""
        pattern_files = self.patterns_dir.glob("pattern_*.json")
        
        for pattern_file in pattern_files:
            try:
                with open(pattern_file, 'r') as f:
                    data = json.load(f)
                    pattern = FailurePattern(**data)
                    self.patterns[pattern.pattern_id] = pattern
                    self._register_pattern_signature(
                        pattern.pattern_id,
                        pattern.failure_type,
                        pattern.root_cause,
                    )
                    for legacy_id in pattern.legacy_ids:
                        self._legacy_id_map.setdefault(legacy_id, pattern.pattern_id)
            except Exception as e:
                logger.warning(f"Failed to load pattern from {pattern_file}: {e}")
    
    def record_triage_outcome(
        self,
        batch_id: str,
        failures: List[Dict[str, Any]],
        outcomes: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Record triage outcomes for learning.
        
        Args:
            batch_id: Unique identifier for this batch
            failures: List of failure records
            outcomes: Optional list of remediation outcomes
        """
        timestamp = datetime.now().isoformat()
        outcome_file = self.patterns_dir / f"batch_{batch_id}_{timestamp.replace(':', '-')}.json"
        
        data = {
            "batch_id": batch_id,
            "timestamp": timestamp,
            "total_failures": len(failures),
            "failures": failures,
            "outcomes": outcomes or [],
            "patterns_detected": self._extract_patterns_from_batch(failures),
        }
        
        # Save to file
        with open(outcome_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Update patterns
        for pattern_data in data["patterns_detected"]:
            self._update_or_create_pattern(pattern_data)
        
        logger.info(f"Recorded triage outcome for batch {batch_id}")
    
    def _extract_patterns_from_batch(self, failures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract patterns from a batch of failures."""
        pattern_groups = defaultdict(list)
        
        for failure in failures:
            key = (failure.get("failure_type"), failure.get("root_cause"))
            pattern_groups[key].append(failure)
        
        patterns = []
        for (failure_type, root_cause), group in pattern_groups.items():
            if not failure_type or not root_cause:
                continue
            
            # Extract common symptoms
            symptoms = set()
            for failure in group:
                for issue in failure.get("detected_issues", []):
                    symptoms.add(issue.get("description", "")[:100])
            
            pattern = {
                "pattern_id": self._generate_pattern_id(failure_type, root_cause),
                "legacy_ids": [],
                "failure_type": failure_type,
                "root_cause": root_cause,
                "common_symptoms": list(symptoms)[:5],
                "occurrences": len(group),
            }
            patterns.append(pattern)
        
        return patterns
    
    def _generate_pattern_id(self, failure_type: str, root_cause: str, register: bool = True) -> str:
        """Generate a unique pattern ID.
        
        Args:
            failure_type: Type of failure
            root_cause: Root cause of failure
            register: Whether to register the pattern signature (default: True)
        
        Returns:
            Generated pattern ID
        """
        content = f"{failure_type}:{root_cause}"
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[: self.SHA256_PREFIX_LENGTH]
        pattern_id = f"pattern_{digest}"
        if register:
            self._register_pattern_signature(pattern_id, failure_type, root_cause)
        return pattern_id

    def _register_pattern_signature(self, pattern_id: str, failure_type: str, root_cause: str) -> None:
        """Detect and alert on collisions for generated IDs.
        
        Checks both the in-memory cache and all loaded patterns to ensure
        comprehensive collision detection across sessions.
        """
        content = f"{failure_type}:{root_cause}"
        # Check in-memory cache first
        cached = self._pattern_id_cache.get(pattern_id)
        if cached and cached != content:
            logger.critical(
                "Hash collision detected for %s (%s vs %s)",
                pattern_id,
                cached,
                content,
            )
            raise ValueError(f"Hash collision detected for {pattern_id}")
        
        # Also check against all loaded patterns to detect collisions from previous sessions
        if pattern_id in self.patterns:
            existing_pattern = self.patterns[pattern_id]
            if (existing_pattern.failure_type != failure_type or 
                existing_pattern.root_cause != root_cause):
                logger.critical(
                    "Hash collision detected for %s across sessions (existing: %s:%s vs new: %s:%s)",
                    pattern_id,
                    existing_pattern.failure_type,
                    existing_pattern.root_cause,
                    failure_type,
                    root_cause,
                )
                raise ValueError(f"Hash collision detected for {pattern_id} with existing pattern")
        
        self._pattern_id_cache[pattern_id] = content

    def _legacy_pattern_id(self, failure_type: str, root_cause: str) -> str:
        """Generate a legacy MD5-based pattern ID for backward compatibility.

        This helper exists solely to resolve and map pre-existing pattern IDs
        that were generated using MD5. It MUST NOT be used for new pattern ID
        generation. New IDs should always be created via `_generate_pattern_id`,
        which uses a SHA-256-based identifier.
        """
        content = f"{failure_type}:{root_cause}"
        digest = hashlib.md5(content.encode("utf-8")).hexdigest()[:12]
        return f"pattern_{digest}"

    def _resolve_pattern_id(self, pattern_id: str) -> Optional[str]:
        if pattern_id in self.patterns:
            return pattern_id
        mapped = self._legacy_id_map.get(pattern_id)
        if mapped and mapped in self.patterns:
            return mapped
        for pattern in self.patterns.values():
            if pattern_id in pattern.legacy_ids:
                self._legacy_id_map.setdefault(pattern_id, pattern.pattern_id)
                return pattern.pattern_id
        return None

    def _find_pattern_by_signature(self, failure_type: str, root_cause: str) -> Optional[FailurePattern]:
        for pattern in self.patterns.values():
            if pattern.failure_type == failure_type and pattern.root_cause == root_cause:
                return pattern
        return None

    def migrate_existing_patterns(self) -> Dict[str, str]:
        """Migrate existing patterns to SHA-256 IDs with legacy alias support.

        The migration is performed in two phases to avoid data loss:
        1. Compute migrations and write all new pattern files.
        2. Only after successful writes, update in-memory mappings and delete legacy files.
        """
        migrations: Dict[str, str] = {}
        # Phase 0: build migration plan without modifying original pattern objects
        migration_plan: List[tuple[str, str, FailurePattern]] = []
        for legacy_id, original_pattern in list(self.patterns.items()):
            # Generate new ID without registering to avoid side effects during planning
            content_id = self._generate_pattern_id(
                original_pattern.failure_type, 
                original_pattern.root_cause,
                register=False
            )
            if content_id == legacy_id:
                # Already using content-based ID; nothing to migrate.
                continue
            
            # Create a copy of the pattern with updated ID and legacy alias
            import copy
            pattern_copy = copy.deepcopy(original_pattern)
            if legacy_id not in pattern_copy.legacy_ids:
                pattern_copy.legacy_ids.append(legacy_id)
            pattern_copy.pattern_id = content_id
            
            migration_plan.append((legacy_id, content_id, pattern_copy))

        if not migration_plan:
            return migrations

        # Phase 1: write new pattern files. If any write fails, abort without deleting legacy files.
        write_failed = False
        for legacy_id, content_id, pattern_copy in migration_plan:
            pattern_file = self.patterns_dir / f"{content_id}.json"
            try:
                with open(pattern_file, "w") as f:
                    json.dump(pattern_copy.to_dict(), f, indent=2)
                logger.info(f"Wrote migrated pattern to {pattern_file}")
            except Exception as e:
                logger.error(f"Failed to write migrated pattern {content_id}: {e}")
                write_failed = True
                break
        
        if write_failed:
            logger.error("Migration aborted: failed to write one or more pattern files")
            return {}
        
        # Phase 2: Update in-memory mappings and delete legacy files only after successful writes
        for legacy_id, content_id, pattern_copy in migration_plan:
            # Now register the new pattern signature and update in-memory structures
            self._register_pattern_signature(content_id, pattern_copy.failure_type, pattern_copy.root_cause)
            self.patterns.pop(legacy_id, None)
            self.patterns[content_id] = pattern_copy
            migrations[legacy_id] = content_id
            self._legacy_id_map[legacy_id] = content_id
            legacy_file = self.patterns_dir / f"{legacy_id}.json"
            if legacy_file.exists():
                try:
                    legacy_file.unlink()
                    logger.info(f"Deleted legacy pattern file {legacy_file}")
                except Exception as e:
                    logger.warning(f"Could not delete legacy file {legacy_file}: {e}")
        
        if migrations:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "mappings": migrations,
                "total_migrated": len(migrations),
            }
            with open(self._migration_map_path, "w") as f:
                json.dump(payload, f, indent=2)
        return migrations
    
    def _update_or_create_pattern(self, pattern_data: Dict[str, Any]) -> None:
        """Update existing pattern or create new one."""
        pattern_id = pattern_data["pattern_id"]
        resolved_id = self._resolve_pattern_id(pattern_id)
        if resolved_id:
            pattern_id = resolved_id
        else:
            existing_pattern = self._find_pattern_by_signature(
                pattern_data.get("failure_type", ""),
                pattern_data.get("root_cause", ""),
            )
            if existing_pattern:
                pattern_id = existing_pattern.pattern_id
        
        if pattern_id in self.patterns:
            # Update existing
            pattern = self.patterns[pattern_id]
            pattern.occurrences += pattern_data.get("occurrences", 1)
            pattern.last_seen = datetime.now().isoformat()
            for legacy_id in pattern_data.get("legacy_ids", []):
                if legacy_id not in pattern.legacy_ids:
                    pattern.legacy_ids.append(legacy_id)
        else:
            # Create new
            pattern_data["pattern_id"] = pattern_id
            pattern = FailurePattern(**pattern_data)
            self.patterns[pattern_id] = pattern
        
        # Save to file
        pattern_file = self.patterns_dir / f"{pattern_id}.json"
        with open(pattern_file, 'w') as f:
            json.dump(pattern.to_dict(), f, indent=2)
    
    def track_remediation_outcome(
        self,
        remediation_id: str,
        pattern_id: str,
        success: bool,
        resolution_time_hours: Optional[float] = None,
    ) -> None:
        """
        Track remediation success/failure for learning.
        
        Args:
            remediation_id: Unique identifier for the remediation
            pattern_id: Associated pattern ID
            success: Whether remediation was successful
            resolution_time_hours: Time to resolve in hours
        """
        resolved_id = self._resolve_pattern_id(pattern_id) or pattern_id
        entry = {
            "remediation_id": remediation_id,
            "pattern_id": resolved_id,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "resolution_time_hours": resolution_time_hours,
        }
        
        # Append to JSONL
        with open(self.remediations_db, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        # Update pattern success rate
        if resolved_id in self.patterns:
            self._recalculate_pattern_success_rate(resolved_id)
        
        logger.info(f"Tracked remediation outcome: {remediation_id} - {'success' if success else 'failure'}")
    
    def _recalculate_pattern_success_rate(self, pattern_id: str) -> None:
        """Recalculate success rate for a pattern."""
        if not self.remediations_db.exists():
            return
        
        successes = 0
        total = 0
        resolution_times = []
        
        with open(self.remediations_db, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("pattern_id") == pattern_id:
                        total += 1
                        if entry.get("success"):
                            successes += 1
                        if entry.get("resolution_time_hours"):
                            resolution_times.append(entry["resolution_time_hours"])
                except json.JSONDecodeError:
                    continue
        
        if total > 0:
            pattern = self.patterns[pattern_id]
            pattern.success_rate = successes / total
            if resolution_times:
                pattern.avg_resolution_time_hours = sum(resolution_times) / len(resolution_times)
            
            # Save updated pattern
            pattern_file = self.patterns_dir / f"{pattern_id}.json"
            with open(pattern_file, 'w') as f:
                json.dump(pattern.to_dict(), f, indent=2)
    
    def get_pattern(self, failure_type: str, root_cause: str) -> Optional[FailurePattern]:
        """
        Get pattern matching failure type and root cause.
        
        Args:
            failure_type: Type of failure
            root_cause: Root cause description
            
        Returns:
            Matching pattern or None
        """
        pattern_id = self._generate_pattern_id(failure_type, root_cause)
        pattern = self.patterns.get(pattern_id)
        if pattern:
            return pattern
        return self._find_pattern_by_signature(failure_type, root_cause)
    
    def get_best_remediation(self, failure_type: str, root_cause: str) -> Optional[Dict[str, Any]]:
        """
        Get best remediation based on historical success rates.
        
        Args:
            failure_type: Type of failure
            root_cause: Root cause description
            
        Returns:
            Best remediation or None
        """
        pattern = self.get_pattern(failure_type, root_cause)
        
        if not pattern or not pattern.recommended_actions:
            return None
        
        return {
            "actions": pattern.recommended_actions,
            "success_rate": pattern.success_rate,
            "avg_resolution_time_hours": pattern.avg_resolution_time_hours,
            "confidence": "high" if pattern.success_rate >= 0.7 else "medium" if pattern.success_rate >= 0.5 else "low",
        }
    
    def cleanup_expired_patterns(self) -> int:
        """
        Remove expired patterns.
        
        Returns:
            Number of patterns removed
        """
        expiry_date = datetime.now() - timedelta(days=self.pattern_expiry_days)
        removed = 0
        
        for pattern_id, pattern in list(self.patterns.items()):
            try:
                last_seen = datetime.fromisoformat(pattern.last_seen)
                if last_seen < expiry_date:
                    # Remove from memory and disk
                    del self.patterns[pattern_id]
                    pattern_file = self.patterns_dir / f"{pattern_id}.json"
                    if pattern_file.exists():
                        pattern_file.unlink()
                    removed += 1
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse date for pattern {pattern_id}: {e}")
        
        logger.info(f"Cleaned up {removed} expired patterns")
        return removed
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get learning statistics.
        
        Returns:
            Dictionary of statistics
        """
        stable_patterns = [p for p in self.patterns.values() if p.occurrences >= self.min_occurrences]
        high_success = [p for p in stable_patterns if p.success_rate >= 0.7]
        
        return {
            "total_patterns": len(self.patterns),
            "stable_patterns": len(stable_patterns),
            "high_success_patterns": len(high_success),
            "avg_success_rate": sum(p.success_rate for p in self.patterns.values()) / len(self.patterns) if self.patterns else 0.0,
            "most_common_failure_types": self._get_top_failure_types(),
        }
    
    def _get_top_failure_types(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most common failure types."""
        type_counts = defaultdict(int)
        
        for pattern in self.patterns.values():
            type_counts[pattern.failure_type] += pattern.occurrences
        
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"failure_type": ft, "count": count}
            for ft, count in sorted_types[:limit]
        ]
