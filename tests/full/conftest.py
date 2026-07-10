"""
Fixtures and utilities for dev tools validation tests.

This module provides fixtures for testing development tools:
- pytest
- mypy
- ruff
- black
- isort

And experiment tracking fixtures for MLflow and wandb.
"""

import json
import logging
import os
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Generator, List, Optional, Tuple
from unittest.mock import MagicMock, patch

import pytest

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def source_files(project_root: Path) -> List[Path]:
    """Get all Python source files in the project."""
    src_dir = project_root / "src"
    return list(src_dir.glob("**/*.py")) if src_dir.exists() else []


@pytest.fixture(scope="session")
def test_files(project_root: Path) -> List[Path]:
    """Get all test files in the project."""
    tests_dir = project_root / "tests"
    return list(tests_dir.glob("**/*.py")) if tests_dir.exists() else []


@pytest.fixture(scope="session")
def all_python_files(project_root: Path) -> List[Path]:
    """Get all Python files (src + tests)."""
    src_dir = project_root / "src"
    tests_dir = project_root / "tests"
    
    files = []
    if src_dir.exists():
        files.extend(src_dir.glob("**/*.py"))
    if tests_dir.exists():
        files.extend(tests_dir.glob("**/*.py"))
    return files


@pytest.fixture
def run_tool_command():
    """Fixture to run a tool command and capture output."""
    def _run(
        cmd: List[str],
        cwd: Path = None,
        check: bool = False
    ) -> Tuple[int, str, str]:
        """Run a command and return (returncode, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out after 60 seconds"
        except Exception as e:
            return -1, "", str(e)
    
    return _run


@pytest.fixture
def tool_versions() -> Dict[str, str]:
    """Get versions of installed dev tools."""
    versions = {}
    
    tools = ["pytest", "mypy", "ruff", "black", "isort"]
    
    for tool in tools:
        try:
            result = subprocess.run(
                [sys.executable, "-m", tool, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                versions[tool] = result.stdout.strip()
            else:
                versions[tool] = "unknown (error)"
        except subprocess.TimeoutExpired:
            versions[tool] = "unknown (timeout)"
        except Exception as e:
            versions[tool] = f"unknown ({type(e).__name__})"
    
    return versions


@pytest.fixture
def check_tool_installed():
    """Check if a tool is installed and working."""
    def _check(tool_name: str, module_name: str = None) -> Tuple[bool, str]:
        """Check if a tool is installed. Returns (installed, version_string)."""
        if module_name is None:
            module_name = tool_name
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", module_name, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            # Some tools use -h to show version
            result = subprocess.run(
                [sys.executable, "-m", module_name, "-h"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0, "installed"
        except Exception:
            return False, ""
    
    return _check


# ============================================================================
# Experiment Tracking Fixtures for Full Profile Validation
# ============================================================================


@pytest.fixture
def mlflow_temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for MLflow artifacts and runs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        (path / "mlruns").mkdir(exist_ok=True)
        (path / "artifacts").mkdir(exist_ok=True)
        (path / "models").mkdir(exist_ok=True)
        yield path


@pytest.fixture
def mlflow_tracking_uri_full(mlflow_temp_dir: Path) -> str:
    """Get SQLite-based tracking URI for full profile testing."""
    db_path = mlflow_temp_dir / "mlruns" / "mlruns.db"
    uri = f"sqlite:///{db_path}"
    return uri


@pytest.fixture
def mlflow_client_full(mlflow_tracking_uri_full: str):
    """Create MLflow client for full profile testing."""
    try:
        import mlflow
        from mlflow.tracking import MlflowClient

        mlflow.set_tracking_uri(mlflow_tracking_uri_full)
        client = MlflowClient(tracking_uri=mlflow_tracking_uri_full)
        yield client
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def parent_experiment(mlflow_client_full):
    """Create a parent experiment for nested experiment testing."""
    try:
        import mlflow

        parent_name = "parent_experiment_full"
        experiment = None
        try:
            experiment = mlflow_client_full.get_experiment_by_name(parent_name)
        except Exception:
            pass

        if experiment is None:
            parent_id = mlflow_client_full.create_experiment(parent_name)
        else:
            parent_id = experiment.experiment_id

        yield {
            "id": parent_id,
            "name": parent_name,
        }
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def child_experiment(mlflow_client_full, parent_experiment):
    """Create a child experiment for nested experiment hierarchy."""
    try:
        import mlflow

        child_name = f"{parent_experiment['name']}_child"
        experiment = None
        try:
            experiment = mlflow_client_full.get_experiment_by_name(child_name)
        except Exception:
            pass

        if experiment is None:
            child_id = mlflow_client_full.create_experiment(child_name)
        else:
            child_id = experiment.experiment_id

        yield {
            "id": child_id,
            "name": child_name,
            "parent_id": parent_experiment["id"],
        }
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def parent_run(mlflow_client_full, parent_experiment):
    """Create a parent run for nested run hierarchy."""
    try:
        import mlflow

        exp_id = parent_experiment["id"]
        run = mlflow_client_full.create_run(
            experiment_id=exp_id,
            tags={"run_type": "parent", "test_suite": "full_profile"},
        )

        yield {
            "id": run.info.run_id,
            "experiment_id": exp_id,
            "status": "RUNNING",
        }

        # Cleanup
        try:
            mlflow_client_full.set_terminated(run.info.run_id)
        except Exception:
            pass
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def child_run(mlflow_client_full, parent_experiment, parent_run):
    """Create a child run within parent run for nested run testing."""
    try:
        import mlflow

        exp_id = parent_experiment["id"]
        # Note: parent_run_id may not be supported in all MLflow versions
        # Create a child run using tags to indicate hierarchy
        run = mlflow_client_full.create_run(
            experiment_id=exp_id,
            tags={"run_type": "child", "parent": parent_run["id"]},
        )

        yield {
            "id": run.info.run_id,
            "experiment_id": exp_id,
            "parent_run_id": parent_run["id"],
            "status": "RUNNING",
        }

        # Cleanup
        try:
            mlflow_client_full.set_terminated(run.info.run_id)
        except Exception:
            pass
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def multi_metric_run(mlflow_client_full, parent_experiment):
    """Create a run for multi-metric tracking (100+ metrics)."""
    try:
        import mlflow

        exp_id = parent_experiment["id"]
        run = mlflow_client_full.create_run(
            experiment_id=exp_id,
            tags={"test_type": "multi_metric", "metric_count": "150"},
        )

        # Log 150 metrics
        for i in range(150):
            mlflow_client_full.log_metric(
                run.info.run_id, f"metric_{i:03d}", float(i) * 1.5, step=0
            )

        yield {
            "id": run.info.run_id,
            "experiment_id": exp_id,
            "metric_count": 150,
        }

        # Cleanup
        try:
            mlflow_client_full.set_terminated(run.info.run_id)
        except Exception:
            pass
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def artifact_run(mlflow_client_full, parent_experiment, mlflow_temp_dir):
    """Create a run for artifact management testing."""
    try:
        import mlflow

        exp_id = parent_experiment["id"]
        run = mlflow_client_full.create_run(
            experiment_id=exp_id,
            tags={"test_type": "artifact", "artifact_count": "5"},
        )

        # Create some test artifacts
        artifacts_dir = mlflow_temp_dir / "test_artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        for i in range(5):
            artifact_path = artifacts_dir / f"artifact_{i}.txt"
            artifact_path.write_text(f"Test artifact content {i}\n" * 100)

        # Log artifacts would happen in the test
        yield {
            "id": run.info.run_id,
            "experiment_id": exp_id,
            "artifacts_dir": str(artifacts_dir),
        }

        # Cleanup
        try:
            mlflow_client_full.set_terminated(run.info.run_id)
        except Exception:
            pass
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def sweep_run_set(mlflow_client_full, parent_experiment):
    """Create multiple runs for hyperparameter sweep logging."""
    try:
        import mlflow

        exp_id = parent_experiment["id"]
        runs = []

        # Create 10 runs with different hyperparameters
        hyperparams = [
            {"lr": 0.001, "batch_size": 32, "epochs": 10},
            {"lr": 0.001, "batch_size": 64, "epochs": 10},
            {"lr": 0.001, "batch_size": 128, "epochs": 10},
            {"lr": 0.01, "batch_size": 32, "epochs": 10},
            {"lr": 0.01, "batch_size": 64, "epochs": 10},
            {"lr": 0.01, "batch_size": 128, "epochs": 10},
            {"lr": 0.1, "batch_size": 32, "epochs": 10},
            {"lr": 0.1, "batch_size": 64, "epochs": 10},
            {"lr": 0.1, "batch_size": 128, "epochs": 10},
            {"lr": 0.001, "batch_size": 32, "epochs": 20},
        ]

        for params in hyperparams:
            run = mlflow_client_full.create_run(
                experiment_id=exp_id,
                tags={"test_type": "hyperparameter_sweep"},
            )

            # Log hyperparameters
            for key, value in params.items():
                mlflow_client_full.log_param(run.info.run_id, key, value)

            # Log some dummy metrics
            accuracy = 0.85 + (params["lr"] * 0.1) - (params["batch_size"] / 1000)
            mlflow_client_full.log_metric(run.info.run_id, "accuracy", accuracy)

            runs.append(
                {
                    "id": run.info.run_id,
                    "experiment_id": exp_id,
                    "hyperparams": params,
                }
            )

        yield runs

        # Cleanup
        for run in runs:
            try:
                mlflow_client_full.set_terminated(run["id"])
            except Exception:
                pass
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def distributed_run_set(mlflow_client_full, parent_experiment):
    """Create multiple runs for distributed logging testing."""
    try:
        import mlflow

        exp_id = parent_experiment["id"]
        runs = []

        # Create 5 runs simulating distributed training
        for i in range(5):
            run = mlflow_client_full.create_run(
                experiment_id=exp_id,
                tags={
                    "test_type": "distributed",
                    "rank": str(i),
                    "world_size": "5",
                },
            )

            # Log metrics from different ranks
            for step in range(10):
                metric_value = (i + 1) * (step + 1) * 0.1
                mlflow_client_full.log_metric(
                    run.info.run_id, f"rank_{i}_loss", metric_value, step=step
                )

            runs.append(
                {
                    "id": run.info.run_id,
                    "experiment_id": exp_id,
                    "rank": i,
                }
            )

        yield runs

        # Cleanup
        for run in runs:
            try:
                mlflow_client_full.set_terminated(run["id"])
            except Exception:
                pass
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def model_registry_run(mlflow_client_full, parent_experiment):
    """Create a run for model registry testing."""
    try:
        import mlflow

        exp_id = parent_experiment["id"]
        run = mlflow_client_full.create_run(
            experiment_id=exp_id,
            tags={"test_type": "model_registry"},
        )

        # Create a mock model artifact
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "model"
            model_dir.mkdir()
            (model_dir / "model.pkl").write_text("mock model data")
            (model_dir / "config.json").write_text(
                json.dumps({"framework": "sklearn"})
            )

            yield {
                "id": run.info.run_id,
                "experiment_id": exp_id,
                "model_dir": str(model_dir),
            }

        # Cleanup
        try:
            mlflow_client_full.set_terminated(run.info.run_id)
        except Exception:
            pass
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def export_import_run(mlflow_client_full, parent_experiment):
    """Create a run for export/import testing."""
    try:
        import mlflow

        exp_id = parent_experiment["id"]
        run = mlflow_client_full.create_run(
            experiment_id=exp_id,
            tags={"test_type": "export_import"},
        )

        # Log some data for export
        mlflow_client_full.log_param(run.info.run_id, "param1", "value1")
        mlflow_client_full.log_metric(run.info.run_id, "metric1", 0.95)
        mlflow_client_full.log_metric(run.info.run_id, "metric1", 0.97, step=1)

        yield {
            "id": run.info.run_id,
            "experiment_id": exp_id,
            "data": {"params": {"param1": "value1"}, "metrics": {"metric1": 0.97}},
        }

        # Cleanup
        try:
            mlflow_client_full.set_terminated(run.info.run_id)
        except Exception:
            pass
    except ImportError:
        pytest.skip("MLflow not installed")



# ============================================================================
# Quality Check Fixtures (Phase 3 Lane 3.4)
# ============================================================================

import ast
import re
from typing import Optional, Set, Tuple


class DocstringAnalyzer:
    """Analyzes docstring coverage in Python files."""
    
    @staticmethod
    def has_docstring(node: ast.AST) -> bool:
        """Check if an AST node has a docstring."""
        return (
            ast.get_docstring(node) is not None
            and len(ast.get_docstring(node).strip()) > 0
        )
    
    @staticmethod
    def analyze_file(file_path: Path) -> Dict[str, any]:
        """Analyze docstring coverage in a Python file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            functions = [
                n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) or isinstance(n, ast.AsyncFunctionDef)
            ]
            
            documented_classes = sum(
                1 for c in classes if DocstringAnalyzer.has_docstring(c)
            )
            documented_functions = sum(
                1 for f in functions if DocstringAnalyzer.has_docstring(f)
            )
            
            return {
                "file": str(file_path),
                "classes": len(classes),
                "documented_classes": documented_classes,
                "functions": len(functions),
                "documented_functions": documented_functions,
                "has_module_docstring": DocstringAnalyzer.has_docstring(tree),
                "coverage_pct": (
                    (documented_classes + documented_functions)
                    / max(len(classes) + len(functions), 1)
                    * 100
                ),
            }
        except Exception as e:
            return {
                "file": str(file_path),
                "error": str(e),
                "coverage_pct": 0,
            }


