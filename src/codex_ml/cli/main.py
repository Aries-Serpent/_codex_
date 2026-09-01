"""Codex ML command-line interfaces."""

from __future__ import annotations

import logging

from codex.logging.adapter import get_default_logger

logger = logging.getLogger(__name__)

import importlib
import importlib.resources as importlib_resources
import importlib.util
import json
import os
import sys
import textwrap
from collections.abc import Iterable
from pathlib import Path
from types import ModuleType
from typing import Annotated, Any, Optional

yaml: ModuleType | None
try:  # Optional dependency used for loading curriculum presets
    import yaml as _yaml_module

    yaml = _yaml_module
except (IOError, OSError, ModuleNotFoundError, ImportError):  # pragma: no cover - PyYAML is optional
    yaml = None


def _load_typer():
    spec = importlib.util.find_spec("typer")
    if spec is None:
        return None
    module = importlib.import_module("typer")
    return module if hasattr(module, "Typer") else None


typer = _load_typer()

# Hoist evaluate_datasets to module scope so it can be patched by tests via
# monkeypatch.setattr("codex_ml.cli.main.evaluate_datasets", ...).
try:  # pragma: no cover - evaluation is optional
    from codex_ml.eval.eval_runner import evaluate_datasets
except (ImportError, AttributeError):  # pragma: no cover

    def evaluate_datasets(*args, **kwargs) -> None:
        return None


