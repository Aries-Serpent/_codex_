# [Validation]: Coverage Gate Remediation — Dependency & Marker Stabilization

## Acceptance Criteria (Post-Remediation)
| Gate | Criterion |
|------|-----------|
| Collection | Zero import errors (errors downgraded to skips if optional) |
| Coverage XML | artifacts/coverage.xml created |
| Torch availability | Torch functional modules import (torch.nn.functional) or tests with requires_torch skipped |
| Optional deps | sentencepiece, hydra-core, defusedxml, requests installed OR relevant tests skipped |
| Marker warnings | Unknown marker warnings reduced to zero |
| Per-target coverage | Each targeted file ≥96% lines |

## Commands
```bash
nox -s coverage
```text

## Troubleshooting
| Symptom | Likely Cause | Action |
|---------|--------------|-------|
| torch import fails | Wheel not installed | Pin trio: torch torchvision torchaudio |
| defusedxml missing | Not listed in dev requirements | Add `defusedxml>=0.7.1` |
| hydra-core missing | Omitted from requirements | Add `hydra-core>=1.3.2` |
| Unknown marker warnings | Marker not registered | Add to pytest.ini markers list |
| SentencePiece errors | Missing `sentencepiece` build | Add `sentencepiece>=0.1.99` (pure wheel) |

## Skip Logic Summary
| Marker | Skip Condition |
|--------|----------------|
| requires_torch | torch import fails |
| requires_sentencepiece | sentencepiece not installed |
| requires_transformers | transformers not installed |
| ml | torch missing |
| integration | hydra-core missing or INTEGRATION_ALLOW=0 |
| perf | PERF_ALLOW=0 |
| slow | SLOW_TESTS=0 |
| net | RUN_NET_TESTS=0 |
| deferred | RUN_DEFERRED_TESTS=0 |

## Remediation Applied
1. Added missing dependencies: torch trio, hydra-core, defusedxml, sentencepiece, requests
2. Registered all markers in pytest.ini to eliminate warnings
3. Created tools/testing/optional_deps.py for centralized dependency checking
4. Enhanced noxfile.py coverage session to explicitly install all required dependencies
5. Existing conftest.py already has comprehensive skip logic for optional dependencies

— End —
