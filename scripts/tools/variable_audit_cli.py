#!/usr/bin/env python3
"""
variable_audit_cli.py — Copilot-agent-executable CLI for auditing and
reporting on ALL GitHub variable/secret storage layers against the
authoritative GITHUB_VARIABLES_MASTER_GUIDE.md.

Usage
-----
  python scripts/tools/variable_audit_cli.py check   [--format table|json|md] [--layer all|org-secrets|repo-secrets|repo-vars|env-vars|env-secrets|codespace]
  python scripts/tools/variable_audit_cli.py report  [--out PATH]
  python scripts/tools/variable_audit_cli.py expected [--layer all|...]
  python scripts/tools/variable_audit_cli.py diff    [--out PATH]
  python scripts/tools/variable_audit_cli.py rotate-check [--days 90]

Auth
----
  Requires CODEX_MASTER_KEY env var (or CODEX_BACKUP_KEY fallback) for live
  API calls.  Without a valid token the ``check`` / ``diff`` commands fall back
  to reporting the *expected* state only (marked as UNKNOWN in live columns).

Exit codes
----------
  0  All expected variables present, no anomalies
  1  One or more expected variables absent or mismatched
  2  Authentication error (no token / 403)
  3  Invalid arguments / usage error
"""
from __future__ import annotations

import argparse
import json
import sys
import textwrap
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Re-use the existing VariableManager transport layer.
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

try:
    from tools.variable_manager import (  # type: ignore[import]
        VariableManager,
        _gh_request,
        _resolve_token,
    )
    _VM_AVAILABLE = True
except Exception:  # pragma: no cover
    _VM_AVAILABLE = False  # offline / import failed — degrade gracefully

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_OWNER = "Aries-Serpent"
_REPO  = "_codex_"
_ENV   = "Aries_Serpent_codex_"

# Storage-layer identifiers used in the registry
LAYER_ORG_SECRETS   = "org-secrets"
LAYER_REPO_SECRETS  = "repo-secrets"
LAYER_ENV_SECRETS   = "env-secrets"
LAYER_REPO_VARS     = "repo-vars"
LAYER_ENV_VARS      = "env-vars"
LAYER_CODESPACE     = "codespace"

# Report colours (ANSI — stripped when piped)
_GREEN  = "\033[32m"
_RED    = "\033[31m"
_YELLOW = "\033[33m"
_CYAN   = "\033[36m"
_RESET  = "\033[0m"
_BOLD   = "\033[1m"

_USE_COLOUR = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    return f"{code}{text}{_RESET}" if _USE_COLOUR else text


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ExpectedEntry:
    """An entry from the master guide's expected registry."""
    name: str
    layer: str
    required: bool       # False = optional / informational
    category: str        # e.g. "Cognitive Brain", "CI/CD", "GitHub App"
    purpose: str
    # human_governance: If True, automated writes must be blocked
    human_governance: bool = False


@dataclass
class AuditResult:
    """Live-vs-expected comparison result for one entry."""
    entry: ExpectedEntry
    live_status: str     # "present" | "absent" | "unknown" | "extra"
    note: str = ""


@dataclass
class AuditReport:
    timestamp: str
    owner: str
    repo: str
    results: list[AuditResult] = field(default_factory=list)
    extra_vars: list[str] = field(default_factory=list)  # in live but not expected
    auth_ok: bool = True


# ---------------------------------------------------------------------------
# Expected-variable registry
# Built from GITHUB_VARIABLES_MASTER_GUIDE.md — keep in sync with §3–§9.
# ---------------------------------------------------------------------------

