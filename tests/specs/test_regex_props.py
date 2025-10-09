from __future__ import annotations

import time

from src.codex_utils.regex_patterns import ENV_ASSIGNMENT as ENV
from src.codex_utils.regex_patterns import PEM_BLOCK as PEM


def test_env_valid_and_invalid():
    assert ENV.fullmatch("FOO=bar")
    assert ENV.fullmatch("FOO_BAR")
    assert not ENV.fullmatch("9BAD=x")


def test_pem_bounds_noncatastrophic():
    noise = "A" * 4096 + "\n"
    s = "-----BEGIN CERT-----\n" + noise + "-----END CERT-----\n"
    t0 = time.time()
    ok = PEM.match(s) is not None
    dt = time.time() - t0
    assert ok and dt < 0.5


def test_pem_negative_fast():
    s = "-----BEGIN CERT-----\n" + ("Z" * 4096) + "\n-----END CERT-----\n"
    t0 = time.time()
    ok = PEM.match(s) is None
    dt = time.time() - t0
    assert ok and dt < 0.5
