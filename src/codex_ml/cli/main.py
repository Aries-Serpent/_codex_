"""Codex ML command-line interfaces."""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Annotated, Any


def _load_typer():
    spec = importlib.util.find_spec("typer")
    if spec is None:
        return None
    module = importlib.import_module("typer")
    return module if hasattr(module, "Typer") else None


typer = _load_typer()

if typer is not None:
    app = typer.Typer(help="Codex ML CLI")

    from codex_ml.cli import _load_training_config

    def _value_from_config(
        cli_value: Any,
        default_value: Any,
        cfg: dict[str, Any],
        *keys: str,
    ) -> Any:
        if cli_value != default_value:
            return cli_value
        for key in keys:
            if key in cfg:
                return cfg[key]
        return cfg.get(keys[0], default_value) if keys else cli_value

    @app.command()
    def train(
        config: str | None = typer.Option(None, "--config", help="Path to training config YAML"),
        model_name: str = typer.Option("dummy", "--model-name", help="Model name or identifier"),
        epochs: int = typer.Option(1, "--epochs", help="Number of training epochs"),
        batch_size: int = typer.Option(8, "--batch-size", help="Batch size"),
        grad_accum: int = typer.Option(1, "--grad-accum", help="Gradient accumulation steps"),
        learning_rate: float = typer.Option(3e-4, "--learning-rate", help="Learning rate"),
        seed: int = typer.Option(42, "--seed", help="Random seed"),
        output_dir: str = typer.Option("runs/unified", "--output-dir", help="Output directory"),
        backend: str | None = typer.Option(
            None, "--backend", help="Backend strategy (functional or legacy)"
        ),
        mlflow_enable: bool = typer.Option(False, "--mlflow", help="Enable MLflow tracking"),
        wandb_enable: bool = typer.Option(False, "--wandb", help="Enable Weights & Biases logging"),
        grad_clip_norm: float | None = typer.Option(
            None, "--grad-clip-norm", help="Gradient clipping norm"
        ),
        dtype: str = typer.Option("fp32", "--dtype", help="Data type (fp32, fp16, bf16)"),
        resume_from: str | None = typer.Option(
            None, "--resume-from", help="Checkpoint path to resume from"
        ),
    ) -> None:
        """Start a training run. Config file values are overridden by CLI options."""
        from codex_ml.training.unified_training import UnifiedTrainingConfig, run_unified_training

        cfg_data = _load_training_config(config) if config else {}
        train_cfg = cfg_data.get("training", cfg_data) if isinstance(cfg_data, dict) else {}

        def _int_value(value: Any) -> int | None:
            try:
                return None if value is None else int(value)
            except (TypeError, ValueError):
                return None

        actual_epochs = (
            _int_value(_value_from_config(epochs, 1, train_cfg, "epochs", "num_train_epochs"))
            or epochs
        )
        actual_grad_accum = (
            _int_value(_value_from_config(grad_accum, 1, train_cfg, "gradient_accumulation_steps"))
            or grad_accum
        )
        actual_model_name = str(_value_from_config(model_name, "dummy", train_cfg, "model_name"))
        actual_lr = float(_value_from_config(learning_rate, 3e-4, train_cfg, "learning_rate"))
        actual_batch_size = (
            _int_value(_value_from_config(batch_size, 8, train_cfg, "batch_size")) or batch_size
        )
        actual_seed = _int_value(_value_from_config(seed, 42, train_cfg, "seed")) or seed
        actual_output_dir = str(
            _value_from_config(output_dir, "runs/unified", train_cfg, "output_dir")
        )
        actual_backend = backend or train_cfg.get("backend")
        actual_grad_clip = _value_from_config(grad_clip_norm, None, train_cfg, "grad_clip_norm")
        actual_dtype = str(_value_from_config(dtype, "fp32", train_cfg, "dtype"))
        actual_resume = resume_from or train_cfg.get("resume_from")

        cfg = UnifiedTrainingConfig(
            model_name=actual_model_name,
            epochs=actual_epochs,
            batch_size=actual_batch_size,
            grad_accum=actual_grad_accum,
            learning_rate=actual_lr,
            seed=actual_seed,
            output_dir=actual_output_dir,
            backend=actual_backend,
            mlflow_enable=mlflow_enable or bool(train_cfg.get("mlflow_enable", False)),
            wandb_enable=wandb_enable or bool(train_cfg.get("wandb_enable", False)),
            grad_clip_norm=actual_grad_clip,
            dtype=actual_dtype,
            resume_from=actual_resume,
        )
        result = run_unified_training(cfg)
        typer.echo(json.dumps({"ok": True, "train_result": result}, indent=2))

    @app.command()
    def resume(
        checkpoint: Annotated[
            str,
            typer.Argument(help="Path to checkpoint directory or file for resuming"),
        ],
        epochs: Annotated[
            int,
            typer.Option(
                "--epochs",
                help="New total number of epochs to run (including already completed)",
            ),
        ] = 1,
        other_args: Annotated[
            list[str] | None,
            typer.Option(
                "--override",
                help="Additional config overrides (currently not used)",
                show_default=False,
            ),
        ] = None,
    ) -> None:
        """Resume training from a checkpoint."""
        from codex_ml.training.unified_training import UnifiedTrainingConfig, run_unified_training

        _ = other_args or []  # Placeholder for future override handling
        cfg = UnifiedTrainingConfig(resume_from=checkpoint, epochs=epochs)
        result = run_unified_training(cfg)
        typer.echo(json.dumps({"ok": True, "resume_result": result}, indent=2))

    @app.command()
    def evaluate(
        dry_run: bool = typer.Option(
            False, "--dry-run", help="Parse evaluation config and exit without running"
        ),
        probe_json: bool = typer.Option(
            False, "--probe-json", help="Output diagnostic JSON and exit"
        ),
    ) -> None:
        """Run evaluation using available evaluation modules."""
        from codex_ml.cli import entrypoints as entry

        eval_args: list[str] = []
        if dry_run:
            eval_args.append("--dry-run")
        if probe_json:
            eval_args.append("--probe-json")

        original_argv = sys.argv
        try:
            sys.argv = ["codex-eval", *eval_args]
            exit_code = entry.eval_main()
        finally:
            sys.argv = original_argv
        raise typer.Exit(code=exit_code)

    @app.command()
    def version() -> None:
        """Print the Codex ML package version."""
        import codex_ml

        typer.echo(getattr(codex_ml, "__version__", "unknown"))

    @app.command()
    def info() -> None:
        """Show environment and configuration info."""
        import importlib

        from codex_ml.utils.checkpoint_core import capture_environment_summary

        info = capture_environment_summary()
        info["codex_ml_version"] = getattr(
            importlib.import_module("codex_ml"), "__version__", "unknown"
        )
        info["mlflow"] = None
        info["wandb"] = None
        mlflow_spec = importlib.util.find_spec("mlflow")
        if mlflow_spec is not None:
            mlflow_module = importlib.import_module("mlflow")
            info["mlflow"] = getattr(mlflow_module, "__version__", None)
        wandb_spec = importlib.util.find_spec("wandb")
        if wandb_spec is not None:
            wandb_module = importlib.import_module("wandb")
            info["wandb"] = getattr(wandb_module, "__version__", None)

        typer.echo(f"Codex ML version: {info['codex_ml_version']}")
        if "python_version" in info and "python_implementation" in info:
            typer.echo(f"Python: {info['python_version']} [{info['python_implementation']}]")
        if "platform" in info and "machine" in info:
            typer.echo(f"Platform: {info['platform']} ({info['machine']})")
        if "numpy_version" in info:
            typer.echo(f"NumPy: {info['numpy_version']}")
        if "torch_version" in info:
            cuda_available = info.get("torch_cuda_available")
            typer.echo(f"PyTorch: {info['torch_version']} (CUDA available: {cuda_available})")
        typer.echo("MLflow: {}".format("available" if info.get("mlflow") else "not installed"))
        typer.echo("W&B: {}".format("available" if info.get("wandb") else "not installed"))

    cli = app

