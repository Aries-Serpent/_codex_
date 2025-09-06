from pathlib import Path

from codex_ml.tracking import init_experiment


class DummyCfg:
    def __init__(self, outdir: Path) -> None:
        self.experiment = "exp"
        self.model = "m"
        self.dataset = "d"
        self.seed = 1
        self.precision = "fp32"
        self.lora = False
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


def test_init_experiment_tags(tmp_path: Path) -> None:
    cfg = DummyCfg(tmp_path)
    ctx = init_experiment(cfg)
    assert ctx.tags["model"] == "m"
    assert ctx.experiment_name == "exp"
    ctx.finalize()
