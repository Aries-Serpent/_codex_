from typing import Any, Dict, Set
import hashlib
import json


def checksum_for_item(item: Dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class InMemoryDeduper:
    def __init__(self):
        self._seen: Set[str] = set()

    def is_duplicate(self, item: Dict[str, Any]) -> bool:
        c = checksum_for_item(item)
        if c in self._seen:
            return True
        self._seen.add(c)
        return False
