# Conventional Commit Guidelines

To keep version history consistent we follow the [Conventional Commits](https://www.conventionalcommits.org/) standard.

## Format

```text
<type>(<scope>): <summary>
```

* Use lowercase types such as `feat`, `fix`, `docs`, `test`, or `chore`.
* Scope is optional but encouraged for large areas like `training`, `ops`, or `docs`.
* Summary should be written in the imperative mood (e.g. `add offline evaluator`).

## Examples

- `feat(training): add early stopping hook`
- `fix(utils): guard optional numpy import`
- `docs(ops): document release tagging workflow`

## Verification

A local gate is available via `nox -s conventional` which runs `cz check` over the latest commits. The `commitizen` commit-msg hook also prevents non-conforming messages during development.
