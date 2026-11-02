"""Read-only recovery identities, not credentials or evidence of consumption.

An injected snapshot context must yield an ExternalSnapshot of a present,
readable external store and exclude *all* external writers until it exits. Acquire it
before the evidence transaction, matching the tracker's external->journal order.
The tracker lock alone excludes tracker writers, not arbitrary SDK writers.
Neither a pattern's rate nor its application count proves which observation was
consumed. Independent consumption verification must consult a trusted receipt.
"""

from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, ContextManager, Iterator, Mapping

DecisionVerifier = Callable[[Mapping[str, Any]], bool]


@dataclass(frozen=True)
class ExternalSnapshot:
    """Non-secret identity and a fresh read of that identity under the held lock.

    ``recheck`` must freshly read the same present, readable store, raising on
    missing/unreadable data, not return a cached identity. The caller supplies
    the locking protocol: this class cannot exclude arbitrary SDK writers.
    """

    identity: str
    recheck: Callable[[], str]


SnapshotReader = Callable[[], ContextManager[ExternalSnapshot]]

_locks_guard = threading.Lock()
_locks: dict[tuple[int, str], threading.RLock] = {}
_held = threading.local()


@contextmanager
def pattern_store_lock(path: Path) -> Iterator[None]:
    """Exclude participating maintained writers across atomic file replacement.

    Lock the existing parent directory, not the replaceable store inode. No
    directory, store or lock file is created. All stores in that directory share
    this lock. POSIX advisory locking cannot exclude nonparticipating writers;
    unsupported platforms fail closed. Acquire before any evidence journal lock.
    """
    try:
        import fcntl
    except ImportError as exc:
        raise OSError("maintained pattern locking requires POSIX flock") from exc

    directory = Path(path).absolute().parent.resolve(strict=True)
    key = (os.getpid(), str(directory))
    with _locks_guard:
        lock = _locks.setdefault(key, threading.RLock())
    with lock:
        held = getattr(_held, "directories", None)
        if held is None:
            held = _held.directories = set()
        if key in held:
            yield
            return
        fd = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            actual = os.fstat(fd)
            current = directory.stat()
            if (actual.st_dev, actual.st_ino) != (current.st_dev, current.st_ino):
                raise OSError("pattern directory changed while acquiring exclusion")
            held.add(key)
            try:
                yield
            finally:
                held.remove(key)
        finally:
            os.close(fd)


@dataclass(frozen=True)
class LearningRecovery:
    """Exact persisted identity plus the two snapshots inspected by the operator."""

    observation_key: str
    observation_id: str | None
    event_id: str
    pattern_id: str | None
    patch_hash: str | None
    merged_sha: str | None
    outcome: str
    attempt_id: str | None
    attempt_ids: tuple[str, ...]
    observation_hash: str
    state: str
    journal_sha256: str
    external_snapshot: str

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["attempt_ids"] = list(self.attempt_ids)
        return result
