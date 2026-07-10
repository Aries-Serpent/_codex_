#!/usr/bin/env python3
"""
Root Folder Audit Script

Discovers all root-level files, categorizes them by type, and generates
a comprehensive dependency map showing references across the codebase.

Usage:
    python scripts/root_org/audit_root_files.py [--output-dir .codex]
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime


def get_root_files(root_dir: Path) -> Dict[str, List[Path]]:
    """Discover all root-level files and categorize them."""
    categories = {
        "critical_keep": [],
        "active_baselines": [],
        "phase_reports": [],
        "audit_reports": [],
        "release_packages": [],
        "requirement_files": [],
        "mutation_configs": [],
        "other": [],
    }

    for item in root_dir.iterdir():
        if not item.is_file() or item.name.startswith('.'):
            continue

        # Categorize
        if item.name in {"README.md", "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md", 
                         "CODE_OF_CONDUCT.md", "LICENSE", "pyproject.toml", "package.json",
                         "noxfile.py", "pytest.ini", "Cargo.toml", "Cargo.lock", "CITATION.cff"}:
            categories["critical_keep"].append(item)
        elif item.name in {"coverage.json", "coverage_cache.json", "coverage_post_ws1.json",
                          "performance_baseline.json", "decision_history.json", ".coverage_baseline.json"}:
            categories["active_baselines"].append(item)
        elif re.match(r"^PHASE_.*\.(txt|md)$", item.name) or \
             re.match(r"^(PHASE|STREAM|RELEASE)_.*_(SUMMARY|COMPLETION|REPORT|DELIVERABLE|FINAL).*\.(txt|md)$", item.name):
            categories["phase_reports"].append(item)
        elif re.match(r"^.*_AUDIT.*\.json$", item.name) or \
             re.match(r"^(API_|DOCUMENTATION_|workflow-|link-|test_validation_gate|registry_|infrastructure_|mutation_analysis_).*\.json$", item.name):
            categories["audit_reports"].append(item)
        elif item.suffix in {".zip", ".tar.gz"} or item.suffix == ".sha256":
            categories["release_packages"].append(item)
        elif item.name.startswith("requirements-") and item.suffix == ".txt":
            categories["requirement_files"].append(item)
        elif item.name.startswith(".mutmut") and item.suffix == ".ini":
            categories["mutation_configs"].append(item)
        else:
            categories["other"].append(item)

    return categories


def find_references(root_dir: Path, filename: str) -> Dict[str, List[Dict]]:
    """Find all references to a file in workflows, scripts, and docs."""
    references = {
        "workflows": [],
        "scripts": [],
        "documentation": [],
        "conditional": [],
    }

    # Search patterns to use
    patterns = [
        filename,  # Direct filename
        filename.replace('.json', ''),  # Without extension
        filename.replace('_', '-'),  # With dashes instead of underscores
    ]

    try:
        # Search in workflows
        result = subprocess.run(
            ['grep', '-r', '--include=*.yml', filename, '.github/workflows/'],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        for line in result.stdout.split('\n'):
            if line.strip():
                references["workflows"].append({
                    "file": line.split(':')[0],
                    "context": ':'.join(line.split(':')[1:])[:100],
                })

        # Search in scripts
        result = subprocess.run(
            ['grep', '-r', '--include=*.py', filename, 'scripts/'],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        for line in result.stdout.split('\n'):
            if line.strip():
                references["scripts"].append({
                    "file": line.split(':')[0],
                    "context": ':'.join(line.split(':')[1:])[:100],
                })

        # Search in documentation
        result = subprocess.run(
            ['grep', '-r', '--include=*.md', filename, 'docs/'],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        for line in result.stdout.split('\n'):
            if line.strip():
                references["documentation"].append({
                    "file": line.split(':')[0],
                    "context": ':'.join(line.split(':')[1:])[:100],
                })

        # Search for conditional checks
        result = subprocess.run(
            ['grep', '-r', f'-f "{filename}"', '--include=*.sh', '--include=*.yml'],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        for line in result.stdout.split('\n'):
            if line.strip():
                references["conditional"].append({
                    "file": line.split(':')[0],
                    "context": ':'.join(line.split(':')[1:])[:100],
                })

    except subprocess.TimeoutExpired:
        pass
    except Exception as e:
        pass

    return references


def assess_risk(refs: Dict) -> str:
    """Assess risk level based on number and type of references."""
    total_refs = sum(len(v) for v in refs.values() if isinstance(v, list))
    
    # Count critical reference types
    critical_count = len(refs.get("workflows", [])) + len(refs.get("scripts", []))
    
    if critical_count > 5:
        return "CRITICAL"
    elif critical_count > 0 or total_refs > 5:
        return "HIGH"
    elif total_refs > 2:
        return "MEDIUM"
    else:
        return "LOW"


def generate_dependency_map(root_dir: Path, output_dir: Path) -> None:
    """Generate comprehensive dependency map."""
    categories = get_root_files(root_dir)
    
    dependency_map = {
        "generated_at": datetime.now().isoformat() + "Z",
        "repository": "Aries-Serpent/_codex_",
        "summary": {
            "critical_keep": len(categories["critical_keep"]),
            "active_baselines": len(categories["active_baselines"]),
            "phase_reports": len(categories["phase_reports"]),
            "audit_reports": len(categories["audit_reports"]),
            "release_packages": len(categories["release_packages"]),
            "requirement_files": len(categories["requirement_files"]),
            "mutation_configs": len(categories["mutation_configs"]),
            "other": len(categories["other"]),
            "total": sum(len(v) for v in categories.values()),
        },
        "files_by_category": {},
        "files_by_risk": {},
        "files_needing_link_updates": [],
    }

    # Analyze each file
    all_files_analyzed = {}
    
    for category, files in categories.items():
        dependency_map["files_by_category"][category] = []
        
        for file_path in sorted(files):
            references = find_references(root_dir, file_path.name)
            risk_level = assess_risk(references)
            
            file_info = {
                "name": file_path.name,
                "size_bytes": file_path.stat().st_size,
                "risk_level": risk_level,
                "reference_count": sum(len(v) for v in references.values() if isinstance(v, list)),
                "references": references,
                "target_directory": get_target_directory(category, file_path.name),
            }
            
            dependency_map["files_by_category"][category].append(file_info)
            
            if risk_level not in dependency_map["files_by_risk"]:
                dependency_map["files_by_risk"][risk_level] = []
            dependency_map["files_by_risk"][risk_level].append(file_info["name"])
            
            if risk_level in {"CRITICAL", "HIGH", "MEDIUM"}:
                if file_path.name not in {"coverage.json", ".coverage_baseline.json", "coverage_cache.json"}:
                    dependency_map["files_needing_link_updates"].append(file_info["name"])

    # Write dependency map
    output_file = output_dir / "ROOT_FOLDER_ORGANIZATION_DEPENDENCY_MAP.json"
    with open(output_file, 'w') as f:
        json.dump(dependency_map, f, indent=2)
    
    print(f"✅ Generated {output_file}")
    print(f"\n📊 Summary:")
    print(f"   Total files: {dependency_map['summary']['total']}")
    print(f"   Critical (keep): {dependency_map['summary']['critical_keep']}")
    print(f"   Active baselines: {dependency_map['summary']['active_baselines']}")
    print(f"   Phase reports: {dependency_map['summary']['phase_reports']}")
    print(f"   Audit reports: {dependency_map['summary']['audit_reports']}")
    print(f"   Release packages: {dependency_map['summary']['release_packages']}")
    print(f"   Requirement files: {dependency_map['summary']['requirement_files']}")
    print(f"   Mutation configs: {dependency_map['summary']['mutation_configs']}")
    print(f"\n⚠️  Files needing link updates: {len(dependency_map['files_needing_link_updates'])}")
    print(f"   Risk breakdown: {dependency_map['files_by_risk']}")


def get_target_directory(category: str, filename: str) -> str:
    """Determine target directory for a file."""
    if category == "critical_keep":
        return "[KEEP ON ROOT]"
    elif category == "active_baselines":
        return ".codex/baselines/"
    elif category == "phase_reports":
        return ".codex/archive/phase_logs/"
    elif category == "audit_reports":
        return ".codex/archive/reports/"
    elif category == "release_packages":
        return ".codex/archive/releases/"
    elif category == "requirement_files":
        return "requirements/"
    elif category == "mutation_configs":
        return ".mutmut/"
    else:
        return "[REVIEW NEEDED]"


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Audit root folder and generate dependency map")
    parser.add_argument("--root", default=".", help="Repository root directory")
    parser.add_argument("--output-dir", default=".codex", help="Output directory for reports")
    
    args = parser.parse_args()
    
    root_dir = Path(args.root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generate_dependency_map(root_dir, output_dir)