class TypeHintValidator:
    """Validates type hint coverage in Python files."""
    
    @staticmethod
    def has_type_hints(node: ast.FunctionDef) -> bool:
        """Check if a function has type hints."""
        has_return_hint = node.returns is not None
        has_param_hints = all(
            arg.annotation is not None
            for arg in node.args.args
            if arg.arg != "self"
        )
        return has_return_hint or has_param_hints
    
    @staticmethod
    def analyze_file(file_path: Path) -> Dict[str, any]:
        """Analyze type hint coverage in a Python file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content)
            functions = [
                n for n in ast.walk(tree)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            
            hinted_functions = sum(
                1 for f in functions if TypeHintValidator.has_type_hints(f)
            )
            
            return {
                "file": str(file_path),
                "total_functions": len(functions),
                "functions_with_hints": hinted_functions,
                "coverage_pct": (
                    hinted_functions / max(len(functions), 1) * 100
                ),
            }
        except Exception as e:
            return {
                "file": str(file_path),
                "error": str(e),
                "coverage_pct": 0,
            }


class SecretScanner:
    """Scans files for hardcoded secrets and credentials."""
    
    # Patterns to detect potential secrets
    PATTERNS = {
        "api_key": re.compile(r"['\"]?api[_-]?key['\"]?\s*[:=]\s*['\"]?[a-zA-Z0-9]{20,}"),
        "password": re.compile(r"['\"]?password['\"]?\s*[:=]\s*['\"]?[^\s'\"]+"),
        "token": re.compile(r"['\"]?token['\"]?\s*[:=]\s*['\"]?[a-zA-Z0-9]{20,}"),
        "secret": re.compile(r"['\"]?secret['\"]?\s*[:=]\s*['\"]?[^\s'\"]+"),
        "credentials": re.compile(r"['\"]?credentials['\"]?\s*[:=]"),
        "aws_key": re.compile(r"AKIA[0-9A-Z]{16}"),
        "github_token": re.compile(r"gh[pousr]{1,4}_[a-zA-Z0-9_]{36,255}"),
    }
    
    @staticmethod
    def scan_file(file_path: Path) -> Dict[str, any]:
        """Scan a file for potential secrets."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            findings = []
            for pattern_name, pattern in SecretScanner.PATTERNS.items():
                matches = pattern.finditer(content)
                for match in matches:
                    line_num = content[:match.start()].count("\n") + 1
                    findings.append({
                        "type": pattern_name,
                        "line": line_num,
                        "match": match.group()[:50],  # Truncate for safety
                    })
            
            return {
                "file": str(file_path),
                "findings": findings,
                "has_secrets": len(findings) > 0,
            }
        except Exception as e:
            return {
                "file": str(file_path),
                "error": str(e),
                "has_secrets": False,
            }


