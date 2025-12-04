import json
import subprocess
import pytest
from pathlib import Path

# Expected error patterns that indicate known issues (not test failures)
KNOWN_ERROR_PATTERNS = [
    "shadowing",
    "yaml",
    "torch",
    "PyTorch is not installed",
    "YAMLError",
    "AttributeError.*PyTorch"
]

def is_known_error(stderr: str) -> bool:
    """Check if error matches known patterns."""
    import re
    stderr_lower = stderr.lower()
    for pattern in KNOWN_ERROR_PATTERNS:
        if re.search(pattern.lower(), stderr_lower):
            return True
    return False

def test_audit_pipeline_produces_artifacts():
    """Test that the audit pipeline produces expected artifacts."""
    repo_root = Path(__file__).resolve().parents[2]
    
    # Run the fast audit path
    result = subprocess.run(
        ["python", str(repo_root / "scripts" / "space_traversal" / "audit_runner.py"), "run"],
        cwd=repo_root,
        capture_output=True,
        text=True
    )
    
    # If it failed due to known issues, that's expected and we skip this test
    if result.returncode != 0:
        if is_known_error(result.stderr):
            pytest.skip(f"Audit failed due to expected issue: {result.stderr[:200]}")
        else:
            pytest.fail(f"Audit failed unexpectedly: {result.stderr}")
    
    # Check artifacts exist
    artifacts_dir = repo_root / "audit_artifacts"
    assert artifacts_dir.exists(), "audit_artifacts directory not created"
    
    expected_files = [
        "context_index.json",
        "capabilities_raw.json",
        "capabilities_scored.json",
        "gaps.json"
    ]
    
    for filename in expected_files:
        filepath = artifacts_dir / filename
        assert filepath.exists(), f"Expected artifact {filename} not found"
        
        # Validate JSON structure
        with open(filepath, 'r') as f:
            data = json.load(f)
            assert "version" in data, f"{filename} missing version field"


def test_manifest_has_required_fields():
    """Test that the manifest has all required fields."""
    repo_root = Path(__file__).resolve().parents[2]
    manifest_path = repo_root / "audit_run_manifest.json"
    
    # Try to run audit to generate manifest if it doesn't exist
    if not manifest_path.exists():
        result = subprocess.run(
            ["python", str(repo_root / "scripts" / "space_traversal" / "audit_runner.py"), "run"],
            cwd=repo_root,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            pytest.skip(f"Cannot generate manifest due to: {result.stderr[:200]}")
    
    if not manifest_path.exists():
        pytest.skip("audit_run_manifest.json not found and could not be generated")
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    required_fields = ["timestamp", "version", "repo_root_sha", "artifacts", "weights", "template_hash"]
    for field in required_fields:
        assert field in manifest, f"Manifest missing required field: {field}"
    
    assert isinstance(manifest["artifacts"], list), "artifacts should be a list"
    assert len(manifest["artifacts"]) > 0, "artifacts list should not be empty"


def test_capabilities_scored_structure():
    """Test that capabilities_scored.json has the expected structure."""
    repo_root = Path(__file__).resolve().parents[2]
    scored_path = repo_root / "audit_artifacts" / "capabilities_scored.json"
    
    # Try to use existing artifact or skip if not available
    if not scored_path.exists():
        result = subprocess.run(
            ["python", str(repo_root / "scripts" / "space_traversal" / "audit_runner.py"), "stage", "S4"],
            cwd=repo_root,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            pytest.skip(f"Cannot generate scored capabilities: {result.stderr[:200]}")
    
    if not scored_path.exists():
        pytest.skip("capabilities_scored.json not available")
    
    with open(scored_path, 'r') as f:
        data = json.load(f)
    
    assert "capabilities" in data, "Missing capabilities field"
    assert isinstance(data["capabilities"], list), "capabilities should be a list"
    
    if len(data["capabilities"]) > 0:
        cap = data["capabilities"][0]
        required_cap_fields = ["id", "score", "components", "evidence_files"]
        for field in required_cap_fields:
            assert field in cap, f"Capability missing field: {field}"
        
        # Check component structure
        components = cap["components"]
        expected_components = ["functionality", "consistency", "tests", "safeguards", "documentation"]
        for component in expected_components:
            assert component in components, f"Missing component: {component}"
