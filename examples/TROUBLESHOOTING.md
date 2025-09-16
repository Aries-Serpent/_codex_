# Examples Troubleshooting

* **Tokenizer downloads** – the HF-backed tokenizer example requires
  ``transformers`` and locally cached weights.  Pre-download models with
  ``python -m transformers.models.auto.tokenization_auto --model sshleifer/tiny-gpt2``
  or override the registry to use ``examples.plugins.toy_tokenizer`` as shown in
  ``examples/tokenize.py``.
* **Training dependencies** – ``run_functional_training`` expects
  ``datasets`` and ``transformers``.  Install the optional ``test`` extras or
  monkeypatch the registries in tests to avoid heavyweight imports.
* **Run directory permissions** – by default all examples write to ``./runs``.
  Override ``tracking.output_dir`` in the config if your environment requires a
  different location.
* **MLflow offline store** – keep ``CODEX_MLFLOW_ENABLE`` unset unless you have
  MLflow installed locally.  The ``examples/mlflow_offline.py`` helper prints
  ready-to-copy commands once a run completes.