class LinkValidator:
    """Validates links in markdown files."""
    
    # Markdown link patterns
    MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    
    @staticmethod
    def extract_links(content: str) -> List[str]:
        """Extract links from markdown content."""
        matches = LinkValidator.MARKDOWN_LINK_PATTERN.finditer(content)
        return [match.group(2) for match in matches]
    
    @staticmethod
    def is_external_link(link: str) -> bool:
        """Check if a link is external."""
        return link.startswith(("http://", "https://", "ftp://"))
    
    @staticmethod
    def validate_file(file_path: Path, root_dir: Path) -> Dict[str, any]:
        """Validate links in a markdown file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            links = LinkValidator.extract_links(content)
            
            broken_links = []
            valid_links = []
            
            for link in links:
                if LinkValidator.is_external_link(link):
                    # Skip external links for now
                    continue
                
                # Remove anchor
                link_path = link.split("#")[0]
                
                if not link_path:  # Anchor-only link
                    valid_links.append(link)
                    continue
                
                # Resolve path relative to markdown file
                target_path = (file_path.parent / link_path).resolve()
                
                if target_path.exists():
                    valid_links.append(link)
                else:
                    broken_links.append({
                        "link": link,
                        "resolved_path": str(target_path),
                    })
            
            return {
                "file": str(file_path),
                "total_links": len(links),
                "valid_links": len(valid_links),
                "broken_links": broken_links,
                "has_broken_links": len(broken_links) > 0,
            }
        except Exception as e:
            return {
                "file": str(file_path),
                "error": str(e),
                "has_broken_links": False,
            }


@pytest.fixture
def docstring_analyzer() -> DocstringAnalyzer:
    """Fixture to access docstring analyzer."""
    return DocstringAnalyzer()


@pytest.fixture
def type_hint_validator() -> TypeHintValidator:
    """Fixture to access type hint validator."""
    return TypeHintValidator()


@pytest.fixture
def secret_scanner() -> SecretScanner:
    """Fixture to access secret scanner."""
    return SecretScanner()


@pytest.fixture
def link_validator() -> LinkValidator:
    """Fixture to access link validator."""
    return LinkValidator()


@pytest.fixture(scope="session")
def docs_dir(project_root: Path) -> Path:
    """Get the docs directory."""
    return project_root / "docs"


@pytest.fixture(scope="session")
def readme_file(project_root: Path) -> Path:
    """Get the README.md file."""
    return project_root / "README.md"


@pytest.fixture(scope="session")
def source_dir(project_root: Path) -> Path:
    """Get the source code directory."""
    return project_root / "src"


@pytest.fixture(scope="session")
def doc_files(docs_dir: Path) -> List[Path]:
    """Get all markdown documentation files."""
    if not docs_dir.exists():
        return []
    return list(docs_dir.glob("**/*.md"))


@pytest.fixture(scope="session")
def all_markdown_files(project_root: Path, docs_dir: Path) -> List[Path]:
    """Get all markdown files including root level."""
    files = []
    
    # Root level markdown files
    files.extend(project_root.glob("*.md"))
    
    # Docs directory markdown files
    if docs_dir.exists():
        files.extend(docs_dir.glob("**/*.md"))
    
    return files

# Import training fixtures so they're available to all tests
from tests.full.training_fixtures import (
    device,
    model_config,
    training_config,
    data_config,
    synthetic_train_dataset,
    synthetic_val_dataset,
    train_dataloader,
    val_dataloader,
    model,
    optimizer,
    lr_scheduler,
    checkpoint_dir,
    training_metrics,
    training_state,
)

__all__ = [
    "device",
    "model_config",
    "training_config",
    "data_config",
    "synthetic_train_dataset",
    "synthetic_val_dataset",
    "train_dataloader",
    "val_dataloader",
    "model",
    "optimizer",
    "lr_scheduler",
    "checkpoint_dir",
    "training_metrics",
    "training_state",
]
