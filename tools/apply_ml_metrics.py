#!/usr/bin/env python3
"""
Apply ML metrics & training integration (Codex-local only).

Delivers:
- src/codex_ml/eval/metrics.py with perplexity, token_accuracy, optional BLEU/ROUGE,
  and code metrics (exact match, unit-test hook).
- src/codex_ml/train_loop.py with a toy trainer that evaluates after each epoch and
  on the best checkpoint; persists artifacts/metrics/metrics.json with timestamps & config hash.
- tests/test_metrics.py covering core metrics.
- README.md minimal reference cleanup (best-effort).
- All errors logged as ChatGPT-5 research questions in .codex/errors.ndjson.

IMPORTANT:
- DO NOT ACTIVATE ANY GitHub Actions Online files.
- All lint/tests/validation run INSIDE the Codex environment.

"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CODEX = REPO / ".codex"
ART = REPO / "artifacts" / "metrics"
CODEX.mkdir(parents=True, exist_ok=True)
ART.mkdir(parents=True, exist_ok=True)

CHANGE_LOG = CODEX / "change_log.md"
ERRORS = CODEX / "errors.ndjson"
RESULTS = CODEX / "results.md"


def ts() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def append(path: Path, txt: str) -> None:
    path.write_text(
        path.read_text(encoding="utf-8") + txt, encoding="utf-8"
    ) if path.exists() else path.write_text(txt, encoding="utf-8")


def log_change(title: str, path: Path, rationale: str, content_preview: str) -> None:
    append(
        CHANGE_LOG,
        textwrap.dedent(f"""
    ## {ts()} — {path.relative_to(REPO)}
    - **Action:** {title}
    - **Rationale:** {rationale}
    ```text
    {content_preview[:4000]}
    ```
    """).lstrip(),
    )


def q5(step: str, err: str, ctx: str) -> None:
    prompt = textwrap.dedent(f"""\
    Question for ChatGPT-5 {ts()}:
    While performing [{step}], encountered the following error:
    {err}
    Context: {ctx}
    What are the possible causes, and how can this be resolved while preserving intended functionality?
    """)
    append(
        ERRORS,
        json.dumps({"ts": ts(), "step": step, "error": err, "context": ctx}) + "\n",
    )
    sys.stderr.write(prompt + "\n")


def config_hash() -> str:
    # Best-effort: hash common config files or empty dict
    candidates = ["config.yaml", "config.yml", "config.json", "pyproject.toml"]
    h = hashlib.sha256()
    any_found = False
    for name in candidates:
        p = REPO / name
        if p.exists():
            any_found = True
            h.update(p.read_bytes())
    if not any_found:
        h.update(json.dumps({"default": True}, sort_keys=True).encode())
    return h.hexdigest()


# ----- File contents -----
METRICS_PATH = REPO / "src" / "codex_ml" / "eval" / "metrics.py"
METRICS_SENT = "# BEGIN: CODEX_METRICS"

METRICS_CONTENT = f"""{METRICS_SENT}
\"\"\"General-purpose and code-specific evaluation metrics.

- perplexity: supports logits -> NLL or direct NLL arrays
- token_accuracy: Ignores positions matching ignore_index
- Optional BLEU/ROUGE if dependencies present
- exact_match_strict: normalized string equivalence
- run_unit_tests: hook executing pytest against provided tests directory
\"\"\"

from __future__ import annotations
import math
import tempfile
import subprocess
from pathlib import Path
from typing import Iterable, List, Tuple, Optional, Dict

try:
    import numpy as np
except Exception:
    np = None  # graceful degradation

def _softmax_row(logits: List[float]) -> List[float]:
    m = max(logits)
    exps = [math.exp(x - m) for x in logits]
    s = sum(exps)
    return [e / s for e in exps]

