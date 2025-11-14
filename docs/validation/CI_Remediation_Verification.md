# [Validation]: CI Remediation Verification

## Post-Patch Verification Steps
| Step | Command | Expected Result |
|------|---------|-----------------|
| Dependency sanity | `python .github/scripts/ci_dependency_sanity.py` | All critical imports OK |
| Coverage run | `nox -s coverage` | No collection errors; coverage.xml produced |
| Security run | `nox -s security` | Artifacts with 0 High/Critical OR allowed |
| Type check | `nox -s typecheck` | mypy_summary.txt with success |
| Torch functional | Implicit (sanity script) | Imports torch.nn.functional |
| Hydra exists shim | test_hydra_degrade passes | Uses safe_exists without AttributeError |
| Metrics test rename | Only one metrics test module | No duplicate import warnings |

## Acceptance Gates
| Gate | Criterion |
|------|-----------|
| Import stability | 0 hard import errors |
| Coverage | Repo ≥95%, targets ≥96% |
| Security | No unallowlisted High/Critical |
| Markers | Unknown marker warnings reduced to zero |
| Optional deps | Missing ones produce skips, not errors |

## If Failure Persists
| Symptom | Mitigation |
|---------|------------|
| torch _C still missing | Force reinstall: `pip install --force-reinstall torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1` |
| transformers attribute missing | Pin different version (e.g. `transformers==4.36.2`) |
| Hydra ConfigStore errors | Ensure hydra-core ≥1.3.2; re-run sanity |
| Excess unknown markers | Add to pytest.ini markers list |

— End —
