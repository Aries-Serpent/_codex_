from typing import Iterable, Any, Generator
import hashlib
import json


def compute_checksum(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def batch_iterable(iterable: Iterable[Any], batch_size: int) -> Generator[list[Any], None, None]:
    batch = []
    for it in iterable:
        batch.append(it)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
