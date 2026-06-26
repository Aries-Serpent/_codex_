"""
Test Simple Dataset

Test module for simple dataset.
"""

from codex_ml.data.simple_dataset import Sample, SimpleDataset


def test_simple_dataset_deterministic_encoding():
    samples = [
        Sample(text="a", label=0),
        Sample(text="b", label=1),
        Sample(text="c", label=0),
    ]

    ds1 = SimpleDataset(samples, seed=7)
    ds2 = SimpleDataset(samples, seed=7)

    enc1 = ds1.encoded()
    enc2 = ds2.encoded()

    assert len(enc1) == len(enc2) == 3, "Enc1 must not be empty"
    assert [e.label for e in enc1] == [e.label for e in enc2], "Condition must be true"
    assert [e.tokens for e in enc1] == [e.tokens for e in enc2], "Condition must be true"
