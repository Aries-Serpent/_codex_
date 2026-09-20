from __future__ import annotations

from collections import deque


def traverse_related(start_id: str, rel_rows: list[dict], depth: int = 1) -> list[dict]:
    adjacency: dict[str, list[dict]] = {}
    for r in rel_rows:
        adjacency.setdefault(r.get("source_id", ""), []).append(r)
        adjacency.setdefault(r.get("target_id", ""), []).append(r)

    seen = {start_id}
    queue = deque([(start_id, 0)])
    paths = []
    while queue:
        node, d = queue.popleft()
        if d >= depth:
            continue
        for edge in adjacency.get(node, []):
            nxt = edge.get("target_id") if edge.get("source_id") == node else edge.get("source_id")
            if nxt and nxt not in seen:
                seen.add(nxt)
                paths.append(edge)
                queue.append((nxt, d + 1))
    return paths
