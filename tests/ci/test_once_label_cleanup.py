"""Offline workflow condition evaluation: no actual GitHub operations."""

import ast
import json
import subprocess
import sys
from itertools import product
from pathlib import Path

import pytest
import yaml

WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/auto-approve-workflows.yml"


def _condition(expression, values):
    for key in sorted(values, key=len, reverse=True):
        expression = expression.replace(key, repr(values[key]))
    expression = expression.replace("&&", " and ").replace("||", " or ").replace("!", "not ")
    expression = expression.replace("not =", "!=")

    def visit(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return not visit(node.operand)
        if isinstance(node, ast.BoolOp):
            values = [visit(value) for value in node.values]
            return all(values) if isinstance(node.op, ast.And) else any(values)
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            left, right = visit(node.left), visit(node.comparators[0])
            if isinstance(node.ops[0], ast.Eq):
                return left == right
            if isinstance(node.ops[0], ast.NotEq):
                return left != right
        raise AssertionError(f"unsupported workflow expression: {ast.dump(node)}")

    return visit(ast.parse(expression.strip(), mode="eval").body)


def test_cleanup_truth_table_requires_actual_success_not_dry_run():
    workflow = yaml.safe_load(WORKFLOW.read_text())
    condition = workflow["jobs"]["cleanup-single-session"]["if"]
    for cancelled, result, approved, dry_run, proceed, source in product(
        (True, False),
        ("success", "failure", "cancelled", "skipped"),
        ("true", "false", ""),
        ("true", "false", ""),
        ("true", "false"),
        ("self-approve-pending-runs", "trigger-on-approval", "other"),
    ):
        values = {
            "cancelled()": cancelled,
            "needs.execute-approval.result": result,
            "needs.execute-approval.outputs.approved_any": approved,
            "github.event.inputs.dry_run": dry_run,
            "needs.evaluate-approval.outputs.should_proceed": proceed,
            "github.event.inputs.approval_source": source,
        }
        assert _condition(condition, values) == (
            not cancelled
            and result == "success"
            and approved == "true"
            and dry_run != "true"
            and proceed == "true"
            and source in ("self-approve-pending-runs", "trigger-on-approval")
        )


def test_approval_outputs_bind_actual_mutation_and_sha():
    workflow = yaml.safe_load(WORKFLOW.read_text())
    execution = workflow["jobs"]["execute-approval"]
    assert "steps.scoped_approval.outputs.approved_any" in execution["outputs"]["approved_any"]
    step = next(step for step in execution["steps"] if step.get("id") == "scoped_approval")
    script = step["run"].split("python3 - <<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
    compile(script, "approval-output", "exec")
    cleanup = workflow["jobs"]["cleanup-single-session"]["steps"][0]
    assert "needs.execute-approval.outputs.approved_sha" in cleanup["env"]["APPROVED_SHA"]
    assert cleanup["run"].index('"$CURRENT_SHA" != "$APPROVED_SHA"') < cleanup["run"].index(
        "gh pr edit"
    )


@pytest.mark.parametrize(
    "decisions,expected",
    [
        ([], False),
        ([{"outcome": "dry-run", "pr": "1", "rule": "authorized", "head_sha": "a" * 40}], False),
        ([{"outcome": "denied", "pr": "1", "rule": "missing-review", "head_sha": "a" * 40}], False),
        ([{"outcome": "skipped", "pr": "1", "rule": "authorized", "head_sha": "a" * 40}], False),
        ([{"outcome": "approved", "pr": "1", "rule": "authorized", "head_sha": "a" * 40}], True),
        ([{"outcome": "approved", "pr": "2", "rule": "authorized", "head_sha": "a" * 40}], False),
        (
            [
                {"outcome": "approved", "pr": "1", "rule": "authorized", "head_sha": sha}
                for sha in ("a" * 40, "b" * 40)
            ],
            False,
        ),
    ],
)
def test_actual_output_script_does_not_consume_denied_or_dry_run(tmp_path, decisions, expected):
    workflow = yaml.safe_load(WORKFLOW.read_text())
    step = next(
        step
        for step in workflow["jobs"]["execute-approval"]["steps"]
        if step.get("id") == "scoped_approval"
    )
    script = step["run"].split("python3 - <<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
    (tmp_path / "approval-decision.json").write_text(json.dumps({"decisions": decisions}))
    output = tmp_path / "output"
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        env={"GITHUB_OUTPUT": str(output), "PR_NUMBER": "1"},
        capture_output=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert output.read_text().splitlines()[0] == f"approved_any={str(expected).lower()}"
    assert ("approved_sha=" in output.read_text()) == expected