_REGISTRY: list[ExpectedEntry] = [
    # ── §3 Organisation Secrets ──────────────────────────────────────────
    ExpectedEntry("CODECOV_TOKEN",              LAYER_ORG_SECRETS, True,  "CI/CD", "Code coverage upload to codecov.io"),
    ExpectedEntry("CODEX_ADMIN_KEY",            LAYER_ORG_SECRETS, True,  "Auth",  "Fine-grained PAT (Webhooks:write)"),
    ExpectedEntry("CODEX_BACKUP_KEY",           LAYER_ORG_SECRETS, True,  "Auth",  "Fallback GitHub PAT"),
    ExpectedEntry("CODEX_MASTER_KEY",           LAYER_ORG_SECRETS, True,  "Auth",  "Primary full-scope GitHub PAT"),
    ExpectedEntry("HF_TOKEN",                   LAYER_ORG_SECRETS, True,  "ML",    "HuggingFace API token"),
    ExpectedEntry("NPM_TOKEN",                  LAYER_ORG_SECRETS, False, "Publish","npm publish auth"),
    ExpectedEntry("PYPI_TOKEN",                 LAYER_ORG_SECRETS, False, "Publish","PyPI publish auth"),
    ExpectedEntry("RAG_OPENAI_KEY",             LAYER_ORG_SECRETS, True,  "ML",    "OpenAI key for RAG embeddings"),
    ExpectedEntry("_CODEX_ACTION_RUNNER",       LAYER_ORG_SECRETS, True,  "CI/CD", "Runner registration token"),
    ExpectedEntry("_GITHUB_APP_CLIENT_SECRET",  LAYER_ORG_SECRETS, True,  "GitHub App", "OAuth client secret", human_governance=True),
    ExpectedEntry("_GITHUB_APP_ID",             LAYER_ORG_SECRETS, True,  "GitHub App", "Numeric App ID"),
    ExpectedEntry("_GITHUB_APP_INSTALLATION_ID",LAYER_ORG_SECRETS, True,  "GitHub App", "App installation ID"),
    ExpectedEntry("_GITHUB_APP_PRIVATE_KEY",    LAYER_ORG_SECRETS, True,  "GitHub App", "RSA-2048 PEM private key"),

    # ── §4 Repository Secrets ────────────────────────────────────────────
    ExpectedEntry("CODEX_GHP_TOKEN_BASE64",    LAYER_REPO_SECRETS, True,  "Auth",   "Base64-encoded GHP token"),
    ExpectedEntry("CODEX_GHP_TOKEN_HEX",       LAYER_REPO_SECRETS, True,  "Auth",   "Hex-encoded GHP token"),
    ExpectedEntry("CODEX_GHP_TOKEN_SHA256",    LAYER_REPO_SECRETS, True,  "Auth",   "SHA-256 hash of GHP token"),
    ExpectedEntry("CODEX_REPO_ID",             LAYER_REPO_SECRETS, True,  "Config", "Repository numeric ID"),
    ExpectedEntry("CODEX_WEBHOOK_SECRET",      LAYER_REPO_SECRETS, True,  "Auth",   "HMAC-SHA256 webhook verification"),
    ExpectedEntry("OPENAI_API_KEY",            LAYER_REPO_SECRETS, True,  "ML",     "OpenAI API key for LLM agents"),
    ExpectedEntry("_CODEX_BOT_RUNNER",         LAYER_REPO_SECRETS, True,  "CI/CD",  "Bot runner token"),

    # ── §5 Environment Secrets (Aries_Serpent_codex_) ───────────────────
    ExpectedEntry("CODEX_ENVIRONMENT_RUNNER",  LAYER_ENV_SECRETS, True,  "CI/CD", "Environment runner token"),
    ExpectedEntry("CODEX_RUNNER_SHA256",       LAYER_ENV_SECRETS, True,  "CI/CD", "Runner token SHA-256"),
    ExpectedEntry("CODEX_RUNNER_TOKEN",        LAYER_ENV_SECRETS, True,  "CI/CD", "Runner registration token"),

    # ── §6 Repository Variables ───────────────────────────────────────────
    # §6a Cognitive Brain
    ExpectedEntry("COGNITIVE_BRAIN_ALLOWED_ACTORS",        LAYER_REPO_VARS, True,  "Cognitive Brain", "Permitted actors for cognitive brain"),
    ExpectedEntry("COGNITIVE_BRAIN_INJECTION_ENABLED",     LAYER_REPO_VARS, True,  "Cognitive Brain", "Master switch for context injection"),
    ExpectedEntry("COGNITIVE_BRAIN_LTM_RETENTION_DAYS",    LAYER_REPO_VARS, True,  "Cognitive Brain", "LTM retention days"),
    ExpectedEntry("COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS",    LAYER_REPO_VARS, True,  "Cognitive Brain", "Max tokens for context injection"),
    ExpectedEntry("COGNITIVE_BRAIN_MEMORY_TIER",           LAYER_REPO_VARS, True,  "Cognitive Brain", "Memory tier"),
    ExpectedEntry("COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE",LAYER_REPO_VARS, True,  "Cognitive Brain", "Min pattern confidence"),
    ExpectedEntry("COGNITIVE_BRAIN_SESSION_NUMBER",        LAYER_REPO_VARS, True,  "Cognitive Brain", "Current session number (auto-increments)"),
    # §6b Copilot Runtime
    ExpectedEntry("COPILOT_AGENT_AUTH_ENABLED",            LAYER_REPO_VARS, True,  "Copilot Runtime", "Gates token delegation", human_governance=True),
    ExpectedEntry("COPILOT_AGENT_FIREWALL_ENABLED",        LAYER_REPO_VARS, True,  "Copilot Runtime", "Network isolation control", human_governance=True),
    ExpectedEntry("COPILOT_AGENT_FIREWALL_ALLOW_LIST_ADDITIONS", LAYER_REPO_VARS, True, "Copilot Runtime", "Firewall allow-list additions"),
    ExpectedEntry("COPILOT_AGENT_MAX_AUTONOMY_LEVEL",      LAYER_REPO_VARS, True,  "Copilot Runtime", "Max autonomy level"),
    ExpectedEntry("COPILOT_AGENT_SESSION_RESTORE_ENABLED", LAYER_REPO_VARS, True,  "Copilot Runtime", "Session context restoration"),
    ExpectedEntry("COPILOT_CLI_BASE_URL",                  LAYER_REPO_VARS, True,  "Copilot Runtime", "Cognitive Brain CLI API URL"),
    ExpectedEntry("COPILOT_CLI_ENABLED",                   LAYER_REPO_VARS, True,  "Copilot Runtime", "CLI API server integration switch"),
    # §6c CI/CD
    ExpectedEntry("AGENT_HANDOFF_TIMEOUT_SECONDS", LAYER_REPO_VARS, True, "CI/CD", "Agent handoff timeout"),
    ExpectedEntry("AUTO_PROMOTE_TIER_ENABLED",     LAYER_REPO_VARS, True, "CI/CD", "Auto-promotion tier"),
    ExpectedEntry("AUTONOMOUS_ACTIONS_ENABLED",    LAYER_REPO_VARS, True, "CI/CD", "Gates autonomous actions", human_governance=True),
    ExpectedEntry("CODEX_CI_FAILURE_RATE",         LAYER_REPO_VARS, True, "CI/CD", "CI failure rate (auto-updated)"),
    ExpectedEntry("CODEX_CI_FAILURE_THRESHOLD",    LAYER_REPO_VARS, True, "CI/CD", "CI failure rate threshold"),
    ExpectedEntry("CODEX_CI_LAST_GREEN_SHA",       LAYER_REPO_VARS, True, "CI/CD", "Last all-green commit SHA"),
    ExpectedEntry("EMBEDDING_INDEX_AUTO_REBUILD",  LAYER_REPO_VARS, True, "CI/CD", "Auto-rebuild FAISS index"),
    # §6d Identity
    ExpectedEntry("AUDIT_RETENTION_DAYS",    LAYER_REPO_VARS, True, "Config", "Audit artifact retention"),
    ExpectedEntry("CODEX_AGENT_NAME",        LAYER_REPO_VARS, True, "Config", "Agent identity name"),
    ExpectedEntry("CODEX_API_VERSION",       LAYER_REPO_VARS, True, "Config", "GitHub API version pin"),
    ExpectedEntry("CODEX_ISOLATED_PATH",     LAYER_REPO_VARS, True, "Config", "Network isolation path"),
    ExpectedEntry("CODEX_LOG_LEVEL",         LAYER_REPO_VARS, True, "Config", "Logging verbosity"),
    ExpectedEntry("CODEX_NETWORK_MODE",      LAYER_REPO_VARS, True, "Config", "Network mode policy"),
    ExpectedEntry("CODEX_ORG_NAME",          LAYER_REPO_VARS, True, "Config", "Organization name constant"),
    ExpectedEntry("GENESIS_TIMESTAMP",       LAYER_REPO_VARS, True, "Config", "Repository genesis timestamp (immutable)"),
    # §6e Runtime/Build
    ExpectedEntry("CODEX_CACHE_VERSION",        LAYER_REPO_VARS, True, "Build", "Cache-busting version"),
    ExpectedEntry("CODEX_CLI_API_URL",          LAYER_REPO_VARS, True, "Build", "CLI API server URL"),
    ExpectedEntry("CODEX_COVERAGE_THRESHOLD",   LAYER_REPO_VARS, True, "Build", "Test coverage gate %"),
    ExpectedEntry("CODEX_D365_POLICIES_PATH",   LAYER_REPO_VARS, True, "Build", "D365 SLA policies path"),
    ExpectedEntry("CODEX_FORCE_CPU",            LAYER_REPO_VARS, True, "Build", "Force CPU-only torch"),
    ExpectedEntry("CODEX_LINT_STRICT",          LAYER_REPO_VARS, True, "Build", "Strict Ruff/mypy mode"),
    ExpectedEntry("CODEX_LLM_MODEL",            LAYER_REPO_VARS, True, "Build", "LLM model for agents"),
    ExpectedEntry("CODEX_LLM_RATE_LIMIT_DELAY", LAYER_REPO_VARS, True, "Build", "LLM request delay"),
    ExpectedEntry("CODEX_OFFLINE",              LAYER_REPO_VARS, True, "Build", "Offline mode flag"),
    ExpectedEntry("CODEX_PYTHON_VERSION",       LAYER_REPO_VARS, True, "Build", "Python version"),
    ExpectedEntry("CODEX_SANDBOX_TIMEOUT",      LAYER_REPO_VARS, True, "Build", "Sandbox operation timeout"),
    ExpectedEntry("CODEX_SESSION_ID",           LAYER_REPO_VARS, True, "Build", "Current session ID (auto-set)"),
    ExpectedEntry("CODEX_SESSION_LOG_DIR",      LAYER_REPO_VARS, True, "Build", "Session log directory"),
    ExpectedEntry("CODEX_TEST_PARALLELISM",     LAYER_REPO_VARS, True, "Build", "Pytest parallelism mode"),
    ExpectedEntry("CODEX_ZENDESK_DOCS_ROOT",    LAYER_REPO_VARS, False,"Build", "Zendesk docs root"),
    ExpectedEntry("ENABLE_LIVE_TESTS",          LAYER_REPO_VARS, True, "Build", "Enable live/integration tests"),
    # §6f ML
    ExpectedEntry("COMPOSE_DOCKER_CLI_BUILD",LAYER_REPO_VARS, False, "ML", "Docker Compose BuildKit"),
    ExpectedEntry("DOCKER_BUILDKIT",         LAYER_REPO_VARS, False, "ML", "Docker BuildKit flag"),
    ExpectedEntry("GPU_OPT",                 LAYER_REPO_VARS, False, "ML", "Docker GPU passthrough"),
    ExpectedEntry("HF_HOME",                 LAYER_REPO_VARS, True,  "ML", "HuggingFace cache dir"),
    ExpectedEntry("MLFLOW_EXPERIMENT_NAME",  LAYER_REPO_VARS, False, "ML", "MLflow experiment name"),
    ExpectedEntry("TORCH_HOME",              LAYER_REPO_VARS, True,  "ML", "PyTorch cache dir"),
    ExpectedEntry("TRANSFORMERS_OFFLINE",    LAYER_REPO_VARS, True,  "ML", "HF Transformers offline mode"),
    ExpectedEntry("WANDB_MODE",              LAYER_REPO_VARS, False, "ML", "W&B run mode"),
    ExpectedEntry("ZENDESK_RATE_LIMIT",      LAYER_REPO_VARS, False, "ML", "Zendesk API rate limit"),
    ExpectedEntry("ZENDESK_SYNC_INTERVAL",   LAYER_REPO_VARS, False, "ML", "Zendesk sync interval"),
    # §6g Webhook/Infra
    ExpectedEntry("CODEX_ACTIVE_CODESPACE",  LAYER_REPO_VARS, True, "Webhook/Infra", "Active Codespace name (auto-set)"),
    ExpectedEntry("WEBHOOK_RECEIVER_URL",    LAYER_REPO_VARS, True, "Webhook/Infra", "Public webhook receiver URL (auto-set)"),

    # §6h Autonomous Agent Config (S116/PR #3508)
    ExpectedEntry("AGENT_KILL_SWITCH",            LAYER_REPO_VARS, True,  "Autonomous Agent", "Emergency stop for all agent loops (0=run, 1=halt)", human_governance=True),
    ExpectedEntry("AUTONOMY_BUDGET_SECONDS",      LAYER_REPO_VARS, False, "Autonomous Agent", "Max wall-clock budget for autonomy_scheduler (Phase 1)"),
    ExpectedEntry("AUTONOMY_MAX_ITERATIONS",      LAYER_REPO_VARS, False, "Autonomous Agent", "Max iterations per autonomy_scheduler run (Phase 1)"),
    ExpectedEntry("AUTONOMY_DRY_RUN",             LAYER_REPO_VARS, False, "Autonomous Agent", "Disable mutating writes in autonomy_scheduler (0/1)"),
    ExpectedEntry("AGENT_RUNNER_BUDGET_SECONDS",  LAYER_REPO_VARS, False, "Autonomous Agent", "Total wall-clock budget for agent_runner (Phase 7)"),
    ExpectedEntry("AGENT_RUNNER_ITERATIONS",      LAYER_REPO_VARS, False, "Autonomous Agent", "Phase loop iterations per agent_runner invocation"),
    ExpectedEntry("AGENT_RUNNER_DRY_RUN",         LAYER_REPO_VARS, False, "Autonomous Agent", "Skip write operations in agent_runner (0/1)"),
    ExpectedEntry("UNCERTAINTY_BUDGET_SECONDS",   LAYER_REPO_VARS, False, "Autonomous Agent", "Per-query cap for Dirichlet inference (Phases 4/5)"),

    # ── §7 Environment Variables (Aries_Serpent_codex_) ─────────────────
    ExpectedEntry("CODEX_ENV_NODE_VERSION",   LAYER_ENV_VARS, True, "Build", "Node.js version"),
    ExpectedEntry("CODEX_ENV_PYTHON_VERSION", LAYER_ENV_VARS, True, "Build", "Python version"),

    # ── §8 Codespace Secrets — ALL CONFIRMED ✅ (SAR-G01 COMPLETE 2026-03-07) ──────
    ExpectedEntry("CODEX_MASTER_KEY",              LAYER_CODESPACE, True,  "Auth",       "Primary PAT (org-level Codespace secret ✅)"),
    ExpectedEntry("CODEX_BACKUP_KEY",              LAYER_CODESPACE, True,  "Auth",       "Fallback PAT (user Codespace secret ✅ 2026-03-06)"),
    ExpectedEntry("CODEX_ADMIN_KEY",               LAYER_CODESPACE, True,  "Auth",       "Admin PAT (user Codespace secret ✅ 2026-03-06)"),
    ExpectedEntry("_GITHUB_APP_ID",                LAYER_CODESPACE, True,  "GitHub App", "App ID (user Codespace secret ✅ 2026-03-06)"),
    ExpectedEntry("_GITHUB_APP_PRIVATE_KEY",       LAYER_CODESPACE, True,  "GitHub App", "PEM key (user Codespace secret ✅ 2026-03-06)"),
    ExpectedEntry("_GITHUB_APP_INSTALLATION_ID",   LAYER_CODESPACE, True,  "GitHub App", "Installation ID (user Codespace secret ✅ 2026-03-06)"),
    ExpectedEntry("_GITHUB_APP_CLIENT_SECRET",     LAYER_CODESPACE, True,  "GitHub App", "OAuth client secret (user Codespace secret ✅ 2026-03-07)"),
    ExpectedEntry("WEBHOOK_SECRET",                LAYER_CODESPACE, True,  "Webhook/Infra","Webhook HMAC secret (user Codespace secret ✅ 2026-03-06)"),
    ExpectedEntry("WEBHOOK_RECEIVER_URL",          LAYER_CODESPACE, False, "Webhook/Infra","Receiver URL (user Codespace secret ✅ 2026-03-06; also auto-set as repo var)"),
]