def perplexity(logits_or_nll: Iterable, targets: Iterable[int], from_logits: bool = True, ignore_index: int = -100) -> float:
    \"\"\"Compute perplexity over a batch.
    If from_logits=True, logits_or_nll is shape [B, V] per token (flattened or per-step);
    otherwise it's a list of negative log-likelihoods (NLLs) per token.
    \"\"\"
    nll_vals: List[float] = []
    if from_logits:
        if np is not None:
            arr = np.asarray(list(logits_or_nll), dtype=float)
            tgt = np.asarray(list(targets), dtype=int)
            assert arr.ndim == 2 and arr.shape[0] == tgt.shape[0], "logits shape [N,V] and targets [N]"
            # stable softmax log prob
            maxes = np.max(arr, axis=1, keepdims=True)
            exps = np.exp(arr - maxes)
            probs = exps / np.sum(exps, axis=1, keepdims=True)
            for i, y in enumerate(tgt):
                if int(y) == ignore_index:
                    continue
                p = float(probs[i, int(y)])
                nll_vals.append(-math.log(max(p, 1e-12)))
        else:
            # fallback pure-python path; expects iterable of (logits_row, y)
            for (logits_row, y) in logits_or_nll:
                if y == ignore_index:
                    continue
                probs = _softmax_row(list(logits_row))
                p = probs[int(y)]
                nll_vals.append(-math.log(max(p, 1e-12)))
    else:
        for nll, y in zip(logits_or_nll, targets):
            if int(y) == ignore_index:
                continue
            nll_vals.append(float(nll))
    if not nll_vals:
        return float("inf")
    avg_nll = sum(nll_vals) / len(nll_vals)
    return float(math.exp(avg_nll))

def token_accuracy(pred_ids: Iterable[int], target_ids: Iterable[int], ignore_index: int = -100) -> float:
    correct = 0
    total = 0
    for p, t in zip(pred_ids, target_ids):
        if int(t) == ignore_index:
            continue
        total += 1
        correct += int(p) == int(t)
    return float(correct / total) if total else 0.0

def exact_match_strict(pred: str, ref: str) -> float:
    norm = lambda s: " ".join(str(s).strip().split())
    return 1.0 if norm(pred) == norm(ref) else 0.0

def bleu(candidates: List[str], references: List[str], lowercase: bool = True) -> Optional[float]:
    try:
        import nltk
        from nltk.translate.bleu_score import corpus_bleu, SmoothingFunction
    except Exception:
        return None
    if lowercase:
        candidates = [c.lower() for c in candidates]
        references = [r.lower() for r in references]
    # NLTK corpus_bleu expects list of tokens
    cand_tok = [c.split() for c in candidates]
    ref_tok = [[r.split()] for r in references]
    smoothie = SmoothingFunction().method3
    try:
        score = corpus_bleu(ref_tok, cand_tok, smoothing_function=smoothie)
        return float(score)
    except Exception:
        return None

def rouge_l(candidates: List[str], references: List[str], lowercase: bool = True) -> Optional[Dict[str, float]]:
    try:
        from rouge_score import rouge_scorer
    except Exception:
        return None
    if lowercase:
        candidates = [c.lower() for c in candidates]
        references = [r.lower() for r in references]
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = [scorer.score(r, c)['rougeL'].fmeasure for c, r in zip(candidates, references)]
    if not scores:
        return None
    return {{"rougeL_f": float(sum(scores)/len(scores))}}

def run_unit_tests(code_str: str, tests_dir: str) -> Dict[str, int]:
    \"\"\"Write code_str to a temp module and run pytest against tests_dir.
    Returns a summary dict: {{passed, failed, errors}}.
    \"\"\"
    tmpdir = Path(tempfile.mkdtemp())
    mod = tmpdir / "candidate.py"
    mod.write_text(code_str, encoding="utf-8")
    # Run pytest
    proc = subprocess.run(["pytest", "-q", tests_dir], cwd=str(tmpdir), capture_output=True, text=True)
    out = proc.stdout + proc.stderr
    # heuristic parse
    passed = len(re.findall(r"\\b(\\d+) passed\\b", out)) and int(re.findall(r"\\b(\\d+) passed\\b", out)[-1]) or 0
    failed = len(re.findall(r"\\b(\\d+) failed\\b", out)) and int(re.findall(r"\\b(\\d+) failed\\b", out)[-1]) or 0
    errors = len(re.findall(r"\\b(\\d+) error\\b", out)) and int(re.findall(r"\\b(\\d+) error\\b", out)[-1]) or 0
    return {{"passed": passed, "failed": failed, "errors": errors}}
