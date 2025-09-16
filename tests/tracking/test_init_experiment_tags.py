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


def test_init_experiment_creates_unique_run_dir(tmp_path: Path) -> None:
    ctx1 = init_experiment(DummyCfg(tmp_path))
    ctx2 = init_experiment(DummyCfg(tmp_path))
    try:
        assert ctx1.run_dir != ctx2.run_dir
        assert ctx1.run_dir.parent == tmp_path
        assert ctx2.run_dir.parent == tmp_path
    finally:
        ctx1.finalize()
        ctx2.finalize()