# ---------------------------------------------------------------------------
# Live-state fetchers
# ---------------------------------------------------------------------------

def _fetch_repo_vars(vm: VariableManager) -> dict[str, Any]:
    """Return {name: entry} for all live repo variables."""
    try:
        rows = vm.list_repo_vars(_OWNER, _REPO)
        return {r["name"]: r for r in rows}
    except Exception as exc:
        return {"_error": str(exc)}


def _fetch_repo_secrets(token: str) -> dict[str, Any]:
    """Return {name: {}} for repo secrets (names only — values never exposed)."""
    try:
        status, body = _gh_request(
            "GET",
            f"/repos/{_OWNER}/{_REPO}/actions/secrets",
            token=token,
        )
        secrets = body.get("secrets", []) if isinstance(body, dict) else []
        return {s["name"]: s for s in secrets}
    except Exception as exc:
        return {"_error": str(exc)}


def _fetch_org_secrets(token: str) -> dict[str, Any]:
    """Return {name: {}} for org secrets the repo can access."""
    try:
        status, body = _gh_request(
            "GET",
            f"/orgs/{_OWNER}/actions/secrets",
            token=token,
        )
        secrets = body.get("secrets", []) if isinstance(body, dict) else []
        return {s["name"]: s for s in secrets}
    except Exception as exc:
        return {"_error": str(exc)}


