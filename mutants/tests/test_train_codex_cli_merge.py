"""
Test Train Codex Cli Merge

Test module for train codex cli merge.
"""

import pytest

pytest.importorskip("transformers")

import argparse

from cli import train_codex


def test_merge_preserves_yaml_booleans_when_flag_absent():
    parser = train_codex.build_parser()
    args = parser.parse_args([])
    config = {"use_lora": True, "fp16": True}

    merged = train_codex._merge(args, config)

    assert merged["use_lora"] is True, "Condition must be true"
    assert merged["fp16"] is True, "Condition must be true"
    # Namespace should not include suppressed flags when not provided
    assert "use_lora" not in vars(args), "Condition must be true"
    assert "fp16" not in vars(args), "Condition must be true"


def test_merge_applies_explicit_cli_overrides():
    parser = train_codex.build_parser()
    args = parser.parse_args(["--use-lora", "--fp16", "--allow-remote"])
    config = {"use_lora": False, "fp16": False, "allow_remote": False}

    merged = train_codex._merge(args, config)

    assert merged["use_lora"] is True, "Condition must be true"
    assert merged["fp16"] is True, "Condition must be true"
    assert merged["allow_remote"] is True, "Condition must be true"


def test_merge_leaves_other_defaults_intact():
    namespace = argparse.Namespace(train_file=None, output_dir=None)
    merged = train_codex._merge(namespace, {"use_lora": False})
    assert merged["use_lora"] is False, "Condition must be true"
    assert "train_file" not in merged, "Condition must be true"
    assert "output_dir" not in merged, "Condition must be true"
