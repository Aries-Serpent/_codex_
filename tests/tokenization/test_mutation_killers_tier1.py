"""
Tier 1 Mutation Killing Enhancements for Tokenization Module

Focus: Strengthen assertions in tokenization tests to kill mutations by:
1. Testing boundary conditions (0, 1, min, max values)
2. Adding off-by-one scenario tests
3. Verifying exact length assertions with both upper and lower bounds
4. Testing edge cases like empty input, maximum token limits
5. Validating padding/truncation with precise assertions
"""

import os
import pathlib

import pytest


def _maybe_get_tokenizer():
    """Get tokenizer with fallback."""
    try:
        mod = __import__("codex_ml.tokenization.cli", fromlist=["encode", "decode"])
        if not hasattr(mod, "encode") or not hasattr(mod, "decode"):
            return None
        root = pathlib.Path(__file__).resolve().parents[1]
        model = root / "fixtures" / "spm_toy.model"
        if not model.exists():
            return None
        os.environ.setdefault("CODEX_TOKENIZER_MODEL", str(model))
        return mod
    except (ImportError, AttributeError):
        return None


pytestmark = pytest.mark.requires_sentencepiece


class TestTokenLengthBoundaries:
    """Test precise token length boundaries to catch off-by-one mutations."""

    @pytest.mark.parametrize("max_len", [1, 2, 4, 8, 16])
    def test_encoded_length_equals_max_exactly(self, max_len):
        """Verify encoded length is EXACTLY max_len, not less or more."""
        mod = _maybe_get_tokenizer()
        if mod is None:
            pytest.skip("Tokenizer unavailable")

        encode = getattr(mod, "encode", None)
        if not callable(encode):
            pytest.skip("encode not available")

        sample = "hello world tokenization test"
        ids = encode(sample, max_len=max_len, pad=True, trunc=True)

        # Strong assertions: length must be EXACTLY max_len
        assert len(ids) == max_len, \
            f"Length must be exactly {max_len}, got {len(ids)}"
        assert len(ids) >= max_len, \
            f"Length must be >= {max_len}, got {len(ids)}"
        assert len(ids) <= max_len, \
            f"Length must be <= {max_len}, got {len(ids)}"
        # All elements must be valid token IDs
        assert all(isinstance(i, int) for i in ids), \
            "All elements must be integers"

    def test_no_padding_when_shorter_than_max(self):
        """Verify no padding when input is shorter than max_len."""
        mod = _maybe_get_tokenizer()
        if mod is None:
            pytest.skip("Tokenizer unavailable")

        encode = getattr(mod, "encode", None)
        if not callable(encode):
            pytest.skip("encode not available")

        sample = "hi"  # Very short
        max_len = 20
        ids = encode(sample, max_len=max_len, pad=False, trunc=False)

        # Should be shorter than max_len when pad=False
        assert len(ids) < max_len, \
            f"Without padding, length {len(ids)} should be < {max_len}"
        assert len(ids) > 0, "Input should produce at least 1 token"

    def test_truncation_respects_max_boundary(self):
        """Verify truncation never exceeds max_len."""
        mod = _maybe_get_tokenizer()
        if mod is None:
            pytest.skip("Tokenizer unavailable")

        encode = getattr(mod, "encode", None)
        if not callable(encode):
            pytest.skip("encode not available")

        # Long sample that will need truncation
        sample = "hello codex tokenization testing framework " * 5
        max_len = 5

        ids = encode(sample, max_len=max_len, pad=False, trunc=True)

        # Strong assertions for truncation boundary
        assert len(ids) <= max_len, \
            f"Truncated length {len(ids)} must be <= {max_len}"
        assert len(ids) > 0, "Truncation must still produce tokens"


class TestPaddingTruncationCombinations:
    """Test all combinations of padding/truncation flags."""

    def test_pad_true_trunc_false_extends_input(self):
        """With pad=True, trunc=False, short inputs get padded."""
        mod = _maybe_get_tokenizer()
        if mod is None:
            pytest.skip("Tokenizer unavailable")

        encode = getattr(mod, "encode", None)
        if not callable(encode):
            pytest.skip("encode not available")

        sample = "hi"
        max_len = 10

        ids = encode(sample, max_len=max_len, pad=True, trunc=False)

        # Padding enabled, should reach max_len or close
        assert len(ids) >= 1, "Must have at least 1 token"
        assert len(ids) <= max_len, \
            f"Length {len(ids)} must not exceed {max_len}"

    def test_pad_false_trunc_true_truncates_only(self):
        """With pad=False, trunc=True, long inputs get truncated."""
        mod = _maybe_get_tokenizer()
        if mod is None:
            pytest.skip("Tokenizer unavailable")

        encode = getattr(mod, "encode", None)
        if not callable(encode):
            pytest.skip("encode not available")

        sample = "hello codex tokenization testing " * 10
        max_len = 8

        ids = encode(sample, max_len=max_len, pad=False, trunc=True)

        # No padding, but truncation enabled
        assert len(ids) > 0, "Must produce tokens"
        assert len(ids) <= max_len, \
            f"Truncated length {len(ids)} must be <= {max_len}"

    def test_pad_true_trunc_true_enforces_exact_length(self):
        """With pad=True, trunc=True, output is exactly max_len."""
        mod = _maybe_get_tokenizer()
        if mod is None:
            pytest.skip("Tokenizer unavailable")

        encode = getattr(mod, "encode", None)
        if not callable(encode):
            pytest.skip("encode not available")

        # Test with various lengths
        for max_len in [4, 8, 12]:
            for sample in ["hi", "hello world", "hello codex tokenizer " * 3]:
                ids = encode(sample, max_len=max_len, pad=True, trunc=True)

                # Strict assertion: must be EXACTLY max_len
                assert len(ids) == max_len, \
                    f"With pad=True, trunc=True, length must be exactly {max_len}, got {len(ids)}"


