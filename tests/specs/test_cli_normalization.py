from __future__ import annotations

import argparse


def _parser():
    p = argparse.ArgumentParser(prog="codex")
    sub = p.add_subparsers(dest="cmd", required=True)
    admin = sub.add_parser("repo_admin_bootstrap")
    admin.add_argument("--owner", required=True)
    admin.add_argument("--repo", required=True)
    admin.add_argument("--apply", action="store_true")
    metrics = sub.add_parser("metrics")
    msub = metrics.add_subparsers(dest="mcmd", required=True)
    ing = msub.add_parser("ingest")
    ing.add_argument("--input", required=True)
    ing.add_argument("--out-csv", required=True)
    summ = msub.add_parser("summary")
    summ.add_argument("--input", required=True)
    return p


def _parse(argv: list[str]) -> dict:
    ns = _parser().parse_args(argv)
    return vars(ns)


def test_flag_equivalence():
    a = _parse(["repo_admin_bootstrap", "--owner", "o", "--repo", "r"])
    b = _parse(["repo_admin_bootstrap", "--owner=o", "--repo=r"])
    assert a["cmd"] == b["cmd"] == "repo_admin_bootstrap"
    assert a["owner"] == b["owner"] == "o"
    assert a["repo"] == b["repo"] == "r"