def _fetch_env_secrets(token: str) -> dict[str, Any]:
    """Return {name: {}} for environment secrets."""
    try:
        status, body = _gh_request(
            "GET",
            f"/repos/{_OWNER}/{_REPO}/environments/{_ENV}/secrets",
            token=token,
        )
        secrets = body.get("secrets", []) if isinstance(body, dict) else []
        return {s["name"]: s for s in secrets}
    except Exception as exc:
        return {"_error": str(exc)}


def _fetch_env_vars(token: str) -> dict[str, Any]:
    """Return {name: entry} for environment variables."""
    try:
        status, body = _gh_request(
            "GET",
            f"/repos/{_OWNER}/{_REPO}/environments/{_ENV}/variables",
            token=token,
        )
        variables = body.get("variables", []) if isinstance(body, dict) else []
        return {v["name"]: v for v in variables}
    except Exception as exc:
        return {"_error": str(exc)}


def _fetch_codespace_secrets(token: str) -> dict[str, Any]:
    """
    Codespace secrets cannot be listed via API by a bot token — only org admins
    can enumerate them.  We return a sentinel dict so the audit can flag these
    as UNKNOWN and prompt human verification.
    """
    return {"_codespace_api_unavailable": True}


# ---------------------------------------------------------------------------
# Audit engine
# ---------------------------------------------------------------------------

