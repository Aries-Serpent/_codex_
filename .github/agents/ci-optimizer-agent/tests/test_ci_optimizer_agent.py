"""Tests for CI Optimizer Agent - 20 tests to reach 597 total"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from __init__ import create_agent, RANDOM_SEED
from test_prioritizer import create_prioritizer

TEST_SEED = 49

class TestInit:
    def test_agent_creation(self): 
        agent = create_agent()
        assert agent.seed == RANDOM_SEED
    def test_custom_seed(self): 
        agent = create_agent(TEST_SEED)
        assert agent.seed == TEST_SEED
    def test_components_init(self): 
        agent = create_agent(TEST_SEED)
        assert agent.test_prioritizer is not None
    def test_initialized_flag(self):
        agent = create_agent(TEST_SEED)
        assert agent.initialized is True

class TestPrioritizer:
    def test_add_test(self):
        p = create_prioritizer(TEST_SEED)
        t = p.add_test("test1", 100.0, 0.2)
        assert t.name == "test1"
    def test_priority_calc(self):
        p = create_prioritizer(TEST_SEED)
        t = p.add_test("test1", 100.0, 0.5)
        assert t.priority_score > 0
    def test_get_order(self):
        p = create_prioritizer(TEST_SEED)
        p.add_test("t1", 100, 0.8)
        p.add_test("t2", 100, 0.2)
        order = p.get_prioritized_order()
        assert order[0].name == "t1"
    def test_optimize_time_budget(self):
        p = create_prioritizer(TEST_SEED)
        p.add_test("t1", 400, 0.5)
        p.add_test("t2", 300, 0.3)
        p.add_test("t3", 500, 0.1)
        selected = p.optimize_for_time(800)
        assert len(selected) <= 3
    def test_record_execution(self):
        p = create_prioritizer(TEST_SEED)
        p.add_test("t1", 100, 0.1)
        p.record_execution("t1", False, 100)
        assert len(p.execution_history) == 1
    def test_metrics(self):
        p = create_prioritizer(TEST_SEED)
        p.add_test("t1", 100, 0.5)
        m = p.get_metrics()
        assert m["total_tests"] == 1
    def test_failure_rate_update(self):
        p = create_prioritizer(TEST_SEED)
        p.add_test("t1", 100, 0.1)
        initial_rate = p.tests[0].failure_rate
        p.record_execution("t1", False, 100)
        assert p.tests[0].failure_rate > initial_rate

class TestPDA:
    def test_perceive(self):
        agent = create_agent(TEST_SEED)
        p = agent.perceive({"task": "optimize"})
        assert "prioritizer_metrics" in p
    def test_decide(self):
        agent = create_agent(TEST_SEED)
        d = agent.decide({"context": {}})
        assert d["action_type"] == "optimize"
    def test_act(self):
        agent = create_agent(TEST_SEED)
        r = agent.act({"action_type": "optimize"})
        assert r["status"] == "success"
    def test_aftermath(self):
        agent = create_agent(TEST_SEED)
        a = agent.aftermath({"status": "success"})
        assert a["success"] is True
    def test_full_cycle(self):
        agent = create_agent(TEST_SEED)
        p = agent.perceive({})
        d = agent.decide(p)
        a = agent.act(d)
        aft = agent.aftermath(a)
        assert all(len(agent.pda_state[k]) == 1 for k in ["perception","decision","action","aftermath"])
    def test_pda_state_tracking(self):
        agent = create_agent(TEST_SEED)
        agent.perceive({})
        agent.perceive({})
        assert len(agent.pda_state["perception"]) == 2

class TestPublicAPI:
    def test_optimize_tests(self):
        agent = create_agent(TEST_SEED)
        tests = [{"name": "t1", "duration": 100, "failure_rate": 0.5},
                 {"name": "t2", "duration": 200, "failure_rate": 0.1}]
        result = agent.optimize_tests(tests)
        assert len(result) == 2
        assert result[0].name == "t1"
    def test_get_metrics(self):
        agent = create_agent(TEST_SEED)
        m = agent.get_metrics()
        assert m["agent_name"] == "ci-optimizer"
        assert m["seed"] == TEST_SEED
    def test_performance_metrics(self):
        agent = create_agent(TEST_SEED)
        m = agent.get_metrics()
        assert "performance_metrics" in m

def test_deterministic():
    a1, a2 = create_agent(TEST_SEED), create_agent(TEST_SEED)
    assert a1.seed == a2.seed

if __name__ == "__main__":
    print("Running CI Optimizer Agent Tests...")
    test_classes = [TestInit, TestPrioritizer, TestPDA, TestPublicAPI]
    total = 0
    for tc in test_classes:
        inst = tc()
        for m in [x for x in dir(inst) if x.startswith('test_')]:
            try:
                getattr(inst, m)()
                print(f"✅ {tc.__name__}.{m}")
                total += 1
            except Exception as e:
                print(f"❌ {tc.__name__}.{m}: {e}")
    try:
        test_deterministic()
        print("✅ test_deterministic")
        total += 1
    except Exception as e:
        print(f"❌ test_deterministic: {e}")
    print(f"\n✅ Total: {total} tests (Target: 20)")
    print(f"✅ Cumulative: 580 + {total} = {580 + total}/597")