else:
    from typing import Any

    from codex_ml.codex_structured_logging import (
        ArgparseJSONParser,
        capture_exceptions,
        init_json_logging,
        log_event,
        run_cmd,
    )
    from codex_ml.pipeline import run_codex_pipeline_from_config
    from codex_ml.utils.optional import optional_import

    _ = (ArgparseJSONParser, run_cmd)

    hydra, _HAS_HYDRA = optional_import("hydra")
    if not _HAS_HYDRA:
        os.environ.setdefault("CODEX_ALLOW_MISSING_HYDRA_EXTRA", "1")
        hydra, _HAS_HYDRA = optional_import("hydra")
    if not _HAS_HYDRA:
        hydra = None

    try:
        from omegaconf import DictConfig, OmegaConf  # pragma: no cover - optional
    except Exception:  # pragma: no cover - optional
        DictConfig = Any  # type: ignore
        OmegaConf = None  # type: ignore

    try:  # pragma: no cover - optional dependency
        from codex_digest.error_capture import log_error as _log_error
    except Exception:  # pragma: no cover

        def _log_error(step_no: str, step_desc: str, msg: str, ctx: str) -> None:  # type: ignore[func-returns-value]
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
        main_fn = _load_functional_training_main()
        if main_fn is None:  # pragma: no cover - safety fallback
            raise RuntimeError("codex.training.main is unavailable")

        hydra_global_spec = importlib.util.find_spec("hydra.core.global_hydra")
        if hydra_global_spec is not None:
            global_hydra_module = importlib.import_module("hydra.core.global_hydra")
            global_hydra_cls = getattr(global_hydra_module, "GlobalHydra", None)
            if global_hydra_cls is not None and global_hydra_cls().is_initialized():
                global_hydra_cls.instance().clear()

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

    if _HAS_HYDRA and hydra is not None:

        @hydra.main(version_base="1.3", config_path="../../../configs", config_name="config")
        def main(cfg: DictConfig) -> None:  # pragma: no cover - simple dispatcher
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
                "hydra-core is required to use codex_ml.cli.main; "
                "install it with `pip install hydra-core`."
            )

    def cli(argv: list[str] | None = None) -> int:
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
            sys.argv = [sys.argv[0], *args, *overrides]
            try:
                main()
            except Exception as exc:  # pragma: no cover - logging path
                _log_error("STEP cli", "codex_ml.cli.main", str(exc), f"argv={args}")
                log_event(logger, "cli.finish", prog=sys.argv[0], status="error")
                raise
            log_event(logger, "cli.finish", prog=sys.argv[0], status="ok")
            return 0

    cli = cli

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(cli())
