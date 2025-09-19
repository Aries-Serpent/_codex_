# CLI

The Click-based CLI groups common operations:

```bash
python -m codex_ml.cli.codex_cli tokenize "hello"
python -m codex_ml.cli.codex_cli metrics-server --port 9000
```

Subcommands: `train`, `evaluate`, `tokenize`, `repo-map`, `metrics-server`.

### Tokenizer commands

`codex tokenizer train` accepts streaming flags for large corpora:

```bash
codex tokenizer train --streaming --stream-chunk-size 524288
```

Enable `--streaming` to iterate over the corpus without loading entire files
into memory; add `--stream-chunk-size` to tune the chunk size (defaults to
1&nbsp;MiB when streaming is enabled). Use `--no-streaming` to force the legacy
in-memory path when benchmarking throughput.

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