if typer is not None:
    app = typer.Typer(
        help="Codex ML CLI\n\nPowered by Hydra (install hydra-core for advanced configuration).",
        add_completion=False,
    )

    _tokenizer_flag = os.getenv("CODEX_ENABLE_TOKENIZER_CLI", "1").lower()
    if _tokenizer_flag in {"1", "true", "yes", "on"}:
        try:  # pragma: no cover - optional import, guard mirrors Typer discovery
            from codex_ml.cli import tokenizer as tokenizer_cli
            app.add_typer(tokenizer_cli.app, name="tokenizer")
        except (ImportError, AttributeError) as e:
            error_type = type(e).__name__
            get_default_logger().debug("Exception: <ERROR_TYPE>")
            get_default_logger().warning("Exception: <ERROR_TYPE>", exc_info=True)

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
        config: Optional[str] = typer.Option(None, "--config", help="Path to training config YAML"),
        model_name: str = typer.Option("dummy", "--model-name", help="Model name or identifier"),
        epochs: int = typer.Option(1, "--epochs", help="Number of training epochs"),
        batch_size: int = typer.Option(8, "--batch-size", help="Batch size"),
        grad_accum: int = typer.Option(1, "--grad-accum", help="Gradient accumulation steps"),
        learning_rate: float = typer.Option(3e-4, "--learning-rate", help="Learning rate"),
        seed: int = typer.Option(42, "--seed", help="Random seed"),
        output_dir: str = typer.Option("runs/unified", "--output-dir", help="Output directory"),
        backend: Optional[str] = typer.Option(
            None, "--backend", help="Backend strategy (functional or legacy)"
        ),
        mlflow_enable: bool = typer.Option(False, "--mlflow", help="Enable MLflow tracking"),
        wandb_enable: bool = typer.Option(False, "--wandb", help="Enable Weights & Biases logging"),
        grad_clip_norm: Optional[float] = typer.Option(
            None, "--grad-clip-norm", help="Gradient clipping norm"
        ),
        dtype: str = typer.Option("fp32", "--dtype", help="Data type (fp32, fp16, bf16)"),
        resume_from: Optional[str] = typer.Option(
            None, "--resume-from", help="Checkpoint path to resume from"
        ),
        corpora: Optional[list[str]] = typer.Option(
            None,
            "--corpus",
            "-c",
            help="Reasoning corpus to include (see codex_ml.data.list_reasoning_corpora).",
        ),
        corpus_root: Optional[str] = typer.Option(
            None,
            "--corpus-root",
            help="Override root directory used to resolve reasoning corpora.",
        ),
        curriculum: Optional[str] = typer.Option(
            None,
            "--curriculum",
            help="Continual curriculum preset from configs/training/continual.",
        ),
        difficulty_target: Optional[str] = typer.Option(
            None,
            "--difficulty-target",
            help="Override target difficulty for curriculum schedules (e.g. easy, hard, adaptive).",
        ),
        rehearsal_ratio: Optional[float] = typer.Option(
            None,
            "--rehearsal-ratio",
            help="Override replay ratio for interleaved rehearsal phases (0-1).",
        ),
        strict_corpus_validation: bool = typer.Option(
            True,
            "--strict-corpus-validation/--no-strict-corpus-validation",
            help="Fail when selected corpora are missing or checksums mismatch.",
        ),
    ) -> None:
        """Start a training run. Config file values are overridden by CLI options."""
        from codex_ml.training.unified_training import (
            UnifiedTrainingConfig,
            run_unified_training,
        )

        cfg_data = _load_training_config(config) if config else {}
        train_cfg = cfg_data.get("training", cfg_data) if isinstance(cfg_data, dict) else {}
        data_cfg = cfg_data.get("data", {}) if isinstance(cfg_data, dict) else {}
        tracking_cfg = cfg_data.get("tracking", {}) if isinstance(cfg_data, dict) else {}

        continual_cfg: Optional[dict[str, Any]] = None
        if isinstance(train_cfg, dict):
            raw_continual = train_cfg.get("continual")
            if isinstance(raw_continual, dict):
                continual_cfg = dict(raw_continual)
        if continual_cfg is None and isinstance(cfg_data, dict):
            raw_continual = cfg_data.get("continual")
            if isinstance(raw_continual, dict):
                continual_cfg = dict(raw_continual)

        def _load_curriculum_preset(name: str) -> dict[str, Any]:
            if yaml is None:
                raise typer.BadParameter(
                    "PyYAML is required to load curriculum presets; install with `pip install pyyaml`."  # noqa: E501
                )
            preset_text: Optional[str] = None

            try:
                resource_root = importlib_resources.files("configs").joinpath(
                    "training", "continual"
                )
            except (ModuleNotFoundError, AttributeError):
                resource_root = None

            if resource_root is not None:
                resource_candidate = resource_root.joinpath(f"{name}.yaml")
                if resource_candidate.is_file():
                    preset_text = resource_candidate.read_text(encoding="utf-8")

            if preset_text is None:
                cli_path = Path(__file__).resolve()
                search_roots: list[Path] = []
                for depth in (2, 3):
                    try:
                        root = cli_path.parents[depth]
                    except IndexError as e:
                        type(e).__name__
                        get_default_logger().debug("IndexError: <ERROR_TYPE>")
                        get_default_logger().warning("IndexError: <ERROR_TYPE>", exc_info=True)
                        continue
                    search_roots.append(root / "configs" / "training" / "continual")

                for root in search_roots:
                    candidate_path = root / f"{name}.yaml"
                    if candidate_path.is_file():
                        preset_text = candidate_path.read_text(encoding="utf-8")
                        break

            if preset_text is None:
                raise typer.BadParameter(f"Unknown continual curriculum preset '{name}'.")

            loaded = yaml.safe_load(preset_text) or {}
            if not isinstance(loaded, dict):
                raise typer.BadParameter(
                    f"Curriculum preset '{name}' must decode to a mapping, received {type(loaded).__name__}."  # noqa: E501
                )
            if "continual" in loaded and isinstance(loaded["continual"], dict):
                return dict(loaded["continual"])
            return dict(loaded)

        if curriculum:
            continual_cfg = _load_curriculum_preset(curriculum)

        def _int_value(value: Any) -> Optional[int]:
            try:
                return None if value is None else int(value)
            except (TypeError, ValueError):
                get_default_logger().debug("Exception caught, returning", exc_info=True)
                return None

        actual_epochs = _int_value(
            _value_from_config(epochs, 1, train_cfg, "epochs", "num_train_epochs")
        )
        if actual_epochs is None:
            actual_epochs = epochs
        actual_grad_accum = _int_value(
            _value_from_config(grad_accum, 1, train_cfg, "gradient_accumulation_steps")
        )
        if actual_grad_accum is None:
            actual_grad_accum = grad_accum
        actual_model_name = str(_value_from_config(model_name, "dummy", train_cfg, "model_name"))
        actual_lr = float(_value_from_config(learning_rate, 3e-4, train_cfg, "learning_rate"))
        actual_batch_size = _int_value(_value_from_config(batch_size, 8, train_cfg, "batch_size"))
        if actual_batch_size is None:
            actual_batch_size = batch_size
        actual_seed = _int_value(_value_from_config(seed, 42, train_cfg, "seed"))
        if actual_seed is None:
            actual_seed = seed
        actual_output_dir = str(
            _value_from_config(output_dir, "runs/unified", train_cfg, "output_dir")
        )
        actual_backend = backend or train_cfg.get("backend")
        actual_grad_clip = _value_from_config(grad_clip_norm, None, train_cfg, "grad_clip_norm")
        actual_dtype = str(_value_from_config(dtype, "fp32", train_cfg, "dtype"))
        actual_resume = resume_from or train_cfg.get("resume_from")

        if continual_cfg is not None:
            if difficulty_target is not None:
                curriculum_section = continual_cfg.setdefault("curriculum", {})
                curriculum_section["target_difficulty"] = str(difficulty_target)
            if rehearsal_ratio is not None:
                try:
                    ratio_value = float(rehearsal_ratio)
                except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
                    raise typer.BadParameter("rehearsal-ratio must be numeric") from exc
                if not 0.0 <= ratio_value <= 1.0:
                    raise typer.BadParameter("rehearsal-ratio must be between 0 and 1")
                rehearsal_section = continual_cfg.setdefault("rehearsal", {})
                rehearsal_section["default_ratio"] = ratio_value
                for phase in continual_cfg.get("phases", []):
                    if isinstance(phase, dict) and "replay_ratio" in phase:
                        phase["replay_ratio"] = ratio_value

        reasoning_extra: dict[str, Any] = {}
        selected_corpora = list(corpora or [])
        if selected_corpora:
            from codex_ml.data.reasoning_manifest import (
                ReasoningCorpusError,
                build_corpus_selection,
            )

            try:
                selection_payload = build_corpus_selection(
                    selected_corpora,
                    root=corpus_root,
                    strict=strict_corpus_validation,
                )
            except ReasoningCorpusError as exc:  # pragma: no cover - validation error
                raise typer.BadParameter(str(exc)) from exc

            reasoning_extra = dict(selection_payload)
            reasoning_extra["requested"] = selected_corpora
            reasoning_extra["strict_validation"] = strict_corpus_validation
            if not strict_corpus_validation:
                failures = [
                    corpus
                    for corpus in reasoning_extra.get("corpora", [])
                    if corpus.get("status") != "ok"
                ]
                if failures:
                    typer.echo(
                        json.dumps(
                            {
                                "warning": "corpus validation issues",
                                "corpora": failures,
                            }
                        ),
                        err=True,
                    )

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
            extra={
                **({"data": data_cfg} if isinstance(data_cfg, dict) and data_cfg else {}),
                **(
                    {"tracking": tracking_cfg}
                    if isinstance(tracking_cfg, dict) and tracking_cfg
                    else {}
                ),
                **({"reasoning": reasoning_extra} if reasoning_extra else {}),
            },
            continual=continual_cfg or None,
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
            Optional[list[str]],
            typer.Option(
                "--override",
                help="Additional config overrides (currently not used)",
                show_default=False,
            ),
        ] = None,
    ) -> None:
        """Resume training from a checkpoint."""
        from codex_ml.training.unified_training import (
            UnifiedTrainingConfig,
            run_unified_training,
        )

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
    def package_service(
        model_dir: Path = typer.Argument(..., help="Path to the trained model directory"),
        output: Path = typer.Option(
            Path("artifacts/packages/service.tar.gz"),
            "--output",
            help="Path to write the packaged archive",
        ),
        metadata_json: Optional[str] = typer.Option(
            None,
            "--metadata-json",
            help="Optional JSON metadata to include in the package",
        ),
        prompt: Optional[str] = typer.Option(None, "--prompt", help="Prompt to scan for safety"),
        secret: Optional[list[str]] = typer.Option(
            None,
            "--secret",
            help="Secret names to load from the offline store",
        ),
    ) -> None:
        """Package a model directory into an offline deployable tarball."""

        from codex_ml.deployment.package import build_service_package

        try:
            meta_payload = json.loads(metadata_json) if metadata_json else {}
            if not isinstance(meta_payload, dict):
                raise ValueError("metadata must decode to a JSON object")
        except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
            type(exc).__name__
            get_default_logger().debug("Exception: <ERROR_TYPE>")
            raise typer.BadParameter(str(exc)) from exc

        result = build_service_package(
            model_dir=model_dir,
            output_path=output,
            metadata=meta_payload,
            prompt=prompt,
            secret_names=secret,
        )
        typer.echo(json.dumps(result, indent=2, sort_keys=True))

    @app.command()
    def version() -> None:
        """Print the Codex ML package version."""
        import codex_ml

        typer.echo(getattr(codex_ml, "__version__", "unknown"))

    @app.command()
    def info() -> None:
        """Show environment and configuration info."""
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

    def _typer_cli_wrapper(args: Optional[list[str]] = None) -> int:
        """Wrapper around Typer app to handle --version/-V before Typer processes args."""
        import sys

        argv = args if args is not None else sys.argv[1:]

        # Handle --version and -V before Typer sees them
        if "--version" in argv or "-V" in argv:
            from codex import __version__ as codex_version

            get_default_logger().info(f"codex-ml-cli {codex_version}")
            return 0

        # Let Typer handle the rest
        try:
            app(args)
            return 0
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 0
            return code if code is not None else 0

    cli = _typer_cli_wrapper

    def run_training(cfg, output_dir=None) -> None:
        """Module-level stub for patching in tests (typer branch).

        The typer ``train`` command implements training directly; this stub
        ensures ``@patch("codex_ml.cli.main.run_training")`` is valid when
        typer is available.
        """

