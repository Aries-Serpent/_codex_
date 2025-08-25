# BEGIN: CODEX_DATA_INIT
"""Data loader utilities."""
from .loaders import collect_stats, iter_jsonl, iter_txt, stream_paths

__all__ = ["collect_stats", "iter_jsonl", "iter_txt", "stream_paths"]
# END: CODEX_DATA_INIT
