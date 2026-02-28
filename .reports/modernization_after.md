# Modernization Scanner Report

**Total Issues**: 212

## By Severity

- error: 0
- warning: 0
- suggestion: 212
- auto_refactor: 0

## By Category

- typing-union: 193
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
|factory.py|141|Class '_MockModel' could be converted to a dataclass|suggestion|
|legacy_api.py|990|Class '_DictDataset' could be converted to a dataclass|suggestion|
|__init__.py|27|Class '_DummyModel' could be converted to a dataclass|suggestion|

### string-format (11 issues)

|File|Line|Message|Severity|
|----|----|-------|--------|
|hf_pinning.py|82|Consider using f-string instead of .format()|suggestion|
|metrics_cli.py|370|Consider using f-string instead of .format()|suggestion|
|main.py|389|Consider using f-string instead of .format()|suggestion|
|main.py|390|Consider using f-string instead of .format()|suggestion|
|hydra_audit.py|349|Consider using f-string instead of .format()|suggestion|
|registries.py|119|Consider using f-string instead of .format()|suggestion|
|registries.py|156|Consider using f-string instead of .format()|suggestion|
|registries.py|363|Consider using f-string instead of .format()|suggestion|
|registries.py|528|Consider using f-string instead of .format()|suggestion|
|registries.py|701|Consider using f-string instead of .format()|suggestion|

*...and 1 more*

### typing-union (193 issues)

|File|Line|Message|Severity|
|----|----|-------|--------|
|logging_factory.py|5|Consider using | None syntax instead of typing.Optional|suggestion|
|training_callbacks.py|8|Consider using | None syntax instead of typing.Optional|suggestion|
|app.py|7|Consider using | None syntax instead of typing.Optional|suggestion|
|app.py|8|Consider using | None syntax instead of typing.Optional|suggestion|
|codeowners_validate.py|6|Consider using | None syntax instead of typing.Optional|suggestion|
|codeowners_validate.py|7|Consider using | None syntax instead of typing.Optional|suggestion|
|__init__.py|14|Consider using | None syntax instead of typing.Optional|suggestion|
|chat.py|22|Consider using | None syntax instead of typing.Optional|suggestion|
|training.py|17|Consider using | None syntax instead of typing.Optional|suggestion|
|training.py|18|Consider using | None syntax instead of typing.Optional|suggestion|

*...and 183 more*
