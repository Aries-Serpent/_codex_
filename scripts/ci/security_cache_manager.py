#!/usr/bin/env python3
"""
Security Cache Manager

Purpose:
    Manages a rolling cache of security findings for historical trend analysis.
    Retains last 30 runs for pattern detection and remediation tracking.

Usage:
    python scripts/ci/security_cache_manager.py \
      --action cache-findings \
      --findings-json .codex/security-findings-comprehensive.json \
      --run-id 12345 \
      --commit-sha abc123def

    python scripts/ci/security_cache_manager.py \
      --action compute-trends \
      --output-file .codex/security-findings-trend-metrics.json

Environment Variables:
    GITHUB_RUN_ID: GitHub Actions run ID
    GITHUB_SHA: Commit SHA
    GITHUB_REPOSITORY: Repository name (owner/repo)
"""

import argparse
import hashlib
import json
import logging
import os
import shutil
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
CACHE_DIR = Path(".codex/security-cache")
RUNS_DIR = CACHE_DIR / "runs"
INDEX_FILE = CACHE_DIR / "index.json"
DEDUP_LEDGER = CACHE_DIR / "dedup-hashes.jsonl"
METRICS_FILE = CACHE_DIR / "trend-metrics.json"
MAX_CACHED_RUNS = 30


@dataclass
class CacheMetadata:
    """Metadata for a cached run"""
    run_id: str
    commit_sha: str
    timestamp: str
    findings_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    repo: str
    url: str = ""


@dataclass
class TrendMetrics:
    """Trend metrics across runs"""
    run_count: int
    total_findings: int
    avg_critical: float = 0.0
    avg_high: float = 0.0
    avg_medium: float = 0.0
    avg_low: float = 0.0
    new_findings_last_run: int = 0
    resolved_findings_last_run: int = 0
    avg_remediation_days: float = 0.0
    most_common_cwes: List[Tuple[str, int]] = field(default_factory=list)
    trending_up: bool = False


