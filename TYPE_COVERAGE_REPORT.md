# Type Coverage Report

**Total Errors**: 582
**Files Affected**: 137
**Error Types**: 20

---

## Error Categories (Top 10)

### attr-defined (229 errors)

- `src/codex_ml/cli/repo_map.py` - "dict[str, list[str]]" has no attribute "append"  [attr-defined]
- `src/codex_ml/cli/repo_map.py` - "dict[str, list[str]]" has no attribute "append"  [attr-defined]
- `src/codex_ml/cli/repo_map.py` - "dict[str, list[str]]" has no attribute "append"  [attr-defined]
- `src/codex_ml/cli/repo_map.py` - "dict[str, list[str]]" has no attribute "append"  [attr-defined]
- `src/codex_ml/cli/repo_map.py` - "dict[str, list[str]]" has no attribute "append"  [attr-defined]
- ... and 224 more

### valid-type (75 errors)

- `src/codex_ml/metrics/text.py` - Variable "torch.Tensor" is not valid as a type  [valid-type]
- `src/codex_ml/interfaces/tokenizer_hf.py` - Variable "torch.Tensor" is not valid as a type  [valid-type]
- `src/codex_ml/interfaces/tokenizer_hf.py` - Variable "torch.dtype" is not valid as a type  [valid-type]
- `src/codex_ml/model_registry.py` - Variable "torch.device" is not valid as a type  [valid-type]
- `src/codex_ml/model_registry.py` - Variable "torch.dtype" is not valid as a type  [valid-type]
- ... and 70 more

### misc (38 errors)

- `src/codex_ml/cli/repo_map.py` - Unpacking a string is disallowed  [misc]
- `src/tokenization/sentencepiece_adapter.py` - Cannot assign to a type  [misc]
- `src/tokenization/sentencepiece_adapter.py` - All conditional function variants must have identical signatures  [misc]
- `src/codex_ml/config/__init__.py` - Cannot assign to a type  [misc]
- `src/codex_ml/config/__init__.py` - Cannot assign to a type  [misc]
- ... and 33 more

### var-annotated (38 errors)

- `src/codex_ml/metrics/evaluator.py` - Need type annotation for "preds"  [var-annotated]
- `src/codex_ml/interfaces/tokenizer_hf.py` - Need type annotation for "target_device"  [var-annotated]
- `src/codex_ml/models/generate.py` - Need type annotation for "probs"  [var-annotated]
- `src/codex_ml/models/generate.py` - Need type annotation for "padding"  [var-annotated]
- `src/codex_ml/evaluation/loop.py` - Need type annotation for "target_device"  [var-annotated]
- ... and 33 more

### assignment (37 errors)

- `codex_utils/logging_setup.py` - Incompatible types in assignment (expression has type "Iterable[tuple[str, float]]", variable has type "dict_items[Any, Any] | dict_items[str, float]")  [assignment]
- `config_legacy/__init__.py` - Incompatible types in assignment (expression has type "str | Path", variable has type "Path")  [assignment]
- `src/codex_ml/tracking/writers.py` - Incompatible types in assignment (expression has type "OrderedDict[str, Any]", target has type "str")  [assignment]
- `src/codex_ml/tracking/writers.py` - Incompatible types in assignment (expression has type "OrderedDict[Never, Never]", target has type "str")  [assignment]
- `src/tokenization/train_tokenizer.py` - Incompatible types in assignment (expression has type "None", variable has type Module)  [assignment]
- ... and 32 more

### arg-type (30 errors)

- `src/codex_ml/cli/hydra_audit.py` - Argument 1 to "_self_position" has incompatible type "Any | None"; expected "Sequence[Any]"  [arg-type]
- `src/codex_ml/metrics/registry.py` - Argument 1 has incompatible type "object"; expected "Callable[..., object]"  [arg-type]
- `src/codex_ml/metrics/reward.py` - Argument 1 has incompatible type "object"; expected "Callable[..., object]"  [arg-type]
- `src/codex_ml/metrics/reward.py` - Argument 1 has incompatible type "object"; expected "Callable[..., object]"  [arg-type]
- `src/codex_ml/tracking/init_experiment.py` - Argument 1 to "asdict" has incompatible type "DataclassInstance | type[DataclassInstance]"; expected "DataclassInstance"  [arg-type]
- ... and 25 more

### union-attr (23 errors)

