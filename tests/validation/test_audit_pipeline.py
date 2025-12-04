import json
import subprocess
from pathlib import Path

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
    
    # Check if it succeeded or at least ran
    assert result.returncode == 0, f"Audit failed: {result.stderr}"
    
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
    
    if not manifest_path.exists():
        # Run audit to generate manifest
        subprocess.run(
            ["python", str(repo_root / "scripts" / "space_traversal" / "audit_runner.py"), "run"],
            cwd=repo_root,
            check=True
        )
    
    assert manifest_path.exists(), "audit_run_manifest.json not found"
    
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
    
    if not scored_path.exists():
        subprocess.run(
            ["python", str(repo_root / "scripts" / "space_traversal" / "audit_runner.py"), "run"],
            cwd=repo_root,
            check=True
        )
    
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
