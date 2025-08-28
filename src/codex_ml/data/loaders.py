# BEGIN: CODEX_DATA_LOADERS
"""Streaming data loaders for JSONL and TXT prompt-completion pairs."""

from __future__ import annotations

import json
import queue
import threading
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, Optional, Union

# Optional deps
try:  # pragma: no cover - optional
    _HAS_PYD = True
except Exception:  # pragma: no cover - optional
    _HAS_PYD = False

try:  # pragma: no cover - optional
    import pyarrow as pa

    _HAS_ARROW = True
except Exception:  # pragma: no cover - optional
    _HAS_ARROW = False

try:  # pragma: no cover - optional
    import tiktoken as _tke

    _HAS_TKE = True
except Exception:  # pragma: no cover - optional
    _HAS_TKE = False

if _HAS_PYD:
    try:  # pydantic v2
        from pydantic import BaseModel

        class PromptCompletion(BaseModel):
            prompt: str
            completion: str
    except Exception:  # pragma: no cover - pydantic v1
        from pydantic import BaseModel  # type: ignore

        class PromptCompletion(BaseModel):  # type: ignore
            prompt: str
            completion: str
else:

    class PromptCompletion:  # minimal fallback
        def __init__(self, prompt: str, completion: str) -> None:
            if not isinstance(prompt, str) or not isinstance(completion, str):
                raise TypeError("prompt and completion must be str")
            self.prompt = prompt
            self.completion = completion


def _token_count(text: str) -> int:
    if _HAS_TKE:
        try:
            enc = _tke.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except Exception:
            pass
    return len(text.split())


def _parse_jsonl_line(line: str, *, file: Path, ln: int) -> Dict[str, str]:
    try:
        obj = json.loads(line)
    except Exception as e:  # pragma: no cover - json errors
        raise ValueError(f"JSON parse error at {file}:{ln}: {e}")
    if not isinstance(obj, dict):
        raise ValueError(f"Expected object at {file}:{ln}, got {type(obj).__name__}")
    p, c = obj.get("prompt"), obj.get("completion")
    if not isinstance(p, str) or not isinstance(c, str):
        raise ValueError(f"Missing/invalid 'prompt' or 'completion' at {file}:{ln}")
    return {"prompt": p, "completion": c}


def _parse_txt_line(
    line: str, *, file: Path, ln: int, delimiter: str
) -> Dict[str, str]:
    if delimiter not in line:
        raise ValueError(f"Delimiter '{delimiter}' not found at {file}:{ln}")
    p, c = line.split(delimiter, 1)
    p, c = p.rstrip("\n\r"), c.rstrip("\n\r")
    if not p or not c:
        raise ValueError(f"Empty prompt or completion at {file}:{ln}")
    return {"prompt": p, "completion": c}


def iter_jsonl(path: Union[str, Path]) -> Iterator[PromptCompletion]:
    file = Path(path)
    with file.open("r", encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            d = _parse_jsonl_line(line, file=file, ln=i)
            yield (
                PromptCompletion(**d)
                if hasattr(PromptCompletion, "__annotations__")
                else PromptCompletion(d["prompt"], d["completion"])
            )


def iter_txt(
    path: Union[str, Path], *, delimiter: str = "\t"
) -> Iterator[PromptCompletion]:
    file = Path(path)
    with file.open("r", encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            if not line.strip():
                continue
            d = _parse_txt_line(line, file=file, ln=i, delimiter=delimiter)
            yield (
                PromptCompletion(**d)
                if hasattr(PromptCompletion, "__annotations__")
                else PromptCompletion(d["prompt"], d["completion"])
            )


def stream_paths(
    paths: Iterable[Union[str, Path]],
    *,
    fmt: str = "jsonl",
    num_workers: int = 0,
    prefetch: int = 0,
    max_samples: Optional[int] = None,
    delimiter: str = "\t",
) -> Iterator[PromptCompletion]:
    paths = [Path(p) for p in paths]
    fmt = fmt.lower()
    if num_workers <= 0 and prefetch <= 0:
        count = 0
        for p in paths:
            it = iter_jsonl(p) if fmt == "jsonl" else iter_txt(p, delimiter=delimiter)
            for item in it:
                yield item
                count += 1
                if max_samples is not None and count >= max_samples:
                    return
        return

    q: "queue.Queue[Optional[PromptCompletion]]" = queue.Queue(maxsize=max(1, prefetch))

    def producer() -> None:
        try:
            if num_workers > 0:

                def read_file(p: Path) -> None:
                    it = (
                        iter_jsonl(p)
                        if fmt == "jsonl"
                        else iter_txt(p, delimiter=delimiter)
                    )
                    for item in it:
                        q.put(item)

                threads = []
                for p in paths:
                    t = threading.Thread(target=read_file, args=(p,), daemon=True)
                    t.start()
                    threads.append(t)
                for t in threads:
                    t.join()
            else:
                for p in paths:
                    it = (
                        iter_jsonl(p)
                        if fmt == "jsonl"
                        else iter_txt(p, delimiter=delimiter)
                    )
                    for item in it:
                        q.put(item)
        finally:
            q.put(None)

    th = threading.Thread(target=producer, daemon=True)
    th.start()
    seen = 0
    while True:
        item = q.get()
        if item is None:
            break
        yield item
        seen += 1
        if max_samples is not None and seen >= max_samples:
            break


def split_indices(
    n: int, *, val_split: float = 0.1, test_split: float = 0.0, seed: int = 0
) -> tuple[list[int], list[int], list[int]]:
    """Return deterministic train/val/test indices for *n* samples."""
    assert 0.0 <= test_split < 1.0 and 0.0 <= val_split < 1.0
    import random as _rnd

    idx = list(range(n))
    _rnd.seed(seed)
    _rnd.shuffle(idx)
    n_test = int(n * test_split)
    n_val = int(n * val_split)
    test_idx = idx[:n_test]
    val_idx = idx[n_test : n_test + n_val]
    train_idx = idx[n_test + n_val :]
    return train_idx, val_idx, test_idx


def collect_stats(
    stream: Iterable[PromptCompletion], sample_limit: Optional[int] = None
) -> Dict[str, Any]:
    total = plen = clen = ptok = ctok = 0
    for item in stream:
        p = getattr(item, "prompt", None)
        c = getattr(item, "completion", None)
        if not isinstance(p, str) or not isinstance(c, str):
            continue
        total += 1
        plen += len(p)
        clen += len(c)
        ptok += _token_count(p)
        ctok += _token_count(c)
        if sample_limit is not None and total >= sample_limit:
            break
    return {
        "samples": total,
        "prompt_chars": plen,
        "completion_chars": clen,
        "prompt_tokens": ptok,
        "completion_tokens": ctok,
        "avg_prompt_len": (plen / total) if total else 0.0,
        "avg_completion_len": (clen / total) if total else 0.0,
        "avg_prompt_tokens": (ptok / total) if total else 0.0,
        "avg_completion_tokens": (ctok / total) if total else 0.0,
    }


def to_arrow(rows: Iterable[PromptCompletion]):
    if not _HAS_ARROW:
        raise RuntimeError("pyarrow not installed")
    prompts, completions = [], []
    for r in rows:
        prompts.append(r.prompt)
        completions.append(r.completion)
    table = pa.table({"prompt": prompts, "completion": completions})
    return table


# END: CODEX_DATA_LOADERS