- `src/codex_ml/tracking/mlflow_utils.py` - Item "None" of "Any | None" has no attribute "set_tracking_uri"  [union-attr]
- `src/codex_ml/tracking/mlflow_utils.py` - Item "None" of "Any | None" has no attribute "set_experiment"  [union-attr]
- `src/codex_ml/tracking/mlflow_utils.py` - Item "None" of "Any | None" has no attribute "start_run"  [union-attr]
- `src/codex_ml/tracking/mlflow_utils.py` - Item "None" of "Any | None" has no attribute "start_run"  [union-attr]
- `src/codex_ml/tracking/mlflow_utils.py` - Item "None" of "Any | None" has no attribute "set_tag"  [union-attr]
- ... and 18 more

### index (21 errors)

- `src/codex_ml/training/ab_testing.py` - Unsupported target for indexed assignment ("bool | dict[Any, Any] | str | None")  [index]
- `src/codex_ml/safety/filters.py` - Invalid index type "str | None" for "dict[str, Any]"; expected type "str"  [index]
- `src/codex_ml/safety/filters.py` - Invalid index type "str | None" for "dict[str, Any]"; expected type "str"  [index]
- `src/codex_ml/safety/filters.py` - Invalid index type "str | None" for "dict[str, Any]"; expected type "str"  [index]
- `src/codex_ml/safety/filters.py` - Invalid index type "str | None" for "dict[str, Any]"; expected type "str"  [index]
- ... and 16 more

### operator (17 errors)

- `src/codex_ml/cli/hydra_audit.py` - Unsupported right operand type for in ("Any | None")  [operator]
- `src/tokenization/cli.py` - "object" not callable  [operator]
- `src/codex_ml/monitoring/drift_detection.py` - Unsupported right operand type for in ("object")  [operator]
- `src/codex_ml/monitoring/drift_detection.py` - Unsupported right operand type for in ("object")  [operator]
- `src/codex_ml/monitoring/drift_detection.py` - Unsupported operand types for + ("object" and "int")  [operator]
- ... and 12 more

### no-redef (16 errors)

- `codex_utils/json_report.py` - Name "lines" already defined on line 119  [no-redef]
- `codex_utils/json_report.py` - Name "lines" already defined on line 119  [no-redef]
- `torch/__init__.py` - Name "__all__" already defined on line 40  [no-redef]
- `src/codex_ml/cli/repo_map.py` - Name "sections" already defined on line 260  [no-redef]
- `src/codex_ml/interfaces/tokenizer.py` - Attribute "_decode_cache" already defined on line 389  [no-redef]
- ... and 11 more

---

## Most Affected Files (Top 15)

### src/codex_ml/models/decoder_only.py (58 errors)

- `attr-defined`: 29
- `valid-type`: 21
- `var-annotated`: 3
- `index`: 2
- `operator`: 2
- `has-type`: 1

### src/codex_ml/models/reasoning.py (34 errors)

- `attr-defined`: 18
- `valid-type`: 11
- `var-annotated`: 2
- `index`: 2
- `operator`: 1

### src/codex_ml/evaluation/cli.py (33 errors)

- `attr-defined`: 33

### src/codex_ml/training/legacy_api.py (26 errors)

- `valid-type`: 6
- `arg-type`: 4
- `has-type`: 4
- `attr-defined`: 3
- `misc`: 2
- `name-defined`: 2
- `var-annotated`: 2
- `no-redef`: 2
- `index`: 1

### src/codex_ml/models/minilm.py (19 errors)

- `attr-defined`: 16
- `valid-type`: 2
- `var-annotated`: 1

### src/codex_ml/train_loop.py (19 errors)

- `assignment`: 5
- `var-annotated`: 4
- `operator`: 3
- `has-type`: 2
- `arg-type`: 2
- `attr-defined`: 1
- `no-redef`: 1
- `union-attr`: 1

### src/codex_ml/tokenization/hf_tokenizer.py (16 errors)

- `attr-defined`: 11
- `valid-type`: 4
- `misc`: 1

### src/codex_ml/cli/migrate_data.py (15 errors)

- `attr-defined`: 15

### src/codex_ml/tokenization/adapter.py (14 errors)

- `name-defined`: 4
- `arg-type`: 3
- `attr-defined`: 2
- `override`: 2
- `operator`: 1
- `union-attr`: 1
- `has-type`: 1

### src/codex_ml/hf_loader.py (11 errors)

- `valid-type`: 7
- `attr-defined`: 4

### src/codex_ml/cli/features.py (11 errors)

- `attr-defined`: 11

### src/codex_ml/cli/repo_map.py (9 errors)

- `attr-defined`: 7
- `no-redef`: 1
- `misc`: 1

### src/codex_ml/models/generate.py (9 errors)

- `valid-type`: 3
- `misc`: 2
- `var-annotated`: 2
- `attr-defined`: 2

### src/codex_ml/monitoring/drift_detection.py (9 errors)

- `index`: 6
- `operator`: 3

### src/codex_ml/cli/plugins_cli.py (9 errors)

- `attr-defined`: 9
