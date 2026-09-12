# Offline ZIP Keymaster standalone package

This staging project packages the existing `offline_zip_keymaster` source tree as a
self-contained wheel or sdist without publishing to PyPI or any external registry.

Build locally from the repository checkout:

```bash
python scripts/build_offline_zip_keymaster_artifact.py
```

Artifacts are written under `staging/offline_zip_keymaster/dist/`.
