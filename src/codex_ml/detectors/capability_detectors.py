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


# --- Logging Capability Detector ---


def detector_logging() -> DetectorResult:
    """Detect logging and monitoring capability maturity.

    Checks:
    - Centralized metrics sink
    - Prometheus/OTel exporters
    - Log rotation
    - PII scrubbing
    - Alerting
    """
    score = 0.0
    details: dict[str, Any] = {"checks": {}}

    # Check logging module exists
    logging_paths = ["src/codex/logging/", "src/codex_ml/logging/", "monitoring/"]
    logging_files = 0
    for p in logging_paths:
        if _check_path_exists(p):
            logging_files += _count_python_files(p)

    if logging_files > 0:
        score += 0.15
        details["checks"]["logging_module"] = logging_files

    # Check for logging tests
    logging_tests = _count_test_files("tests/capabilities/logging")
    logging_tests += _count_test_files("tests/logging")
    if logging_tests > 0:
        score += 0.2
        details["checks"]["logging_tests"] = logging_tests

    # Check for metrics sink
    if _check_file_content(
        "tests/capabilities/logging/test_logging_comprehensive.py",
        ["MetricsSink", "record"],
    ).get("MetricsSink", False):
        score += 0.15
        details["checks"]["metrics_sink"] = True

    # Check for Prometheus exporter
    if _check_file_content(
        "tests/capabilities/logging/test_logging_comprehensive.py",
        ["PrometheusExporter", "export"],
    ).get("PrometheusExporter", False):
        score += 0.1
        details["checks"]["prometheus_exporter"] = True

    # Check for PII scrubbing
    if _check_file_content(
        "tests/capabilities/logging/test_logging_comprehensive.py",
        ["scrub_pii", "PII_PATTERNS"],
    ).get("scrub_pii", False):
        score += 0.15
        details["checks"]["pii_scrubbing"] = True

    # Check for alerting
    if _check_file_content(
        "tests/capabilities/logging/test_logging_comprehensive.py",
        ["AlertRule", "AlertManager"],
    ).get("AlertRule", False):
        score += 0.15
        details["checks"]["alerting"] = True

    # Check for log rotation
    if _check_file_content(
        "tests/capabilities/logging/test_logging_comprehensive.py",
        ["LogRotator", "should_rotate"],
    ).get("LogRotator", False):
        score += 0.1
        details["checks"]["log_rotation"] = True

    return DetectorResult(
        name="logging",
        score=clamp01(score),
        details=details,
    )


# --- Checkpointing Capability Detector ---


def detector_checkpointing() -> DetectorResult:
    """Detect checkpointing and resume capability maturity.

    Checks:
    - RNG state validation
    - Checksum verification
    - Best-k retention
    - Corruption handling
    """
    score = 0.0
    details: dict[str, Any] = {"checks": {}}

    # Check checkpointing module exists
    ckpt_paths = ["src/training/checkpoint_manager.py", "src/codex_ml/checkpointing/"]
    ckpt_found = any(_check_path_exists(p) for p in ckpt_paths)
    if ckpt_found:
        score += 0.15
        details["checks"]["checkpointing_module"] = True

    # Check for checkpointing tests
    ckpt_tests = _count_test_files("tests/capabilities/checkpoint_capability")
    ckpt_tests += sum(1 for f in Path("tests/").rglob("test_checkpoint*.py") if f.exists())
    if ckpt_tests > 0:
        score += 0.2
        details["checks"]["checkpointing_tests"] = ckpt_tests

    # Check for RNG state tests
    if _check_file_content(
        "tests/capabilities/checkpoint_capability/test_checkpointing_comprehensive.py",
        ["RNGState", "python_state"],
    ).get("RNGState", False):
        score += 0.15
        details["checks"]["rng_state"] = True

    # Check for checksum validation
    if _check_file_content(
        "tests/capabilities/checkpoint_capability/test_checkpointing_comprehensive.py",
        ["compute_checkpoint_checksum", "verify_checksum"],
    ).get("compute_checkpoint_checksum", False):
        score += 0.15
        details["checks"]["checksum_validation"] = True

    # Check for best-k retention
    if _check_file_content(
        "tests/capabilities/checkpoint_capability/test_checkpointing_comprehensive.py",
        ["BestKCheckpointManager", "get_checkpoints_to_delete"],
    ).get("BestKCheckpointManager", False):
        score += 0.15
        details["checks"]["best_k_retention"] = True

    # Check for corruption handling
    if _check_file_content(
        "tests/capabilities/checkpoint_capability/test_checkpointing_comprehensive.py",
        ["CorruptionDetector", "AutoHealManager"],
    ).get("CorruptionDetector", False):
        score += 0.2
        details["checks"]["corruption_handling"] = True

    return DetectorResult(
        name="checkpointing",
        score=clamp01(score),
        details=details,
    )


