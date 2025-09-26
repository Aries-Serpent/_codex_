# Removing tracked `.env` files

The repository no longer tracks a real `.env` file. Instead, secrets live in a
local-only copy that every developer creates from the committed template:

```bash
cp .env.example .env
```
This protects credentials by keeping them out of Git history and CI mirrors.
Only `.env.example` remains in the repo so we have a documented list of the
expected keys.

## Why `.env` stays untracked

* `.gitignore` excludes `.env`, `.envrc`, and related secret-bearing files.
* A `pre-commit` hook named `block-env-files` fails fast if someone tries to
  add `.env`, `.envrc`, or other secret suffixes (`*.secret`, `*.secrets`,
  `*.vault`).
* Secret scanners (`git-secrets`, the `.secrets.baseline` detectors) still run
  in CI as a defence-in-depth layer.

If you need to reset credentials, delete your local `.env` and re-copy the
template. Never commit real tokens.
