from scripts.ci import environment_preflight as mod


def test_detect_environment_type_flags_ml_rag_signals() -> None:
    environment_type, reason = mod._detect_environment_type([
        "RAG Module Tests",
        "ML Components Test Suite",
        "numpy",
        "torch",
    ])

    assert environment_type == "ml-heavy"
    assert "ML/RAG signal" in reason


def test_detect_environment_type_ignores_ml_substring_in_yaml() -> None:
    environment_type, reason = mod._detect_environment_type([
        "yaml config",
        "ci workflow",
        "deployment pipeline",
    ])

    assert environment_type == "standard"
    assert "No ML/RAG" in reason


def test_detect_missing_runtime_dependencies_uses_runtime_package_names(monkeypatch) -> None:
    def fake_find_spec(name: str):
        if name in {"numpy", "torch", "faiss"}:
            return None
        return object()

    monkeypatch.setattr(mod.importlib.util, "find_spec", fake_find_spec)

    missing = mod._detect_missing_runtime_dependencies([
        "numpy>=2.5.2,<3",
        "torch>=2.6.1,<3.0.0; platform_system != 'Windows'",
        "faiss-cpu>=1.15.0,<2.0.0",
    ])

    assert missing == [
        "numpy>=2.5.2,<3",
        "torch>=2.6.1,<3.0.0; platform_system != 'Windows'",
        "faiss-cpu>=1.15.0,<2.0.0",
    ]
