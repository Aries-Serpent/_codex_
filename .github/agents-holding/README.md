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
