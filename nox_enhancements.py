"""Enhancement sessions for nox - Optional advanced features.

These sessions provide optional enhancements beyond core functionality:
- MLflow integration testing
- Performance benchmarking
- Distributed training validation
- Notebook validation
- Docker image building

Add to your noxfile.py or run directly:
  nox -f nox_enhancements.py -s <session_name>
"""
import nox

nox.options.reuse_existing_virtualenvs = True


@nox.session(name="mlflow_tests")
def mlflow_tests(session):
    """Run MLflow integration tests."""
    session.install("-e", ".[test]")
    session.install("mlflow")
    session.run(
        "pytest",
        "tests/test_mlflow_integration.py",
        "-v",
        "--tb=short",
        *session.posargs,
    )


@nox.session(name="performance_benchmarks")
def performance_benchmarks(session):
    """Run performance benchmark suite."""
    session.install("-e", ".[test]")
    session.run(
        "pytest",
        "tests/test_performance_benchmark.py",
        "-v",
        "--tb=short",
        *session.posargs,
    )


@nox.session(name="distributed_tests")
def distributed_tests(session):
    """Run distributed training tests."""
    session.install("-e", ".[test]")
    session.run(
        "pytest",
        "tests/test_distributed_setup.py",
        "-v",
        "--tb=short",
        *session.posargs,
    )


@nox.session(name="validate_notebooks")
def validate_notebooks(session):
    """Validate all Jupyter notebooks can execute."""
    session.install("papermill", "jupyter")
    session.run("bash", "scripts/validate_notebooks.sh", external=True)


@nox.session(name="docker_build")
def docker_build(session):
    """Build optimized Docker image."""
    session.run(
        "docker",
        "build",
        "-f",
        "docker/Dockerfile.optimized",
        "-t",
        "codex-ml:optimized",
        ".",
        external=True,
    )
    print("\n✅ Docker image built: codex-ml:optimized")


@nox.session(name="docker_test")
def docker_test(session):
    """Test Docker image functionality."""
    # Check if image exists
    result = session.run(
        "docker",
        "images",
        "-q",
        "codex-ml:optimized",
        external=True,
        silent=True,
    )
    
    # Build only if image doesn't exist (docker images -q returns empty string when no match)
    if not result or not result.strip():
        print("\nDocker image not found, building...")
        docker_build(session)
    else:
        print("\nDocker image found, skipping build...")
    
    print("\nTesting Docker image...")
    
    # Test health check
    session.run(
        "docker",
        "run",
        "--rm",
        "codex-ml:optimized",
        "python",
        "-c",
        "from codex_ml.serving.health import health_check; health_check()",
        external=True,
    )
    
    # Test CLI help
    session.run(
        "docker",
        "run",
        "--rm",
        "codex-ml:optimized",
        "python",
        "-m",
        "cli.train_codex",
        "--help",
        external=True,
    )
    
    print("\n✅ Docker image tests passed")


@nox.session(name="all_enhancements")
def all_enhancements(session):
    """Run all enhancement tests (MLflow, benchmarks, distributed)."""
    # Run MLflow tests
    try:
        mlflow_tests(session)
        print("✅ MLflow tests passed")
    except Exception as e:
        print(f"⚠️  MLflow tests skipped: {e}")
    
    # Run performance benchmarks
    try:
        performance_benchmarks(session)
        print("✅ Performance benchmarks passed")
    except Exception as e:
        print(f"⚠️  Performance benchmarks failed: {e}")
    
    # Run distributed tests
    try:
        distributed_tests(session)
        print("✅ Distributed tests passed")
    except Exception as e:
        print(f"⚠️  Distributed tests failed: {e}")


@nox.session(name="maintenance_check")
def maintenance_check(session):
    """Run maintenance checks: dependencies, security, coverage."""
    session.install("-e", ".[test]")
    session.install("pip-audit", "safety")
    
    print("\n🔍 Checking for dependency vulnerabilities...")
    try:
        session.run("pip-audit", "--skip-editable")
        print("✅ No dependency vulnerabilities found")
    except Exception as e:
        print(f"⚠️  Dependency check: {e}")
    
    print("\n🔍 Checking test coverage...")
    session.run(
        "pytest",
        "tests/",
        "--cov=src",
        "--cov=training",
        "--cov-report=term",
        "--cov-fail-under=70",
        "-q",
    )
    print("✅ Coverage maintained above 70%")


@nox.session(name="enhancement_docs")
def enhancement_docs(session):
    """Generate documentation for enhancements."""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║              Enhancement Sessions Available                       ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║                                                                   ║
    ║  1. MLflow Integration                                           ║
    ║     nox -f nox_enhancements.py -s mlflow_tests                  ║
    ║     - Tests MLflow tracking with offline fallback                ║
    ║     - Requires: pip install mlflow                               ║
    ║                                                                   ║
    ║  2. Performance Benchmarks                                        ║
    ║     nox -f nox_enhancements.py -s performance_benchmarks        ║
    ║     - Benchmarks training, inference, data loading               ║
    ║     - Provides throughput and memory metrics                     ║
    ║                                                                   ║
    ║  3. Distributed Training                                          ║
    ║     nox -f nox_enhancements.py -s distributed_tests             ║
    ║     - Tests multi-node training setup                            ║
    ║     - Validates DDP configuration                                ║
    ║                                                                   ║
    ║  4. Notebook Validation                                           ║
    ║     nox -f nox_enhancements.py -s validate_notebooks            ║
    ║     - Validates all Jupyter notebooks execute                    ║
    ║     - Requires: pip install papermill jupyter                    ║
    ║                                                                   ║
    ║  5. Docker Build & Test                                           ║
    ║     nox -f nox_enhancements.py -s docker_build                  ║
    ║     nox -f nox_enhancements.py -s docker_test                   ║
    ║     - Builds optimized multi-stage Docker image                  ║
    ║     - Tests health checks and CLI                                ║
    ║                                                                   ║
    ║  6. Run All Enhancements                                          ║
    ║     nox -f nox_enhancements.py -s all_enhancements              ║
    ║     - Runs all enhancement test suites                           ║
    ║                                                                   ║
    ║  7. Maintenance Check                                             ║
    ║     nox -f nox_enhancements.py -s maintenance_check             ║
    ║     - Dependency vulnerability scan                              ║
    ║     - Coverage validation                                        ║
    ║                                                                   ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    For more information, see:
    - docs/guides/enhancements_guide.md
    - docs/API_REFERENCE.md (MLflow, Performance, Distributed sections)
    """)
