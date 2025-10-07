import warnings
import pytest
from codex_ml.training import unified_training as ut


def test_legacy_wrappers_emit_deprecation():
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always", DeprecationWarning)
        try:
            ut.train_loop(cfg=None, model=None, optimizer=None, loss_fn=None, train_loader=[])
        except Exception:
            pass
        assert any(isinstance(w.message, DeprecationWarning) for w in rec)

    with pytest.warns(DeprecationWarning):
        try:
            ut.functional_training(
                cfg=None, model=None, optimizer=None, loss_fn=None, train_loader=[]
            )
        except Exception:
            # allow failure due to missing torch in minimal env
            pass
