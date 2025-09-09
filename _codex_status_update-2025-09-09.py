#!/usr/bin/env python3
"""
Codex end-to-end script to implement audit fixes in _codex_ repository.
This script:
1. Parses README and replaces placeholders.
2. Scans files for gaps highlighted in the audit and attempts to implement fixes.
3. Logs actions, captures errors, and formats questions for ChatGPT-5.
4. Runs local tests and reports results.
"""

import os
import json
import subprocess
from datetime import datetime


def readme_cleanup(readme_path: str) -> None:
    """Remove placeholder sections and insert quickstart instructions."""
    with open(readme_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        if "TODO" in line:
            continue
        new_lines.append(line.replace("{{project_name}}", "codex"))
    new_lines.append(
        "\n## Quickstart\nRun `python -m codex.cli train --help` to see available options.\n"
    )
    with open(readme_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def add_resume_flag(cli_path: str) -> None:
    """Inject --resume-from option into Typer CLI parser."""
    with open(cli_path, "r", encoding="utf-8") as f:
        contents = f.read()
    if "--resume-from" in contents:
        return
    insertion = (
        "\n    @app.command()\n"
        "    def train(resume_from: str = typer.Option(None, help=\"Path to checkpoint to resume from.\")):\n"
        "        ...\n"
        "        # pass resume_from to training engine\n"
    )
    with open(cli_path, "w", encoding="utf-8") as f:
        f.write(contents + insertion)


def deterministic_split(data_module: str) -> None:
    """Ensure deterministic data splitting by seeding random generators."""
    with open(data_module, "r", encoding="utf-8") as f:
        contents = f.read()
    if "seed=" in contents:
        return
    contents = contents.replace("train_test_split(", "train_test_split(random_state=42, ")
    with open(data_module, "w", encoding="utf-8") as f:
        f.write(contents)


def run_tests() -> None:
    """Execute pytest and capture results."""
    try:
        subprocess.run(["pytest", "-q", "--maxfail=1"], check=True)
    except subprocess.CalledProcessError as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        question = (
            f"Question for ChatGPT-5 {timestamp}: While performing run_tests, encountered the following error: {e}. "
            f"Context: running pytest on updated repository. "
            "What are the possible causes, and how can this be resolved while preserving intended functionality?"
        )
        with open("error_log.md", "a", encoding="utf-8") as f:
            f.write(question + "\n\n")
        print(question)


def main() -> None:
    readme_cleanup("README.md")
    add_resume_flag("codex_cli/cli.py")
    deterministic_split("codex_ml/data_module.py")
    run_tests()
    print("Audit fix script completed. Check error_log.md for any errors.")


if __name__ == "__main__":
    main()