def run_audit(
    layer_filter: str = "all",
    owner: str = _OWNER,
    repo: str = _REPO,
) -> AuditReport:
    """
    Compare expected registry against live GitHub state.

    Returns an :class:`AuditReport` with per-entry results.
    When API calls fail (no token / 403) results are marked ``unknown``.
    """
    report = AuditReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        owner=owner,
        repo=repo,
        auth_ok=False,  # default False; set True only after successful token resolution
    )

    # ── resolve auth ───────────────────────────────────────────────────
    token: Optional[str] = None
    vm: Optional[Any] = None
    if _VM_AVAILABLE:
        try:
            token, _source = _resolve_token()
            vm = VariableManager()
            report.auth_ok = True
        except Exception:
            report.auth_ok = False

    # ── fetch live state ───────────────────────────────────────────────
    live: dict[str, dict[str, Any]] = {
        LAYER_ORG_SECRETS:  {},
        LAYER_REPO_SECRETS: {},
        LAYER_ENV_SECRETS:  {},
        LAYER_REPO_VARS:    {},
        LAYER_ENV_VARS:     {},
        LAYER_CODESPACE:    {},
    }

    if token:
        live[LAYER_ORG_SECRETS]  = _fetch_org_secrets(token)
        live[LAYER_REPO_SECRETS] = _fetch_repo_secrets(token)
        live[LAYER_ENV_SECRETS]  = _fetch_env_secrets(token)
        live[LAYER_ENV_VARS]     = _fetch_env_vars(token)
        live[LAYER_CODESPACE]    = _fetch_codespace_secrets(token)
    if vm:
        live[LAYER_REPO_VARS] = _fetch_repo_vars(vm)

    # ── build results ──────────────────────────────────────────────────
    layers = (
        [layer_filter] if layer_filter != "all"
        else list(live.keys())
    )

    for entry in _REGISTRY:
        if entry.layer not in layers:
            continue

        live_layer = live.get(entry.layer, {})

        if "_error" in live_layer:
            status = "unknown"
            note   = f"API error: {live_layer['_error']}"
        elif "_codespace_api_unavailable" in live_layer:
            # Codespace secrets: we know CODEX_MASTER_KEY is confirmed org-level;
            # the 7 remaining ones are BLOCKER as documented in §8.
            status = "unknown"
            note   = "Codespace secrets cannot be listed via API — verify manually in §8"
        elif not token and not vm:
            status = "unknown"
            note   = "No auth token — run with CODEX_MASTER_KEY set for live checks"
        elif entry.name in live_layer:
            status = "present"
            note   = ""
        else:
            status = "absent"
            note   = "⚠️ BLOCKER" if entry.required else "optional"

        report.results.append(AuditResult(entry=entry, live_status=status, note=note))

    # ── detect extra variables (present in live but not in expected) ───
    expected_names_per_layer: dict[str, set] = {lyr: set() for lyr in layers}
    for entry in _REGISTRY:
        if entry.layer in layers:
            expected_names_per_layer[entry.layer].add(entry.name)

    for lyr in layers:
        for name in live.get(lyr, {}):
            if name.startswith("_"):
                continue  # skip internal sentinel keys
            if name not in expected_names_per_layer.get(lyr, set()):
                report.extra_vars.append(f"{lyr}/{name}")

    return report


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

