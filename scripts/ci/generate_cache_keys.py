#!/usr/bin/env python3
"""Generate standardized cache keys using CacheManager.

This script bridges the CacheManager Python module with GitHub Actions workflows.
Workflows call this script to get consistent cache keys, paths, and restore-keys
that align with the centralized cache management strategy.

Usage (in GitHub Actions):
    python scripts/ci/generate_cache_keys.py --type pip --workflow pr-checks
    python scripts/ci/generate_cache_keys.py --type pytest --workflow test-rag --health

Output: JSON to stdout with key, restore-keys, and paths for actions/cache.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from codex.ci.cache_manager import CacheManager, CacheType


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate standardized cache keys via CacheManager"
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=[ct.value for ct in CacheType],
        help="Cache type (pip, pytest, nox, etc.)",
    )
    parser.add_argument(
        "--workflow",
        default=None,
        help="Workflow name for key scoping",
    )
    parser.add_argument(
        "--job",
        default=None,
        help="Job name for extra identification",
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Include cache health report in output",
    )
    parser.add_argument(
        "--github-output",
        action="store_true",
        help="Write results to $GITHUB_OUTPUT for workflow steps",
    )
    args = parser.parse_args()

    manager = CacheManager()
    cache_type = CacheType(args.type)

    extra_ids = {}
    if args.job:
        extra_ids["job"] = args.job

    config = manager.create_cache_config(
        cache_type=cache_type,
        workflow_name=args.workflow,
        extra_identifiers=extra_ids if extra_ids else None,
    )

    result = {
        # CacheManager.create_cache_config() always puts the full key as the
        # single element in key_components; extract it directly.
        "cache_key": config.key_components[0] if config.key_components else "",
        "restore_keys": config.restore_keys,
        "paths": config.paths,
        "cache_type": cache_type.value,
        "workflow": args.workflow or os.environ.get("GITHUB_WORKFLOW", "unknown"),
    }

    if args.health:
        health = manager.validate_cache_health()
        result["health"] = {
            "total_size_gb": health.total_size_gb,
            "total_caches": health.total_caches,
            "status": health.status,
            "recommendations": health.recommendations,
        }

    # Write to GITHUB_OUTPUT if requested and available
    if args.github_output:
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            newline = "\n"
            with open(github_output, "a") as f:
                f.write(f"cache-key={result['cache_key']}\n")
                f.write(f"restore-keys={json.dumps(result['restore_keys'])}\n")
                f.write(f"cache-paths={newline.join(result['paths'])}\n")

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
