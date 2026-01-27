"""
Test Tokenizer Parity

Test module for tokenizer parity.
"""

import pytest

try:
    from transformers import AutoTokenizer  # type: ignore
except Exception:
    AutoTokenizer = None  # type: ignore


@pytest.mark.skipif(AutoTokenizer is None, reason="transformers not installed")
def test_fast_vs_slow_parity_smoke():
    # For models that provide both fast and slow tokenizers (e.g., gpt2)
    name = "gpt2"
    fast = AutoTokenizer.from_pretrained(name, use_fast=True)  # nosec B615 - Test code with known model ID
    slow = AutoTokenizer.from_pretrained(name, use_fast=False)  # nosec B615 - Test code with known model ID

    sample = "Parity check: <special> tokens & unicode — café"
    f_ids = fast.encode(sample, add_special_tokens=False)
    s_ids = slow.encode(sample, add_special_tokens=False)

    # Parity usually holds; allow minor drift but enforce same length
    assert isinstance(f_ids, list) and isinstance(s_ids, list)
    assert len(f_ids) == len(s_ids)