_STATUS_ICON: dict[str, str] = {
    "present": "✅",
    "absent":  "❌",
    "unknown": "❓",
    "extra":   "➕",
}

_STATUS_COLOUR: dict[str, str] = {
    "present": _GREEN,
    "absent":  _RED,
    "unknown": _YELLOW,
    "extra":   _CYAN,
}


def _icon(status: str) -> str:
    return _STATUS_ICON.get(status, "?")


def format_table(report: AuditReport) -> str:
    """Render a human-readable terminal table."""
    lines: list[str] = []
    lines.append(_c(_BOLD, f"\n{'─'*72}"))
    lines.append(_c(_BOLD, "  Variable / Secret Audit Report"))
    lines.append(f"  Repo   : {report.owner}/{report.repo}")
    lines.append(f"  Time   : {report.timestamp}")
    lines.append(f"  Auth   : {'✅ token active' if report.auth_ok else '❌ no token (expected-only mode)'}")
    lines.append(_c(_BOLD, f"{'─'*72}"))

    current_layer = ""
    for result in report.results:
        if result.entry.layer != current_layer:
            current_layer = result.entry.layer
            lines.append(f"\n  {'─'*30}  {_c(_BOLD, current_layer.upper())}  {'─'*30}\n")
        icon  = _icon(result.live_status)
        gov   = _c(_YELLOW, " [HUMAN-GOV]") if result.entry.human_governance else ""
        req   = "" if result.entry.required else _c(_CYAN, " [optional]")
        col   = _STATUS_COLOUR.get(result.live_status, "")
        name  = _c(col, f"{result.entry.name:<48}")
        note  = f"  {result.note}" if result.note else ""
        lines.append(f"  {icon}  {name}{gov}{req}{note}")

    # summary
    present = sum(1 for r in report.results if r.live_status == "present")
    absent  = sum(1 for r in report.results if r.live_status == "absent")
    unknown = sum(1 for r in report.results if r.live_status == "unknown")
    total   = len(report.results)

    lines.append(f"\n{'─'*72}")
    lines.append(f"  TOTAL {total}  |  ✅ present {present}  |  ❌ absent {absent}  |  ❓ unknown {unknown}")
    if report.extra_vars:
        lines.append(f"\n  ➕ Extra (in live, not in guide): {len(report.extra_vars)}")
        for ev in report.extra_vars[:10]:
            lines.append(f"      {ev}")
        if len(report.extra_vars) > 10:
            lines.append(f"      … and {len(report.extra_vars)-10} more")
    lines.append(f"{'─'*72}\n")
    return "\n".join(lines)


def format_json(report: AuditReport) -> str:
    """Render JSON output."""
    def _result_dict(r: AuditResult) -> dict:
        return {
            "name":   r.entry.name,
            "layer":  r.entry.layer,
            "status": r.live_status,
            "required": r.entry.required,
            "category": r.entry.category,
            "human_governance": r.entry.human_governance,
            "note":   r.note,
        }
    out = {
        "timestamp":   report.timestamp,
        "owner":       report.owner,
        "repo":        report.repo,
        "auth_ok":     report.auth_ok,
        "summary": {
            "total":   len(report.results),
            "present": sum(1 for r in report.results if r.live_status == "present"),
            "absent":  sum(1 for r in report.results if r.live_status == "absent"),
            "unknown": sum(1 for r in report.results if r.live_status == "unknown"),
        },
        "results":    [_result_dict(r) for r in report.results],
        "extra_vars": report.extra_vars,
    }
    return json.dumps(out, indent=2)


