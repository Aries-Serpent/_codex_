# SOP (Local/Self-hosted): How ChatGPT Codex proposes PRs here

1) **PRs are text-only.** If a change includes binaries (`*.model`, `*.zip`, `*.7z`, etc.), Codex must exclude them.
2) **Binaries travel via Releases.** A maintainer (or CI on self-hosted) attaches binaries to the Release. Keep `SHA256SUMS` in Git.
3) **Small test fixtures** (<100 MiB) may be committed directly by a human via CLI. The ChatGPT PR excludes them; a maintainer pushes them later.
4) **Self-hosted only.** All workflows use `runs-on: self-hosted`. If you see a job targeting `ubuntu-latest`, convert it to self-hosted.
5) **Artifact hygiene.** If any artifact upload is needed, set `retention-days: 1`. Prefer not uploading artifacts at all.
6) **Skip CI when appropriate.** Use `[skip ci]` for doc/README-only pushes or mass renames.
