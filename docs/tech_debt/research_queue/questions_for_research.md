# Questions Requiring Deep Research - PR #3344 (S66)

**Created**: 2026-02-22 08:30  
**Status**: Awaiting Research  
**Total Questions**: 5
**PR**: https://github.com/Aries-Serpent/_codex_/pull/3344  
**Branch**: `copilot/sub-pr-3336-again`

---

## Question Queue

---

### Q001: Should `_emit_provenance_summary` Output Go to stdout or stderr?

**Category**: API Design/Contract  
**Priority**: High  
**Impact**: High  
**Created**: 2026-02-22  
**Status**: ⏳ Awaiting Research

#### Context
**Where discovered**: `src/codex_ml/cli/codex_cli.py:109–113`, `tests/cli/test_evaluation_cli.py::test_evaluate_cli_writes_metrics_log`  
**What happened**: The `evaluate` CLI command emits the evaluation summary JSON to stdout, then calls `_emit_provenance_summary()` which also calls `click.echo(json.dumps(summary))` to stdout. Tests using `CliRunner().invoke()` receive both JSON blobs in `result.output`. `json.loads(result.output)` fails (two root JSON objects), and the fallback line-by-line parser picks the LAST valid compact JSON — which is the provenance dict — instead of the multi-line evaluation summary. Result: `KeyError: 'metrics_path'`.  
**Current behavior**: Provenance summary written to stdout alongside primary output.  
**Expected behavior**: Unclear — may be intentional for piping to log aggregators, or may be an oversight.

#### The Question
Is `_emit_provenance_summary()` designed to go to stdout (machine-readable, part of the primary output contract) or to stderr (diagnostic/supplementary)? What do the 5 other call sites (`train`, `evaluate`, `prepare-data`, `deploy`) expect callers to do with the provenance JSON?

#### Why This Needs Research
- [ ] Requires reviewing original design intent (commit history / PR where `_emit_provenance_summary` was introduced)
- [ ] Requires checking if any downstream consumer (CI pipelines, log parsers, dashboards) reads provenance from stdout
- [ ] Could break other CLI users if provenance is moved to stderr

#### Current Hypothesis
**Your best guess**: Provenance is supplementary/diagnostic — should go to stderr.  
**Confidence level**: Medium  
**Evidence supporting hypothesis**: Other well-known CLIs (`kubectl`, `aws-cli`, `gh`) separate machine output (stdout) from diagnostic info (stderr). The evaluation summary is the primary contract; provenance is metadata.

#### Information to Guide Research

**Suggested search queries**:
1. "click CLI best practice stdout stderr diagnostic output machine readable"
2. "cli design primary output vs supplementary metadata stream separation"
3. "git grep '_emit_provenance_summary' site:github.com/Aries-Serpent/_codex_"

**Suggested sources**:
- [ ] Click documentation: https://click.palletsprojects.com/en/stable/api/#click.echo (`err` parameter)
- [ ] Git log: `git log --oneline --follow src/codex_ml/cli/codex_cli.py` — find when `_emit_provenance_summary` was introduced and what the PR description says
- [ ] Any CI pipeline scripts in `.github/workflows/` that parse CLI output

**Related files in codebase**:
- `src/codex_ml/cli/codex_cli.py:109` — `_emit_provenance_summary` definition
- `src/codex_ml/utils/provenance.py` — `load_environment_summary` implementation
- `tests/cli/test_evaluation_cli.py` — affected test

**Related tests**:
- `tests/cli/test_evaluation_cli.py::test_evaluate_cli_writes_metrics_log` — fails due to provenance pollution

**Version information**:
- Python: 3.12.12
- Click: pinned in `pyproject.toml`

#### Dependencies
**Blocks**: `test_evaluate_cli_writes_metrics_log` fix  
**Blocked by**: None  
**Related to**: Q004

#### Acceptance Criteria
Research is complete when:
- [ ] Design intent confirmed (stdout vs stderr)
- [ ] All downstream consumers of provenance output identified
- [ ] Clear recommendation: change to `err=True` or keep in stdout and fix tests differently

#### Notes
Interim fix applied (S66): changed to `err=True` and used `CliRunner(mix_stderr=False)` in tests. If research shows stdout was intentional, this fix must be reverted and the test must use a different parsing strategy.

