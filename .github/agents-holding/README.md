# Staged agent profiles

This directory is a holding area for profile candidates that cannot yet be
placed in the repository's active `.github/agents` location. Files here are
ordinary repository content; they are not proof of agent registration,
selection, activation, hosted availability, or permissions.

Before moving a candidate into `.github/agents`, inspect the current authorized
profile and registry conventions, adapt its metadata and tool policy, validate
the profile and registry, and obtain any applicable review. Do not copy
profiles into a different active location as a workaround.

`cdx-archive-lifecycle.agent.md` is a staged candidate for pack/query/verify/
rehydrate operations. It relies on the existing `scripts/archive` tools and
requires the packer's exact, fail-closed secret-scanning gate.

## Next-session plan: restore the pinned Gitleaks preflight

The last recorded preflight stopped before scanning because `gitleaks` was not
available; `detect-secrets` 1.5.0 was present at that time. Treat this as
historical environment evidence. In the next Copilot Cloud Agent session,
recheck the live environment and the candidate tree before relying on either
fact. The packer pins Gitleaks 8.30.1 and detect-secrets 1.5.0 in
`scripts/archive/cdx_common.py`; do not change those pins to accommodate the
runner.

### Decision options and adversarial check

1. **Use an already-installed, verified Gitleaks 8.30.1 — preferred when
   available.** Check its resolved executable and version. Adversarial check:
   a `gitleaks` found earlier on `PATH` may be a different version or binary;
   verify the exact version and invoke that resolved executable.
2. **Install the exact official Gitleaks 8.30.1 binary into a session-only
   temporary directory — selected fallback.** Determine runner OS/architecture,
   download only the matching official release, and verify its published
   checksum or signature against independently obtained official release
   metadata before execution. Add only that temporary directory to this
   process's `PATH`; do not use `sudo`, run remote shell installers, alter
   project dependencies, or commit the binary. Adversarial check: a correct
   version string alone does not establish artifact authenticity; reject
   unverified downloads and mismatched checksums.
3. **Install a system package, use an arbitrary mirror/latest version, update
   the scanner pin, or bypass Gitleaks. — rejected.** These options expand the
   environment or weaken/change the gate without evidence that scanner behavior
   is equivalent. If the official pinned binary cannot be verified or fetched,
   keep the gate blocked and report the concrete limitation; never substitute a
   successful detect-secrets-only run.

**Verified aggregate decision:** first reuse a verified exact-version
installation; otherwise use the verified session-local official binary. If
neither is possible, fail closed. Scanner availability does not itself
authorize archive creation or resolve any findings.

### Copy-ready Copilot Cloud Agent prompt

```text
Resume the CDX archive scanner-preflight recovery. Read the current
.codex/CODEBASE_AGENCY_POLICY.md, .github/AGENTS.md,
.github/agents-holding/cdx-archive-lifecycle.agent.md,
scripts/archive/CDX_SQLITE.md, and scripts/archive/cdx_common.py before acting.

1. Record `git status --short --branch`; preserve all existing dirty work,
   especially generated metadata. Do not reset, stash, clean, or rewrite it.
   Recompute a private fingerprint for the exact selected source tree
   (currently `.codex/archive`) and identify the current scanner executable
   paths/versions. Do not reuse the historical 16,532-entry fingerprint or
   historical 408-finding count as current results.
2. Inspect `PATH` for Gitleaks. If the resolved executable reports exactly
   8.30.1, use it. Otherwise determine the runner OS/architecture and obtain
   only the matching Gitleaks 8.30.1 release from the official upstream source
   into a session-only directory under `/tmp`. Verify the artifact against
   official published checksum/signature metadata obtained independently.
   Do not use sudo, remote shell scripts, unverified mirrors, repository
   dependency changes, global installation, or a different version. If
   verification or download is unavailable, stop the scan and report it as
   BLOCKED; do not weaken the gate.
3. Independently require detect-secrets 1.5.0. Verify both tools' version
   outputs and the Gitleaks `dir` command expected by the packer. Do not print
   credentials, matched values, source lines, or raw scanner reports.
4. Run both scanners using the existing `cdx_common.run_secret_scanners`
   contract on a private temporary snapshot of the exact selected source tree.
   Keep any inventory and temporary key outside all scanned roots. If findings
   require an HMAC key, generate/provision it privately for this session; never
   put it in command arguments, shell history, repository files, or logs.
   Preserve only the redacted inventory and its fingerprint when useful.
   Do not make or approve finding dispositions: each requires affirmative
   exact-finding evidence. Never create an archive during this preflight.
5. If either scanner is unavailable, exits unsuccessfully, changes version,
   emits malformed output, or leaves findings without current exact
   evidence-bound dispositions, report BLOCKED and stop. Do not scan only one
   tool and call it a pass. If both succeed with no findings, report a clean
   preflight for that exact fingerprint; this does not authorize or perform
   packing. A later packing invocation must use the existing packer, which
   independently snapshots and rescans the content it packs.
6. Remove only temporary files created by this task, never repository/user
   files. Report the OS/architecture, verified binary source and digest (not
   secrets), exact scanner versions, source fingerprint and entry count,
   redacted results, test/check results, and any blocker. Distinguish a
   successful preflight from archive creation, and do not claim an archive
   exists.

Decision check: the alternatives are a verified existing pinned binary, a
verified official session-local pinned binary, or fail-closed blocking if
neither is available. The first is preferred, the second is the selected
fallback, and unverified downloads, version changes, and partial/bypassed
scans are rejected. Challenge the fallback against artifact substitution and
environment persistence before use.
```
