"""
Validate codex.cli export surface.

Goal:
- Ensure `from codex.cli import cli` is importable and is a Click Group.
- Ensure Typer exports remain available (`app`, `main`).
- Provide deterministic failure messages for CI + AI agents.
"""

from __future__ import annotations


def main() -> int:
    """Validate CLI exports."""
    critical_failures: list[str] = []
    warnings: list[str] = []

    # Contract 1: codex.cli.cli exists
    try:
        from codex.cli import cli  # noqa: WPS433
    except Exception as exc:
        critical_failures.append(f"Import failed: from codex.cli import cli -> {exc!r}")
        cli = None

    if cli is None:
        critical_failures.append("codex.cli.cli is None (Click group could not be loaded).")
    else:
        try:
            import click  # noqa: WPS433

            if not isinstance(cli, click.core.Group):
                critical_failures.append(
                    f"codex.cli.cli is not click.Group (got {type(cli)})."
                )
        except Exception as exc:
            warnings.append(f"Could not validate click.Group type: {exc!r}")

    # Contract 2: codex.cli.app and codex.cli.main exist
    try:
        from codex.cli import app, main as entry_main  # noqa: WPS433

        if app is None:
            warnings.append("codex.cli.app is None (Typer may be unavailable).")
        if not callable(entry_main):
            critical_failures.append("codex.cli.main is not callable.")
    except Exception as exc:
        critical_failures.append(f"Import failed: from codex.cli import app, main -> {exc!r}")

    # Contract 3: __all__ includes required exports
    try:
        import codex.cli as codex_cli  # noqa: WPS433

        exported = set(getattr(codex_cli, "__all__", []))
        expected = {"app", "main", "cli"}
        if exported != expected:
            missing = expected - exported
            extra = exported - expected
            if missing:
                critical_failures.append(
                    f"codex.cli.__all__ missing: {sorted(missing)}"
                )
            if extra:
                warnings.append(f"codex.cli.__all__ has extra entries: {sorted(extra)}")
    except Exception as exc:
        warnings.append(f"Could not validate codex.cli.__all__: {exc!r}")

    # Output summary
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"- {w}")

    if critical_failures:
        print("CRITICAL FAILURES:")
        for f in critical_failures:
            print(f"- {f}")
        return 1

    print("OK: codex.cli export surface validated (cli/app/main).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