---

### Q002: Root Cause of `TestManageTenantIndices` Failures — Source Bug or Test Mock Issue?

**Category**: Bug Root Cause  
**Priority**: High  
**Impact**: High  
**Created**: 2026-02-22  
**Status**: ⏳ Awaiting Research

#### Context
**Where discovered**: `tests/test_rag_tenant_management.py::TestManageTenantIndices` (9 tests)  
**What happened**: All `TestManageTenantIndices` tests fail with `assert False is True` on `TenantOperationResult.success=False`. Error message: `"Failed to create any indices for tenant 'customer_a'"`. The test mocks `SentenceTransformer` but the underlying FAISS index creation still fails.  
**Current behavior**: `manage_tenant_indices("create", ...)` returns `success=False` even with mocked SentenceTransformer.  
**Expected behavior**: With a properly mocked SentenceTransformer and FAISS, `success=True` should be returned.

#### The Question
Is the failure in `manage_tenant_indices` due to: (a) the mock not being applied to the correct import path, (b) FAISS itself not being installed and the code not gracefully handling that, (c) a file system path issue where the index cannot be persisted, or (d) a genuine logic bug where the creation silently fails?

#### Why This Needs Research
- [ ] Cannot verify without `faiss-cpu` installed — not available in the local sandbox
- [ ] The mock patching path (`@patch("sentence_transformers.SentenceTransformer")`) may differ from the import used inside `manage_tenant_indices`
- [ ] Need to trace the exact code path in `manage_tenant_indices` to find the first point of failure

#### Current Hypothesis
**Your best guess**: FAISS is either not installed or the mock is patching the wrong import path (e.g., the function imports `from rag.indexing import SentenceTransformer` not `sentence_transformers.SentenceTransformer` directly).  
**Confidence level**: Medium  
**Evidence supporting hypothesis**: S65 commit described these as "FAISS index persistence path mismatch with mock SentenceTransformer".

#### Information to Guide Research

**Suggested search queries**:
1. "pytest mock patch wrong import path fix — where to patch not what to patch"
2. "faiss IndexFlatL2 graceful failure when faiss not installed Python"
3. "manage_tenant_indices FAISS mock SentenceTransformer patch path"

**Suggested sources**:
- [ ] Python mocking docs: https://docs.python.org/3/library/unittest.mock.html#where-to-patch
- [ ] FAISS Python docs: https://faiss.ai/
- [ ] Source: `src/rag/tenant_management.py` — trace the import chain for SentenceTransformer

**Related files in codebase**:
- `tests/test_rag_tenant_management.py` — test file with mock setup
- `src/rag/tenant_management.py` (or similar) — `manage_tenant_indices` implementation

**Related tests**:
- `tests/test_rag_tenant_management.py::TestManageTenantIndices::test_create_operation_success`
- (9 total tests in this class)

**Version information**:
- faiss-cpu: not installed locally
- sentence-transformers: not installed locally
- Python: 3.12.12

#### Dependencies
**Blocks**: Removing these from `conftest._PREEXISTING_FAILURES`  
**Blocked by**: faiss-cpu installation  
**Related to**: None

#### Acceptance Criteria
Research is complete when:
- [ ] Exact failure point in `manage_tenant_indices` identified
- [ ] Correct mock patch path confirmed
- [ ] Either source fix applied or confirmed as environment limitation

---

### Q003: Why Does `IncrementalSyncDecider::test_micro_update` Compute 95% Change Ratio for a Punctuation-Only Edit?

**Category**: Bug Root Cause  
**Priority**: Medium  
**Impact**: Medium  
**Created**: 2026-02-22  
**Status**: ⏳ Awaiting Research

#### Context
**Where discovered**: `tests/services/crawler/test_semantic_differ.py::TestIncrementalSyncDecider::test_micro_update`  
**What happened**: A punctuation-only change (e.g., adding a period) is classified as a "major" update (95% change ratio) by `ContentDiffer.diff()`, instead of "micro". The test expects `decision == "micro_update"` but gets a decision indicating major change.  
**Current behavior**: `ContentDiffer.diff(old_text, new_text_with_punctuation)` returns `change_ratio ≈ 0.95`.  
**Expected behavior**: Punctuation-only change should yield `change_ratio < 0.1`, triggering `"micro_update"` decision.

