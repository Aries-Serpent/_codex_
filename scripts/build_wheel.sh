#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)
cd "$ROOT"

LOCAL_BUILD=0
if [[ "${1:-}" == "--local" ]]; then
  LOCAL_BUILD=1
fi

ORIG_VERSION=$(python - <<'PY'
import tomllib
import sys
with open('pyproject.toml','rb') as f:
    data=tomllib.load(f)
print(data['project']['version'])
PY
)
if [[ $LOCAL_BUILD -eq 1 ]]; then
  NEW_VERSION="${ORIG_VERSION}+local.$(date +%Y%m%d%H%M)"
  sed -i.bak "s/^version = \"${ORIG_VERSION}\"/version = \"${NEW_VERSION}\"/" pyproject.toml
  trap 'mv pyproject.toml.bak pyproject.toml' EXIT
fi

rm -rf build dist *.egg-info || true
python -m build --no-isolation

if command -v twine >/dev/null 2>&1; then
  twine check dist/* || true
else
  echo "twine not available; skipping wheel verification" >&2
fi

python - <<'PY'
import hashlib, json, glob, subprocess, sys, datetime, os
paths = glob.glob('dist/*')
sha = {os.path.basename(p): hashlib.sha256(open(p,'rb').read()).hexdigest() for p in paths}
with open('SHA256SUMS','w') as fh:
    for name, digest in sha.items():
        fh.write(f"{digest}  {name}\n")
manifest = {
    'python': sys.version,
    'pip_freeze': subprocess.getoutput(f"{sys.executable} -m pip freeze"),
    'git_commit': subprocess.getoutput('git rev-parse HEAD'),
    'built_at': datetime.datetime.utcnow().isoformat() + 'Z',
}
with open('build_manifest.json','w') as fh:
    json.dump(manifest, fh, indent=2)
print('Wheels:', list(sha))
PY

echo "Wheel build complete."
