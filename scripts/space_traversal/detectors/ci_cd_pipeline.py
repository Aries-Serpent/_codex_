"""Dynamic detector for CI/CD pipeline capability.

Detects GitHub Actions, pre-commit hooks, CI configurations, and
automated testing/deployment workflows.
"""
from __future__ import annotations


def detect(file_index: dict) -> dict:
    """Detect CI/CD pipeline capability.

    Args:
        file_index: Context index from S1 with file metadata

    Returns:
        Capability detection result
    """
    files = file_index.get("files", [])

    # Evidence collection
    github_actions = []
    pre_commit = []
    ci_configs = []
    test_scripts = []

    for f in files:
        path = f["path"]

        # GitHub Actions (note: per AGENTS.md, not activated)
        if path.startswith(".github/workflows/"):
            github_actions.append(path)

        # Pre-commit hooks
        if ".pre-commit-config" in path or path.startswith(".pre-commit"):
            pre_commit.append(path)

        # Other CI configs
        if any(
            name in path
            for name in [
                ".gitlab-ci.yml",
                ".travis.yml",
                "circle.yml",
                "tox.ini",
                "noxfile.py",
            ]
        ):
            ci_configs.append(path)

        # Test/validation scripts
        if any(
            kw in path.lower()
            for kw in [
                "validate",
                "lint",
                "check",
                "audit",
                "gates",
                "pre-commit",
            ]
        ) and path.endswith((".sh", ".py")):
            test_scripts.append(path)

    # Pattern detection
    found_patterns = []
    required_patterns = ["ci", "pre-commit", "workflow", "automation", "validation"]

    evidence_files = sorted(set(github_actions + pre_commit + ci_configs + test_scripts))

    if github_actions or ci_configs:
        found_patterns.append("ci")
    if pre_commit:
        found_patterns.append("pre-commit")
    if github_actions:
        found_patterns.append("workflow")
    if test_scripts or ci_configs:
        found_patterns.append("automation")
    if any("validate" in f.lower() or "audit" in f.lower() for f in test_scripts):
        found_patterns.append("validation")

    return {
        "id": "ci-cd-pipeline",
        "evidence_files": evidence_files,
        "found_patterns": sorted(set(found_patterns)),
        "required_patterns": required_patterns,
        "meta": {
            "github_actions": len(github_actions),
            "pre_commit_hooks": len(pre_commit),
            "ci_configs": len(ci_configs),
            "validation_scripts": len(test_scripts),
            "note": "GitHub Actions present but not activated per AGENTS.md",
        },
    }
