# BEGIN: CODEX_METRICS
"""General-purpose and code-specific evaluation metrics.

- perplexity: supports logits -> NLL or direct NLL arrays
- token_accuracy: Ignores positions matching ignore_index
- Optional BLEU/ROUGE if dependencies present
- exact_match_strict: normalized string equivalence
- run_unit_tests: hook executing pytest against provided tests directory
"""

from __future__ import annotations

import math
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional

try:
    import numpy as np
except Exception:
    np = None  # graceful degradation


def _softmax_row(logits: List[float]) -> List[float]:
    m = max(logits)
    exps = [math.exp(x - m) for x in logits]
    s = sum(exps)
    return [e / s for e in exps]


def perplexity(
    logits_or_nll: Iterable,
    targets: Iterable[int],
    from_logits: bool = True,
    ignore_index: int = -100,
) -> float:
    """Compute perplexity over a batch.
    If from_logits=True, logits_or_nll is shape [B, V] per token (flattened or per-step);
    otherwise it's a list of negative log-likelihoods (NLLs) per token.
    """
    nll_vals: List[float] = []
    if from_logits:
        if np is not None:
            arr = np.asarray(list(logits_or_nll), dtype=float)
            tgt = np.asarray(list(targets), dtype=int)
            assert (
                arr.ndim == 2 and arr.shape[0] == tgt.shape[0]
            ), "logits shape [N,V] and targets [N]"
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
            # fallback pure-python path; iterate alongside targets
            for logits_row, y in zip(logits_or_nll, targets):
                if int(y) == ignore_index:
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


def token_accuracy(
    pred_ids: Iterable[int], target_ids: Iterable[int], ignore_index: int = -100
) -> float:
    correct = 0
    total = 0
    for p, t in zip(pred_ids, target_ids):
        if int(t) == ignore_index:
            continue
        total += 1
        correct += int(p) == int(t)
    return float(correct / total) if total else 0.0


def exact_match_strict(pred: str, ref: str) -> float:
    def norm(s: str) -> str:
        return " ".join(str(s).strip().split())

    return 1.0 if norm(pred) == norm(ref) else 0.0


def bleu(candidates: List[str], references: List[str], lowercase: bool = True) -> Optional[float]:
    try:
        from nltk.translate.bleu_score import SmoothingFunction, corpus_bleu
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


def rouge_l(
    candidates: List[str], references: List[str], lowercase: bool = True
) -> Optional[Dict[str, float]]:
    try:
        from rouge_score import rouge_scorer
    except Exception:
        return None
    if lowercase:
        candidates = [c.lower() for c in candidates]
        references = [r.lower() for r in references]
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    scores = [scorer.score(r, c)["rougeL"].fmeasure for c, r in zip(candidates, references)]
    if not scores:
        return None
    return {"rougeL_f": float(sum(scores) / len(scores))}


def run_unit_tests(code_str: str, tests_dir: str) -> Dict[str, int]:
    """Write code_str to a temp module and run pytest against tests_dir.
    Returns a summary dict: {passed, failed, errors}.
    """
    tmpdir = Path(tempfile.mkdtemp())
    mod = tmpdir / "candidate.py"
    mod.write_text(code_str, encoding="utf-8")
    # Run pytest
    proc = subprocess.run(
        ["pytest", "-q", tests_dir], cwd=str(tmpdir), capture_output=True, text=True
    )
    out = proc.stdout + proc.stderr

    def _count(pattern: str) -> int:
        matches = re.findall(pattern, out)
        return int(matches[-1]) if matches else 0

    return {
        "passed": _count(r"\b(\d+)\s+passed\b"),
        "failed": _count(r"\b(\d+)\s+failed\b"),
        "errors": _count(r"\b(\d+)\s+errors?\b"),
    }


# END: CODEX_METRICS
