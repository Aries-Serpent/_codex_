from agents.self_healing import SelfHealingEngine
from agents.workflow_navigator import WorkflowNavigator
from cognitive_brain.base import Planner


def test_ooda_inheritance():
    assert issubclass(SelfHealingEngine, Planner)
    assert issubclass(WorkflowNavigator, Planner)


def test_self_healing_ooda():
    engine = SelfHealingEngine()
    obs = engine.observe({"log_output": "error", "run_checks": False})
    assert "issues" in obs.data, "Data must not be empty"

    ori = engine.orient(obs)
    assert ori.analysis in ["CRITICAL", "WARNING"]

    dec = engine.decide(ori)
    assert dec.action == "execute_remediation", "action is not valid"

    act = engine.act(dec)
    assert act.success is True, "success is not valid"


def test_workflow_navigator_ooda():
    nav = WorkflowNavigator()
    obs = nav.observe({"event": "audit"})
    assert "trigger" in obs.data, "Data must not be empty"

    ori = nav.orient(obs)
    assert "next_token" in ori.context, "Condition must be true"

    dec = nav.decide(ori)
    assert dec.action.startswith("execute_workflow_step"), "Condition must be true"

    act = nav.act(dec)
    assert act.success is True, "success is not valid"
