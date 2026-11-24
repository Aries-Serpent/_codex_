"""Offline workflow condition evaluation: no actual GitHub operations."""

from pathlib import Path

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
    jobs = workflow["jobs"]
    assert "approve-original" in jobs
    assert "cleanup-single-session" not in jobs
    approve_job = jobs["approve-original"]
    assert approve_job["permissions"]["actions"] == "write"
    assert "approve_pending_runs.py" in "\n".join(
        step.get("run", "") for step in approve_job["steps"]
    )


def test_approval_outputs_bind_actual_mutation_and_sha():
    workflow = yaml.safe_load(WORKFLOW.read_text())
    approve_job = workflow["jobs"]["approve-original"]
    step = next(
        step for step in approve_job["steps"] if "approve_pending_runs.py" in step.get("run", "")
    )
    assert "DRY_RUN" in step["env"]
    assert "PR_NUMBER" in step["env"]
    assert "TARGET_RUN_ID" in step["env"]
    assert "PR_NUMBER" in step["env"]


def test_actual_output_script_does_not_consume_denied_or_dry_run():
    script = Path("scripts/ci/approve_pending_runs.py").read_text(encoding="utf-8")
    assert "def _consume_once_grant" in script
    assert "if dry_run:" in script
    consume_pos = script.index("_consume_once_grant(")
    dry_run_pos = script.index("if dry_run:")
    assert dry_run_pos < consume_pos
