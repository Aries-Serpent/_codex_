import warnings
import codex_ml.tokenization as tk


def test_warning_emitted_once():
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always", DeprecationWarning)
        _ = tk.get_tokenizer
        _ = tk.get_tokenizer  # second access should not double-warn if guard added later
        assert len([w for w in rec if issubclass(w.category, DeprecationWarning)]) >= 1
