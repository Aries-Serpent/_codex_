import json
from pathlib import Path

from codex_ml.tracking import init_experiment

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"
PARAMS_SCHEMA = json.loads((SCHEMA_DIR / "run_params.schema.json").read_text(encoding="utf-8"))
METRICS_SCHEMA = json.loads((SCHEMA_DIR / "run_metrics.schema.json").read_text(encoding="utf-8"))


def _is_type(value: object, type_name: str) -> bool:
    if type_name == "string":
        return isinstance(value, str)
    if type_name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if type_name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if type_name == "object":
        return isinstance(value, dict)
    if type_name == "array":
        return isinstance(value, list)
    if type_name == "null":
        return value is None
    if type_name == "boolean":
        return isinstance(value, bool)
    return False


def _validate(record: dict, schema: dict) -> None:
    for key in schema.get("required", []):
        assert key in record, f"missing key: {key}"
    properties = schema.get("properties", {})
    for key, spec in properties.items():
        if key not in record:
            continue
        value = record[key]
        type_spec = spec.get("type")
        if isinstance(type_spec, list):
            assert any(_is_type(value, t) for t in type_spec), f"{key} has invalid type"
        elif isinstance(type_spec, str):
            assert _is_type(value, type_spec), f"{key} has invalid type"
        const = spec.get("const")
        if const is not None:
            assert value == const, f"{key} expected const {const}, got {value}"


class DummyCfg:
    def __init__(self, outdir: Path) -> None:
        self.experiment = "exp"
        self.seed = 123
        self.batch_size = 4
        self.gradient_accumulation = 2
        self.cli_args = ["--epochs", "1"]
        self.cli_options = {"epochs": 1}
        self.config_dict = {"trainer": {"epochs": 1}}
        self.tracking = type(
            "T",
            (),
            {
                "tensorboard": False,
                "mlflow": False,
                "wandb": False,
                "output_dir": str(outdir),
            },
        )()


def _load_records(path: Path) -> list[dict]:
    content = path.read_text(encoding="utf-8").strip().splitlines()
    return [json.loads(line) for line in content if line.strip()]


def test_run_logger_schema(tmp_path: Path) -> None:
    cfg = DummyCfg(tmp_path)
    ctx = init_experiment(cfg)
    ctx.log_metric(step=1, split="train", metric="loss", value=0.5)
    ctx.finalize()

    params_records = _load_records(ctx.params_path)
    metrics_records = _load_records(ctx.metrics_path)
    assert params_records and metrics_records

    _validate(params_records[0], PARAMS_SCHEMA)
    _validate(metrics_records[0], METRICS_SCHEMA)

    derived = params_records[0]["derived"]
    assert derived["effective_batch_size"] == 8
    assert derived["seed"] == 123
    assert params_records[0]["cli"]["argv"] == ["--epochs", "1"]


def test_run_logger_custom_paths(tmp_path: Path) -> None:
    base = tmp_path / "run"
    cfg = DummyCfg(base)
    cfg.tracking = type(
        "T",
        (),
        {
            "tensorboard": False,
            "mlflow": False,
            "wandb": False,
            "output_dir": str(base),
            "ndjson_path": str(tmp_path / "custom" / "metrics.ndjson"),
            "params_path": str(tmp_path / "custom" / "params.ndjson"),
        },
    )()

    ctx = init_experiment(cfg)
    ctx.log_metric(step=0, split="train", metric="acc", value=0.9)
    ctx.finalize()

    assert Path(cfg.tracking.ndjson_path).exists()
    assert Path(cfg.tracking.params_path).exists()