#### The Question
What diff algorithm does `ContentDiffer.diff()` use, and why does it compute ~95% change ratio for a single punctuation character added to a sentence? Is it comparing at the character level (where adding `.` to a 20-char sentence is 1/21 = ~5% change, not 95%), at the token/word level, or is there a normalization bug?

#### Why This Needs Research
- [ ] `ContentDiffer` source code not fully traced — need to identify the exact diff algorithm and normalization
- [ ] `difflib.SequenceMatcher` ratio is computed as `2.0 * M / T` where M=matching chars, T=total chars — a period addition should give high match ratio (low change), not 95% change
- [ ] If the ratio is `1 - SequenceMatcher.ratio()`, then a ratio of 0.95 means 5% match — that would mean the texts are almost completely different, which contradicts adding one character

#### Current Hypothesis
**Your best guess**: `change_ratio` is computed as `1 - similarity_ratio`, and the similarity function somehow computes near-zero similarity for the two texts despite them differing only in punctuation. Possible cause: the diff is comparing tokenized/stemmed forms where punctuation removal makes the texts identical at the normalized level but the raw comparison sees large differences.  
**Confidence level**: Low  
**Evidence supporting hypothesis**: None — pure speculation.

#### Information to Guide Research

**Suggested search queries**:
1. "difflib SequenceMatcher ratio punctuation sensitivity Python"
2. "ContentDiffer change_ratio 1-similarity text comparison unexpected result"
3. "semantic diff token-level vs character-level change ratio normalization"

**Suggested sources**:
- [ ] Python difflib docs: https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.ratio
- [ ] Source: `src/services/crawler/content_diff.py` — `ContentDiffer.diff()` implementation

**Related files in codebase**:
- `src/services/crawler/content_diff.py` — `ContentDiffer` implementation
- `tests/services/crawler/test_semantic_differ.py` — failing test

**Related tests**:
- `tests/services/crawler/test_semantic_differ.py::TestIncrementalSyncDecider::test_micro_update`

**Version information**:
- Python: 3.12.12 (stdlib difflib)

#### Dependencies
**Blocks**: Nothing immediate (catalogued as pre-existing)  
**Blocked by**: None  
**Related to**: None

#### Acceptance Criteria
Research is complete when:
- [ ] Exact `ContentDiffer.diff()` algorithm identified (character-level, token-level, semantic)
- [ ] Root cause of 95% change ratio for punctuation-only edit explained
- [ ] Fix proposed: either algorithm change or test update

---

### Q004: How Should Multi-Output CLI Commands Be Tested When stdout Contains Multiple JSON Objects?

**Category**: API Design/Contract  
**Priority**: Medium  
**Impact**: Medium  
**Created**: 2026-02-22  
**Status**: ⏳ Awaiting Research

#### Context
**Where discovered**: `tests/cli/test_evaluation_cli.py::test_evaluate_cli_writes_metrics_log`  
**What happened**: The `evaluate` CLI command outputs: (1) exception tracebacks from optional-dep failures, (2) the evaluation summary JSON (multi-line, indented), (3) the provenance summary JSON (compact, single-line). When `CliRunner(mix_stderr=True)` is used (default), all three appear in `result.output`. `json.loads(result.output)` fails; the fallback line parser picks the wrong JSON.  
**Current behavior**: Tests fail with `KeyError: 'metrics_path'` because the provenance JSON is picked up instead of the evaluation summary.  
**Expected behavior**: Tests reliably parse the evaluation summary from CLI output.

#### The Question
What is the canonical pattern for testing Click CLI commands that: (a) emit multiple JSON objects to stdout, (b) have logging output that may bleed into stdout via `mix_stderr=True`, and (c) need the test to reliably identify and parse a specific JSON object? Is `CliRunner(mix_stderr=False)` sufficient, or should the CLI architecture change?

#### Why This Needs Research
- [ ] Click documentation on `mix_stderr` does not clearly address multi-JSON-object output testing
- [ ] Industry patterns for this scenario are unclear
- [ ] The fix of `mix_stderr=False` + `err=True` for provenance may not cover all edge cases (e.g., logging handlers writing to stdout)

