"""Enhanced capability detectors with advanced patterns.

Provides detectors for:
- Configuration capability
- Tokenization capability
- Evaluation capability
- Security capability
- Extensibility capability
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .core import DetectorResult, clamp01


def _check_path_exists(path: str | Path) -> bool:
    """Check if path exists."""
    return Path(path).exists()


def _count_python_files(directory: str | Path) -> int:
    """Count Python files in directory."""
    path = Path(directory)
    if not path.exists():
        return 0
    return sum(1 for _ in path.rglob("*.py"))


def _count_test_files(directory: str | Path) -> int:
    """Count test files in directory."""
    path = Path(directory)
    if not path.exists():
        return 0
    return sum(1 for f in path.rglob("test_*.py"))


def _check_file_content(filepath: str | Path, patterns: list[str]) -> dict[str, bool]:
    """Check if file contains specified patterns."""
    path = Path(filepath)
    if not path.exists():
        return {p: False for p in patterns}

    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        return {p: p in content for p in patterns}
    except Exception:
        return {p: False for p in patterns}


# --- Configuration Capability Detector ---


def detector_configuration() -> DetectorResult:
    """Detect configuration capability maturity.

    Checks:
    - Schema enforcement (pydantic/dataclass configs)
    - Config hashing for reproducibility
    - Drift detection capability
    - Defaults coverage
    - YAML loading support
    """
    score = 0.0
    details: dict[str, Any] = {"checks": {}}

    # Check config schema exists
    config_schema_path = Path("src/codex_ml/config_schema.py")
    if _check_path_exists(config_schema_path):
        score += 0.15
        details["checks"]["config_schema_exists"] = True

        # Check for pydantic validation
        patterns = _check_file_content(
            config_schema_path,
            ["BaseModel", "field_validator", "ValidationError", "model_validate"],
        )
        if all(patterns.values()):
            score += 0.15
            details["checks"]["pydantic_validation"] = True
        else:
            details["checks"]["pydantic_validation"] = patterns
    else:
        details["checks"]["config_schema_exists"] = False

    # Check for Hydra configs
    configs_dirs = ["configs/", "conf/", "config/"]
    config_files = 0
    for d in configs_dirs:
        if _check_path_exists(d):
            config_files += len(list(Path(d).rglob("*.yaml")))
    if config_files > 0:
        score += 0.15
        details["checks"]["hydra_configs"] = config_files
    else:
        details["checks"]["hydra_configs"] = 0

    # Check for config tests
    config_tests = _count_test_files("tests/capabilities/configuration")
    config_tests += _count_test_files("tests/config")
    if config_tests > 0:
        score += 0.2
        details["checks"]["config_tests"] = config_tests
    else:
        details["checks"]["config_tests"] = 0

    # Check for schema validation tests
    test_patterns = ["test_schema", "validate_config", "TestSchema"]
    for test_dir in ["tests/", "tests/config/"]:
        if _check_path_exists(test_dir):
            for f in Path(test_dir).rglob("test_*.py"):
                patterns = _check_file_content(f, test_patterns)
                if any(patterns.values()):
                    score += 0.1
                    details["checks"]["schema_validation_tests"] = True
                    break

    # Check for environment override support
    if _check_file_content(config_schema_path, ["Field", "default", "description"]).get("Field", False):
        score += 0.1
        details["checks"]["field_documentation"] = True

    # Check for config hashing capability
    if _check_file_content(
        "tests/capabilities/configuration/test_config_schema_validation.py",
        ["compute_config_hash", "sha256"],
    ).get("compute_config_hash", False):
        score += 0.15
        details["checks"]["config_hashing"] = True

    details["score_breakdown"] = {
        "schema_exists": 0.15,
        "pydantic_validation": 0.15,
        "hydra_configs": 0.15,
        "config_tests": 0.2,
        "schema_validation_tests": 0.1,
        "field_documentation": 0.1,
        "config_hashing": 0.15,
    }

    return DetectorResult(
        name="configuration",
        score=clamp01(score),
        details=details,
    )


# --- Tokenization Capability Detector ---


def detector_tokenization() -> DetectorResult:
    """Detect tokenization capability maturity.

    Checks:
    - Tokenizer implementations
    - Fast tokenizer support
    - Vocab management
    - Special token handling
    - Multilingual support
    - Checksum validation
    """
    score = 0.0
    details: dict[str, Any] = {"checks": {}}

    # Check tokenization module exists
    tokenization_paths = [
        "src/codex_ml/tokenization/",
        "src/tokenization/",
        "tokenization/",
    ]
    tokenization_files = 0
    for p in tokenization_paths:
        if _check_path_exists(p):
            tokenization_files += _count_python_files(p)

    if tokenization_files > 0:
        score += 0.15
        details["checks"]["tokenization_module"] = tokenization_files
    else:
        details["checks"]["tokenization_module"] = 0

    # Check for HF tokenizer integration
    hf_patterns = ["HfTokenizer", "AutoTokenizer", "PreTrainedTokenizer"]
    for p in tokenization_paths:
        if _check_path_exists(p):
            for f in Path(p).rglob("*.py"):
                patterns = _check_file_content(f, hf_patterns)
                if any(patterns.values()):
                    score += 0.1
                    details["checks"]["hf_integration"] = True
                    break

    # Check for SentencePiece integration
    sp_patterns = ["sentencepiece", "SentencePiece", "sp_model"]
    for p in tokenization_paths:
        if _check_path_exists(p):
            for f in Path(p).rglob("*.py"):
                patterns = _check_file_content(f, sp_patterns)
                if any(patterns.values()):
                    score += 0.1
                    details["checks"]["sentencepiece_integration"] = True
                    break

    # Check for tokenization tests
    tokenization_tests = _count_test_files("tests/capabilities/tokenization")
    tokenization_tests += sum(
        1 for f in Path("tests/").rglob("test_token*.py") if f.exists()
    )
    if tokenization_tests > 0:
        score += 0.2
        details["checks"]["tokenization_tests"] = tokenization_tests
    else:
        details["checks"]["tokenization_tests"] = 0

    # Check for vocab checksum validation
    if _check_file_content(
        "tests/capabilities/tokenization/test_tokenization_comprehensive.py",
        ["compute_vocab_checksum", "checksum"],
    ).get("compute_vocab_checksum", False):
        score += 0.15
        details["checks"]["vocab_checksum"] = True

    # Check for special token handling
    special_token_patterns = ["<pad>", "<unk>", "<bos>", "<eos>", "special_tokens"]
    for p in tokenization_paths:
        if _check_path_exists(p):
            for f in Path(p).rglob("*.py"):
                patterns = _check_file_content(f, special_token_patterns)
                if sum(patterns.values()) >= 2:
                    score += 0.1
                    details["checks"]["special_tokens"] = True
                    break

    # Check for streaming tokenization
    if _check_file_content(
        "tests/capabilities/tokenization/test_tokenization_comprehensive.py",
        ["StreamingTokenizer", "streaming"],
    ).get("StreamingTokenizer", False):
        score += 0.1
        details["checks"]["streaming_tokenization"] = True

    # Check for multilingual support tests
    if _check_file_content(
        "tests/capabilities/tokenization/test_tokenization_comprehensive.py",
        ["multilingual", "unicode", "cjk", "emoji"],
    ).get("unicode", False):
        score += 0.1
        details["checks"]["multilingual_support"] = True

    return DetectorResult(
        name="tokenization",
        score=clamp01(score),
        details=details,
    )


# --- Evaluation Capability Detector ---


def detector_evaluation() -> DetectorResult:
    """Detect evaluation and metrics capability maturity.

    Checks:
    - Metric implementations
    - Determinism enforcement
    - NDJSON/CSV schema validation
    - Regression suite coverage
    - Metric registry
    """
    score = 0.0
    details: dict[str, Any] = {"checks": {}}

    # Check metrics module exists
    metrics_paths = ["src/codex_ml/metrics/", "src/codex_ml/eval/"]
    metrics_files = 0
    for p in metrics_paths:
        if _check_path_exists(p):
            metrics_files += _count_python_files(p)

    if metrics_files > 0:
        score += 0.15
        details["checks"]["metrics_module"] = metrics_files
    else:
        details["checks"]["metrics_module"] = 0

    # Check for metric registry
    registry_patterns = ["MetricRegistry", "register_metric", "get_metric"]
    for p in metrics_paths:
        if _check_path_exists(p):
            for f in Path(p).rglob("*.py"):
                patterns = _check_file_content(f, registry_patterns)
                if any(patterns.values()):
                    score += 0.1
                    details["checks"]["metric_registry"] = True
                    break

    # Check for evaluation tests
    eval_tests = _count_test_files("tests/capabilities/evaluation")
    eval_tests += sum(1 for f in Path("tests/").rglob("test_eval*.py") if f.exists())
    eval_tests += sum(1 for f in Path("tests/").rglob("test_metric*.py") if f.exists())
    if eval_tests > 0:
        score += 0.2
        details["checks"]["evaluation_tests"] = eval_tests
    else:
        details["checks"]["evaluation_tests"] = 0

    # Check for determinism tests
    if _check_file_content(
        "tests/capabilities/evaluation/test_evaluation_comprehensive.py",
        ["deterministic", "TestMetricDeterminism"],
    ).get("deterministic", False):
        score += 0.15
        details["checks"]["determinism_tests"] = True

    # Check for NDJSON schema validation
    if _check_file_content(
        "tests/capabilities/evaluation/test_evaluation_comprehensive.py",
        ["NDJSON_SCHEMA", "validate_ndjson"],
    ).get("NDJSON_SCHEMA", False):
        score += 0.1
        details["checks"]["ndjson_schema"] = True

    # Check for regression suite
    if _check_file_content(
        "tests/capabilities/evaluation/test_evaluation_comprehensive.py",
        ["RegressionSuite", "check_regression"],
    ).get("RegressionSuite", False):
        score += 0.15
        details["checks"]["regression_suite"] = True

    # Check for eval data versioning
    if _check_file_content(
        "tests/capabilities/evaluation/test_evaluation_comprehensive.py",
        ["EvalDataVersion", "data_checksum"],
    ).get("EvalDataVersion", False):
        score += 0.15
        details["checks"]["eval_data_versioning"] = True

    return DetectorResult(
        name="evaluation",
        score=clamp01(score),
        details=details,
    )


# --- Security Capability Detector ---


def detector_security() -> DetectorResult:
    """Detect security and safety capability maturity.

    Checks:
    - Secrets scanning
    - Dependency scanning
    - Prompt sanitization
    - SBOM generation
    - Provenance tracking
    """
    score = 0.0
    details: dict[str, Any] = {"checks": {}}

    # Check security config files
    security_files = [
        ".secrets.baseline",
        "bandit.yaml",
        ".bandit.yml",
        ".gitleaks.toml",
    ]
    found_security_files = sum(1 for f in security_files if _check_path_exists(f))
    if found_security_files > 0:
        score += 0.1 * min(found_security_files, 3)
        details["checks"]["security_configs"] = found_security_files

    # Check for semgrep rules
    if _check_path_exists("semgrep_rules/"):
        rule_count = len(list(Path("semgrep_rules/").rglob("*.yaml")))
        if rule_count > 0:
            score += 0.1
            details["checks"]["semgrep_rules"] = rule_count

    # Check security module
    security_paths = ["src/codex_ml/security/", "src/codex_ml/safety/"]
    security_files_count = 0
    for p in security_paths:
        if _check_path_exists(p):
            security_files_count += _count_python_files(p)

    if security_files_count > 0:
        score += 0.1
        details["checks"]["security_module"] = security_files_count

    # Check for security tests
    security_tests = _count_test_files("tests/capabilities/security")
    security_tests += _count_test_files("tests/security")
    security_tests += _count_test_files("tests/safety")
    if security_tests > 0:
        score += 0.2
        details["checks"]["security_tests"] = security_tests
    else:
        details["checks"]["security_tests"] = 0

    # Check for secrets scanning tests
    if _check_file_content(
        "tests/capabilities/security/test_security_comprehensive.py",
        ["scan_for_secrets", "SECRET_PATTERNS"],
    ).get("scan_for_secrets", False):
        score += 0.1
        details["checks"]["secrets_scanning"] = True

    # Check for dependency scanning tests
    if _check_file_content(
        "tests/capabilities/security/test_security_comprehensive.py",
        ["DependencyScanner", "CVE"],
    ).get("DependencyScanner", False):
        score += 0.1
        details["checks"]["dependency_scanning"] = True

    # Check for prompt sanitization
    if _check_file_content(
        "tests/capabilities/security/test_security_comprehensive.py",
        ["sanitize_prompt", "DANGEROUS_PATTERNS"],
    ).get("sanitize_prompt", False):
        score += 0.1
        details["checks"]["prompt_sanitization"] = True

    # Check for SBOM generation
    if _check_file_content(
        "tests/capabilities/security/test_security_comprehensive.py",
        ["SBOMGenerator", "CycloneDX", "SPDX"],
    ).get("SBOMGenerator", False):
        score += 0.1
        details["checks"]["sbom_generation"] = True

    return DetectorResult(
        name="security",
        score=clamp01(score),
        details=details,
    )


# --- Extensibility Capability Detector ---


def detector_extensibility() -> DetectorResult:
    """Detect extensibility capability maturity.

    Checks:
    - Plugin system
    - Registry patterns
    - Contract tests
    - Version compatibility
    - Self-healing discovery
    """
    score = 0.0
    details: dict[str, Any] = {"checks": {}}

    # Check plugin system
    plugin_paths = ["src/codex_ml/plugins/", "src/codex_ml/registry/"]
    plugin_files = 0
    for p in plugin_paths:
        if _check_path_exists(p):
            plugin_files += _count_python_files(p)

    if plugin_files > 0:
        score += 0.15
        details["checks"]["plugin_system"] = plugin_files

    # Check for base plugin interface
    if _check_path_exists("src/codex_ml/plugins/base.py"):
        patterns = _check_file_content(
            "src/codex_ml/plugins/base.py",
            ["BasePlugin", "abstractmethod", "name", "version"],
        )
        if sum(patterns.values()) >= 3:
            score += 0.1
            details["checks"]["plugin_interface"] = True

    # Check for registry implementations
    registry_patterns = ["register", "get", "list_"]
    for p in plugin_paths:
        if _check_path_exists(p):
            for f in Path(p).rglob("*.py"):
                patterns = _check_file_content(f, registry_patterns)
                if sum(patterns.values()) >= 2:
                    score += 0.1
                    details["checks"]["registry_implementation"] = True
                    break

    # Check for extensibility tests
    ext_tests = _count_test_files("tests/capabilities/extensibility")
    ext_tests += _count_test_files("tests/plugins")
    if ext_tests > 0:
        score += 0.2
        details["checks"]["extensibility_tests"] = ext_tests
    else:
        details["checks"]["extensibility_tests"] = 0

    # Check for contract tests
    if _check_file_content(
        "tests/capabilities/extensibility/test_extensibility_comprehensive.py",
        ["PluginInterface", "TestPluginContract"],
    ).get("PluginInterface", False):
        score += 0.1
        details["checks"]["contract_tests"] = True

    # Check for version compatibility
    if _check_file_content(
        "tests/capabilities/extensibility/test_extensibility_comprehensive.py",
        ["VersionCompatibility", "is_compatible"],
    ).get("VersionCompatibility", False):
        score += 0.1
        details["checks"]["version_compatibility"] = True

    # Check for sandbox tests
    if _check_file_content(
        "tests/capabilities/extensibility/test_extensibility_comprehensive.py",
        ["PluginSandbox", "validate_plugin_code"],
    ).get("PluginSandbox", False):
        score += 0.1
        details["checks"]["plugin_sandboxing"] = True

    # Check for self-healing discovery
    if _check_file_content(
        "tests/capabilities/extensibility/test_extensibility_comprehensive.py",
        ["SelfHealingDiscovery", "discover_plugin"],
    ).get("SelfHealingDiscovery", False):
        score += 0.15
        details["checks"]["self_healing_discovery"] = True

    return DetectorResult(
        name="extensibility",
        score=clamp01(score),
        details=details,
    )


# --- Aggregate Capability Scorecard ---


def get_capability_detectors() -> list:
    """Get all capability detectors."""
    return [
        detector_configuration,
        detector_tokenization,
        detector_evaluation,
        detector_security,
        detector_extensibility,
    ]


def run_capability_audit() -> dict[str, Any]:
    """Run full capability audit and return scorecard."""
    results = []
    for detector in get_capability_detectors():
        result = detector()
        results.append(result)

    total_score = sum(r.score for r in results) / len(results) if results else 0.0

    return {
        "total_score": round(total_score, 4),
        "by_capability": {r.name: round(r.score, 4) for r in results},
        "details": [{**r.__dict__} for r in results],
        "threshold": 0.85,
        "passing": total_score >= 0.85,
    }


__all__ = [
    "detector_configuration",
    "detector_tokenization",
    "detector_evaluation",
    "detector_security",
    "detector_extensibility",
    "get_capability_detectors",
    "run_capability_audit",
]
