from pathlib import Path


class _DummyTok:
    def set_special_tokens(self, _): pass
    def encode_batch(self, xs, **kw): return {"input_ids":[list(range(kw.get("max_length",8))) for _ in xs]}
    def decode_batch(self, ids): return ["".join(map(str, row)) for row in ids]

def load_tokenizer(cache_dir="artifacts/tokenizer_cache", allow_remote=False):
    # Placeholder implementation; replace with real tokenizer init if available.
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    if not allow_remote:
        # enforce offline posture (no downloads)
        pass
    return _DummyTok()
