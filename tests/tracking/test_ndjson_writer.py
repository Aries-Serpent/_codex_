import json
from pathlib import Path

from codex_ml.tracking import init_experiment


class DummyCfg:
    def __init__(self, outdir: Path) -> None:
        self.experiment = "exp"
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


def test_ndjson_basic(tmp_path: Path) -> None:
    cfg = DummyCfg(tmp_path)
    ctx = init_experiment(cfg)
    ctx.log_metric(step=1, split="train", metric="loss", value=1.23)
    ctx.finalize()
    data = (tmp_path / "metrics.ndjson").read_text().strip().splitlines()
    row = json.loads(data[0])
    assert row["metric"] == "loss"
    assert row["value"] == 1.23
    assert row["schema"] == "v1"
