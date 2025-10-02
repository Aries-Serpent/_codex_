from codex_utils.json_report import generate_report


def test_generate_report_with_multiple_versions():
    payload = {
        "draft_a": {
            "overview": [
                "tracking/offline_bootstrap.py — enforce file:// mlflow fallback",
                "docs/logging/offline.md — note guardrails for air-gapped runs",
            ],
            "open_items": [
                {
                    "question": "How should we store MLflow runs offline?",
                    "options": [
                        {
                            "label": "FileStore",
                            "description": "Use file:// backed MLflow FileStore",
                            "status": "preferred",
                        },
                        {
                            "label": "SQLite",
                            "description": "Rely on SQLite backend store",
                        },
                    ],
                }
            ],
            "next_steps": [
                "Bootstrap mlflow tracking URI when absent.",
            ],
            "tests": [
                "pytest -q tests/tracking/test_mlflow_offline.py",
            ],
            "docs": [
                "docs/logging/offline.md",
            ],
        },
        "v2": {
            "summary": "codex_utils/ndjson.py — rotate ndjson files at 50MB cap",
            "unresolved": [
                {
                    "question": "Do we need rotation for NDJSON logs?",
                    "options": [
                        {
                            "label": "Add rotation",
                            "description": "✅ keep bounded ndjson artifacts",
                        },
                        {
                            "label": "Defer",
                            "description": "Rely on external logrotate",
                        },
                    ],
                }
            ],
            "plan": [
                "Add NDJSON rotation guard tied to manifest.",
            ],
            "tests": [
                "pytest -q tests/logging/test_ndjson_writer.py",
            ],
            "documentation": [
                "docs/logging/ndjson.md#rotation",
            ],
        },
        "@codex implement plan": "Ignore this block",
    }

    report = generate_report(payload)

    assert "### 1) Consolidated Summary" in report
    assert "tracking/offline_bootstrap.py — enforce file:// mlflow fallback" in report
    assert "codex_utils/ndjson.py — rotate ndjson files at 50MB cap" in report
    assert "### 2) Unified Open Questions" in report
    assert "How should we store MLflow runs offline?" in report
    assert "### 3) Next Prompt" in report
    assert "**Scope**" in report
    assert "pytest -q tests/tracking/test_mlflow_offline.py" in report
    assert "docs/logging/ndjson.md#rotation" in report
    assert "Citations" in report
