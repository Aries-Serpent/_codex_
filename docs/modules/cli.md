# CLI

The Click-based CLI groups common operations:

```bash
python -m codex_ml.cli.codex_cli tokenize "hello"
python -m codex_ml.cli.codex_cli metrics-server --port 9000
```

Subcommands: `train`, `evaluate`, `tokenize`, `repo-map`, `metrics-server`.

## Maintenance tasks

The repository also provides a lightweight maintenance CLI at
`codex.cli`. Tasks are listed via:

```bash
python -m codex.cli tasks
```

One useful utility is `pool-fix`, which resets the global tokenization
thread pool and enables SQLite connection pooling for session logs. It
accepts an optional `--max-workers` argument to limit the number of
threads and warm connections:

```bash
python -m codex.cli run pool-fix
```

This can resolve hangs caused by runaway threads in tokenizers on some
platforms.
