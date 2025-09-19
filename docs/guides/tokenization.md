# Tokenization pipeline

The Codex tokenizer utilities now support streaming ingestion, allowing large
corpora to be trained without loading entire shards into memory. Training,
validation, and encoding/decoding are exposed via the primary `codex` CLI so
pipelines can be automated alongside model training workflows.

## Streaming ingestion

Tokenizer training honours the `stream_chunk_size` configuration option. When
omitted the trainer defaults to 65,536-character chunks, reading files via the
shared ingestion helpers so encodings are normalised before they reach the
SentencePiece or BPE trainers. The chunk size can be overridden in
`configs/tokenization/base.yaml` or on the command line with
`--stream-chunk-size`.

Setting a larger chunk size improves throughput at the cost of memory; smaller
chunks reduce the peak footprint but may incur a small overhead while the
trainer stitches shards back together. The default works well for most
workloads, but specialised corpora may benefit from tuning.

## CLI usage

All tokenizer functionality lives under the `codex tokenizer` command group.
Examples:

```bash
# Train with streaming enabled (default chunk size)
codex tokenizer train --config configs/tokenization/base.yaml

# Override the chunk size and preview the plan without training
codex tokenizer train --stream-chunk-size 131072 --dry-run

# Validate corpus manifests and cached artifacts
codex tokenizer validate --config configs/tokenization/base.yaml

# Encode and decode with a trained tokenizer
codex tokenizer encode "Hello Codex" --tokenizer-path path/to/tokenizer.json
codex tokenizer decode 42 1337 9 --tokenizer-path path/to/tokenizer.json
```

When no text (for `encode`) or IDs (for `decode`) are supplied on the command
line the CLI falls back to reading from standard input, making it easy to pipe
data from other tools.

## Configuration reference

`TrainTokenizerConfig` gained a `stream_chunk_size` field. The value is emitted
in `manifest.json` alongside other hyperparameters, enabling reproducibility and
audit trails. Existing configurations continue to work; leaving the field unset
will use the default streaming chunk size.

```yaml
tokenization:
  corpus_glob: data/tokenizer/*.txt
  vocab_size: 32000
  stream_chunk_size: null  # defaults to 65536 when training
```

The CLI updates the configuration in-memory, so command-line overrides are
captured in manifests without mutating on-disk YAML files.