# END: CODEX_METRICS
"""

TRAIN_PATH = REPO / "src" / "codex_ml" / "train_loop.py"
TRAIN_SENT = "# BEGIN: CODEX_TRAIN_LOOP"

TRAIN_CONTENT = f"""{TRAIN_SENT}
\"\"\"Toy training loop with evaluation hooks and metrics persistence.

Usage:
    python -m codex_ml.train_loop --epochs 3

This is a best-effort integration: if your project has an existing trainer,
adapt the callback pattern below and invoke `record_metrics(...)`.
\"\"\"
from __future__ import annotations
import argparse, json, random
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from codex_ml.eval.metrics import token_accuracy, perplexity, bleu, rouge_l

ART_DIR = Path("artifacts/metrics")
ART_DIR.mkdir(parents=True, exist_ok=True)

def _ts() -> str:
    from datetime import datetime
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def record_metrics(phase: str, epoch: int, metrics: Dict[str, Any], cfg_hash: str, notes: str = "toy-eval") -> None:
    payload = {{
        "ts": _ts(),
        "phase": phase,
        "epoch": epoch,
        "metrics": metrics,
        "config_hash": cfg_hash,
        "notes": notes,
    }}
    out = ART_DIR / "metrics.json"
    prev: List[Dict[str, Any]] = []
    if out.exists():
        try:
            prev = json.loads(out.read_text(encoding="utf-8"))
            if not isinstance(prev, list):
                prev = []
        except Exception:
            prev = []
    prev.append(payload)
    out.write_text(json.dumps(prev, indent=2), encoding="utf-8")

def demo_epoch(epoch: int) -> Dict[str, float]:
    # Create a toy prediction/target scenario where accuracy and ppl can improve
    random.seed(42 + epoch)
    targets = [random.randint(0, 4) for _ in range(100)]
    preds = [t if random.random() < (0.4 + 0.15 * epoch) else random.randint(0, 4) for t in targets]
    acc = token_accuracy(preds, targets)
    # Build logits such that correct class probability improves per epoch
    logits = []
    for t in targets:
        base = [0.0]*5
        base[t] = 1.0 + 0.3*epoch
        logits.append(base)
    ppl = perplexity(logits, targets, from_logits=True)
    return {{"acc": acc, "ppl": ppl}}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=3)
    args = ap.parse_args()
    cfg_hash = "{config_hash()}"
    best = {{"epoch": -1, "acc": -1.0}}
    for ep in range(args.epochs):
        m = demo_epoch(ep)
        record_metrics("epoch_end", ep, m, cfg_hash)
        if m["acc"] > best["acc"]:
            best = {{"epoch": ep, "acc": m["acc"]}}
    # evaluate "best checkpoint" = best epoch metrics
    record_metrics("best_checkpoint", best["epoch"], {{"acc": best["acc"], "ppl": None}}, cfg_hash, notes="best-of-toy")
    print(f"Saved metrics.json; best epoch={{best['epoch']}} acc={{best['acc']:.3f}}")

if __name__ == "__main__":
    main()
# END: CODEX_TRAIN_LOOP
"""

TEST_PATH = REPO / "tests" / "test_metrics.py"
TEST_SENT = "# BEGIN: CODEX_TEST_METRICS"
TEST_CONTENT = f"""{TEST_SENT}
import math
import pytest
from codex_ml.eval import metrics as M

def test_token_accuracy_basic():
    pred = [1,2,3,4,5]
    targ = [1,9,3,0,5]
    assert M.token_accuracy(pred, targ) == pytest.approx(3/5)

def test_token_accuracy_ignore_index():
    pred = [1,2,3]
    targ = [1,-100,9]
    assert M.token_accuracy(pred, targ, ignore_index=-100) == pytest.approx(1/2)

