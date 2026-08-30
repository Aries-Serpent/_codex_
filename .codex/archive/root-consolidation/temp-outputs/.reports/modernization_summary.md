# Modernization Scanner Report

**Total Issues**: 366

## By Severity

- error: 0
- warning: 230
- suggestion: 136
- auto_refactor: 0

## By Category

- typing-builtin: 230
- typing-union: 117
- string-format: 11
- dataclass-candidate: 8

## Issues by Category

### dataclass-candidate (8 issues)

|File|Line|Message|Severity|
|----|----|-------|--------|
|codex_structured_logging.py|338|Class '_CaptureExceptionsContext' could be converted to a dataclass|suggestion|
|__init__.py|26|Class '_MissingConfig' could be converted to a dataclass|suggestion|
|__init__.py|69|Class '_MissingSymbolic' could be converted to a dataclass|suggestion|
|metrics.py|62|Class 'MetricsAggregator' could be converted to a dataclass|suggestion|
|session_hooks.py|144|Class 'session' could be converted to a dataclass|suggestion|
|factory.py|140|Class '_MockModel' could be converted to a dataclass|suggestion|
|legacy_api.py|989|Class '_DictDataset' could be converted to a dataclass|suggestion|
|__init__.py|26|Class '_DummyModel' could be converted to a dataclass|suggestion|

### string-format (11 issues)

|File|Line|Message|Severity|
|----|----|-------|--------|
|hf_pinning.py|81|Consider using f-string instead of .format()|suggestion|
|metrics_cli.py|370|Consider using f-string instead of .format()|suggestion|
|main.py|389|Consider using f-string instead of .format()|suggestion|
|main.py|390|Consider using f-string instead of .format()|suggestion|
|hydra_audit.py|348|Consider using f-string instead of .format()|suggestion|
|registries.py|118|Consider using f-string instead of .format()|suggestion|
|registries.py|155|Consider using f-string instead of .format()|suggestion|
|registries.py|362|Consider using f-string instead of .format()|suggestion|
|registries.py|527|Consider using f-string instead of .format()|suggestion|
|registries.py|700|Consider using f-string instead of .format()|suggestion|

*...and 1 more*

### typing-builtin (230 issues)

|File|Line|Message|Severity|
|----|----|-------|--------|
|checkpointing.py|10|Use built-in dict instead of typing.Dict|warning|
|app.py|7|Use built-in tuple instead of typing.Tuple|warning|
|github_client.py|3|Use built-in dict instead of typing.Dict|warning|
|github_client.py|3|Use built-in list instead of typing.List|warning|
|codeowners_validate.py|6|Use built-in list instead of typing.List|warning|
|codeowners_validate.py|6|Use built-in dict instead of typing.Dict|warning|
|fast_tokenizer.py|4|Use built-in list instead of typing.List|warning|
|registry.py|6|Use built-in dict instead of typing.Dict|warning|
|training.py|17|Use built-in dict instead of typing.Dict|warning|
|training.py|17|Use built-in list instead of typing.List|warning|

*...and 220 more*

### typing-union (117 issues)

|File|Line|Message|Severity|
|----|----|-------|--------|
|logging_factory.py|5|Consider using | None syntax instead of typing.Optional|suggestion|
|training_callbacks.py|8|Consider using | None syntax instead of typing.Optional|suggestion|
|app.py|7|Consider using | None syntax instead of typing.Optional|suggestion|
|codeowners_validate.py|6|Consider using | None syntax instead of typing.Optional|suggestion|
|__init__.py|14|Consider using | None syntax instead of typing.Optional|suggestion|
|chat.py|22|Consider using | None syntax instead of typing.Optional|suggestion|
|training.py|17|Consider using | None syntax instead of typing.Optional|suggestion|
|train_tokenizer.py|11|Consider using | None syntax instead of typing.Optional|suggestion|
|encoding_detect.py|20|Consider using | None syntax instead of typing.Optional|suggestion|
|__init__.py|21|Consider using | None syntax instead of typing.Optional|suggestion|

*...and 107 more*
