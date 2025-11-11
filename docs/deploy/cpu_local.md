# CPU-only Docker: Local Parity with nox/pytest
> Generated: 2025-11-11 07:55:43 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Doc Author], [Secondary: Verifier] ⚡ Energy: 5/5  
⚛️ Physics: Path🛤️ [Build → Cache → Run] Fields🔄 [Docker, Python] Patterns👁️ [Slim base, non-root] Redundancy🔀 [Multi-stage (opt)] Balance⚖️ [Parity vs. size]

## Build Image
```bash
docker build -f docker/Dockerfile.cpu -t codex-cpu:latest .
```

## Run Tests
```bash
docker run --rm -v "$PWD":/app -w /app codex-cpu:latest pytest -q
```

## Run nox Sessions (inside container)
```bash
docker run --rm -v "$PWD":/app -w /app codex-cpu:latest nox -s tests
```

## Tips
- Use `.dockerignore` to reduce context (`.git`, `.venv`, `__pycache__`).
- For local dev parity, mount the workspace with `-v "$PWD":/app` and run nox/pytest.

— End —