#### Current Hypothesis
**Your best guess**: `CliRunner(mix_stderr=False)` + move provenance to `err=True` is the correct fix. But there may be other locations where logging goes to stdout.  
**Confidence level**: Medium  
**Evidence supporting hypothesis**: Click docs state `mix_stderr=False` gives separate `result.stderr` and clean `result.output`.

#### Information to Guide Research

**Suggested search queries**:
1. "click CliRunner mix_stderr false test multiple json output"
2. "pytest click CLI test parse specific json from multiple json objects stdout"
3. "click echo err=True diagnostic output separation best practice"

**Suggested sources**:
- [ ] Click testing docs: https://click.palletsprojects.com/en/stable/testing/
- [ ] Click source: `mix_stderr` parameter behavior

**Related files in codebase**:
- `src/codex_ml/cli/codex_cli.py` — all CLI commands using `_emit_provenance_summary`
- `tests/cli/test_evaluation_cli.py` — affected test

**Related tests**:
- `tests/cli/test_evaluation_cli.py::test_evaluate_cli_writes_metrics_log`

**Version information**:
- Click: pinned in `pyproject.toml`

#### Dependencies
**Blocks**: Nothing critical  
**Blocked by**: Q001 (provenance stdout vs stderr)  
**Related to**: Q001

#### Acceptance Criteria
Research is complete when:
- [ ] Canonical Click pattern for multi-output JSON testing documented
- [ ] Confirmation that `mix_stderr=False` + `err=True` is correct and complete fix

---

### Q005: What Environment Flags Cause `audit_runner.py` to Produce Full vs. Minimal Output?

**Category**: Compatibility/Version Issues  
**Priority**: Medium  
**Impact**: Medium  
**Created**: 2026-02-22  
**Status**: ⏳ Awaiting Research

#### Context
**Where discovered**: `tests/validation/test_audit_pipeline.py` (3 tests)  
**What happened**: In CI, `audit_runner.py run` exits with code 0 but writes a minimal `audit_run_manifest.json` containing only `{"stage": "S7", "timestamp": "...", "warnings": []}` — missing `version`, `repo_root_sha`, `artifacts`, `weights`, `template_hash`. The test has a guard `if result.returncode != 0: pytest.skip(...)` but the returncode IS 0, so the test proceeds to assert on the missing fields.  
**Current behavior**: Subprocess succeeds with minimal output; test fails asserting on `version` field.  
**Expected behavior**: Either (a) subprocess produces full output including all required fields, or (b) test has a content-based skip guard.

#### The Question
What environment dependencies does `audit_runner.py` require to produce a full manifest (with `version`, `artifacts`, `weights`, etc.) vs. the minimal `{"stage": "S7", ...}` output? Are there missing dependencies (e.g., `audit_artifacts/` not pre-populated, specific Python packages), environment variables, or CLI arguments needed for full output?

#### Why This Needs Research
- [ ] `audit_runner.py` code not fully traced — need to identify conditions under which it produces minimal output
- [ ] Cannot reproduce CI environment locally (different dependency set)
- [ ] Need to understand if `audit_artifacts/` directory must be pre-populated

#### Current Hypothesis
**Your best guess**: `audit_runner.py` requires `audit_artifacts/` to exist with pre-populated capability data, OR requires specific Python packages (e.g., `pydantic`, `great_expectations`) that are not installed in the minimal CI environment.  
**Confidence level**: Low  
**Evidence supporting hypothesis**: The manifest stage `"S7"` suggests it ran but completed early without full artifacts.

#### Information to Guide Research

**Suggested search queries**:
1. "audit_runner.py stage S7 minimal output environment dependencies"
2. "scripts/space_traversal/audit_runner.py required dependencies full manifest"
3. "CODEX_CI_FULL environment variable audit pipeline"

**Suggested sources**:
- [ ] Source: `scripts/space_traversal/audit_runner.py` — trace what produces the manifest
- [ ] CI workflow: `.github/workflows/*.yml` — check what's installed before tests run
- [ ] Manifest schema: search for `"version"` and `"template_hash"` in `audit_runner.py`

