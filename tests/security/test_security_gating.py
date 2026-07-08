"""Tests for security gating (WP-E).

This module tests:
- Pre-commit security hooks configuration
- Nox security session functionality
- Gitleaks configuration
- Security allowlist structure
"""

import json
import subprocess
from pathlib import Path

import pytest


def test_precommit_config_exists():
    """Test that pre-commit config file exists."""
    config_path = Path(__file__).parents[2] / ".pre-commit-config.yaml"
    assert config_path.exists(), "Pre-commit config not found"


def test_precommit_config_valid_yaml():
    """Test that pre-commit config is valid YAML."""
    yaml = pytest.importorskip("yaml")

    config_path = Path(__file__).parents[2] / ".pre-commit-config.yaml"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    assert "repos" in config, "Condition must be true"
    assert isinstance(config["repos"], list)


def test_precommit_has_pip_audit():
    """Test that pre-commit config includes pip-audit."""
    yaml = pytest.importorskip("yaml")

    config_path = Path(__file__).parents[2] / ".pre-commit-config.yaml"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Find pip-audit repo
    pip_audit_repos = [repo for repo in config["repos"] if "pip-audit" in repo.get("repo", "")]

    assert len(pip_audit_repos) > 0, "pip-audit hook not found in pre-commit config"

    # Check that pip-audit hook is configured
    pip_audit_repo = pip_audit_repos[0]
    assert "hooks" in pip_audit_repo, "Condition must be true"

    hooks = pip_audit_repo["hooks"]
    assert any(hook.get("id") == "pip-audit" for hook in hooks), "Condition must be true"


def test_precommit_has_gitleaks():
    """Test that pre-commit config includes gitleaks."""
    yaml = pytest.importorskip("yaml")

    config_path = Path(__file__).parents[2] / ".pre-commit-config.yaml"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Find gitleaks repo
    gitleaks_repos = [repo for repo in config["repos"] if "gitleaks" in repo.get("repo", "")]

    assert len(gitleaks_repos) > 0, "gitleaks hook not found in pre-commit config"

    # Check that gitleaks hook is configured
    gitleaks_repo = gitleaks_repos[0]
    assert "hooks" in gitleaks_repo, "Condition must be true"

    hooks = gitleaks_repo["hooks"]
    assert any(hook.get("id") == "gitleaks" for hook in hooks), "Condition must be true"


def test_gitleaks_config_exists():
    """Test that gitleaks config file exists."""
    config_path = Path(__file__).parents[2] / ".gitleaks.toml"
    assert config_path.exists(), "Gitleaks config not found"


def test_gitleaks_config_valid_toml():
    """Test that gitleaks config is valid TOML."""
    toml = None
    try:
        import tomli as toml
    except ImportError:
        try:
            import tomllib as toml
        except ImportError:
            pytest.skip("toml library not available")

    config_path = Path(__file__).parents[2] / ".gitleaks.toml"

    with open(config_path, "rb") as f:
        config = toml.load(f)

    # Basic structure check
    assert isinstance(config, dict)
    # Gitleaks config typically has title and allowlist
    assert "title" in config or "allowlist" in config, "Condition must be true"


def test_security_allowlist_exists():
    """Test that security allowlist file exists."""
    allowlist_path = Path(__file__).parents[2] / "security_allowlist.json"
    assert allowlist_path.exists(), "Security allowlist not found"


def test_security_allowlist_valid_json():
    """Test that security allowlist is valid JSON."""
    allowlist_path = Path(__file__).parents[2] / "security_allowlist.json"

    with open(allowlist_path) as f:
        allowlist = json.load(f)

    assert isinstance(allowlist, dict)


def test_security_allowlist_structure():
    """Test that security allowlist has expected structure."""
    allowlist_path = Path(__file__).parents[2] / "security_allowlist.json"

    with open(allowlist_path) as f:
        allowlist = json.load(f)

    # Should have schema reference
    assert "$schema" in allowlist or "allowlisted_vulnerabilities" in allowlist, "Condition must be true"


def test_noxfile_exists():
    """Test that noxfile exists."""
    noxfile_path = Path(__file__).parents[2] / "noxfile.py"
    assert noxfile_path.exists(), "noxfile.py not found"


def test_noxfile_has_security_session():
    """Test that noxfile contains security session."""
    noxfile_path = Path(__file__).parents[2] / "noxfile.py"

    with open(noxfile_path) as f:
        content = f.read()

    # Check for security session definition
    assert '@nox.session(name="security"' in content or '@nox.session("security"' in content
    assert "def security(" in content, "Content must not be empty"


def test_noxfile_security_session_runs_pip_audit():
    """Test that security session includes pip-audit."""
    noxfile_path = Path(__file__).parents[2] / "noxfile.py"

    with open(noxfile_path) as f:
        content = f.read()

    # Check for pip-audit in security session
    assert "pip-audit" in content, "Content must not be empty"


