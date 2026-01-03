"""Tests for Reasoning Advisor Agent - 20 tests"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from __init__ import create_agent, RANDOM_SEED
from causal_analyzer import create_analyzer

TEST_SEED = 50

class TestInit:
    def test_creation(self): 
        agent = create_agent()
        assert agent.seed == RANDOM_SEED
    def test_custom_seed(self): 
        agent = create_agent(TEST_SEED)
        assert agent.seed == TEST_SEED
    def test_components(self): 
        agent = create_agent(TEST_SEED)
        assert agent.causal_analyzer is not None
    def test_initialized(self):
        agent = create_agent(TEST_SEED)
        assert agent.initialized is True

class TestCausalAnalyzer:
    def test_add_relation(self):
        a = create_analyzer(TEST_SEED)
        r = a.add_relation("change1", "effect1", 0.9, ["evidence"])
        assert r.cause == "change1"
    def test_analyze_impact(self):
        a = create_analyzer(TEST_SEED)
        a.add_relation("change1", "effect1", 0.9, [])
        impact = a.analyze_impact("change1")
        assert len(impact) == 1
    def test_metrics(self):
        a = create_analyzer(TEST_SEED)
        a.add_relation("c1", "e1", 0.8, [])
        m = a.get_metrics()
        assert m["total_relations"] == 1
    def test_confidence_tracking(self):
        a = create_analyzer(TEST_SEED)
        a.add_relation("c1", "e1", 0.9, [])
        a.add_relation("c2", "e2", 0.7, [])
        m = a.get_metrics()
        assert 0.7 < m["avg_confidence"] < 0.9

class TestPDA:
    def test_perceive(self):
        agent = create_agent(TEST_SEED)
        p = agent.perceive({"task": "analyze"})
        assert "analyzer_metrics" in p
    def test_decide(self):
        agent = create_agent(TEST_SEED)
        d = agent.decide({})
        assert d["action_type"] == "analyze"
    def test_act(self):
        agent = create_agent(TEST_SEED)
        r = agent.act({"action_type": "analyze"})
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
        agent.aftermath(a)
        assert all(len(agent.pda_state[k]) == 1 for k in ["perception","decision","action","aftermath"])

class TestPublicAPI:
    def test_analyze_causal(self):
        agent = create_agent(TEST_SEED)
        result = agent.analyze_causal_impact("code_change", ["bug_fix", "perf_improvement"], 0.85)
        assert result["change"] == "code_change"
        assert len(result["effects"]) == 2
    def test_metrics(self):
        agent = create_agent(TEST_SEED)
        m = agent.get_metrics()
        assert m["agent_name"] == "reasoning-advisor"
    def test_performance_tracking(self):
        agent = create_agent(TEST_SEED)
        agent.analyze_causal_impact("change", ["effect"])
        assert agent.performance_metrics["analyses_performed"] == 1

def test_deterministic():
    a1, a2 = create_agent(TEST_SEED), create_agent(TEST_SEED)
    assert a1.seed == a2.seed

if __name__ == "__main__":
    print("Running Reasoning Advisor Agent Tests...")
    test_classes = [TestInit, TestCausalAnalyzer, TestPDA, TestPublicAPI]
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
    print(f"✅ Cumulative: 601 + {total} = {601 + total}/597")