def format_markdown(report: AuditReport) -> str:
    """Render a Markdown audit report."""
    lines: list[str] = []
    lines.append("# Variable / Secret Audit Report\n")
    lines.append(f"**Repository:** `{report.owner}/{report.repo}`  ")
    lines.append(f"**Generated:** `{report.timestamp}`  ")
    lines.append(f"**Auth:** {'✅ token active' if report.auth_ok else '❌ no token (expected-only mode)'}\n")

    present = sum(1 for r in report.results if r.live_status == "present")
    absent  = sum(1 for r in report.results if r.live_status == "absent")
    unknown = sum(1 for r in report.results if r.live_status == "unknown")

    lines.append("## Summary\n")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Total expected | {len(report.results)} |")
    lines.append(f"| ✅ Present | {present} |")
    lines.append(f"| ❌ Absent (required) | {absent} |")
    lines.append(f"| ❓ Unknown (no API access) | {unknown} |")
    lines.append(f"| ➕ Extra (not in guide) | {len(report.extra_vars)} |\n")

    current_layer = ""
    for result in report.results:
        if result.entry.layer != current_layer:
            current_layer = result.entry.layer
            lines.append(f"\n## Layer: `{current_layer}`\n")
            lines.append("| Status | Name | Category | Required | Notes |")
            lines.append("|--------|------|----------|----------|-------|")
        icon = _STATUS_ICON.get(result.live_status, "?")
        gov  = " 🔒" if result.entry.human_governance else ""
        req  = "yes" if result.entry.required else "optional"
        note = result.note or ""
        lines.append(f"| {icon} | `{result.entry.name}`{gov} | {result.entry.category} | {req} | {note} |")

    if report.extra_vars:
        lines.append("\n## Extra Variables (present in live, not in guide)\n")
        for ev in report.extra_vars:
            lines.append(f"- `{ev}`")

    lines.append("\n---\n")
    lines.append("_Generated by `scripts/tools/variable_audit_cli.py`._")
    return "\n".join(lines)