**Related files in codebase**:
- `scripts/space_traversal/audit_runner.py` — audit runner implementation
- `tests/validation/test_audit_pipeline.py` — affected tests
- `audit_run_manifest.json` — generated file (missing fields in CI)

**Related tests**:
- `tests/validation/test_audit_pipeline.py::test_manifest_has_required_fields`
- `tests/validation/test_audit_pipeline.py::test_structural_integrity_detector_present`
- `tests/validation/test_audit_pipeline.py::test_capabilities_scored_structure`

**Version information**:
- Python: 3.12.12

#### Dependencies
**Blocks**: Full audit pipeline test coverage  
**Blocked by**: None  
**Related to**: DRQ-007 (Integration tests assuming full env output)

#### Acceptance Criteria
Research is complete when:
- [ ] Dependencies for full audit output identified
- [ ] Environment variable or pre-condition documented
- [ ] Either CI workflow updated to provide full env OR tests updated with content-based skip guards


---

## S67 New Questions (2026-02-22)

---

### Q006: Why Does Pytest String-Path Monkeypatch Fail on Certain Modules in CI?

**Category**: Test Infrastructure / Pytest Internals  
**Priority**: High  
**Impact**: High  
**Created**: 2026-02-22 (S67)  
**Status**: ⏳ Awaiting Research — **Interim Fix Applied**: object-based patching

#### Context
**Where discovered**: `tests/tracking/test_tracking_writers_offline.py:71`, `tests/test_model_registry_helpers.py:90`, `tests/config/test_deprecation.py:65`, `tests/test_fetch_messages.py:181`  
**What happened**: `monkeypatch.setattr("codex_ml.tracking.writers.datetime", ...)` fails in CI with `AttributeError: 'module' object at codex_ml.tracking has no attribute 'tracking'`. The string `codex_ml.tracking` is named in the error, but the module being accessed was `codex_ml.tracking.writers`. The "doubled" attribute name pattern (`tracking.tracking`) implies pytest's import-path resolution retried with a shorter prefix and then tried to traverse a repeated component.  
**Local repro**: NOT reproducible locally with Python 3.12 + pytest installed.  
**Interim fix**: Changed to object-based: `import codex_ml.tracking.writers as _m; monkeypatch.setattr(_m, "datetime", ...)`.

#### The Question
What specific combination of (pytest version, Python version, test execution order, sys.modules state) triggers this failure? Does pytest 8.x change the `derive_importpath` resolution algorithm for string-path `setattr`? Can we reproduce this consistently?

#### Why This Needs Research
- [ ] Cannot reproduce locally — CI-environment specific
- [ ] Affects 9+ tests across 4 test files
- [ ] Root cause unknown — might be test-order pollution or pytest version regression

---

### Q007: OptimizedVectorStore `ResponseCache` Does Not Persist Hits

**Category**: Bug Root Cause  
**Priority**: Medium  
**Impact**: Medium  
**Created**: 2026-02-22 (S67)  
**Status**: ⏳ Awaiting Research

#### Context
**Where discovered**: `tests/retrieval/test_optimizations.py::TestOptimizedVectorStore::test_search_with_cache`  
**What happened**: After two calls to `optimized.search(query, k=5)`, `mock_store.search.call_count == 2` (expected 1 on cache hit). And `len(optimized.cache) == 0` after one search call (cache never populated).  
**Source file**: `src/codex/retrieval/optimizations.py`

#### The Question
Does `OptimizedVectorStore.search()` actually call `self.cache.set(key, results)` after fetching from the underlying store? Does `ResponseCache.__len__` correctly reflect the number of cached entries? Is the cache key generation deterministic for identical numpy arrays?

---

---

### DRQ-S70-001: `test_property_based.py` Fails with `ImportError: Optional dependency 'chat' is not installed`

**Category**: Test Infrastructure / Import Chain  
**Priority**: High  
**Impact**: High — blocks 16 tests in quick suite  
**Created**: 2026-02-23 (S70)  
**Status**: 🔴 OPEN — root cause unresolved  
**CI Run**: `22291570163` (sha `8eab1b2`, branch `copilot/sub-pr-3336-again`)

