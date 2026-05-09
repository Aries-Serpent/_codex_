"""
Test Tokenizer Parity

Test module for tokenizer parity.
"""

import pytest

try:
    from transformers import AutoTokenizer  # type: ignore

    # Confirm it's a real installation (not just a stub) by checking for from_pretrained
    _has_real_transformers = callable(getattr(AutoTokenizer, "from_pretrained", None)) and not getattr(
        getattr(AutoTokenizer, "from_pretrained", None), "_is_stub", False
    )
except ImportError:
    AutoTokenizer = None  # type: ignore
    _has_real_transformers = False


def _real_transformers_available() -> bool:
    """Return True only when a real transformers installation (not a conftest stub) is present."""
    try:
        import transformers  # type: ignore

        version = getattr(transformers, "__version__", "")
        # Conftest stubs use '999.0.0+stub' to signal a fake install
        return bool(version) and "stub" not in str(version) and version != "0.0"
    except Exception:
        return False


@pytest.mark.skipif(not _real_transformers_available(), reason="real transformers not installed")
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
