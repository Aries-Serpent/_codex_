# Module Scan Results

## Tokenisation
- src/codex_ml/tokenization/__init__.py
- src/codex_ml/tokenization/hf_tokenizer.py
- src/codex_ml/tokenization/sentencepiece_adapter.py

## Modelling
- src/codex_ml/models/minilm.py
- src/codex_ml/modeling/codex_model_loader.py
- src/codex_ml/peft/peft_adapter.py

## Training
- src/codex_ml/train_loop.py
- src/codex_ml/training/callbacks.py
- functional_training.py

## Evaluation
- src/codex_ml/eval/evaluator.py
- src/codex_ml/eval/metrics.py

## Monitoring
- src/codex_ml/monitoring/codex_logging.py

## Checkpointing
- src/codex_ml/utils/checkpointing.py
- training/checkpoint_manager.py

## Capability Mapping
- `apply_lora` → LoRA integration (`src/codex_ml/peft/peft_adapter.py`)
- `HFTokenizerAdapter` → tokenisation (`src/codex_ml/tokenization/hf_tokenizer.py`)
- `MiniLM` → demo model (`src/codex_ml/models/minilm.py`)
- `codex_train_step` → training step w/grad accumulation (`functional_training.py`)
- `Evaluator` → evaluation loop (`src/codex_ml/eval/evaluator.py`)
- `CodexLoggers` → monitoring (`src/codex_ml/monitoring/codex_logging.py`)
- `CheckpointManager` → checkpoint handling (`training/checkpoint_manager.py`)

## Missing / To Do
- CLI entry point via Hydra
- Metrics callback with NDJSON support
- Coverage gating in nox
- Lockfile via `pip-compile --generate-hashes`
- Tests for new features

## Quality Checks
### pre-commit
```
black....................................................................[42mPassed[m
ruff.....................................................................[41mFailed[m
[2m- hook id: ruff[m
[2m- files were modified by this hook[m

Found 1 error (1 fixed, 0 remaining).

isort....................................................................[41mFailed[m
[2m- hook id: isort[m
[2m- files were modified by this hook[m

Fixing /workspace/_codex_/functional_training.py

fix end of files.........................................................[42mPassed[m
trim trailing whitespace.................................................[42mPassed[m
```

### pytest
```

============================================================ ERRORS ============================================================
____________________________________ ERROR collecting tests/test_ingestion_auto_encoding.py ____________________________________
ImportError while importing test module '/workspace/_codex_/tests/test_ingestion_auto_encoding.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_ingestion_auto_encoding.py:10: in <module>
    from ingestion import Ingestor  # noqa: E402
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ImportError: cannot import name 'Ingestor' from 'ingestion' (/workspace/_codex_/src/ingestion/__init__.py)
__________________________________ ERROR collecting tests/test_ingestion_encodings_matrix.py ___________________________________
ImportError while importing test module '/workspace/_codex_/tests/test_ingestion_encodings_matrix.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_ingestion_encodings_matrix.py:10: in <module>
    from ingestion import Ingestor  # noqa: E402
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ImportError: cannot import name 'Ingestor' from 'ingestion' (/workspace/_codex_/src/ingestion/__init__.py)
___________________________________ ERROR collecting tests/test_ingestion_family_encoding.py ___________________________________
ImportError while importing test module '/workspace/_codex_/tests/test_ingestion_family_encoding.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_ingestion_family_encoding.py:11: in <module>
    from ingestion.csv_ingestor import load_csv  # noqa: E402
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/ingestion/csv_ingestor.py:7: in <module>
    from .utils import _detect_encoding
E   ImportError: cannot import name '_detect_encoding' from 'ingestion.utils' (/workspace/_codex_/src/ingestion/utils.py). Did you mean: 'detect_encoding'?
_________________________________________ ERROR collecting tests/test_ingestion_io.py __________________________________________
ImportError while importing test module '/workspace/_codex_/tests/test_ingestion_io.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_ingestion_io.py:12: in <module>
    from ingestion import Ingestor, ingest  # noqa: E402
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ImportError: cannot import name 'Ingestor' from 'ingestion' (/workspace/_codex_/src/ingestion/__init__.py)
______________________________________ ERROR collecting tests/test_ingestion_read_text.py ______________________________________
ImportError while importing test module '/workspace/_codex_/tests/test_ingestion_read_text.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_ingestion_read_text.py:4: in <module>
    from ingestion.utils import read_text
E   ImportError: cannot import name 'read_text' from 'ingestion.utils' (/workspace/_codex_/src/ingestion/utils.py)
_____________________________________ ERROR collecting tests/tracking/test_mlflow_utils.py _____________________________________
import file mismatch:
imported module 'test_mlflow_utils' has this __file__ attribute:
  /workspace/_codex_/tests/monitoring/test_mlflow_utils.py
which is not the same as the test file we want to collect:
  /workspace/_codex_/tests/tracking/test_mlflow_utils.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
=================================================== short test summary info ====================================================
ERROR tests/test_ingestion_auto_encoding.py
ERROR tests/test_ingestion_encodings_matrix.py
ERROR tests/test_ingestion_family_encoding.py
ERROR tests/test_ingestion_io.py
ERROR tests/test_ingestion_read_text.py
ERROR tests/tracking/test_mlflow_utils.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 6 errors during collection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
1 skipped, 6 errors in 11.54s
```