#### Context
**Where discovered**: `tests/agents/test_property_based.py` — 16 failures in validation (quick) suite  
**What happened**: Pure mathematical/property-based tests (e.g., `test_energy_always_non_negative`,
`test_set_properties`) fail at collection or first execution with
`ImportError: Optional dependency 'chat' is not installed; install it to enable this functionality.`  
**Error origin**: `configs/sitecustomize.py:59` — the `_missing_attr` function of the `chat` stub module  
**Imports in failing file**:
```python
from agents.agent_memory import MemoryEntry
from agents.physics_orchestrator import DecisionState
from agents.quantum_game_theory import StrategyState
```
None of these modules import `chat` at the top level.

#### Research Questions
1. Which code path between `test_property_based.py` import and Hypothesis test execution accesses an attribute of the `chat` stub?
2. Does `configs/sitecustomize.py` run during pytest startup? If yes, which `.pth` / `PYTHONPATH` mechanism triggers it?
3. Does `agents` resolve to `src/agents/` (stub-using orchestrator) or root `agents/` in CI? If `src/agents/`, what does `src/agents/orchestrator.py` import that touches `chat`?
4. Does `_install_optional_stub("chat")` at `sitecustomize.py:88` interfere with `from codex.chat import ChatSession` in other conftest fixtures? Could it poison a session-scoped fixture that all tests in the `agents/` dir inherit?
5. Does Hypothesis's `@given` decorator lazy-import anything that triggers `chat` attribute access?

#### Evidence Log
- `configs/sitecustomize.py:88` — `_install_optional_stub("chat")` installs a stub with `__getattr__` that raises `ImportError`
- `src/agents/orchestrator.py:24` — `from src.config.openai_client import CodexOpenAIClient` → likely imports something via the `chat` path
- Hypothesis `FlakyFailure` trace: `INTERESTING from ImportError at configs/sitecustomize.py:59`

#### Hypothesis
`src/agents/orchestrator.py` imports from `src.config.openai_client` which imports `chat` (the standalone module stubbed in sitecustomize). When pytest collects `tests/agents/`, it loads all conftest fixtures, one of which imports from `src/agents/` (resolves to the stub-touching path), touching `chat` stub's `__getattr__`.

#### Suggested Next Steps
- [ ] Add `print(sys.modules.get('agents'))` debug fixture to `tests/agents/conftest.py` to confirm which `agents` package is loaded
- [ ] Check `src/config/openai_client.py` for `import chat` or `from chat import`
- [ ] Add `pytest.importorskip("chat")` or `@pytest.mark.skipif` to the test file as a temporary bypass
- [ ] Consider moving pure math property tests out of `tests/agents/` to avoid the conftest fixture inheritance

---

### DRQ-S70-002: `test_data_splits.py` `AttributeError: module 'torch' has no attribute 'utils'`

**Category**: Test Infrastructure / Stub Interference  
**Priority**: High  
**Impact**: High — 4 tests blocked in quick suite  
**Created**: 2026-02-23 (S70)  
**Status**: 🔴 OPEN  
**CI Run**: `22291570163`

#### Context
**Where discovered**: `tests/unit/data/test_data_splits.py` — 4 failures  
**What happened**:
```
AttributeError: module 'torch' has no attribute 'utils'
AttributeError: module 'torch' has no attribute 'ones'
```
Tests call `torch.utils.data.TensorDataset(...)` and `torch.ones(...)` after
`torch = pytest.importorskip("torch")` — which should return the real torch (CI installs it).

#### Research Questions
1. Is the `torch` stub from `configs/sitecustomize.py` (only has `float32/float16/bfloat16` attrs) being returned by `pytest.importorskip("torch")` instead of real torch?
2. Under what condition does `_install_optional_stub("torch")` install the stub even when `torch` IS installed? (e.g., if torch initialization fails with `OSError: libgomp.so not found`)
3. Does PyTorch 2.6.x on the GitHub Actions `ubuntu-latest` runner require explicit `import torch.utils.data` before `torch.utils` is accessible as a module attribute?
4. Is `configs/sitecustomize.py` executed via `.pth` file insertion, and does it execute BEFORE torch is fully initialized in the CI environment?

