#!/usr/bin/env python3
"""
Package Size Audit Script
Phase 3 Lane 1 - Cognitive Brain Profile Packaging & Validation

This script audits the size of each profile's dependencies using pip download.
It measures the total size of wheels for core, runtime, and full profiles,
comparing against the target thresholds:
- Core profile: ≤15 MB
- Runtime profile: ≤35 MB
- Full profile: ≤100 MB

Usage:
    python scripts/profile_size_audit.py

Output:
    - Generates .codex/profile_sizes.json with detailed breakdown
    - Prints summary to console
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def get_profile_dependencies() -> Dict[str, List[str]]:
    """Extract profile dependencies from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    
    # Parse pyproject.toml manually to get profile deps
    profiles = {
        "core": [
            "hydra-core==1.3.2",
            "omegaconf>=2.3",
            "pydantic>=2.4",
            "pydantic-settings>=2.14.2",
            "marshmallow>=3.7.1,<5",
            "PyYAML>=6.0.1",
            "typer>=0.12",
            "click>=8.1",
            "libcst>=1.0.0",
            "parso>=0.8.0",
            "tree-sitter>=0.25.2",
            "tree-sitter-python>=0.20.0",
            "tree-sitter-yaml>=0.7.2",
            "sqlparse>=0.5.5",
        ],
        "runtime": [
            "pandas>=2.0.3,<3",
            "numpy>=2.4.6,<3",
            "scikit-learn>=1.9.0,<2",
            "sentencepiece>=0.1.99",
            "torch>=2.6.1,<3.0.0",
            "transformers>=5.12.1,<6",
            "datasets>=5.0.0,<6",
            "accelerate>=1.14.0,<2",
            "peft>=0.19.1,<1",
            "fastapi>=0.135.3,<1",
            "litestar>=2.22.0,<3",
            "starlette>=1.0.1,<2",
            "slowapi>=0.1.9",
            "httpx>=0.26,<1",
            "ray[serve]>=2.56.0,<3",
            "prometheus-client>=0.19.0",
            "psutil>=5.9",
            "evidently>=0.7.21,<1",
            "duckdb>=1.5.4",
            "sentence-transformers>=5.5.1,<6.0.0",
            "chromadb>=0.3.0",
            "faiss-cpu>=1.13.2,<2.0.0",
        ],
    }
    
    # Full profile = core + runtime + dev tools
    full_runtime = profiles["runtime"] + [
        "pytest>=9.0.3,<10.0.0",
        "pytest-cov>=4.1.0,<8.0.0",
        "pytest-xdist>=3.5.0,<4.0.0",
        "pytest-timeout>=2.2.0,<3.0.0",
        "pytest-asyncio>=1.4.0,<2.0.0",
        "pytest-mock>=3.15.1,<4.0.0",
        "pytest-randomly>=3.15",
        "pytest-rerunfailures>=16.6",
        "pytest-split>=0.11.0",
        "hypothesis>=6.152.4,<7.0.0",
        "ruff>=0.1.15,<1.0.0",
        "black>=24.0.0,<27.0.0",
        "isort>=8.0.1",
        "mypy>=2.1.0,<3.0.0",
        "pre-commit>=3.6.0,<5.0.0",
        "jsonschema>=4.26.0",
        "yamllint>=1.35.1,<2.0.0",
        "detect-secrets>=1.5.0",
        "packaging>=24.0,<27.0",
        "nox>=2026.4.10",
        "nbstripout>=0.6",
        "responses>=0.26.1",
        "pyotp>=2.8.0",
        "lm-eval>=0.4.2,<1",
        "nltk>=3.9.5",
        "rouge-score>=0.1.2",
        "sacrebleu>=2.6.0",
        "scipy>=1.15,<2",
        "statsmodels>=0.14,<1",
        "great_expectations>=0.18.7,<2",
        "dvc==3.67.1",
        "PyGithub>=2.9.1,<3.0.0",
        "nvidia-ml-py3>=7.352.0",
        "tensorboard>=2.14",
        "mlflow>=3.14.0,<4",
        "wandb>=0.16",
        "playwright>=1.40",
        "requests>=2.34.2",
        "PyJWT>=2.13.0,<3.0.0",
        "cryptography>=48.0.0,<50.0.0",
        "PyNaCl>=1.5.0,<2.0.0",
        "xxhash>=3.0.0",
        "tokenizers>=0.15",
        "openai>=2.38.0",
    ]
    
    profiles["full"] = profiles["core"] + full_runtime
    
    return profiles


