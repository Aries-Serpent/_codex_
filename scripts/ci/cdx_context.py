"""Offline, source-located CDX skills catalog for session startup packets."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ".github/agents/cdx-archive-lifecycle.agent.md"
CANDIDATE_ID = "cdx-archive-lifecycle"
LEGACY_CANDIDATE = ".github/agents-holding/cdx-archive-lifecycle.agent.md"
MODULES = {
    "common": (
        "scripts/archive/cdx_common.py",
        [
            "iter_deterministic_tree",
            "inspect_text",
            "compute_merkle_root",
            "run_secret_scanners",
            "run_secret_scanner",
            "_scanner_finding",
            "_canonical_scanner_finding",
            "_gitleaks_private_span",
            "_finding_id",
            "_validate_external_path",
            "inspect_and_pack_blob",
            "validate_safe_rel_path",
            "validate_symlink_target",
            "verify_archive_connection",
            "verify_archive",
            "validate_inventory",
            "run_cdx_common_preflight",
            "main",
        ],
        "python -m scripts.archive.cdx_common --preflight-context --json",
        ["tests/archive/test_cdx_sqlite_archive.py", "tests/archive/test_cdx_context.py"],
    ),
    "preflight": (
        "scripts/archive/cdx_preflight.py",
        [
            "digest_document",
            "read_source_file",
            "measure_tree",
            "measure_toolchain",
            "run_preflight",
            "load_preflight",
            "assess_batch",
            "assess_acquired_batch",
            "main",
        ],
        "python -m scripts.archive.cdx_preflight --source SOURCE --private-directory PRIVATE",
        ["tests/archive/test_cdx_preflight.py", "tests/archive/test_cdx_context.py"],
    ),
    "review": (
        "scripts/archive/cdx_review.py",
        [
            "read_private_json",
            "validate_inventory",
            "build_queue",
            "schedule_batch",
            "list_batches",
            "write_checkpoint",
            "main",
        ],
        "python -m scripts.archive.cdx_review --source SOURCE --inventory INVENTORY "
        "--bindings BINDINGS --output OUTPUT",
        ["tests/archive/test_cdx_review.py"],
    ),
    "adapter": (
        "scripts/archive/cdx_adapter.py",
        [
            "measure_adapter",
            "run_adapter",
            "load_adapter",
            "stock_relationship",
            "acquired_span",
            "list_batches",
            "main",
        ],
        "python -m scripts.archive.cdx_adapter --list-batches --source SOURCE "
        "--private-directory PRIVATE --gitleaks-adapter EXECUTABLE",
        ["tests/archive/test_cdx_adapter.py"],
    ),
    "packer": (
        "scripts/archive/codex_packer.py",
        ["pack_archive", "main"],
        "python -m scripts.archive.codex_packer SOURCE OUTPUT.cdx.sqlite",
        ["tests/archive/test_cdx_sqlite_archive.py"],
    ),
    "query": (
        "scripts/archive/codex_query.py",
        [
            "CodexArchiveQuery",
            "CodexArchiveQuery.list_tree",
            "CodexArchiveQuery.read_file_bytes",
            "CodexArchiveQuery.read_file_text",
            "CodexArchiveQuery.search_fts",
            "CodexArchiveQuery.query_symbols",
            "CodexArchiveQuery.query_call_graph",
            "CodexArchiveQuery.build_llm_context",
            "main",
        ],
        "python -m scripts.archive.codex_query ARCHIVE.cdx.sqlite info",
        ["tests/archive/test_cdx_sqlite_archive.py"],
    ),
    "rehydrate": (
        "scripts/archive/codex_rehydrate.py",
        [
            "verify_archive_connection",
            "verify_archive",
            "validate_safe_rel_path",
            "validate_symlink_target",
            "rehydrate_archive",
            "compare_trees",
            "main",
        ],
        "python -m scripts.archive.codex_rehydrate extract ARCHIVE.cdx.sqlite DESTINATION",
        ["tests/archive/test_cdx_sqlite_archive.py"],
    ),
    "gitleaks_adapter": (
        "scripts/archive/gitleaks_adapter/main.go",
        ["provenance", "readFile", "selectedFiles", "localize", "scan", "main"],
        "EXECUTABLE identity; EXECUTABLE < OWNER_ONLY_REQUEST.json",
        ["scripts/archive/gitleaks_adapter/main_test.go"],
    ),
}


def _locations(path: Path) -> dict[str, int]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".go":
        return {
            match.group(1): number
            for number, line in enumerate(text.splitlines(), 1)
            if (match := re.match(r"^func ([A-Za-z_]\w*)\(", line))
        }
    locations = {}
    for node in ast.parse(text).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            locations[node.name] = node.lineno
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        locations[f"{node.name}.{child.name}"] = child.lineno
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Name):
            if node.value.id in locations:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        locations[target.id] = node.lineno
    return locations


def _signatures(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".go":
        return {
            match.group(1): line.rstrip().removesuffix("{").rstrip()
            for line in text.splitlines()
            if (match := re.match(r"^func ([A-Za-z_]\w*)\(", line))
        }
    signatures = {}

    def function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
        return f"{prefix} {node.name}({ast.unparse(node.args)}){returns}"

    for node in ast.parse(text).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            signatures[node.name] = function_signature(node)
        elif isinstance(node, ast.ClassDef):
            bases = ", ".join(ast.unparse(base) for base in node.bases)
            signatures[node.name] = f"class {node.name}" + (f"({bases})" if bases else "")
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    signatures[f"{node.name}.{child.name}"] = function_signature(child)
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Name):
            if node.value.id in signatures:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        signatures[target.id] = signatures[node.value.id]
    return signatures


def _cli_contract(path: Path) -> dict[str, Any]:
    """Locate literal parser subcommands/options without importing or running tools."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".go":
        if 'os.Args[1] == "identity"' not in text or "len(os.Args) != 1" not in text:
            raise ValueError("CDX Go adapter CLI contract changed")
        return {
            "source": "explicit_go_argument_checks",
            "subcommands": {"identity": {"arguments": []}},
            "root": {"arguments": [], "stdin": "owner_only_request_json"},
        }
    tree = ast.parse(text)
    nodes = [
        child
        for function in tree.body
        if isinstance(function, ast.FunctionDef) and function.name in {"main", "_parser"}
        for child in ast.walk(function)
    ]
    commands: dict[str, Any] = {}
    scopes: dict[str, str] = {}
    for node in nodes:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "add_parser"
            and node.value.args
            and isinstance(node.value.args[0], ast.Constant)
            and isinstance(node.value.args[0].value, str)
        ):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    scopes[target.id] = node.value.args[0].value
    root: dict[str, Any] = {"arguments": []}
    for node in sorted(nodes, key=lambda item: getattr(item, "lineno", 0)):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if (
            node.func.attr == "add_parser"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            commands.setdefault(node.args[0].value, {"arguments": []})
        elif node.func.attr == "add_argument":
            names = [
                argument.value
                for argument in node.args
                if isinstance(argument, ast.Constant) and isinstance(argument.value, str)
            ]
            if not names:
                raise ValueError("CDX CLI catalog requires literal argument names")
            argument = {"names": names, "line": node.lineno}
            for keyword in node.keywords:
                if keyword.arg in {"required", "choices", "nargs", "action"}:
                    try:
                        argument[keyword.arg] = ast.literal_eval(keyword.value)
                    except (ValueError, TypeError):
                        raise ValueError(
                            "CDX CLI catalog requires literal option contract"
                        ) from None
            scope = (
                scopes.get(node.func.value.id) if isinstance(node.func.value, ast.Name) else None
            )
            destination = commands.setdefault(scope, {"arguments": []}) if scope else root
            destination["arguments"].append(argument)
    return {"source": "parser_ast", "root": root, "subcommands": commands}


def build_cdx_context(root: Path = ROOT) -> dict[str, Any]:
    """Read only explicit local source/test paths; never scan profile directories."""
    index: dict[str, Any] = {}
    skills: list[dict[str, Any]] = []
    for name, (source, symbols, command, tests) in MODULES.items():
        locations = _locations(root / source)
        signatures = _signatures(root / source)
        functions = {}
        for symbol in symbols:
            if symbol not in locations:
                raise ValueError(f"CDX catalog symbol missing: {source}:{symbol}")
            functions[symbol] = {
                "path": source,
                "line": locations[symbol],
                "location": f"{source}:{locations[symbol]}",
                "signature": signatures[symbol],
            }
        for test in tests:
            if not (root / test).is_file():
                raise ValueError(f"CDX catalog test missing: {test}")
        test_command = (
            "cd scripts/archive/gitleaks_adapter && GOPROXY=off GOSUMDB=off go test ./..."
            if name == "gitleaks_adapter"
            else "python -m pytest " + " ".join(tests)
        )
        index[name] = {
            "path": source,
            "functions": functions,
            "exported_signatures": {
                symbol: {
                    "path": source,
                    "line": locations[symbol],
                    "signature": signature,
                }
                for symbol, signature in signatures.items()
                if not symbol.startswith("_") or symbol in symbols
            },
            "cli": command,
            "cli_contract": _cli_contract(root / source),
            "tests": tests,
            "test_command": test_command,
        }
        if name == "preflight":
            index[name][
                "context_cli"
            ] = "python -m scripts.archive.cdx_preflight --preflight-summary --json"
        skills.append(
            {
                "id": f"cdx_{name}",
                "module_index_key": name,
                "entrypoints": list(functions),
                "cli": command,
                "test_command": test_command,
                "availability": "local_source",
            }
        )
        if name == "preflight":
            skills[-1]["context_cli"] = index[name]["context_cli"]
    if not (root / CANDIDATE).is_file():
        raise ValueError("CDX local profile missing")
    candidate: dict[str, Any] = {
        "id": CANDIDATE_ID,
        "name": "CDX Archive Lifecycle",
        "path": CANDIDATE,
        "status": "local_profile",
        "discoverable": True,
        "hosted_activation": "not_established",
        "authorization": "none_granted",
    }
    skills.append(
        {
            **candidate,
            "kind": "agent_profile",
            "availability": "local_profile",
            "module_index_keys": list(index),
        }
    )
    return {
        "skills_registry": {
            "schema_version": 1,
            "discovery": "offline_explicit_paths_no_network",
            "skills": skills,
            "agent_candidates": [candidate],
        },
        "cdx_module_index": index,
        "cdx_common_preflight": {
            "function": index["common"]["functions"]["run_cdx_common_preflight"],
            "functions": {
                **index["common"]["functions"],
                "pack_archive": index["packer"]["functions"]["pack_archive"],
                "CodexArchiveQuery": index["query"]["functions"]["CodexArchiveQuery"],
                "rehydrate_archive": index["rehydrate"]["functions"]["rehydrate_archive"],
                "common.verify_archive": index["common"]["functions"]["verify_archive"],
                "verify_archive": index["rehydrate"]["functions"]["verify_archive"],
            },
            "name_clarifications": {
                "pack_directory": "does_not_exist_use_pack_archive",
                "run_secret_scanner": "compatibility_alias_of_run_secret_scanners",  # pragma: allowlist secret
            },
            "cli": index["common"]["cli"],
            "tests": index["common"]["tests"],
            "purpose": "offline_capability_context_not_scanner_execution_or_clearance",
        },
    }


def refresh_cdx_context(packet: dict[str, Any]) -> None:
    """Replace CDX catalog data while retaining unrelated registry extensions."""
    catalog = build_cdx_context()
    previous = packet.get("skills_registry", {})
    if isinstance(previous, dict):
        registry = catalog["skills_registry"]
        for key, value in previous.items():
            if key not in registry:
                registry[key] = value
        registry["skills"].extend(
            row
            for row in previous.get("skills", [])
            if isinstance(row, dict)
            and isinstance(row.get("id"), str)
            and not row["id"].startswith(("cdx_", "cdx-"))
        )
        registry["agent_candidates"].extend(
            row
            for row in previous.get("agent_candidates", [])
            if isinstance(row, dict)
            and row.get("id") != CANDIDATE_ID
            and row.get("path") not in {CANDIDATE, LEGACY_CANDIDATE}
        )
    packet.update(catalog)
