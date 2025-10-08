"""Hydra CLI for Codex ML.

This module dispatches pipeline steps based on a Hydra configuration. It is a
lightweight wrapper that calls the training and evaluation utilities when the
corresponding steps are present in the config. The config is composed from the
repository's ``configs`` directory by default.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable

from codex_ml.pipeline import run_codex_pipeline_from_config
from codex_ml.utils.optional import optional_import
from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)

_ = (ArgparseJSONParser, run_cmd)

try:  # pragma: no cover - optional dependency
    from omegaconf import DictConfig, OmegaConf
except Exception:  # pragma: no cover - optional dependency
    DictConfig = Any  # type: ignore
    OmegaConf = None  # type: ignore

hydra, _HAS_HYDRA = optional_import("hydra")
if not _HAS_HYDRA:
    os.environ.setdefault("CODEX_ALLOW_MISSING_HYDRA_EXTRA", "1")
    hydra, _HAS_HYDRA = optional_import("hydra")
if not _HAS_HYDRA or OmegaConf is None:
    hydra = None
    _HAS_HYDRA = False

try:  # pragma: no cover - optional dependency
    from codex_digest.error_capture import log_error as _log_error
except Exception:  # pragma: no cover

    def _log_error(step_no: str, step_desc: str, msg: str, ctx: str) -> None:  # type: ignore[func-returns-value]
        """Fallback logger if codex_digest is not available."""
        return None


_functional_training_main = None


def _load_functional_training_main():
    global _functional_training_main
    if _functional_training_main is None:
        try:
            from codex.training import main as _functional_training  # type: ignore
        except Exception:
            _functional_training_main = None
        else:
            _functional_training_main = _functional_training
    return _functional_training_main


def run_training(cfg: DictConfig | None, output_dir: str | None = None) -> None:
    """Invoke the functional training entry point with overrides from cfg.

    Parameters
    ----------
    cfg:
        Training configuration block.
    output_dir:
        Fallback path for training artifacts if not specified in ``cfg``.
    """
    main_fn = _load_functional_training_main()
    if main_fn is None:  # pragma: no cover - safety fallback
        raise RuntimeError("codex.training.main is unavailable")

    try:
        from hydra.core.global_hydra import GlobalHydra

        if GlobalHydra().is_initialized():
            GlobalHydra.instance().clear()
    except Exception:
        pass

    if cfg is None or OmegaConf is None:
        cfg_dict = dict(cfg or {}) if isinstance(cfg, dict) else {}
    else:
        cfg_dict = dict(OmegaConf.to_container(cfg, resolve=True))
    texts = cfg_dict.pop("texts", None)
    val_texts = cfg_dict.pop("val_texts", None)
    cfg_output = cfg_dict.pop("output_dir", None) or output_dir

    def _flatten(prefix: str, obj: Any) -> Iterable[tuple[str, Any]]:
        if isinstance(obj, dict):
            for ik, iv in obj.items():
                new_prefix = f"{prefix}.{ik}" if prefix else ik
                yield from _flatten(new_prefix, iv)
        else:
            yield prefix, obj

    overrides = [f"{key}={json.dumps(val)}" for key, val in _flatten("training", cfg_dict)]

    argv: list[str] = []
    if cfg_output:
        argv.extend(["--output-dir", str(cfg_output)])
    if texts:
        argv.extend(["--texts", *[str(t) for t in texts]])
    if val_texts:
        argv.extend(["--val-texts", *[str(t) for t in val_texts]])
    if overrides:
        argv.extend(["--cfg-override", *overrides])

    main_fn(argv)


try:  # pragma: no cover - evaluation is optional
    from codex_ml.eval.eval_runner import evaluate_datasets  # type: ignore
except Exception:  # pragma: no cover

    def evaluate_datasets(*args, **kwargs):  # type: ignore
        return None


if _HAS_HYDRA:

    @hydra.main(version_base="1.3", config_path="../../../configs", config_name="config")
    def main(cfg: DictConfig) -> None:  # pragma: no cover - simple dispatcher
        """Dispatch pipeline steps defined in the Hydra config."""
        logger = init_json_logging()
        arg_list = sys.argv[1:]
        with capture_exceptions(logger):
            log_event(logger, "cli.start", prog=sys.argv[0], args=arg_list)
            text = OmegaConf.to_yaml(cfg)
            print(text)
            out_dir = Path(".codex/hydra_last")
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "config.yaml").write_text(text)
            for step in cfg.pipeline.steps:
                if step == "train":
                    if cfg.get("dry_run"):
                        continue
                    run_training(cfg.train, cfg.get("output_dir"))
                elif step == "evaluate":
                    eval_cfg = OmegaConf.select(cfg, "eval")
                    if eval_cfg is None:
                        print(
                            "Eval config not found; skipping evaluate step",
                            file=sys.stderr,
                        )
                        continue
                    datasets = eval_cfg.get("datasets", [])
                    metrics = eval_cfg.get("metrics", [])
                    output_dir = cfg.get("output_dir", "runs/eval")
                    evaluate_datasets(datasets, metrics, output_dir)
                elif step == "pipeline":
                    pipeline_cfg = OmegaConf.select(cfg, "pipeline")
                    pipeline_block = (
                        OmegaConf.to_container(pipeline_cfg, resolve=True)
                        if pipeline_cfg is not None
                        else None
                    )
                    if not pipeline_block or "inputs" not in pipeline_block:
                        print(
                            "Pipeline inputs not found; skipping pipeline step",
                            file=sys.stderr,
                        )
                        continue
                    summary = run_codex_pipeline_from_config(
                        pipeline_block["inputs"],
                        seed=pipeline_block.get("seed"),
                        summary_path=pipeline_block.get("summary_path"),
                        log_summary=pipeline_block.get("log_summary"),
                    )
                    if pipeline_block.get("print_summary", True):
                        print(json.dumps(summary, indent=2))
            log_event(logger, "cli.finish", prog=sys.argv[0], status="ok")
            sys.exit(0)

else:  # pragma: no cover - hydra missing

    def main(cfg: Any = None) -> None:  # type: ignore[unused-argument]
        raise ImportError(
            "hydra-core is required to use codex_ml.cli.main; install it with `pip install hydra-core`."
        )


def cli(argv: list[str] | None = None) -> int:
    """Entry point used by console scripts."""
    logger = init_json_logging()
    args = list(argv) if argv is not None else sys.argv[1:]

    with capture_exceptions(logger):
        log_event(logger, "cli.start", prog=sys.argv[0], args=args)
        if "--version" in args or "-V" in args:
            from codex import __version__ as codex_version

            print(f"codex-ml-cli {codex_version}")
            log_event(logger, "cli.finish", prog=sys.argv[0], status="ok")
            return 0
        if "--help" in args or "-h" in args:
            print("codex_ml.cli.main — Hydra-managed pipeline entrypoint")
            print("Powered by Hydra (install hydra-core)")
            if not _HAS_HYDRA:
                guidance = (
                    "Codex ML CLI is powered by Hydra but hydra-core is not installed.\n"
                    "codex-ml-cli requires hydra-core for configuration loading.\n"
                    "Install it with `pip install hydra-core` to access the managed pipeline."
                )
                print("Powered by Hydra (install hydra-core)", file=sys.stderr)
                print(guidance, file=sys.stderr)
            log_event(logger, "cli.finish", prog=sys.argv[0], status="ok")
            return 0
        if not _HAS_HYDRA:
            guidance = (
                "Codex ML CLI is powered by Hydra but hydra-core is not installed.\n"
                "codex-ml-cli requires hydra-core for configuration loading.\n"
                "Install it with `pip install hydra-core` to access the managed pipeline."
            )
            print("Powered by Hydra (install hydra-core)")
            print(guidance, file=sys.stderr)
            log_event(
                logger,
                "cli.finish",
                prog=sys.argv[0],
                status="ok",
                error="hydra-core missing",
            )
            return 0
        overrides: list[str] = []
        i = 0
        while i < len(args):
            a = args[i]
            if a.startswith("--override-file="):
                file = a.split("=", 1)[1]
                overrides.extend(Path(file).read_text().splitlines())
                args.pop(i)
            elif a == "--override-file" and i + 1 < len(args):
                file = args[i + 1]
                overrides.extend(Path(file).read_text().splitlines())
                del args[i : i + 2]
            elif a == "--set" and i + 2 < len(args):
                overrides.extend(args[i + 1 : i + 3])
                del args[i : i + 3]
            else:
                i += 1
        sys.argv = [sys.argv[0]] + args + overrides
        try:
            main()
        except Exception as exc:  # pragma: no cover - logging path
            _log_error("STEP cli", "codex_ml.cli.main", str(exc), f"argv={args}")
            log_event(logger, "cli.finish", prog=sys.argv[0], status="error")
            raise
        log_event(logger, "cli.finish", prog=sys.argv[0], status="ok")
        return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(cli())