def format_expected_table(layer: str = "all") -> str:
    """List all expected entries without live check."""
    lines: list[str] = [
        _c(_BOLD, "\nExpected Variables/Secrets Registry  (source: GITHUB_VARIABLES_MASTER_GUIDE.md)\n"),
        f"  {'NAME':<50} {'LAYER':<20} {'CAT':<20} {'REQ':<5}",
        f"  {'─'*50} {'─'*20} {'─'*20} {'─'*5}",
    ]
    entries = [e for e in _REGISTRY if layer == "all" or e.layer == layer]
    for e in entries:
        req = "yes" if e.required else "opt"
        gov = " 🔒" if e.human_governance else ""
        lines.append(f"  {e.name + gov:<50} {e.layer:<20} {e.category:<20} {req}")
    lines.append(f"\n  Total: {len(entries)} entries\n")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="variable_audit_cli",
        description=textwrap.dedent("""\
            Audit and report on ALL GitHub variable/secret storage layers
            against GITHUB_VARIABLES_MASTER_GUIDE.md.

            Auth: set CODEX_MASTER_KEY (or CODEX_BACKUP_KEY) in the
            environment before running live checks.
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="command", required=True)

    # check -------------------------------------------------------------------
    chk = sub.add_parser(
        "check",
        help="Live API check: compare actual GitHub state against the guide",
    )
    chk.add_argument(
        "--layer",
        default="all",
        choices=["all", LAYER_ORG_SECRETS, LAYER_REPO_SECRETS,
                 LAYER_ENV_SECRETS, LAYER_REPO_VARS, LAYER_ENV_VARS,
                 LAYER_CODESPACE],
        help="Filter to a specific storage layer (default: all)",
    )
    chk.add_argument(
        "--format",
        default="table",
        choices=["table", "json", "md"],
        dest="fmt",
        help="Output format (default: table)",
    )
    chk.add_argument(
        "--out",
        default=None,
        metavar="PATH",
        help="Write output to file instead of stdout",
    )
    chk.add_argument(
        "--fail-on-absent",
        action="store_true",
        default=False,
        help="Exit 1 if any required variable is absent",
    )

    # report ------------------------------------------------------------------
    rep = sub.add_parser(
        "report",
        help="Generate a full Markdown audit report",
    )
    rep.add_argument(
        "--out",
        default=None,
        metavar="PATH",
        help="Write report to file (default: stdout)",
    )

    # expected ----------------------------------------------------------------
    exp = sub.add_parser(
        "expected",
        help="List all expected variables from the guide (offline, no API)",
    )
    exp.add_argument(
        "--layer",
        default="all",
        choices=["all", LAYER_ORG_SECRETS, LAYER_REPO_SECRETS,
                 LAYER_ENV_SECRETS, LAYER_REPO_VARS, LAYER_ENV_VARS,
                 LAYER_CODESPACE],
    )
    exp.add_argument(
        "--format",
        default="table",
        choices=["table", "json"],
        dest="fmt",
    )

    # diff -------------------------------------------------------------------
    diff = sub.add_parser(
        "diff",
        help="Show differences: expected vs live (absent + extra)",
    )
    diff.add_argument(
        "--layer",
        default="all",
        choices=["all", LAYER_ORG_SECRETS, LAYER_REPO_SECRETS,
                 LAYER_ENV_SECRETS, LAYER_REPO_VARS, LAYER_ENV_VARS,
                 LAYER_CODESPACE],
    )
    diff.add_argument(
        "--out",
        default=None,
        metavar="PATH",
        help="Write diff to file",
    )

    # rotate-check -----------------------------------------------------------
    rot = sub.add_parser(
        "rotate-check",
        help="Report secrets that are approaching or past their rotation deadline",
    )
    rot.add_argument(
        "--days",
        type=int,
        default=90,
        metavar="N",
        help="Flag secrets not rotated within N days (default: 90)",
    )

    return p


def _write(content: str, path: Optional[str]) -> None:
    if path:
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        print(f"✅  Written to {out}", file=sys.stderr)
    else:
        print(content)


def main(argv: Optional[list[str]] = None) -> int:  # noqa: C901
    parser = _build_parser()
    args   = parser.parse_args(argv)

    if args.command == "expected":
        if args.fmt == "json":
            entries = [e for e in _REGISTRY if args.layer == "all" or e.layer == args.layer]
            print(json.dumps([asdict(e) for e in entries], indent=2))
        else:
            print(format_expected_table(args.layer))
        return 0

    if args.command == "check":
        report = run_audit(layer_filter=args.layer)
        if args.fmt == "json":
            output = format_json(report)
        elif args.fmt == "md":
            output = format_markdown(report)
        else:
            output = format_table(report)
        _write(output, getattr(args, "out", None))
        if args.fail_on_absent:
            absent = sum(1 for r in report.results if r.live_status == "absent" and r.entry.required)
            return 1 if absent > 0 else 0
        return 0

    if args.command == "report":
        report = run_audit()
        output = format_markdown(report)
        _write(output, getattr(args, "out", None))
        absent = sum(1 for r in report.results if r.live_status == "absent" and r.entry.required)
        return 1 if absent > 0 else 0

    if args.command == "diff":
        report = run_audit(layer_filter=args.layer)
        absent_req   = [r for r in report.results if r.live_status == "absent" and r.entry.required]
        absent_opt   = [r for r in report.results if r.live_status == "absent" and not r.entry.required]
        unknown      = [r for r in report.results if r.live_status == "unknown"]
        lines: list[str] = [
            _c(_BOLD, f"\nAudit Diff  [{report.timestamp}]"),
            f"Auth: {'✅ token active' if report.auth_ok else '❌ offline mode'}\n",
        ]
        if absent_req:
            lines.append(_c(_RED, f"❌ ABSENT — required ({len(absent_req)}):"))
            for r in absent_req:
                lines.append(f"   {r.entry.layer}/{r.entry.name}")
        if absent_opt:
            lines.append(_c(_YELLOW, f"\n⚠️  ABSENT — optional ({len(absent_opt)}):"))
            for r in absent_opt:
                lines.append(f"   {r.entry.layer}/{r.entry.name}")
        if unknown:
            lines.append(_c(_YELLOW, f"\n❓ UNKNOWN — no API access ({len(unknown)}):"))
            for r in unknown[:5]:
                lines.append(f"   {r.entry.layer}/{r.entry.name}")
            if len(unknown) > 5:
                lines.append(f"   … and {len(unknown)-5} more")
        if report.extra_vars:
            lines.append(_c(_CYAN, f"\n➕ EXTRA — in live, not in guide ({len(report.extra_vars)}):"))
            for ev in report.extra_vars[:10]:
                lines.append(f"   {ev}")
        if not absent_req and not absent_opt and not unknown and not report.extra_vars:
            lines.append(_c(_GREEN, "✅ No differences found — live state matches guide exactly"))
        _write("\n".join(lines), getattr(args, "out", None))
        return 1 if absent_req else 0

    if args.command == "rotate-check":
        # We can only check updated_at timestamps returned by the Secrets API.
        lines: list[str] = [
            _c(_BOLD, f"\nRotation Check  (threshold: {args.days} days)"),
            "Note: GitHub only exposes updated_at for secrets (not variables).\n",
        ]
        token = None
        if _VM_AVAILABLE:
            try:
                token, _ = _resolve_token()
            except Exception as exc:  # best-effort — failure falls through to "No token" branch
                print(f"[variable_audit_cli] token resolution failed: {type(exc).__name__}: {exc}", file=sys.stderr)

        if not token:
            lines.append(_c(_YELLOW, "❌ No token — cannot fetch live rotation timestamps."))
            lines.append("   Set CODEX_MASTER_KEY and re-run.")
            print("\n".join(lines))
            return 2

        now = datetime.now(timezone.utc)
        for fetch_fn, label in [
            (lambda: _fetch_org_secrets(token), "org-secrets"),
            (lambda: _fetch_repo_secrets(token), "repo-secrets"),
            (lambda: _fetch_env_secrets(token), "env-secrets"),
        ]:
            live = fetch_fn()
            for name, meta in live.items():
                if name.startswith("_"):
                    continue
                updated = meta.get("updated_at", "")
                if not updated:
                    continue
                try:
                    dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                    age = (now - dt).days
                    if age >= args.days:
                        lines.append(_c(_RED, f"⚠️  {label}/{name}  —  {age}d ago  (last: {updated[:10]})"))
                except Exception as exc:  # skip entries with unparseable timestamps
                    print(
                        f"[variable_audit_cli] could not parse updated_at={updated!r}: "
                        f"{type(exc).__name__}: {exc}",
                        file=sys.stderr,
                    )
        print("\n".join(lines))
        return 0

    return 3


if __name__ == "__main__":
    sys.exit(main())
