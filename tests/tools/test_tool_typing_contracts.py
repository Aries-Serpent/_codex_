"""Behavioral contracts for typed tool reports and optional detection inputs."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from tools import (
    codex_data_audit,
    codex_dataset_index,
    codex_dep_pin_check,
    codex_experiment_index,
    codex_local_gate_runner,
    codex_secret_scan,
    codex_secret_scan_stub,
    selection_report,
)
from tools.dupinv.ast_parsers.python_parser import PythonASTParser
from tools.dupinv.core import DuplicateScanner
from tools.dupinv.normalize import NormalizedDetector
from tools.dupinv.semantic_detector import MinHashDetector
from tools.dupinv.shim_integration import ShimInventoryReader


def test_dataset_index_preserves_root_and_records(tmp_path: Path) -> None:
    (tmp_path / "data.csv").write_text("a\n1\n", encoding="utf-8")
    index = codex_dataset_index.build_index(tmp_path)
    assert index["root"] == str(tmp_path)
    assert [(f.path, f.kind, f.size_bytes) for f in index["files"]] == [("data.csv", "csv", 4)]
    out = tmp_path / "index.json"
    codex_dataset_index._write_json(index, out)
    assert json.loads(out.read_text())["files"][0]["size_bytes"] == 4


@pytest.mark.parametrize("context", [None, [], "not a mapping", {}, {"run_id": "explicit"}])
def test_experiment_context_is_narrowed(tmp_path: Path, context: object) -> None:
    run_dir = tmp_path / "fallback"
    run_dir.mkdir()
    (run_dir / "meta.json").write_text(json.dumps({"context": context}), encoding="utf-8")
    index = codex_experiment_index.build_index(tmp_path)
    expected_id = "explicit" if isinstance(context, dict) and context else "fallback"
    assert index["runs"][0].run_id == expected_id
    out = tmp_path / "index.json"
    codex_experiment_index._write_json(index, out)
    assert json.loads(out.read_text())["runs"][0]["meta"] == {"context": context}


def test_audit_report_preserves_numeric_totals(tmp_path: Path) -> None:
    (tmp_path / "data.txt").write_text("abc", encoding="utf-8")
    report = codex_data_audit.build_report([tmp_path])
    assert report == {
        "roots": [{"root": str(tmp_path), "num_files": 1, "total_bytes": 3}],
        "total_roots": 1,
        "total_files": 1,
        "total_bytes": 3,
    }
    out = tmp_path / "audit.md"
    codex_data_audit._write_markdown(out, report)
    assert f"| `{tmp_path}` | 1 | 3 |" in out.read_text()
    assert codex_data_audit.build_report([])["roots"] == []


def test_secret_report_retains_hit_and_summary_shapes(tmp_path: Path) -> None:
    (tmp_path / "example.txt").write_text("PRIVATE_KEY", encoding="utf-8")
    report = codex_secret_scan.run_scan(tmp_path)
    assert report["summary"]["total_hits"] == 0
    stub_report = codex_secret_scan_stub.scan(tmp_path)
    assert stub_report["total_findings"] == 1
    assert stub_report["findings"][0]["pattern"] == "PRIVATE_KEY"
    out = tmp_path / "stub.json"
    codex_secret_scan_stub._write_json(out, stub_report)
    persisted = json.loads(out.read_text())
    assert persisted["total_findings"] == 1
    assert persisted["findings"][0]["snippet"] == "<redacted>"
    # Serialization must not mutate the caller's report.
    assert stub_report["findings"][0]["snippet"] == "PRIVATE_KEY"


def test_pinning_report_preserves_issue_fields(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("requests\nnumpy==1.0\n", encoding="utf-8")
    report = codex_dep_pin_check.run_check(tmp_path)
    assert report["issue_count"] == 1
    assert report["issues"] == [
        {
            "path": str(tmp_path / "requirements.txt"),
            "line_number": 1,
            "requirement": "requests",
            "reason": "unpinned requirement",
        }
    ]


def test_gate_report_preserves_failure_and_captured_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    command = ["example", "argument"]

    def run_command(args: object, repo_root: Path) -> subprocess.CompletedProcess[str]:
        assert args == command
        assert repo_root == tmp_path
        return subprocess.CompletedProcess(command, 7, "out\n", "err\n")

    monkeypatch.setattr(codex_local_gate_runner, "_run_command", run_command)
    report = codex_local_gate_runner.run_gates(
        tmp_path, [codex_local_gate_runner.GateCommand("failure", command)]
    )
    assert report == {
        "overall_returncode": 7,
        "results": [
            {
                "name": "failure",
                "cmd": command,
                "returncode": 7,
                "stdout": "out\n",
                "stderr": "err\n",
            }
        ],
    }
    assert codex_local_gate_runner.run_gates(tmp_path, []) == {
        "overall_returncode": 0,
        "results": [],
    }


def test_async_functions_and_methods_keep_signatures(tmp_path: Path) -> None:
    source = tmp_path / "async_example.py"
    source.write_text(
        "async def fetch(value: int) -> int:\n"
        "    return value\n"
        "class Client:\n"
        "    async def send(self, item: str) -> str:\n"
        "        return item\n",
        encoding="utf-8",
    )
    signatures = PythonASTParser().parse_file(source)
    top_level = next(sig for sig in signatures if sig.name == "fetch")
    method = next(sig for sig in signatures if sig.is_method)
    assert (top_level.parameters, top_level.return_type) == (["value"], "int")
    assert (method.name, method.class_name, method.return_type) == ("send", "Client", "str")


def test_minhash_preserves_hash_values_and_empty_signature(tmp_path: Path) -> None:
    detector = MinHashDetector(tmp_path, num_perm=8, exclude_patterns=None)
    shingles = {"alpha beta", "beta gamma"}
    expected = [
        min(
            int(hashlib.sha256(f"{shingle}:{i}".encode()).hexdigest()[:8], 16)
            for shingle in shingles
        )
        for i in range(8)
    ]
    assert detector.compute_minhash(shingles) == expected
    assert all(type(value) is int for value in detector.compute_minhash(shingles))
    assert detector.compute_minhash(set()) == [0] * 8


def test_normalizer_supports_unknown_language(tmp_path: Path) -> None:
    detector = NormalizedDetector(tmp_path, exclude_patterns=None)
    assert detector.normalize_content("a    b\n\n", "unknown") == "a b"
    assert detector.normalize_content("# comment\nx = 1\n", "python") == "x = 1"


def test_scanner_defaults_and_absent_optional_enrichers(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("x = 1\n", encoding="utf-8")
    scanner = DuplicateScanner(tmp_path)
    assert set(scanner.detectors) == {"exact", "normalized", "ast", "semantic"}
    scanner.cross_reference = None
    scanner.git_metadata = None
    groups = scanner.detectors["exact"].scan()
    assert len(groups) == 1
    assert scanner._apply_shim_cross_reference(groups) is groups
    assert scanner._apply_git_metadata(groups) is groups
    inventory = scanner.scan()
    assert set(inventory.metadata.detection_modes) == set(scanner.detectors)
    scanner.write_outputs(inventory, tmp_path / "reports")
    assert {p.suffix for p in (tmp_path / "reports").iterdir()} == {".yaml", ".json", ".csv", ".md"}
    assert scanner.scan([]).duplicate_groups == []


def test_empty_shim_inventory_is_cached(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    github = tmp_path / ".github"
    github.mkdir()
    (github / "SHIM_INVENTORY.yaml").write_text("inventory: []\n", encoding="utf-8")
    reader = ShimInventoryReader(tmp_path)
    assert reader.get_entries_dict() == {}

    def unexpected_reload() -> None:
        pytest.fail("an empty inventory is already loaded")

    monkeypatch.setattr(reader, "load", unexpected_reload)
    assert reader.get_whitelisted_paths() == set()
    assert reader.get_entries_dict() == {}


@pytest.mark.parametrize("invalid", [None, [], "invalid", 1])
def test_selection_text_ignores_noncontainer_fields(invalid: object) -> None:
    assert selection_report._collect_text({"worklog": invalid, "output_items": invalid}) == ""


def test_selection_text_preserves_messages_and_diffs() -> None:
    assert (
        selection_report._collect_text(
            {
                "worklog": {"messages": [{"text": "worklog"}, None, {"content": "content"}]},
                "output_items": [
                    {"title": "title", "output_diff": {"diff": "+changed"}},
                    None,
                ],
            }
        )
        == "worklog\n\ncontent\n\ntitle\n\n+changed"
    )


def test_selection_config_handles_nonmapping_optional_sections(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = tmp_path / "preset.yaml"
    config.write_text(
        "kind: example\nname: demo\nimage: null\nresources: []\n"
        "reasoning: false\nartifacts: not-a-mapping\nnotes: note\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(selection_report, "_timestamp", lambda: "fixed")
    out = tmp_path / "report.json"
    assert (
        selection_report.main(
            [
                "--config",
                str(config),
                "--dry-run",
                "--out",
                str(tmp_path / "report.md"),
                "--emit-json",
                str(out),
            ]
        )
        == 0
    )
    summary = json.loads(out.read_text())["summary"]
    assert summary["image"] == {"repository": None, "tag": None}
    assert summary["resources"] == {}
    assert summary["trace_capture_mode"] is None
    assert summary["artifacts"] == {}
    assert summary["notes"] == ["note"]


def test_selection_report_ranks_typed_candidates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    summary = tmp_path / "summary.json"
    summary.write_text(
        json.dumps(
            {
                "turn_mapping": {
                    "task_e_1~assttrn_1": {"turn": {}},
                    "task_e_1~assttrn_2": {
                        "turn": {
                            "worklog": {"messages": [{"text": "selection guard tests/example.py"}]}
                        }
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(selection_report, "_run", lambda cmd: (0, "", ""))
    out = tmp_path / "selection.md"
    assert selection_report.main(["--summary", str(summary), "--out", str(out)]) == 0
    assert "**Chosen variant:** **2**" in out.read_text()