#### Evidence Log
- `configs/sitecustomize.py:69–76` — `_install_optional_stub("torch", attrs={...})` only provides 3 float-type attrs
- Test pattern: `torch = pytest.importorskip("torch"); torch.utils.data.TensorDataset(...)` 
- CI torch installed via: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu`

#### Hypothesis
`sitecustomize.py` executes during `pip install -e .` (or early Python startup). At that point, torch's C-extension may fail to initialize (no CUDA, missing libgomp on slim CI runner), causing `__import__("torch")` to raise `OSError`. The stub is then registered. When the real `torch` wheel is later pip-installed, it is NOT re-imported into the running process (pip doesn't update `sys.modules`). The next pytest session starts fresh — BUT if `sitecustomize.py` is loaded via a `.pth` file that runs early in the new process, and torch STILL fails to initialize before `.pth` execution completes, the stub gets registered again.

#### Suggested Next Steps
- [ ] Add `_install_optional_stub` debug logging: print which module triggered the fallback path
- [ ] Test: `python -c "import torch; print(torch.__version__); import torch.utils.data; print('ok')"` in CI step before pytest
- [ ] Replace `torch.utils.data.TensorDataset(...)` in tests with explicit `import torch.utils.data; torch.utils.data.TensorDataset(...)` as interim fix
- [ ] Check if `.pth` files in site-packages trigger `sitecustomize.py` re-execution

---

### DRQ-S70-003: `codex.training` Missing `load_training_cfg` and `run_hf_trainer` Public API

**Category**: Missing Implementation  
**Priority**: Medium  
**Impact**: Medium — 3 slow-suite tests blocked  
**Created**: 2026-02-23 (S70)  
**Status**: 🟡 PARTIAL FIX APPLIED (stub added)  
**Tracked tests**: `tests/space_traversal/test_peft_comprehensive/test_functional_training_main.py`

#### Context
`tests/space_traversal/test_peft_comprehensive/test_functional_training_main.py` patches
`codex.training.load_training_cfg` and `codex.training.run_hf_trainer` via `monkeypatch.setattr`.
Neither function exists in `src/codex/training.py`. Additionally `codex.training.main()` does not
accept a `argv` parameter — the test calls `ft.main(["--output-dir", ..., "--engine", "hf"])`.

#### Research Questions
1. Was `load_training_cfg` / `run_hf_trainer` originally in `codex.training` and later removed, or were these tests written ahead of implementation?
2. What should `load_training_cfg(**kwargs)` return? An `OmegaConf` DictConfig? A plain dict? Does it read from a YAML file path or from CLI kwargs?
3. What is the intended behavior of `run_hf_trainer(texts, output_dir, **kwargs)`? Is it a wrapper around `run_functional_training`? Around `codex_ml.train_loop`?
4. Should `main()` in `codex.training` accept `argv`? Or should the test call a different entry point?

#### Interim Fix Applied (S70)
- Added `load_training_cfg` stub returning `OmegaConf.create({})` when OmegaConf available  
- Added `run_hf_trainer` stub delegating to `run_functional_training`  
- Updated `main(argv=None)` to accept args list and parse `--engine`/`--output-dir`  
- See commit `{TO_BE_FILLED}` for exact changes

---

### DRQ-S70-004: `datetime.now()` TZ-naive Usage in 47 Source Files

**Category**: Code Quality / Timezone Safety  
**Priority**: Medium  
**Impact**: Medium — affects timestamp correctness across the codebase  
**Created**: 2026-02-23 (S70)  
**Status**: 🟡 PARTIAL FIX APPLIED  
**Files**: 47 occurrences in `src/` excluding `context_management/`

#### Context
TD-001 (completed S61–S62) fixed `datetime.now()` to `datetime.now(timezone.utc)` in
`src/context_management/`. TD-001 Extension targets the remaining 47 occurrences in:
- `src/bridge_types.py` (9 occurrences)
- `src/cognitive_brain/experiments/exp6_validation.py` (4)
- `src/cognitive_brain/quantum/ghz_states.py` (3)
- `src/cognitive_brain/quantum/multi_agent_coordinator.py` (3)
- `src/codex/cli.py`, `src/codex/rag/analytics/dashboard.py`, `src/codex/logging/error_handler.py`
- `src/codex_ml/events/base.py`, `src/codex_ml/training/curriculum.py`, etc.

#### Research Questions
1. Do any of these naive datetimes interact with external APIs (MLflow, W&B, telemetry) that expect UTC ISO strings?
2. Does `src/codex_ml/tokenization/cache.py` use naive datetimes for TTL comparisons? If so, mixing naive and aware datetimes will raise `TypeError` in Python 3.12.
3. Is `datetime.now()` in `src/cognitive_brain/experiments/` intentionally local-time for human-readable logging?

#### Suggested Fix Pattern
```python
# Before
from datetime import datetime
ts = datetime.now().isoformat()

