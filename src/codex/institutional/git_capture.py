"""Bound both native Git output streams before accumulating them in memory."""

from __future__ import annotations

import selectors
import subprocess
import time
from io import BufferedReader
from typing import cast

MAX_GIT_BYTES = 8 * 1024 * 1024
GIT_TIMEOUT = 20.0


class CaptureLimit(RuntimeError):
    """Output budget or wall-clock budget exceeded; no partial result is usable."""


def capture(command: list[str], env: dict[str, str]) -> bytes:
    """Drain stdout/stderr concurrently with one combined byte budget."""
    with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
    ) as process:
        if process.stdout is None or process.stderr is None:
            raise OSError("Git output pipes unavailable")
        output = bytearray()
        total = 0
        deadline = time.monotonic() + GIT_TIMEOUT
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ, True)
                selector.register(process.stderr, selectors.EVENT_READ, False)
                while selector.get_map():
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise CaptureLimit("GIT_TIMEOUT")
                    for key, _ in selector.select(remaining):
                        pipe = cast(BufferedReader, key.fileobj)
                        chunk = pipe.read1(min(65536, MAX_GIT_BYTES - total + 1))
                        if not chunk:
                            selector.unregister(key.fileobj)
                            continue
                        total += len(chunk)
                        if total > MAX_GIT_BYTES:
                            raise CaptureLimit("GIT_OUTPUT_LIMIT")
                        if key.data:
                            output.extend(chunk)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise CaptureLimit("GIT_TIMEOUT")
            try:
                code = process.wait(timeout=remaining)
            except subprocess.TimeoutExpired as exc:
                raise CaptureLimit("GIT_TIMEOUT") from exc
            if code:
                raise subprocess.CalledProcessError(code, command)
            return bytes(output)
        finally:
            if process.poll() is None:
                process.kill()
            process.wait()
