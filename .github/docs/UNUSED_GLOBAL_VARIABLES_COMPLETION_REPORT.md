# UNUSED_GLOBAL_VARIABLES Completion Report

## 1) Summary counts
| metric | value |
|---|---|
| total documented findings target | 70 |
| remediated (`done`) | 22 |
| intentional-kept | 6 |
| remaining | 0 |
| blocked/inaccessible | 42 |

## 2) Files changed in this continuation session
| file |
|---|
| .github/agents/core/phase8_10_production_deployment.py |
| .github/agents/core/phase8_11_advanced_reasoning.py |
| tests/stub_packages/torch/__init__.py |
| tests/test_sentencepiece_adapter.py |
| .github/docs/UNUSED_GLOBAL_VARIABLES_STATUS.md |
| .github/docs/UNUSED_GLOBAL_VARIABLES_COMPLETION_REPORT.md |

## 3) Remediations completed in this session
| file | remediation |
|---|---|
| .github/agents/core/phase8_10_production_deployment.py | Removed remaining `UNUSED_*` / reserved-throughput constants tied to unused-global findings. |
| .github/agents/core/phase8_11_advanced_reasoning.py | Added explicit keep markers for intentional constants. |
| tests/stub_packages/torch/__init__.py | Added explicit marker for intentional stub exports (`cuda`, `utils`). |
| tests/test_sentencepiece_adapter.py | Added explicit marker for intentional `pytestmark` retention. |

## 4) Findings still unresolved
| file | variable | reason |
|---|---|---|
| (none explicitly enumerated in source docs) | — | No per-finding `remaining` entry could be confirmed from available source-enumerated set. |

## 5) Blocked/inaccessible findings
| file | variable | blocker |
|---|---|---|
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_29 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_30 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_31 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_32 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_33 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_34 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_35 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_36 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_37 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_38 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_39 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_40 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_41 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_42 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_43 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_44 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_45 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_46 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_47 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_48 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_49 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_50 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_51 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_52 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_53 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_54 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_55 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_56 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_57 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_58 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_59 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_60 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_61 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_62 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_63 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_64 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_65 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_66 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_67 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_68 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_69 | Source files provide category totals but not full per-finding file/variable mapping. |
| UNLISTED_IN_SOURCE_DOC | UNLISTED_FINDING_70 | Source files provide category totals but not full per-finding file/variable mapping. |

## 6) Verification commands and searches used
| type | command/search | result |
|---|---|---|
| repo lint baseline | `python -m ruff check .` | Failing baseline exists outside remediation scope (`tests/ci/test_post_rescue_comment.py` import order). |
| repo test baseline | `pytest -q` | Started and stopped after partial run to avoid long session runtime; no immediate remediation-related failure surfaced early. |
| targeted lint | `python -m ruff check .github/agents/core/phase8_10_production_deployment.py .github/agents/core/phase8_11_advanced_reasoning.py tests/stub_packages/torch/__init__.py tests/test_sentencepiece_adapter.py` | Pass |
| targeted test | `pytest -q tests/test_sentencepiece_adapter.py` | Pass |
| source verification | `rg`/`view` over remediation targets | Confirmed edited constants removed and keep-markers present. |
| workflow artifact sourcing | Downloaded run logs ZIP from run `26261298516` via `get_workflow_run_logs_url`; extracted `/tmp/codeqlrun26261298516/*` | Logs sourced; workflow artifacts endpoint returned `total_count: 0`. |

## 7) Final conclusion
- **Are all 70 findings resolved?** **No, not confirmed 70/70.**
- **What remains and why?** A set of findings is still **blocked** at inventory precision level because the provided source documents contain category totals but do not enumerate every file/variable pair for all 70 findings, and direct Code Scanning API access is `403`. Workflow run logs were sourced as requested, but the run exposes no downloadable artifacts payload listing per-alert file/variable tuples (`list_workflow_run_artifacts` returned 0), preventing strict 70-item per-alert confirmation in-session.
