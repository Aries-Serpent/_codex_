"""Minimal smoke script for _codex_ scaffolding.

This script exercises the minimal end-to-end path:
- tokenization
- training loop
- evaluator
- tracking stub

It uses the same core function as the CLI entrypoint
`codex_ml.cli.minimal_train.main`.
"""

from codex_ml.cli.minimal_train import run_minimal


def main() -> None:
    result = run_minimal(experiment_name=None)
    print("loss_before:", result.loss_before)
    print("loss_after:", result.loss_after)
    print("score:", result.score)


if __name__ == "__main__":
    main()