# After
from datetime import datetime, timezone
ts = datetime.now(timezone.utc).isoformat()
```

---

### DRQ-S70-005: Quick-Suite `test_property_based.py` `hypothesis.errors.FlakyFailure`

**Category**: Test Flakiness / Hypothesis  
**Priority**: Medium  
**Impact**: Medium — flaky failures mask real failures in CI  
**Created**: 2026-02-23 (S70)  
**Status**: 🔴 OPEN  

#### Context
Several Hypothesis tests show `FlakyFailure: Inconsistent results from replaying a test case!`  
This means Hypothesis found a failing example, but when it replayed the exact same inputs, it got a different result — indicating **non-determinism** in the test.

The inconsistency is between:
- `INTERESTING from ImportError at configs/sitecustomize.py:59` (first run)
- `INTERESTING from FlakyStrategyDefinition` (replay)

This suggests the `chat` ImportError (DRQ-S70-001) is non-deterministic — sometimes the stub is hit, sometimes it isn't.

#### Research Questions
1. Is there a Hypothesis database (`hypothesis/.hypothesis/`) being reused across test runs, causing replay of previously-found-failing examples that may no longer be reproducible?
2. Does the `chat` import path depend on Python module import ordering which varies by test execution order?
3. Should `@settings(suppress_health_check=[HealthCheck.too_slow])` be added to stabilize flaky Hypothesis tests?

---

## Summary

| ID   | Title                                              | Category        | Priority | Impact  | Status             |
|------|----------------------------------------------------|-----------------|----------|---------|--------------------|
| Q001 | `_emit_provenance_summary` stdout vs stderr        | API Design      | High     | High    | ⏳ Awaiting Research |
| Q002 | `TestManageTenantIndices` root cause               | Bug Root Cause  | High     | High    | ⏳ Awaiting Research |
| Q003 | `IncrementalSyncDecider` 95% change ratio          | Bug Root Cause  | Medium   | Medium  | ⏳ Awaiting Research |
| Q004 | Multi-output CLI JSON testing pattern              | API Design      | Medium   | Medium  | ⏳ Awaiting Research |
| Q005 | `audit_runner.py` full vs minimal output env flags | Compatibility   | Medium   | Medium  | ⏳ Awaiting Research |
| Q006 | Pytest string-path monkeypatch CI failure          | Test Infra      | High     | High    | ⏳ Awaiting Research (S67: interim fix) |
| Q007 | OptimizedVectorStore cache never persists          | Bug Root Cause  | Medium   | Medium  | ⏳ Awaiting Research |
| DRQ-S70-001 | `test_property_based.py` `chat` ImportError stub interference | Test Infra | High | High | ✅ RESOLVED (S71: `_missing_attr` raises `AttributeError` for dunders) |
| DRQ-S70-002 | `test_data_splits.py` torch stub vs real torch | Test Infra | High | High | ✅ RESOLVED (S71: `torch/__init__.py` `__getattr__` + stub factory funcs) |
| DRQ-S70-003 | `codex.training` missing `load_training_cfg`/`run_hf_trainer` | Missing Impl | Medium | Medium | ✅ RESOLVED (S70) |
| DRQ-S70-004 | `datetime.now()` TZ-naive in 47 src/ files | Code Quality | Medium | Medium | 🟡 Partial Fix (3/47 files in S70) |
| DRQ-S70-005 | Hypothesis FlakyFailure from non-deterministic import order | Test Flakiness | Medium | Medium | ✅ RESOLVED (S71: same fix as DRQ-S70-001) |
