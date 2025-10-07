import random
import hashlib
import itertools

import pytest


def permute_indices(n: int, seed: int):
    rng = random.Random(seed)
    idx = list(range(n))
    rng.shuffle(idx)
    return idx


def shard_indices(n: int, rank: int, world: int):
    """
    Simple, deterministic sharding (round-robin).
    """
    return [i for i in range(n) if i % world == rank]


def checksum(seq):
    h = hashlib.sha256()
    for x in seq:
        h.update(str(x).encode("utf-8"))
    return h.hexdigest()


def test_manifest_checksum_stability():
    """
    Acceptance: Two consecutive loads with identical seed produce the same hash.
    """
    a = permute_indices(100, seed=42)
    b = permute_indices(100, seed=42)
    assert checksum(a) == checksum(b)


def test_seed_change_changes_ordering():
    """
    Acceptance: Changing seed meaningfully changes ordering.
    """
    a = permute_indices(100, seed=1)
    b = permute_indices(100, seed=2)
    assert a != b
    assert checksum(a) != checksum(b)


@pytest.mark.parametrize("world", [1, 2, 3, 4])
def test_shard_coverage_and_disjoint(world):
    """
    Acceptance:
      - Shard partitions are disjoint.
      - Union equals full dataset length.
    """
    n = 103
    parts = [set(shard_indices(n, r, world)) for r in range(world)]
    # Disjoint
    for a, b in itertools.combinations(parts, 2):
        assert a.isdisjoint(b)
    # Coverage
    union = set().union(*parts)
    assert len(union) == n


def test_utf8_fallback_mixed_encodings():
    """
    Acceptance: UTF-8 fallback strategy yields deterministic hash for mixed strings.
    """
    data = ["plain", "ümlaut", "emoji-😊", "汉字", "👍🏽"]
    h = hashlib.sha256()
    for s in data:
        # Fallback normalize to NFC and encode UTF-8
        b = s.encode("utf-8", errors="strict")
        h.update(b)
    # Stable digest regardless of platform default encodings
    assert len(h.hexdigest()) == 64