class SecurityCacheManager:
    """Manages security findings cache and historical analysis"""

    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.runs_dir = cache_dir / "runs"
        self.index_file = cache_dir / "index.json"
        self.dedup_ledger = cache_dir / "dedup-hashes.jsonl"
        self.metrics_file = cache_dir / "trend-metrics.json"
        self._ensure_cache_structure()

    def _ensure_cache_structure(self) -> None:
        """Create cache directory structure if it doesn't exist"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.index_file.exists():
            self.index_file.write_text(json.dumps({"runs": []}, indent=2))
        
        if not self.dedup_ledger.exists():
            self.dedup_ledger.touch()

    def _compute_finding_hash(self, finding: Dict[str, Any]) -> str:
        """Compute hash for finding deduplication"""
        key_parts = [
            finding.get("tool", ""),
            finding.get("cwe_id", ""),
            finding.get("file", ""),
            str(finding.get("line", "")),
        ]
        key_str = "|".join(key_parts)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]

    def cache_findings(
        self,
        run_id: str,
        commit_sha: str,
        findings_json_path: Path,
        repo: str = "",
    ) -> Path:
        """
        Cache findings from a security scan run.

        Args:
            run_id: GitHub Actions run ID
            commit_sha: Git commit SHA
            findings_json_path: Path to comprehensive findings JSON
            repo: Repository name (owner/repo)

        Returns:
            Path to cached findings file
        """
        try:
            with open(findings_json_path) as f:
                findings_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load findings: {e}")
            return None

        # Extract summary
        summary = findings_data.get("summary", {})
        
        # Create cache entry
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        cache_entry = {
            "run_id": run_id,
            "commit_sha": commit_sha,
            "timestamp": timestamp,
            "findings_count": summary.get("total_findings", 0),
            "critical_count": summary.get("critical_count", 0),
            "high_count": summary.get("high_count", 0),
            "medium_count": summary.get("medium_count", 0),
            "low_count": summary.get("low_count", 0),
            "repo": repo or os.getenv("GITHUB_REPOSITORY", "unknown"),
        }

        # Write cache file with timestamp
        cache_filename = f"run-{run_id}-{timestamp}.json"
        cache_path = self.runs_dir / cache_filename
        
        cache_data = {
            "metadata": cache_entry,
            "findings": findings_data.get("finding_index", []),
            "summary": summary,
        }
        
        cache_path.write_text(json.dumps(cache_data, indent=2))
        logger.info(f"Cached findings to {cache_path}")

        # Update index
        self._update_index(cache_entry)

        # Compute deduplication hashes
        self._record_dedup_hashes(run_id, findings_data)

        # Prune old runs
        self._prune_old_runs()

        return cache_path

    def _update_index(self, metadata: Dict[str, Any]) -> None:
        """Update the run index"""
        try:
            with open(self.index_file) as f:
                index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            index = {"runs": []}

        # Remove duplicate run_id if exists
        index["runs"] = [r for r in index["runs"] if r["run_id"] != metadata["run_id"]]
        
        # Add new entry (newest first)
        index["runs"].insert(0, metadata)
        
        # Keep only recent entries in index
        index["runs"] = index["runs"][:MAX_CACHED_RUNS]

        with open(self.index_file, "w") as f:
            json.dump(index, f, indent=2)
        
        logger.info(f"Updated index with run {metadata['run_id']}")

    def _record_dedup_hashes(
        self, run_id: str, findings_data: Dict[str, Any]
    ) -> None:
        """Record deduplication hashes for findings"""
        findings = findings_data.get("finding_index", [])
        
        for finding in findings:
            hash_value = self._compute_finding_hash(finding)
            entry = {
                "run_id": run_id,
                "hash": hash_value,
                "tool": finding.get("tool", ""),
                "cwe_id": finding.get("cwe_id", ""),
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            with open(self.dedup_ledger, "a") as f:
                f.write(json.dumps(entry) + "\n")

    def _prune_old_runs(self) -> None:
        """Keep only the 30 most recent cached runs"""
        cache_files = sorted(self.runs_dir.glob("run-*.json"), reverse=True)
        
        if len(cache_files) > MAX_CACHED_RUNS:
            for old_file in cache_files[MAX_CACHED_RUNS:]:
                old_file.unlink()
                logger.info(f"Pruned old cache: {old_file.name}")

    def compute_trend_deltas(self) -> Dict[str, Any]:
        """
        Compute trend deltas between consecutive runs.

        Returns:
            Dictionary with new/resolved/unchanged findings
        """
        try:
            with open(self.index_file) as f:
                index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning("No index found")
            return {
                "new_findings": [],
                "resolved_findings": [],
                "unchanged_findings": [],
                "severity_shifts": [],
            }

        runs = index.get("runs", [])
        if len(runs) < 2:
            return {
                "new_findings": [],
                "resolved_findings": [],
                "unchanged_findings": [],
                "severity_shifts": [],
            }

        # Get last two runs
        current_run = runs[0]
        previous_run = runs[1]

        current_findings = self._load_findings_by_hash(current_run["run_id"])
        previous_findings = self._load_findings_by_hash(previous_run["run_id"])

        # Compute deltas
        current_hashes = set(current_findings.keys())
        previous_hashes = set(previous_findings.keys())

        new_hashes = current_hashes - previous_hashes
        resolved_hashes = previous_hashes - current_hashes
        unchanged_hashes = current_hashes & previous_hashes

        return {
            "new_findings": [
                current_findings[h] for h in sorted(new_hashes)[:10]
            ],  # Top 10
            "resolved_findings": [
                previous_findings[h] for h in sorted(resolved_hashes)[:10]
            ],
            "unchanged_findings": len(unchanged_hashes),
            "new_count": len(new_hashes),
            "resolved_count": len(resolved_hashes),
        }

    def _load_findings_by_hash(self, run_id: str) -> Dict[str, Dict[str, Any]]:
        """Load findings indexed by hash"""
        cache_files = list(self.runs_dir.glob(f"run-{run_id}-*.json"))
        if not cache_files:
            return {}

        try:
            with open(cache_files[0]) as f:
                cache_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

        findings_by_hash = {}
        for finding in cache_data.get("findings", []):
            hash_val = self._compute_finding_hash(finding)
            findings_by_hash[hash_val] = finding

        return findings_by_hash

    def get_historical_findings(
        self, cwe_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get all instances of a CWE across cached runs.

        Args:
            cwe_id: CWE identifier (e.g., "CWE-79")
            limit: Maximum number of findings to return

        Returns:
            List of findings matching the CWE
        """
        try:
            with open(self.index_file) as f:
                index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

        results = []
        for run_metadata in index.get("runs", [])[:10]:  # Check last 10 runs
            cache_files = list(
                self.runs_dir.glob(f"run-{run_metadata['run_id']}-*.json")
            )
            if not cache_files:
                continue

            try:
                with open(cache_files[0]) as f:
                    cache_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                continue

            for finding in cache_data.get("findings", []):
                if finding.get("cwe_id") == cwe_id:
                    finding["run_id"] = run_metadata["run_id"]
                    finding["cached_at"] = run_metadata.get("timestamp", "")
                    results.append(finding)

        return results[:limit]

    def compute_aggregate_metrics(self) -> TrendMetrics:
        """
        Compute aggregate metrics across all cached runs.

        Returns:
            TrendMetrics object with computed statistics
        """
        try:
            with open(self.index_file) as f:
                index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return TrendMetrics(run_count=0, total_findings=0)

        runs = index.get("runs", [])
        if not runs:
            return TrendMetrics(run_count=0, total_findings=0)

        # Compute averages
        total_critical = sum(r.get("critical_count", 0) for r in runs)
        total_high = sum(r.get("high_count", 0) for r in runs)
        total_medium = sum(r.get("medium_count", 0) for r in runs)
        total_low = sum(r.get("low_count", 0) for r in runs)
        total_findings = sum(r.get("findings_count", 0) for r in runs)

        metrics = TrendMetrics(
            run_count=len(runs),
            total_findings=total_findings,
            avg_critical=total_critical / len(runs) if runs else 0,
            avg_high=total_high / len(runs) if runs else 0,
            avg_medium=total_medium / len(runs) if runs else 0,
            avg_low=total_low / len(runs) if runs else 0,
        )

        # Compute trend direction
        if len(runs) >= 2:
            current = runs[0].get("findings_count", 0)
            previous = runs[1].get("findings_count", 0)
            metrics.trending_up = current > previous

        # Get most common CWEs
        metrics.most_common_cwes = self._get_most_common_cwes(limit=5)

        return metrics

    def _get_most_common_cwes(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Get most common CWE IDs across all runs"""
        cwe_counts = defaultdict(int)

        try:
            with open(self.index_file) as f:
                index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

        for run_metadata in index.get("runs", [])[:10]:  # Last 10 runs
            cache_files = list(
                self.runs_dir.glob(f"run-{run_metadata['run_id']}-*.json")
            )
            if not cache_files:
                continue

            try:
                with open(cache_files[0]) as f:
                    cache_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                continue

            for finding in cache_data.get("findings", []):
                if cwe_id := finding.get("cwe_id"):
                    cwe_counts[cwe_id] += 1

        return sorted(cwe_counts.items(), key=lambda x: x[1], reverse=True)[:limit]


def main():
    parser = argparse.ArgumentParser(description="Security Cache Manager")
    parser.add_argument(
        "--action",
        choices=["cache-findings", "compute-trends", "get-historical", "metrics"],
        required=True,
        help="Action to perform",
    )
    parser.add_argument(
        "--findings-json",
        type=Path,
        help="Path to comprehensive findings JSON",
    )
    parser.add_argument("--run-id", help="GitHub Actions run ID")
    parser.add_argument("--commit-sha", help="Git commit SHA")
    parser.add_argument("--output-file", type=Path, help="Output file path")
    parser.add_argument("--cwe-id", help="CWE ID for historical lookup")
    parser.add_argument("--cache-dir", type=Path, default=CACHE_DIR, help="Cache directory")

    args = parser.parse_args()
    manager = SecurityCacheManager(args.cache_dir)

    try:
        if args.action == "cache-findings":
            if not args.findings_json or not args.run_id:
                logger.error("--findings-json and --run-id required for cache-findings")
                return 1

            commit_sha = args.commit_sha or os.getenv("GITHUB_SHA", "unknown")
            cache_path = manager.cache_findings(
                args.run_id, commit_sha, args.findings_json
            )
            if cache_path:
                print(f"CACHE_PATH={cache_path}", file=open(os.devnull, "w"))
                logger.info(f"✅ Cached findings: {cache_path}")
                return 0
            return 1

        elif args.action == "compute-trends":
            deltas = manager.compute_trend_deltas()
            output = args.output_file or Path(".codex/security-findings-trend-deltas.json")
            output.write_text(json.dumps(deltas, indent=2))
            logger.info(f"✅ Trend deltas computed: {output}")
            return 0

        elif args.action == "get-historical":
            if not args.cwe_id:
                logger.error("--cwe-id required for get-historical")
                return 1

            findings = manager.get_historical_findings(args.cwe_id)
            output = args.output_file or Path(".codex/historical-findings.json")
            output.write_text(json.dumps(findings, indent=2))
            logger.info(f"✅ Historical findings: {output} ({len(findings)} results)")
            return 0

        elif args.action == "metrics":
            metrics = manager.compute_aggregate_metrics()
            output = args.output_file or METRICS_FILE
            output.write_text(json.dumps(asdict(metrics), indent=2))
            logger.info(f"✅ Aggregate metrics: {output}")
            return 0

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