else:
    from typing import Any

    from codex_ml.codex_structured_logging import (
        ArgparseJSONParser,
        capture_exceptions,
        init_json_logging,
        log_event,
        run_cmd,
    )
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
    except (ImportError, AttributeError):  # pragma: no cover - optional
        DictConfig = Any
        OmegaConf = None
    try:  # pragma: no cover - optional dependency
        from codex_digest.error_capture import log_error as _log_error
    except (ImportError, AttributeError):  # pragma: no cover

        def _log_error(step_no: str, step_desc: str, msg: str, ctx: str) -> None:  
            return None

    # Module-level variable to cache functional training main for testing/mocking
    _functional_training_main = None

    def _load_functional_training_main():
        """Load functional training entry point (cached at module level)."""
        global _functional_training_main
        if _functional_training_main is None:
            try:
                from codex.training import main as _functional_training
            except (ImportError, AttributeError):
                get_default_logger().debug(
                    "codex.training.main unavailable; functional training disabled"
                )
                _functional_training_main = None
            else:
                _functional_training_main = _functional_training
        return _functional_training_main

    def run_training(cfg: Optional[DictConfig], output_dir: Optional[str] = None) -> None:  
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

    if _HAS_HYDRA and hydra is not None:

        @hydra.main(version_base="1.3", config_path="../../../configs", config_name="config")
        def main(cfg: DictConfig) -> None:  # pragma: no cover - simple dispatcher
            logger = init_json_logging()
            arg_list = sys.argv[1:]
            with capture_exceptions(logger):
                log_event(logger, "cli.start", prog=sys.argv[0], args=arg_list)
                text = OmegaConf.to_yaml(cfg)
                get_default_logger().info(text)
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
                        # Lazy import: only load heavy pipeline module if this step is actually used
                        try:
                            from codex_ml.pipeline import (
                                run_codex_pipeline_from_config,
                            )
                        except (ImportError, ModuleNotFoundError) as e:
                            error_msg = textwrap.dedent(
                                """\
                                Pipeline module is not available.
                                Ensure you have installed codex-ml with the full profile:
                                  pip install codex-ml[full]
                                  or
                                  pip install codex-ml[runtime]
                                """
                            )
                            get_default_logger().error(f"{error_msg}\nOriginal error: {e}")
                            raise ImportError(error_msg) from e
                        
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
                            get_default_logger().info(json.dumps(summary, indent=2))
                log_event(logger, "cli.finish", prog=sys.argv[0], status="ok")
                sys.exit(0)

    else:  # pragma: no cover - hydra missing

        def main(cfg: Any | None = None) -> None:
            raise ImportError(
                "hydra-core is required to use codex_ml.cli.main; "
                "install it with `pip install hydra-core`."
            )

    def cli(argv: Optional[list[str]] = None) -> int:
        logger = init_json_logging()
        args = list(argv) if argv is not None else sys.argv[1:]

        with capture_exceptions(logger):
            log_event(logger, "cli.start", prog=sys.argv[0], args=args)
            if "--version" in args or "-V" in args:
                from codex import __version__ as codex_version

                get_default_logger().info(f"codex-ml-cli {codex_version}")
                log_event(logger, "cli.finish", prog=sys.argv[0], status="ok")
                return 0
            if "--help" in args or "-h" in args:
                get_default_logger().info("codex_ml.cli.main — Hydra-managed pipeline entrypoint")
                get_default_logger().info("Powered by Hydra (install hydra-core)")
                if not _HAS_HYDRA:
                    guidance = (
                        "Codex ML CLI is powered by Hydra but hydra-core is not installed.\n"
                        "codex-ml-cli requires hydra-core for configuration loading.\n"
                        "Install it with `pip install hydra-core` to access the managed pipeline."
                    )
                    print("Powered by Hydra (install hydra-core)", file=sys.stderr)
                    get_default_logger().error(guidance)
                log_event(logger, "cli.finish", prog=sys.argv[0], status="ok")
                sys.exit(0)
            if not _HAS_HYDRA:
                guidance = (
                    "Codex ML CLI is powered by Hydra but hydra-core is not installed.\n"
                    "codex-ml-cli requires hydra-core for configuration loading.\n"
                    "Install it with `pip install hydra-core` to access the managed pipeline."
                )
                get_default_logger().info("Powered by Hydra (install hydra-core)")
                get_default_logger().error(guidance)
                log_event(
                    logger,
                    "cli.finish",
                    prog=sys.argv[0],
                    status="ok",
                    error="hydra-core missing",
                )
                sys.exit(0)
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
            except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - logging path
                _log_error("STEP cli", "codex_ml.cli.main", str(exc), f"argv={args}")
                log_event(logger, "cli.finish", prog=sys.argv[0], status="error")
                raise
            log_event(logger, "cli.finish", prog=sys.argv[0], status="ok")
            return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(cli())