# --- CI/Test Capability Detector ---


def detector_ci_test() -> DetectorResult:
    """Detect CI/Test capability maturity.

    Checks:
    - Coverage gates
    - Nox sessions
    - Deterministic seeding
    - Test isolation
    """
    score = 0.0
    details: dict[str, Any] = {"checks": {}}

    # Check CI infrastructure exists
    ci_files = ["noxfile.py", "pytest.ini", ".pre-commit-config.yaml"]
    ci_found = sum(1 for f in ci_files if _check_path_exists(f))
    if ci_found > 0:
        score += 0.15
        details["checks"]["ci_infrastructure"] = ci_found

    # Check for CI tests
    ci_tests = _count_test_files("tests/capabilities/ci_test")
    ci_tests += _count_test_files("tests/ci")
    if ci_tests > 0:
        score += 0.2
        details["checks"]["ci_tests"] = ci_tests

    # Check for coverage gate tests
    if _check_file_content(
        "tests/capabilities/ci_test/test_ci_comprehensive.py",
        ["CoverageGate", "check"],
    ).get("CoverageGate", False):
        score += 0.15
        details["checks"]["coverage_gates"] = True

    # Check for nox session tests
    if _check_file_content(
        "tests/capabilities/ci_test/test_ci_comprehensive.py",
        ["NoxSession", "NoxConfig"],
    ).get("NoxSession", False):
        score += 0.15
        details["checks"]["nox_sessions"] = True

    # Check for deterministic seeding
    if _check_file_content(
        "tests/capabilities/ci_test/test_ci_comprehensive.py",
        ["DeterministicSeeder", "seed_all"],
    ).get("DeterministicSeeder", False):
        score += 0.15
        details["checks"]["deterministic_seeding"] = True

    # Check for test isolation
    if _check_file_content(
        "tests/capabilities/ci_test/test_ci_comprehensive.py",
        ["IsolationManager", "create_temp_dir"],
    ).get("IsolationManager", False):
        score += 0.2
        details["checks"]["test_isolation"] = True

    return DetectorResult(
        name="ci_test",
        score=clamp01(score),
        details=details,
    )


# --- Versioning Capability Detector ---


