# Sprint Plan — Phase 13.1: MCP Interactive Mode

**Version:** 1.0.0  
**Status:** 🟡 In Planning  
**Owner:** Copilot Coding Agent (S263+)  
**Timeline:** 2026-04-01 → 2026-04-15  
**Phase:** 13.1 (follows Phase 13 CI/Security Hardening, S257–S263)  
**Tracked in:** `docs/evolution/EVOLUTION_TIMELINE.md` v3.0.0  

---

## 🎯 Objective

Implement an **interactive TUI (Terminal UI) mode** for the MCP (Model Context Protocol) package system that provides:
1. **File selector** — tree-based navigation of available MCP context files
2. **Real-time size preview** — live byte/token count as files are toggled
3. **Session injection** — selected files injected into Copilot session context

---

## 📋 Sprint Breakdown

### Sprint 13.1.0 — Foundation (2026-04-01 → 2026-04-05)

| Task | File | Priority | Status |
|------|------|----------|--------|
| S13.1-001 | Create `src/mcp/interactive.py` — TUI entry point | 🔴 P1 | ⏳ Pending |
| S13.1-002 | Create `src/mcp/file_selector.py` — tree file picker | 🔴 P1 | ⏳ Pending |
| S13.1-003 | Create `src/mcp/size_preview.py` — byte + token counter | 🔴 P1 | ⏳ Pending |
| S13.1-004 | Create `src/mcp/__init__.py` — package init with public API | 🟡 P2 | ⏳ Pending |
| S13.1-005 | Add `tests/mcp/test_interactive.py` — unit tests | 🔴 P1 | ⏳ Pending |

### Sprint 13.1.1 — TUI Implementation (2026-04-06 → 2026-04-10)

| Task | File | Priority | Status |
|------|------|----------|--------|
| S13.1-006 | Implement `FileSelector` class with curses/rich fallback | 🔴 P1 | ⏳ Pending |
| S13.1-007 | Implement `SizePreview` with real-time token estimation | 🔴 P1 | ⏳ Pending |
| S13.1-008 | Implement `InteractiveSession` — wires selector + preview | 🔴 P1 | ⏳ Pending |
| S13.1-009 | CLI entry point: `python -m mcp.interactive` | 🟡 P2 | ⏳ Pending |
| S13.1-010 | Integration with `copilot/extension/server/index.js` ITA API | 🟡 P2 | ⏳ Pending |

### Sprint 13.1.2 — Validation & Release (2026-04-11 → 2026-04-15)

| Task | File | Priority | Status |
|------|------|----------|--------|
| S13.1-011 | End-to-end test: file select → session inject → verify context | 🔴 P1 | ⏳ Pending |
| S13.1-012 | Performance test: <100ms render for 1000-file tree | 🟡 P2 | ⏳ Pending |
| S13.1-013 | Update `docs/evolution/EVOLUTION_TIMELINE.md` Phase 13.1 → Complete | 🟡 P2 | ⏳ Pending |
| S13.1-014 | Update `CHANGELOG.md` + accountability report | 🔴 P1 | ⏳ Pending |

---

## 🏗️ Architecture Design

```
src/mcp/
├── __init__.py             # Public API: InteractiveSession, FileSelector, SizePreview
├── interactive.py          # TUI entry point; orchestrates selector + preview
├── file_selector.py        # Tree-based file picker (rich/curses)
├── size_preview.py         # Real-time byte + token size estimation
└── session_injector.py     # Injects selected files into Copilot context

tests/mcp/
├── __init__.py
├── test_interactive.py     # Unit tests for InteractiveSession
├── test_file_selector.py   # Unit tests for FileSelector
└── test_size_preview.py    # Unit tests for SizePreview
```

### Key Interfaces

```python
# src/mcp/interactive.py
class InteractiveSession:
    """Orchestrates the TUI file selector + real-time size preview."""

    def __init__(self, root_dir: Path, max_tokens: int = 4096): ...
    def run(self) -> list[Path]:
        """Launch TUI, return list of selected file paths."""
    def inject_into_context(self, files: list[Path]) -> dict[str, str]:
        """Load file contents for Copilot session injection."""

# src/mcp/file_selector.py
class FileSelector:
    """Tree-based interactive file picker."""

    def __init__(self, root: Path, max_depth: int = 5): ...
    def render(self) -> None: ...
    def toggle(self, path: Path) -> None: ...
    def get_selected(self) -> list[Path]: ...

# src/mcp/size_preview.py
class SizePreview:
    """Real-time byte + approximate token count for selected files."""

    def __init__(self, token_model: str = "cl100k_base"): ...
    def update(self, files: list[Path]) -> dict[str, int]:
        """Returns {'bytes': N, 'tokens': N, 'files': N}"""
    def format_summary(self, stats: dict[str, int]) -> str:
        """Returns formatted string like '42 files · 128 KB · ~3,200 tokens'"""
```

---

## 🔗 Dependencies

| Package | Version | Purpose | Security Check |
|---------|---------|---------|----------------|
| `rich` | `>=13.0` | TUI rendering (tree + live preview) | ✅ No known CVEs |
| `tiktoken` | `>=0.5` | Token counting (optional, falls back to char/4) | ✅ No known CVEs |

Both are optional extras — the module degrades gracefully if not installed:
- Without `rich`: falls back to plain `curses` or non-interactive listing
- Without `tiktoken`: uses `len(text) // 4` as token estimate

---

## ✅ Acceptance Criteria

1. `python -m mcp.interactive` launches without error on Python 3.12
2. File tree renders in ≤ 200ms for repos with ≤ 5,000 files
3. Real-time size preview updates in ≤ 50ms on file toggle
4. Selected files are returned as `list[Path]` and can be injected into session context
5. All unit tests pass (`pytest tests/mcp/ -v`)
6. `ruff check src/mcp/ tests/mcp/` exits 0
7. `EVOLUTION_TIMELINE.md` Phase 13.1 updated to ✅ Complete on merge

---

## 📊 Metrics

| Metric | Target | Measured |
|--------|--------|---------|
| Render time (1k files) | < 100ms | ⏳ TBD |
| Toggle latency | < 50ms | ⏳ TBD |
| Token estimation accuracy vs tiktoken | ≥ 90% | ⏳ TBD |
| Test coverage (src/mcp/) | ≥ 80% | ⏳ TBD |

---

## 📝 Notes

- Phase 13.1 was originally scheduled as part of Phase 13 (S257–S262) but rescheduled to allow CI/Security Hardening to land first.
- The MCP Interactive Mode TUI is intended for local developer use and Copilot session context injection, not production deployment.
- The `session_injector.py` module will integrate with the existing `copilot/extension/server/index.js` ITA (Intelligent Task Allocation) API.
- Token counting uses `cl100k_base` (GPT-4/Claude compatible) by default; this can be overridden via `MCP_TOKEN_MODEL` env var.

---

_Sprint plan created: 2026-04-01 S263_  
_Next review: 2026-04-05 (end of Sprint 13.1.0)_
