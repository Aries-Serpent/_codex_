<!-- BEGIN: CODEX_DOCS_TUTORIALS_QUICKSTART -->

# Quickstart (CPU)

**Last Updated:** 2026-06-22

Get Codex running locally in under five minutes — no GPU required.

## Prerequisites

```bash
python --version   # 3.12+
pip install -e .   # install from repo root
```

## 1 — Start the API

```bash
# Option A: directly
python -m codex.cli serve

# Option B: Docker Compose (recommended for isolation)
docker compose up api
```

The API listens on `http://localhost:8000` by default.

## 2 — Run inference

```bash
curl -X POST http://localhost:8000/infer \
  -H "Content-Type: application/json" \
  -d '{"prompt": "def fibonacci(n):", "max_tokens": 64}'
```

Or open the demo notebook:

```bash
jupyter notebook examples/notebooks/demo_infer.ipynb
```

## 3 — Verify outputs

The response JSON contains `completion`, `tokens_used`, and `model_version`.  
No GPU is required — the symbolic pipeline runs fully on CPU.

## Next steps

| Goal | Guide |
|------|-------|
| Full end-to-end training | [End-to-End CPU tutorial](end_to_end_cpu.md) |
| Deploy to production | [Deploy Pipeline](../deployment/deploy_pipeline.md) |
| Configure the model | [Codex Setup Guide](../guides/codex_setup.md) |
| Understand the architecture | [Architecture](../architecture.md) |
