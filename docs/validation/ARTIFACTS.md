```markdown
# [Docs]: Phase-A Validator Artifacts (base64+gz) — decode, extract, CI

Overview
- The repository stores Phase-A validator snapshots as gzipped JSON encoded in base64 and committed under artifacts/*.json.gz.b64.
- A decoder script and extractor are included to produce validated JSON and human-friendly summaries.

Dev & CI
- Install pinned dev dependencies:
  python -m pip install -r requirements-dev.txt
- Use a venv for sandbox testing and run:
  tools/run_in_sandbox.sh

CLI flags
- --stable-output : deterministic output directory and stable_manifest.json
- --generate-baseline : write baseline/capabilities_scored.json
- --baseline-path <path> : explicit baseline path

CI
- The decode-validate workflow decodes artifacts, runs tests, and uploads decoded artifacts and validated outputs.
```