def test_exact_match_strict():
    assert M.exact_match_strict("foo  bar", "foo bar") == 1.0
    assert M.exact_match_strict("a", "b") == 0.0

def test_perplexity_from_logits_monotonic():
    # two tokens, vocab=2; higher logit on correct class => lower ppl
    logits_low = [[0.2, 0.8],[0.2,0.8]]
    logits_high = [[0.8, 0.2],[0.8,0.2]]
    targets = [1,0]
    ppl_low = M.perplexity(logits_low, targets, from_logits=True)
    ppl_high = M.perplexity(logits_high, targets, from_logits=True)
    assert ppl_high < ppl_low

def test_bleu_and_rouge_optional():
    # should not crash if deps missing; return None
    score = M.bleu(["a b"], ["a b"])
    r = M.rouge_l(["a b"], ["a b"])
    assert (score is None) or (0.0 <= score <= 1.0)
    assert (r is None) or ("rougeL_f" in r)
# END: CODEX_TEST_METRICS
"""


def upsert(path: Path, sentinel: str, content: str, rationale: str) -> None:
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    prev = path.read_text(encoding="utf-8") if path.exists() else ""
    if sentinel in prev:
        return
    path.write_text(content, encoding="utf-8")
    log_change("create" if not prev else "edit", path, rationale, content)


def readme_cleanup():
    p = REPO / "README.md"
    if not p.exists():
        return
    try:
        txt = p.read_text(encoding="utf-8")
        cleaned = re.sub(r"\]\(\)", "](#)", txt)  # replace empty links
        if cleaned != txt:
            p.write_text(cleaned, encoding="utf-8")
            log_change(
                "edit", p, "Normalize empty Markdown links to anchors", cleaned[:500]
            )
    except Exception as e:
        q5("3.README-cleanup", str(e), f"path={p}")


def validate(epochs: int = 3):
    # Run tests then demo training loop
    with RESULTS.open("a", encoding="utf-8") as fh:
        fh.write(f"\n# Validation {ts()}\n")
        cmds = [
            ("pytest (metrics)", ["pytest", "-q", "tests/test_metrics.py"]),
            (
                "train_loop (demo)",
                ["python", "-m", "codex_ml.train_loop", "--epochs", str(epochs)],
            ),
        ]
        for name, cmd in cmds:
            fh.write(f"\n## {name}\n```\n")
            try:
                p = subprocess.run(cmd, capture_output=True, text=True)
                fh.write(p.stdout + p.stderr)
                fh.write(f"\n(exit={p.returncode})\n")
            except Exception as e:
                fh.write(f"ERROR: {e}\n")
                q5("6.validate", str(e), f"cmd={cmd}")
            fh.write("\n```\n")


def apply():
    try:
        upsert(
            METRICS_PATH,
            METRICS_SENT,
            METRICS_CONTENT,
            "Add metrics (ppl, acc, BLEU/ROUGE, exact match, unit-test hook)",
        )
        upsert(
            TRAIN_PATH,
            TRAIN_SENT,
            TRAIN_CONTENT,
            "Add toy training loop with metrics logging",
        )
        upsert(TEST_PATH, TEST_SENT, TEST_CONTENT, "Add unit tests for metrics")
        readme_cleanup()
    except Exception as e:
        q5("3.apply", str(e), "writing files")


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--apply", action="store_true", help="write metrics, trainer, tests"
    )
    ap.add_argument(
        "--validate", action="store_true", help="run tests & demo training loop"
    )
    ap.add_argument(
        "--epochs", type=int, default=3, help="epochs for demo training loop"
    )
    args = ap.parse_args()

    if args.apply:
        apply()
    if args.validate:
        validate(args.epochs)
    if not (args.apply or args.validate):
        print(
            "Usage: --apply [--validate --epochs N]\n\nNOTE: DO NOT ACTIVATE ANY GitHub Actions Online files. Run validations inside the Codex environment only."
        )


if __name__ == "__main__":
    main()
