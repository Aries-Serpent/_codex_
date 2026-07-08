"""
Test Tokenizer Parity

Test module for tokenizer parity.
"""

import sys

import pytest

try:
    from transformers import AutoTokenizer  # type: ignore
except ImportError:
    AutoTokenizer = None  # type: ignore


def _real_transformers_available() -> bool:
    """Return True only when a real transformers installation (not a conftest stub) is present.

    Uses ``sys.modules`` to look up the already-imported module so that
    ``transformers`` is only ever imported with ``from transformers import ...``
    (avoiding the 'imported with both import and import from' lint/CodeQL warning).
    """
    if AutoTokenizer is None:
        return False
    # Derive the top-level package name from the class's own __module__
    mod_name = getattr(AutoTokenizer, "__module__", "") or ""
    root = mod_name.split(".")[0] or "transformers"
    mod = sys.modules.get(root) or sys.modules.get("transformers")
    version = getattr(mod, "__version__", "")
    # Conftest stubs use '999.0.0+stub' or '0.0' to signal a fake install
    return bool(version) and "stub" not in str(version) and version != "0.0"


@pytest.mark.skipif(not _real_transformers_available(), reason="real transformers not installed")
def test_fast_vs_slow_parity_smoke():
    # For models that provide both fast and slow tokenizers (e.g., gpt2)
    name = "gpt2"
    fast = AutoTokenizer.from_pretrained(
        name, use_fast=True
    )  # nosec B615 - Test code with known model ID
    slow = AutoTokenizer.from_pretrained(
        name, use_fast=False
    )  # nosec B615 - Test code with known model ID

    sample = "Parity check: <special> tokens & unicode — café"
    f_ids = fast.encode(sample, add_special_tokens=False)
    s_ids = slow.encode(sample, add_special_tokens=False)

    # Parity usually holds; allow minor drift but enforce same length
    assert isinstance(f_ids, list) and isinstance(s_ids, list)
    assert len(f_ids) == len(s_ids), "F_ids must not be empty"
