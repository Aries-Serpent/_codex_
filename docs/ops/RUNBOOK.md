# docs/ops/RUNBOOK.md — Codex Run as a Dynamical System

> Treat a full Codex run as a hybrid dynamical system: continuous work (phase operators), discrete edits (patches), filtered by quality-gate projectors. This document gives you the mental model, the commands to run, and the minimal troubleshooting you’ll need.

## Table of contents

1. Quick start
2. The model (state, phases, gates, patches)
3. Quality gates → exact commands
4. Patch workflow (small, atomic diffs)
5. Module notes (Tokenizer, Ingestion, MLflow)
6. Error capture format
7. Troubleshooting & references

---

## 1) Quick start

```bash
# lint + format (Python)
ruff check src tests && ruff format --check .     # pass=Π_lint ✓   [oai_citation:0‡Astral Docs](https://docs.astral.sh/ruff/?utm_source=chatgpt.com)

# tests + coverage gate
pytest -q --cov --cov-fail-under=70               # pass=Π_tests ⋂ Π_cov ✓   [oai_citation:1‡pytest-cov](https://pytest-cov.readthedocs.io/en/latest/config.html?utm_source=chatgpt.com)

# (optional) type checks if configured
pyright                                            # pass=Π_types ✓

# one-line smoke (if Makefile present)
make lint && make test
```

---

## 2) The model (state, phases, gates, patches)

Let the repository be a density operator $\rho(t)$ over an abstract “repo” space. The run evolves under phases (Hamiltonians $H_p$) and is interrupted by patch events (unified diffs), with quality gates acting as projectors.

$$
\boxed{
\begin{aligned}
\dot \rho(t)&=\mathcal L(t)[\rho]
=-\tfrac{i}{\hbar}[H(t),\rho]+\sum_k \gamma_k\!\left(L_k \rho L_k^\dagger-\tfrac12\{L_k^\dagger L_k,\rho\}\right),\\[2pt]
H(t)&=\sum_{p\in\{\mathrm{P1..P6}\}} u_p(t)\,H_p,\\[4pt]
\rho(t)&=\!\!\left(\prod_{\tau_m<t}\mathcal P_{\Delta_m}\circ \mathcal P_G\circ
\mathcal T e^{\int_{\tau_{m-1}}^{\tau_m}\mathcal L(u)\,du}\right)\![\rho_0].
\end{aligned}}
$$

* **Phase operators** $H_p$:
  P1 prep · P2 search · P3 build · P4 prune · P5 error-log · P6 final.
* **Quality gate projector** $\mathcal P_G$: filter onto passing subspace.
* **Patch superoperator** $\mathcal P_{\Delta}$: apply a unified diff (atomic edit).

---

## 3) Quality gates → exact commands

| Gate (projector)                  | Definition (what must pass) | Minimal local command                                                        |
| --------------------------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| $\Pi_{\text{lint}}$               | Code style & lint pass      | `ruff check src tests && ruff format --check .` (Ruff provides both lint and a fast formatter).                    |
| $\Pi_{\text{tests}}$              | All tests green             | `pytest -q` (or with coverage flags below).                                                                        |
| $\Pi_{\text{cov}}$                | Coverage ≥ threshold        | `pytest --cov --cov-fail-under=70` (threshold configurable via CLI or coverage config).                            |
| $\Pi_{\text{types}}$ *(optional)* | Type checks pass            | `pyright` (if configured in the repo).                                                                             |

**Strict vs soft gating.** For release builds, use strict pass/fail (treat the projector as Lüders post-selection). For iterative dev, allow “soft” gating (record failures, continue, and open a ticket).

---

## 4) Patch workflow (small, atomic diffs)

1. **Branch & scope:** create a branch per task; keep diffs small and thematic.
2. **Edit:** implement in small steps.
3. **Gate:** run the gate commands (above).
4. **Patch:** commit when all active gates pass.
5. **Repeat:** prefer many small patches over one giant change.

Tip: for file canonicalization (merging suffixed backups into a single canonical file), prefer `git mv -f` (history-preserving) and verify with a must-exist/must-not-exist checklist before finalization.

---

## 5) Module notes (Tokenizer, Ingestion, MLflow)

### 5.1 Tokenizer adapter (`src/codex_ml/interfaces/tokenizer.py`)

* Wrap **Hugging Face** `AutoTokenizer.from_pretrained(...)`.
* Expose helpers for `padding`, `truncation`, and `max_length`, including batch encode/decode; these are first-class tokenizer controls in Transformers.

**Smoke test (tiny public model):**

```python
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("bert-base-uncased")
out = tok(["hello world"], padding="max_length", truncation=True, max_length=8, return_tensors="pt")
assert out["input_ids"].shape[-1] == 8
```

(Transformers docs cover padding/truncation semantics and batch behaviors.)

### 5.2 Ingestion utils (`src/ingestion/encoding_detect.py`, `io_text.py`, `utils.py`)

* `encoding="auto"`: try **charset-normalizer** when available; otherwise fall back to a default (e.g., UTF-8). API supports detecting from a **PathLike** and returning best-guess encoding.
* Return `(text, used_encoding)` and normalize newlines / strip BOM where relevant.

**CLI sanity check (if installed):**

```bash
python -m charset_normalizer normalizer somefile.txt   # has a built-in CLI
```

(Charset-normalizer is a modern alternative to chardet.)

### 5.3 MLflow utils (`src/codex_ml/tracking/mlflow_utils.py`)

* Provide a `MlflowConfig` that can enable or disable **system metrics** logging.
* When the code path sets `log_system_metrics=None`, MLflow defers to the environment variable **`MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING`** (True/False). Ensure the env var name matches MLflow’s docs.

**Example:**

```bash
export MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING=true
python your_train.py   # MLflow may auto-enable system metrics per docs
```

---

## 6) Error capture format

On any failure (setup, import/build, tests), append to `Codex_Questions.md` and include in CI/logs:

```
Question for ChatGPT @codex {{timestamp}}:
While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error:
[ERROR_MESSAGE]
Context: [BRIEF_CONTEXT]
What are the possible causes, and how can this be resolved while preserving intended functionality?
```

---

## 7) Troubleshooting & references

* **Ruff (linter + formatter).** Use `ruff check` and `ruff format`—fast and widely adopted.
* **Coverage gates.** `pytest-cov` supports `--cov` and `--cov-fail-under=MIN` for threshold enforcement (can also be configured in coverage settings).
* **Transformers tokenizers.** Tokenizer fundamentals and padding/truncation controls appear in the official docs.
* **charset-normalizer.** Detect encodings from bytes, fp, or PathLike; expose “best” match.
* **MLflow system metrics.** Controlled via API flag or the env var `MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING`.

---

### One-shot checklist

* [ ] Run **lint/format**: `ruff check … && ruff format --check .` (Π_lint)
* [ ] Run **tests**: `pytest -q` (Π_tests)
* [ ] Enforce **coverage**: `pytest --cov --cov-fail-under=70` (Π_cov)
* [ ] (Optional) **types**: `pyright` (Π_types)
* [ ] Apply **small patch**, re-gate, repeat.
* [ ] If errors occur, log via the **Error capture format** above.

---

> Keep patches tiny, gates clear, and references close. If you need, I can also drop this file into a `docs/` folder and add a `make runbook` target that prints the gate status after each run.