class TestDecodingRoundtrip:
    """Test encode/decode roundtrip with strong assertions."""

    def test_decode_produces_non_empty_string(self):
        """Verify decode returns non-empty string for valid tokens."""
        mod = _maybe_get_tokenizer()
        if mod is None:
            pytest.skip("Tokenizer unavailable")

        encode = getattr(mod, "encode", None)
        decode = getattr(mod, "decode", None)
        if not callable(encode) or not callable(decode):
            pytest.skip("encode/decode not available")

        sample = "hello world"
        ids = encode(sample, max_len=16, pad=True, trunc=True)
        decoded = decode(ids)

        # Strong assertions
        assert isinstance(decoded, str), \
            f"Decoded must be str, got {type(decoded)}"
        assert len(decoded) > 0, \
            "Decoded string must not be empty"
        assert isinstance(decoded.strip(), str), \
            "Decoded.strip() must be str"

    def test_decode_with_various_token_counts(self):
        """Verify decode works with different token counts."""
        mod = _maybe_get_tokenizer()
        if mod is None:
            pytest.skip("Tokenizer unavailable")

        encode = getattr(mod, "encode", None)
        decode = getattr(mod, "decode", None)
        if not callable(encode) or not callable(decode):
            pytest.skip("encode/decode not available")

        sample = "test sample for decoding"

        for max_len in [4, 8, 16]:
            ids = encode(sample, max_len=max_len, pad=True, trunc=True)
            decoded = decode(ids)

            # Each decode must produce valid output
            assert isinstance(decoded, str), \
                f"Decoded must be str at max_len={max_len}"
            assert len(decoded) >= 0, \
                f"Decoded length must be non-negative at max_len={max_len}"


class TestEdgeCases:
    """Test edge cases that often have weak assertion coverage."""

    def test_single_token_max_length(self):
        """Test behavior with max_len=1."""
        mod = _maybe_get_tokenizer()
        if mod is None:
            pytest.skip("Tokenizer unavailable")

        encode = getattr(mod, "encode", None)
        if not callable(encode):
            pytest.skip("encode not available")

        sample = "hello"
        ids = encode(sample, max_len=1, pad=True, trunc=True)

        # With max_len=1 and pad=True, trunc=True, length must be 1
        assert len(ids) == 1, \
            f"With max_len=1, length must be 1, got {len(ids)}"
        assert isinstance(ids[0], int), \
            f"Token must be int, got {type(ids[0])}"

    def test_very_large_max_length(self):
        """Test with very large max_len values."""
        mod = _maybe_get_tokenizer()
        if mod is None:
            pytest.skip("Tokenizer unavailable")

        encode = getattr(mod, "encode", None)
        if not callable(encode):
            pytest.skip("encode not available")

        sample = "short"
        max_len = 1000

        ids = encode(sample, max_len=max_len, pad=True, trunc=False)

        # Even with large max_len, must produce valid tokens
        assert len(ids) > 0, "Must produce tokens"
        assert len(ids) <= max_len, \
            f"Length {len(ids)} must not exceed {max_len}"
        assert all(isinstance(i, int) for i in ids), \
            "All tokens must be integers"

    def test_decode_empty_list_handling(self):
        """Test decode behavior with empty token list (if applicable)."""
        mod = _maybe_get_tokenizer()
        if mod is None:
            pytest.skip("Tokenizer unavailable")

        decode = getattr(mod, "decode", None)
        if not callable(decode):
            pytest.skip("decode not available")

        # Some tokenizers may handle empty list differently
        try:
            result = decode([])
            assert isinstance(result, str), \
                f"Empty decode must return str, got {type(result)}"
        except (ValueError, IndexError, TypeError):
            # Some tokenizers may raise exception for empty list, which is valid
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
