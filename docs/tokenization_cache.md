# Tokenizer Cache Parity (Offline-First)

- Default cache is local at `artifacts/tokenizer_cache/`.
- Remote downloads are **disabled** by default; enable only with explicit flags/env.
- Keep vocab/model files versioned to minimize cross-host cache drift.

## Usage

The tokenization CLI is designed for offline-first operation:

```bash
# Set cache directory
export CODEX_TOKENIZER_CACHE=artifacts/tokenizer_cache

# Use local tokenizer model
python -m codex_ml.tokenization.cli encode --model /path/to/local/model.sp --text "sample"
```text

## Offline Mode

By default, the tokenizer operates in offline mode and will not attempt to download remote models or vocabularies. This ensures:

1. **Reproducibility**: Same tokenizer files produce identical results across environments
2. **Security**: No outbound network calls during tokenization
3. **Performance**: No network latency for tokenization operations

## Cache Management

Keep tokenizer files under version control or maintain a shared artifact store to ensure cache parity across:
- Development environments
- CI/CD pipelines  
- Production deployments

## Recommendations

1. **Version control tokenizer models**: Check vocab files into the repository or maintain a registry
2. **Document tokenizer settings**: Record padding, truncation, and special tokens in configuration
3. **Validate cache integrity**: Use checksums to verify tokenizer files haven't been modified
4. **Test offline mode**: Ensure tokenization works without network access before deployment