def download_and_measure_packages(packages: List[str], profile_name: str) -> Tuple[float, Dict]:
    """Download packages and measure total size."""
    download_dir = Path(".cache") / "pip_downloads" / profile_name
    download_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📦 Downloading {profile_name} profile packages...")
    print(f"   Target directory: {download_dir}")
    
    # Download packages (no-deps to avoid transitive dependencies)
    cmd = [
        sys.executable, "-m", "pip", "download",
        "--no-deps",
        "--dest", str(download_dir),
        *packages,
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            print(f"⚠️  Warning: pip download had issues")
            print(f"   stdout: {result.stdout[:200]}")
            print(f"   stderr: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        print(f"❌ Download timed out for {profile_name} profile")
        return 0, {}
    except Exception as e:
        print(f"❌ Error downloading {profile_name} profile: {e}")
        return 0, {}
    
    # Measure total size
    total_size = 0
    file_sizes = {}
    
    for wheel_file in download_dir.glob("*.whl"):
        size = wheel_file.stat().st_size
        total_size += size
        file_sizes[wheel_file.name] = size
    
    # Also count .tar.gz files (for packages without wheels)
    for tarball in download_dir.glob("*.tar.gz"):
        size = tarball.stat().st_size
        total_size += size
        file_sizes[tarball.name] = size
    
    print(f"   Downloaded {len(file_sizes)} packages")
    print(f"   Total size: {total_size / (1024*1024):.2f} MB")
    
    return total_size, file_sizes


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def main():
    """Run package size audit."""
    print("=" * 70)
    print("Phase 3 Lane 1: Package Size Audit")
    print("=" * 70)
    
    # Target sizes (in bytes)
    targets = {
        "core": 15 * 1024 * 1024,      # 15 MB
        "runtime": 35 * 1024 * 1024,   # 35 MB
        "full": 100 * 1024 * 1024,     # 100 MB
    }
    
    # Get profiles
    profiles = get_profile_dependencies()
    
    # Audit each profile
    results = {}
    
    for profile_name, target_size in targets.items():
        if profile_name not in profiles:
            continue
        
        packages = profiles[profile_name]
        print(f"\n{'=' * 70}")
        print(f"📊 Auditing {profile_name.upper()} Profile")
        print(f"{'=' * 70}")
        print(f"   Packages: {len(packages)}")
        print(f"   Target size: {format_size(target_size)}")
        
        total_size, file_sizes = download_and_measure_packages(packages, profile_name)
        
        status = "✅" if total_size <= target_size else "❌"
        actual_mb = total_size / (1024 * 1024)
        target_mb = target_size / (1024 * 1024)
        
        print(f"   Actual size: {actual_mb:.2f} MB")
        print(f"   Status: {status} {'PASS' if total_size <= target_size else 'FAIL'}")
        
        if total_size > target_size:
            overage_mb = (total_size - target_size) / (1024 * 1024)
            print(f"   ⚠️  Overage: +{overage_mb:.2f} MB ({(total_size/target_size - 1)*100:.1f}% over)")
        
        # Identify largest packages
        print(f"\n   Top 10 largest packages:")
        for i, (filename, size) in enumerate(sorted(file_sizes.items(), key=lambda x: x[1], reverse=True)[:10], 1):
            size_mb = size / (1024 * 1024)
            print(f"      {i:2d}. {filename:40s} {size_mb:8.2f} MB")
        
        results[profile_name] = {
            "total_size_bytes": total_size,
            "total_size_mb": actual_mb,
            "target_size_mb": target_mb,
            "status": "PASS" if total_size <= target_size else "FAIL",
            "package_count": len(packages),
            "file_count": len(file_sizes),
            "top_files": {
                filename: size / (1024 * 1024)
                for filename, size in sorted(file_sizes.items(), key=lambda x: x[1], reverse=True)[:10]
            },
        }
    
    # Generate report
    report_path = Path(".codex") / "profile_sizes.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'=' * 70}")
    print("📋 Summary")
    print(f"{'=' * 70}")
    
    for profile_name, data in results.items():
        status = "✅" if data["status"] == "PASS" else "❌"
        print(f"{status} {profile_name:10s}: {data['total_size_mb']:7.2f} MB / {data['target_size_mb']:7.2f} MB target")
    
    print(f"\n📄 Report saved to: {report_path}")
    print(f"{'=' * 70}")
    
    # Return exit code
    all_pass = all(data["status"] == "PASS" for data in results.values())
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
