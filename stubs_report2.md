# Stub Analysis Report

**Total Stubs**: 12

## Summary by Priority

- **P0**: 8
- **P1**: 0
- **P2**: 4

## Summary by Type

- **NotImplementedError**: 8
- **TODO**: 2
- **FIXME**: 2

## Detailed list


### P0 Priority (8 items)

**src/bridge_manager.py:150** [NotImplementedError]
- Message: NotImplementedError
- Context: `raise NotImplementedError(`

**src/codex/training.py:99** [NotImplementedError]
- Message: NotImplementedError
- Context: `raise NotImplementedError(`

**src/codex_ml/features/feast_compat.py:301** [NotImplementedError]
- Message: NotImplementedError
- Context: `raise NotImplementedError  # Protocol stub — concrete backends supply implementations`

**src/codex_ml/features/feast_compat.py:305** [NotImplementedError]
- Message: NotImplementedError
- Context: `raise NotImplementedError  # Protocol stub — concrete backends supply implementations`

**src/codex_ml/features/feast_compat.py:309** [NotImplementedError]
- Message: NotImplementedError
- Context: `raise NotImplementedError  # Protocol stub — concrete backends supply implementations`

**src/codex_ml/features/feast_compat.py:313** [NotImplementedError]
- Message: NotImplementedError
- Context: `raise NotImplementedError  # Protocol stub — concrete backends supply implementations`

**src/codex_ml/features/feast_compat.py:317** [NotImplementedError]
- Message: NotImplementedError
- Context: `raise NotImplementedError  # Protocol stub — concrete backends supply implementations`

**src/codex_ml/plugins/plugin_registry.py:83** [NotImplementedError]
- Message: 
- Context: `raise NotImplementedError()`


### P2 Priority (4 items)

**src/codex_ml/utils/stub_cleanup.py:206** [TODO]
- Message: Check for TODO
- Context: `# Check for TODO`

**src/codex_ml/utils/stub_cleanup.py:207** [TODO]
- Message: " in line:
- Context: `if "todo" in line_lower and "#" in line:`

**src/codex_ml/utils/stub_cleanup.py:222** [FIXME]
- Message: Check for FIXME
- Context: `# Check for FIXME`

**src/codex_ml/utils/stub_cleanup.py:223** [FIXME]
- Message: " in line:
- Context: `if "fixme" in line_lower and "#" in line:`