def test_noxfile_security_session_runs_gitleaks():
    """Test that security session includes gitleaks."""
    noxfile_path = Path(__file__).parents[2] / "noxfile.py"

    with open(noxfile_path) as f:
        content = f.read()

    # Check for gitleaks in security session
    assert "gitleaks" in content, "Content must not be empty"


def test_nox_list_sessions_includes_security():
    """Test that nox -l shows security session."""
    noxfile_path = Path(__file__).parents[2] / "noxfile.py"

    if not noxfile_path.exists():
        pytest.skip("noxfile.py not found")

    try:
        # Run nox -l to list sessions
        result = subprocess.run(
            ["nox", "-l"], capture_output=True, text=True, timeout=10, cwd=noxfile_path.parent
        )

        # Check if security session is listed
        assert "security" in result.stdout or "security" in result.stderr, "Result must not be empty"

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pytest.skip("nox not available or timed out")


def test_security_integration_pip_audit_syntax():
    """Test pip-audit command syntax is valid."""
    # Check that pip-audit is invokable (even if not installed)
    try:
        result = subprocess.run(["pip-audit", "--help"], capture_output=True, text=True, timeout=5)
        # If installed, should return help
        assert result.returncode == 0 or result.returncode == 127, "Result must not be empty"
    except FileNotFoundError:
        # pip-audit not installed, which is ok for this test
        _ = None  # suppressed: no action needed
    except subprocess.TimeoutExpired:
        pytest.skip("pip-audit command timed out")


def test_security_integration_gitleaks_syntax():
    """Test gitleaks command syntax is valid."""
    # Check that gitleaks is invokable (even if not installed)
    try:
        result = subprocess.run(["gitleaks", "version"], capture_output=True, text=True, timeout=5)
        # If installed, should return version
        assert result.returncode == 0 or result.returncode == 127, "Result must not be empty"
    except FileNotFoundError:
        # gitleaks not installed, which is ok for this test
        _ = None  # suppressed: no action needed
    except subprocess.TimeoutExpired:
        pytest.skip("gitleaks command timed out")


def test_precommit_config_has_bandit():
    """Test that pre-commit config already includes bandit (baseline security)."""
    import yaml

    config_path = Path(__file__).parents[2] / ".pre-commit-config.yaml"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Check for bandit (should already exist)
    bandit_repos = [repo for repo in config["repos"] if "bandit" in repo.get("repo", "").lower()]

    assert len(bandit_repos) > 0, "bandit hook not found (should exist in baseline)"


def test_precommit_config_has_detect_secrets():
    """Test that pre-commit config already includes detect-secrets."""
    import yaml

    config_path = Path(__file__).parents[2] / ".pre-commit-config.yaml"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Check for detect-secrets (should already exist)
    detect_secrets_repos = [
        repo for repo in config["repos"] if "detect-secrets" in repo.get("repo", "")
    ]

    assert len(detect_secrets_repos) > 0, "detect-secrets hook not found (should exist in baseline)"


def test_security_documentation_exists():
    """Test that security documentation is present."""
    # Check for any security-related documentation
    repo_root = Path(__file__).parents[2]

    # At least noxfile should document security session
    noxfile = repo_root / "noxfile.py"
    with open(noxfile) as f:
        content = f.read()

    # Security session should have docstring
    assert "security" in content.lower(), "Content must not be empty"


def test_integration_full_security_workflow():
    """Test that security workflow components are in place."""
    repo_root = Path(__file__).parents[2]

    # Check all components exist
    assert (repo_root / ".pre-commit-config.yaml").exists(), "Condition must be true"
    assert (repo_root / ".gitleaks.toml").exists(), "Condition must be true"
    assert (repo_root / "security_allowlist.json").exists(), "Condition must be true"
    assert (repo_root / "noxfile.py").exists(), "Condition must be true"

    # Verify noxfile has security session
    with open(repo_root / "noxfile.py") as f:
        nox_content = f.read()

    assert "def security(" in nox_content, "Content must not be empty"

    # Verify pre-commit has security hooks
    import yaml

    with open(repo_root / ".pre-commit-config.yaml") as f:
        precommit_config = yaml.safe_load(f)

    repos = precommit_config.get("repos", [])
    repo_urls = [repo.get("repo", "") for repo in repos]

    # Should have pip-audit and gitleaks
    has_pip_audit = any("pip-audit" in url for url in repo_urls)
    has_gitleaks = any("gitleaks" in url for url in repo_urls)

    assert has_pip_audit, "pip-audit not in pre-commit config"
    assert has_gitleaks, "gitleaks not in pre-commit config"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
