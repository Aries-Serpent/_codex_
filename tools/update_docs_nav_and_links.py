#!/usr/bin/env python3
"""Rewrite documentation links and update mkdocs navigation."""
import argparse
import re
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent
LINK_MAP = {
    "AGENTS.md": "docs/guides/AGENTS.md",
    "RUNBOOK.md": "docs/ops/RUNBOOK.md",
}


def update_links() -> list[Path]:
    touched: list[Path] = []
    for path in REPO_ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        new_text = text
        for old, new in LINK_MAP.items():
            new_text = new_text.replace(old, new)
        new_text = re.sub(
            r"CHANGELOG_([\w.-]+)\.md", r"docs/changelog/CHANGELOG_\1.md", new_text
        )
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            touched.append(path)
    return touched


def update_mkdocs() -> None:
    cfg = REPO_ROOT / "mkdocs.yml"
    if not cfg.exists() or yaml is None:
        return
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    nav = data.get("nav", [])

    def rewrite_nav(items):
        for item in items:
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, str):
                        for old, new in LINK_MAP.items():
                            if value.endswith(old):
                                item[key] = value.replace(old, new)
                        if "CHANGELOG_" in value and "docs/changelog/" not in value:
                            item[key] = value.replace(
                                "CHANGELOG_", "docs/changelog/CHANGELOG_"
                            )
                    elif isinstance(value, list):
                        rewrite_nav(value)

    rewrite_nav(nav)
    cfg.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mkdocs", action="store_true", help="Also update mkdocs.yml navigation"
    )
    args = parser.parse_args()
    update_links()
    if args.mkdocs:
        update_mkdocs()


if __name__ == "__main__":
    main()