def detector_versioning() -> DetectorResult:
    """Detect versioning and releases capability maturity.

    Checks:
    - Semantic versioning
    - Release automation
    - Changelog generation
    - Artifact signing
    """
    score = 0.0
    details: dict[str, Any] = {"checks": {}}

    # Check versioning infrastructure
    version_files = ["pyproject.toml", ".github/workflows/"]
    version_found = sum(1 for f in version_files if _check_path_exists(f))
    if version_found > 0:
        score += 0.1
        details["checks"]["versioning_infrastructure"] = version_found

    # Check for versioning tests
    version_tests = _count_test_files("tests/capabilities/versioning")
    if version_tests > 0:
        score += 0.2
        details["checks"]["versioning_tests"] = version_tests

    # Check for semantic version tests
    if _check_file_content(
        "tests/capabilities/versioning/test_versioning_comprehensive.py",
        ["SemanticVersion", "bump_major"],
    ).get("SemanticVersion", False):
        score += 0.15
        details["checks"]["semantic_versioning"] = True

    # Check for changelog tests
    if _check_file_content(
        "tests/capabilities/versioning/test_versioning_comprehensive.py",
        ["Changelog", "ChangelogEntry"],
    ).get("Changelog", False):
        score += 0.15
        details["checks"]["changelog_generation"] = True

    # Check for release automation
    if _check_file_content(
        "tests/capabilities/versioning/test_versioning_comprehensive.py",
        ["ReleaseManager", "create_release"],
    ).get("ReleaseManager", False):
        score += 0.2
        details["checks"]["release_automation"] = True

    # Check for artifact signing
    if _check_file_content(
        "tests/capabilities/versioning/test_versioning_comprehensive.py",
        ["ArtifactSigner", "SignedRelease"],
    ).get("ArtifactSigner", False):
        score += 0.2
        details["checks"]["artifact_signing"] = True

    return DetectorResult(
        name="versioning",
        score=clamp01(score),
        details=details,
    )


# --- Error Handling Capability Detector ---


def detector_error_handling() -> DetectorResult:
    """Detect error handling and recovery capability maturity.

    Checks:
    - Exception hierarchy
    - Retry logic
    - Circuit breakers
    - Dead-letter queues
    - Self-remediation
    """
    score = 0.0
    details: dict[str, Any] = {"checks": {}}

    # Check error handling module exists
    error_paths = ["src/mcp/errors.py", "src/codex_ml/errors.py"]
    error_found = any(_check_path_exists(p) for p in error_paths)
    if error_found:
        score += 0.1
        details["checks"]["error_module"] = True

    # Check for error handling tests
    error_tests = _count_test_files("tests/capabilities/error_handling")
    if error_tests > 0:
        score += 0.2
        details["checks"]["error_tests"] = error_tests

    # Check for exception hierarchy
    if _check_file_content(
        "tests/capabilities/error_handling/test_error_handling_comprehensive.py",
        ["CodexError", "ValidationError", "NetworkError"],
    ).get("CodexError", False):
        score += 0.15
        details["checks"]["exception_hierarchy"] = True

    # Check for retry logic
    if _check_file_content(
        "tests/capabilities/error_handling/test_error_handling_comprehensive.py",
        ["RetryConfig", "Retrier"],
    ).get("RetryConfig", False):
        score += 0.15
        details["checks"]["retry_logic"] = True

    # Check for circuit breakers
    if _check_file_content(
        "tests/capabilities/error_handling/test_error_handling_comprehensive.py",
        ["CircuitBreaker", "CircuitState"],
    ).get("CircuitBreaker", False):
        score += 0.15
        details["checks"]["circuit_breakers"] = True

    # Check for dead-letter queue
    if _check_file_content(
        "tests/capabilities/error_handling/test_error_handling_comprehensive.py",
        ["DeadLetterQueue", "retry"],
    ).get("DeadLetterQueue", False):
        score += 0.15
        details["checks"]["dead_letter_queue"] = True

    # Check for self-remediation
    if _check_file_content(
        "tests/capabilities/error_handling/test_error_handling_comprehensive.py",
        ["RemediationManager", "remediate"],
    ).get("RemediationManager", False):
        score += 0.1
        details["checks"]["self_remediation"] = True

    return DetectorResult(
        name="error_handling",
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
        detector_logging,
        detector_checkpointing,
        detector_ci_test,
        detector_versioning,
        detector_error_handling,
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
    "detector_logging",
    "detector_checkpointing",
    "detector_ci_test",
    "detector_versioning",
    "detector_error_handling",
    "get_capability_detectors",
    "run_capability_audit",
]
