#!/usr/bin/env python3
"""
Enhanced environment snapshot with git commit, conda env, and seed tracking.

This script extends the basic environment snapshot to include:
- Git commit SHA for reproducibility
- Conda environment (if available)
- Python version and packages
- Seed value (if provided)
- System metadata

Usage:
    python scripts/environment_snapshot.py --out env_snapshot.json
    python scripts/environment_snapshot.py --out env_snapshot.json --seed 42
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# Add src to path
_REPO_ROOT = Path(__file__).parent.parent
_SRC_DIR = _REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

def get_conda_env() -> dict[str, Any] | None:
    """Get conda environment information if available.
    
    Returns:
        Dictionary with conda env info or None if conda not available
    """
    try:
        # Check if we're in a conda environment
        conda_prefix = os.environ.get("CONDA_PREFIX")
        conda_default_env = os.environ.get("CONDA_DEFAULT_ENV")
        
        if not conda_prefix and not conda_default_env:
            return None
        
        info: dict[str, Any] = {}
        
        if conda_default_env:
            info["name"] = conda_default_env
        
        if conda_prefix:
            info["prefix"] = conda_prefix
        
        # Try to get conda version
        try:
            conda_version = subprocess.check_output(
                ["conda", "--version"],
                text=True,
                stderr=subprocess.STDOUT,
                timeout=5
            ).strip()
            info["version"] = conda_version
        except Exception:
            # It's non-critical if we can't get the conda version; ignore and continue.
            pass
        
        # Try to get package list
        try:
            packages_output = subprocess.check_output(
                ["conda", "list", "--export"],
                text=True,
                stderr=subprocess.STDOUT,
                timeout=10
            )
            packages = [
                line.strip()
                for line in packages_output.splitlines()
                if line.strip() and not line.startswith("#")
            ]
            info["packages_count"] = len(packages)
            # Store first 10 packages as sample
            info["packages_sample"] = packages[:10]
        except Exception:
            # Non-critical if we can't get conda packages; ignore and continue.
            pass
        
        return info if info else None
        
    except Exception:
        # If conda environment detection fails entirely, return None.
        return None


def get_git_info() -> dict[str, Any] | None:
    """Get detailed git information.
    
    Returns:
        Dictionary with git info or None if not in a git repo
    """
    try:
        # Find git root
        root = Path(__file__).resolve()
        git_dir = None
        for parent in [root] + list(root.parents):
            if (parent / ".git").exists():
                git_dir = parent
                break
        
        if not git_dir:
            return None
        
        info: dict[str, Any] = {}
        
        # Get commit SHA
        try:
            commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=git_dir,
                text=True,
                stderr=subprocess.STDOUT,
                timeout=5
            ).strip()
            info["commit"] = commit
        except Exception:
            # Non-critical if git commit lookup fails; ignore and continue.
            pass
        
        # Get short commit
        try:
            short_commit = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=git_dir,
                text=True,
                stderr=subprocess.STDOUT,
                timeout=5
            ).strip()
            info["commit_short"] = short_commit
        except Exception:
            # Non-critical if short commit lookup fails; ignore and continue.
            pass
        
        # Get branch name
        try:
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=git_dir,
                text=True,
                stderr=subprocess.STDOUT,
                timeout=5
            ).strip()
            info["branch"] = branch
        except Exception:
            # Non-critical if branch name lookup fails; ignore and continue.
            pass
        
        # Check for uncommitted changes
        try:
            status = subprocess.check_output(
                ["git", "status", "--porcelain"],
                cwd=git_dir,
                text=True,
                stderr=subprocess.STDOUT,
                timeout=5
            ).strip()
            info["dirty"] = bool(status)
        except Exception:
            # Non-critical if git status check fails; ignore and continue.
            pass
        
        return info if info else None
        
    except Exception:
        # If git info detection fails entirely, return None.
        return None


def create_enhanced_snapshot(seed: int | None = None) -> dict[str, Any]:
    """Create enhanced environment snapshot with all metadata.
    
    Args:
        seed: Optional seed value for reproducibility
        
    Returns:
        Dictionary with comprehensive environment information
    """
    # Get base environment info using existing provenance utilities
    from codex_ml.utils.provenance import environment_summary
    
    base_info = environment_summary()
    
    # Add conda environment
    conda_env = get_conda_env()
    if conda_env:
        base_info["conda"] = conda_env
    
    # Add enhanced git info
    git_info = get_git_info()
    if git_info:
        base_info["git"] = git_info
    
    # Add seed if provided
    if seed is not None:
        base_info["seed"] = int(seed)
    
    return base_info


def main(argv: list[str] | None = None) -> int:
    """Main entry point for environment snapshot script.
    
    Args:
        argv: Command line arguments
        
    Returns:
        Exit code (0 for success)
    """
    parser = argparse.ArgumentParser(
        description="Capture enhanced environment snapshot for reproducibility"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("env_snapshot.json"),
        help="Output file path (default: env_snapshot.json)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed value for reproducibility tracking"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print snapshot to stdout in addition to file"
    )
    
    args = parser.parse_args(argv)
    
    # Create snapshot
    snapshot = create_enhanced_snapshot(seed=args.seed)
    
    # Write to file
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(snapshot, indent=2, sort_keys=True))
    
    print(f"✓ Environment snapshot written to {args.out}")
    
    # Print summary
    if snapshot.get("git"):
        git_info = snapshot["git"]
        commit = git_info.get("commit_short", git_info.get("commit", "unknown"))
        branch = git_info.get("branch", "unknown")
        dirty = " (dirty)" if git_info.get("dirty") else ""
        print(f"  Git: {commit} on {branch}{dirty}")
    
    if snapshot.get("conda"):
        conda_info = snapshot["conda"]
        env_name = conda_info.get("name", "unknown")
        pkg_count = conda_info.get("packages_count", 0)
        print(f"  Conda: {env_name} ({pkg_count} packages)")
    
    if snapshot.get("seed") is not None:
        print(f"  Seed: {snapshot['seed']}")
    
    if snapshot.get("python"):
        print(f"  Python: {snapshot['python']}")
    
    # Verbose output
    if args.verbose:
        print("\nFull snapshot:")
        print(json.dumps(snapshot, indent=2, sort_keys=True))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
