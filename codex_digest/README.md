# Codex Digest (offline, local-only)

A tiny, modular pipeline that converts context into **organized, prioritized tasks** using a 5-stage process:

1. Tokenization
2. Semantic parsing/intent detection
3. Action mapping
4. Workflow composition
5. Assembly/validation/execution

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

Alternatively place `codex_digest/` at repo root and set `PYTHONPATH=.`.

## Use

```bash
python -m codex_digest.cli --input-file DESCRIPTION.md --context-file CONTEXT.md --dry-run
cat .codex_digest.md
```

## Guarantees

* Offline by default; **no GitHub Actions** or network workflows.
* Error Capture Blocks printed on exceptions.
* Simple redaction heuristics applied to outputs.

## Mapping

* `tokenizer.py` → f₁
* `semparser.py` → f₂
* `mapper.py` → f₃
* `workflow.py` → f₄
* `pipeline.py` → f₅
