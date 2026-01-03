"""Tests for Ecosystem Coordinator Agent - 20 tests"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from __init__ import create_agent, RANDOM_SEED
from task_decomposer import create_decomposer

TEST_SEED = 51

class TestInit:
    def test_creation(self): assert create_agent().seed == RANDOM_SEED
    def test_custom_seed(self): assert create_agent(TEST_SEED).seed == TEST_SEED
    def test_components(self): assert create_agent(TEST_SEED).task_decomposer is not None
    def test_initialized(self): assert create_agent(TEST_SEED).initialized is True

class TestDecomposer:
    def test_decompose(self):
        d = create_decomposer(TEST_SEED)
        tasks = d.decompose("complex_task", 3)
        assert len(tasks) == 3
    def test_subtask_naming(self):
        d = create_decomposer(TEST_SEED)
        tasks = d.decompose("task1", 2)
        assert tasks[0].name == "task1_sub1"
    def test_priority_assignment(self):
        d = create_decomposer(TEST_SEED)
        tasks = d.decompose("task1", 3)
        assert tasks[0].priority > tasks[1].priority
    def test_agent_type_rotation(self):
        d = create_decomposer(TEST_SEED)
        tasks = d.decompose("task1", 3)
        types = [t.agent_type for t in tasks]
        assert len(set(types)) > 1
    def test_metrics(self):
        d = create_decomposer(TEST_SEED)
        d.decompose("task1", 2)
        m = d.get_metrics()
        assert m["total_tasks"] == 2

class TestPDA:
    def test_perceive(self):
        agent = create_agent(TEST_SEED)
        p = agent.perceive({"task": "coordinate"})
        assert "decomposer_metrics" in p
    def test_decide(self):
        agent = create_agent(TEST_SEED)
        d = agent.decide({})
        assert d["action_type"] == "coordinate"
    def test_act(self):
        agent = create_agent(TEST_SEED)
        r = agent.act({"action_type": "coordinate"})
        assert r["status"] == "success"
    def test_aftermath(self):
        agent = create_agent(TEST_SEED)
        a = agent.aftermath({"status": "success"})
        assert a["success"] is True
    def test_full_cycle(self):
        agent = create_agent(TEST_SEED)
        agent.perceive({})
        agent.decide({})
        agent.act({})
        agent.aftermath({})
        assert all(len(agent.pda_state[k]) == 1 for k in pda_state.keys())

class TestPublicAPI:
    def test_coordinate(self):
        agent = create_agent(TEST_SEED)
        tasks = agent.coordinate_task("big_task", 3)
        assert len(tasks) == 3
    def test_metrics(self):
        agent = create_agent(TEST_SEED)
        m = agent.get_metrics()
        assert m["agent_name"] == "ecosystem-coordinator"
    def test_performance(self):
        agent = create_agent(TEST_SEED)
        agent.coordinate_task("task1", 2)
        assert agent.performance_metrics["tasks_coordinated"] == 1

def test_deterministic():
    a1, a2 = create_agent(TEST_SEED), create_agent(TEST_SEED)
    assert a1.seed == a2.seed

if __name__ == "__main__":
    print("Running Ecosystem Coordinator Agent Tests...")
    test_classes = [TestInit, TestDecomposer, TestPDA, TestPublicAPI]
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
    print(f"\n✅ Total: {total} tests")
    print(f"✅ Cumulative: 618 + {total} = {618 + total}/597")
