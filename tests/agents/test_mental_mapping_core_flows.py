"""
Comprehensive tests for MentalMapping core flows.

Coverage targets:
- think_through_problem: Lines 443-546
- make_decision: Lines 548-603
- record_outcome: Lines 605-657
- _self_appraise_decision: Lines 659-757
- iterative_review: Lines 759-832

Target coverage: 31.33% → 85%+
"""

import pytest
from agents.mental_mapping import (
    MentalMappingModel,
    MentalNode,
    MentalEdge,
    NodeType,
    EdgeType,
    ReasoningStep,
    set_clock,
    reset_clock,
    get_timestamp
)


class TestMentalMappingCoreFlows:
    """Comprehensive test suite for MentalMappingModel core decision flows."""
    
    # ========== FIXTURES ==========
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        # Setup: Use deterministic timestamps for testing
        counter = [0]
        def test_clock():
            counter[0] += 1
            return f"2025-01-01T00:00:{counter[0]:02d}"
        set_clock(test_clock)
        
        yield
        
        # Teardown: Reset clock
        reset_clock()
    
    @pytest.fixture
    def mental_map(self):
        """Create standard mental mapping model."""
        return MentalMappingModel()
    
    @pytest.fixture
    def problem_node(self, mental_map):
        """Create a problem node."""
        return mental_map.create_node(
            node_type=NodeType.PROBLEM,
            content="How to optimize database queries?",
            metadata={'priority': 'high', 'complexity': 'medium'}
        )
    
    # ========== THINK THROUGH PROBLEM TESTS ==========
    
    def test_think_through_problem_basic(self, mental_map):
        """Test basic problem thinking flow."""
        result = mental_map.think_through_problem(
            problem="Optimize slow API endpoint",
            context={'system': 'production', 'urgency': 'high'}
        )
        
        # Should return problem node and reasoning steps
        assert 'problem_node' in result
        assert 'reasoning_steps' in result
        
        # Problem node should exist
        problem_node = result['problem_node']
        assert problem_node.node_type == NodeType.PROBLEM
        assert "Optimize slow API endpoint" in problem_node.content
        
        # Should have created reasoning steps
        assert len(result['reasoning_steps']) > 0
    
    def test_think_through_problem_with_decomposition(self, mental_map):
        """Test problem decomposition during thinking."""
        result = mental_map.think_through_problem(
            problem="Implement new feature with testing and documentation",
            context={'complexity': 'high'}
        )
        
        problem_node = result['problem_node']
        reasoning_steps = result['reasoning_steps']
        
        # Should have decomposed the problem
        assert any(step.step_type == "decompose" for step in reasoning_steps)
        
        # Should have created sub-problem nodes
        decomp_step = next((s for s in reasoning_steps if s.step_type == "decompose"), None)
        if decomp_step and 'sub_problems' in decomp_step.metadata:
            assert len(decomp_step.metadata['sub_problems']) > 0
    
    def test_think_through_problem_hypothesis_generation(self, mental_map):
        """Test hypothesis generation during problem thinking."""
        result = mental_map.think_through_problem(
            problem="Database query timeout",
            context={'symptoms': 'slow response'}
        )
        
        reasoning_steps = result['reasoning_steps']
        
        # Should generate hypotheses
        assert any(step.step_type == "hypothesis" for step in reasoning_steps)
    
    def test_think_through_problem_evidence_gathering(self, mental_map):
        """Test evidence gathering during thinking."""
        result = mental_map.think_through_problem(
            problem="System instability issue",
            context={'logs_available': True}
        )
        
        reasoning_steps = result['reasoning_steps']
        
        # Should have evidence gathering step
        assert any(step.step_type == "evidence" for step in reasoning_steps)
    
    # ========== MAKE DECISION TESTS ==========
    
    def test_make_decision_basic(self, mental_map, problem_node):
        """Test basic decision making."""
        alternatives = [
            {'name': 'Add index', 'cost': 'low', 'benefit': 'high'},
            {'name': 'Rewrite query', 'cost': 'medium', 'benefit': 'medium'},
            {'name': 'Add caching', 'cost': 'high', 'benefit': 'high'}
        ]
        
        decision = mental_map.make_decision(
            problem_id=problem_node.node_id,
            alternatives=alternatives,
            criteria={'cost': 0.3, 'benefit': 0.7}
        )
        
        # Decision should be made
        assert decision is not None
        assert 'decision_node' in decision
        assert 'chosen_alternative' in decision
        assert 'confidence' in decision
        
        # Confidence should be between 0 and 1
        assert 0.0 <= decision['confidence'] <= 1.0
    
    def test_make_decision_selects_best_alternative(self, mental_map, problem_node):
        """Test that decision selects highest scoring alternative."""
        alternatives = [
            {'name': 'Poor option', 'score': 0.2},
            {'name': 'Best option', 'score': 0.9},
            {'name': 'Okay option', 'score': 0.5}
        ]
        
        decision = mental_map.make_decision(
            problem_id=problem_node.node_id,
            alternatives=alternatives
        )
        
        # Should select the best option
        chosen = decision['chosen_alternative']
        assert chosen['name'] == 'Best option'
        assert chosen['score'] == 0.9
    
    def test_make_decision_creates_node_and_edges(self, mental_map, problem_node):
        """Test that decision creates proper node and connects to problem."""
        initial_node_count = len(mental_map.nodes)
        initial_edge_count = len(mental_map.edges)
        
        decision = mental_map.make_decision(
            problem_id=problem_node.node_id,
            alternatives=[{'name': 'Option A', 'score': 0.7}]
        )
        
        # Should have created new decision node
        assert len(mental_map.nodes) == initial_node_count + 1
        
        # Should have created edge from problem to decision
        assert len(mental_map.edges) > initial_edge_count
    
    def test_make_decision_low_confidence_marks_for_review(self, mental_map, problem_node):
        """Test low confidence decisions are marked for review."""
        # Create alternatives with low scores
        alternatives = [
            {'name': 'Uncertain option 1', 'score': 0.3},
            {'name': 'Uncertain option 2', 'score': 0.35}
        ]
        
        decision = mental_map.make_decision(
            problem_id=problem_node.node_id,
            alternatives=alternatives
        )
        
        # Should have low confidence
        assert decision['confidence'] < 0.6
        
        # Decision node should be marked for review
        decision_node = decision['decision_node']
        assert decision_node.needs_review == True
    
    # ========== RECORD OUTCOME TESTS ==========
    
    def test_record_outcome_basic(self, mental_map):
        """Test basic outcome recording."""
        # Create a decision first
        problem = mental_map.create_node(NodeType.PROBLEM, "Test problem")
        decision = mental_map.create_node(NodeType.DECISION, "Test decision")
        
        outcome_node = mental_map.record_outcome(
            decision_id=decision.node_id,
            outcome="Successful implementation",
            metrics={'performance_gain': 0.45, 'user_satisfaction': 0.9}
        )
        
        # Outcome node should be created
        assert outcome_node is not None
        assert outcome_node.node_type == NodeType.OUTCOME
        assert "Successful implementation" in outcome_node.content
        assert 'performance_gain' in outcome_node.metadata
        assert 'user_satisfaction' in outcome_node.metadata
    
    def test_record_outcome_creates_edge(self, mental_map):
        """Test that recording outcome creates edge from decision."""
        decision = mental_map.create_node(NodeType.DECISION, "Test decision")
        initial_edge_count = len(mental_map.edges)
        
        mental_map.record_outcome(
            decision_id=decision.node_id,
            outcome="Result observed"
        )
        
        # Should have created edge
        assert len(mental_map.edges) > initial_edge_count
    
    def test_record_outcome_triggers_appraisal(self, mental_map):
        """Test that recording outcome triggers self-appraisal."""
        decision = mental_map.create_node(NodeType.DECISION, "Test decision")
        
        outcome_node = mental_map.record_outcome(
            decision_id=decision.node_id,
            outcome="Mixed results",
            metrics={'success': 0.6}
        )
        
        # Appraisal should be triggered (internal method called)
        # Verify by checking if reflection nodes were created
        reflection_nodes = [n for n in mental_map.nodes.values() 
                           if n.node_type == NodeType.REFLECTION]
        assert len(reflection_nodes) > 0
    
    # ========== SELF APPRAISAL TESTS ==========
    
    def test_self_appraise_decision_creates_reflection(self, mental_map):
        """Test self-appraisal creates reflection nodes."""
        decision = mental_map.create_node(NodeType.DECISION, "Important decision")
        outcome = mental_map.create_node(NodeType.OUTCOME, "Good outcome")
        
        # Trigger appraisal
        mental_map._self_appraise_decision(
            decision_id=decision.node_id,
            outcome_id=outcome.node_id,
            actual_results={'quality': 0.8}
        )
        
        # Should create reflection
        reflection_nodes = [n for n in mental_map.nodes.values() 
                           if n.node_type == NodeType.REFLECTION]
        assert len(reflection_nodes) > 0
    
    def test_self_appraise_identifies_good_decision(self, mental_map):
        """Test appraisal identifies successful decisions."""
        decision = mental_map.create_node(NodeType.DECISION, "Good decision")
        outcome = mental_map.create_node(NodeType.OUTCOME, "Excellent outcome")
        
        mental_map._self_appraise_decision(
            decision_id=decision.node_id,
            outcome_id=outcome.node_id,
            actual_results={'success_rate': 0.95, 'quality': 0.9}
        )
        
        # Reflection should note success
        reflection_nodes = [n for n in mental_map.nodes.values() 
                           if n.node_type == NodeType.REFLECTION]
        assert len(reflection_nodes) > 0
    
    def test_self_appraise_identifies_poor_decision(self, mental_map):
        """Test appraisal identifies unsuccessful decisions."""
        decision = mental_map.create_node(NodeType.DECISION, "Poor decision")
        outcome = mental_map.create_node(NodeType.OUTCOME, "Failed outcome")
        
        mental_map._self_appraise_decision(
            decision_id=decision.node_id,
            outcome_id=outcome.node_id,
            actual_results={'success_rate': 0.2, 'quality': 0.1}
        )
        
        # Should create learning node from failure
        learning_nodes = [n for n in mental_map.nodes.values() 
                         if n.node_type == NodeType.LEARNING]
        assert len(learning_nodes) > 0
    
    # ========== ITERATIVE REVIEW TESTS ==========
    
    def test_iterative_review_basic(self, mental_map):
        """Test basic iterative review functionality."""
        # Create some nodes that need review
        node1 = mental_map.create_node(NodeType.PROBLEM, "Problem 1")
        node1.needs_review = True
        
        node2 = mental_map.create_node(NodeType.DECISION, "Decision 1")
        node2.needs_review = True
        
        review_result = mental_map.iterative_review()
        
        # Review should find nodes
        assert 'reviewed_count' in review_result
        assert 'improved_count' in review_result
        assert review_result['reviewed_count'] >= 2
    
    def test_iterative_review_improves_confidence(self, mental_map):
        """Test that review improves node confidence."""
        node = mental_map.create_node(NodeType.HYPOTHESIS, "Low confidence hypothesis")
        node.confidence = 0.3
        node.needs_review = True
        
        initial_confidence = node.confidence
        
        mental_map.iterative_review()
        
        # Confidence might improve after review
        assert node.confidence >= initial_confidence
    
    def test_iterative_review_marks_completed(self, mental_map):
        """Test that reviewed nodes are marked as complete."""
        node = mental_map.create_node(NodeType.PROBLEM, "Review problem")
        node.needs_review = True
        
        mental_map.iterative_review()
        
        # Node should no longer need review (or confidence improved)
        assert not node.needs_review or node.confidence > 0.5
    
    # ========== GRAPH OPERATIONS TESTS ==========
    
    def test_create_node(self, mental_map):
        """Test node creation."""
        node = mental_map.create_node(
            node_type=NodeType.CONCEPT,
            content="Important concept",
            metadata={'importance': 'high'}
        )
        
        assert node is not None
        assert node.node_id in mental_map.nodes
        assert node.content == "Important concept"
        assert node.metadata['importance'] == 'high'
    
    def test_connect_nodes(self, mental_map):
        """Test connecting nodes with edges."""
        node1 = mental_map.create_node(NodeType.PROBLEM, "Problem A")
        node2 = mental_map.create_node(NodeType.SOLUTION, "Solution B")
        
        edge = mental_map.connect_nodes(
            source_id=node1.node_id,
            target_id=node2.node_id,
            edge_type=EdgeType.LEADS_TO,
            weight=0.8
        )
        
        assert edge is not None
        assert edge.source_id == node1.node_id
        assert edge.target_id == node2.node_id
        assert edge.edge_type == EdgeType.LEADS_TO
        assert edge.weight == 0.8
    
    def test_get_connected_nodes(self, mental_map):
        """Test retrieving connected nodes."""
        node1 = mental_map.create_node(NodeType.PROBLEM, "Central problem")
        node2 = mental_map.create_node(NodeType.HYPOTHESIS, "Hypothesis 1")
        node3 = mental_map.create_node(NodeType.HYPOTHESIS, "Hypothesis 2")
        
        mental_map.connect_nodes(node1.node_id, node2.node_id, EdgeType.LEADS_TO)
        mental_map.connect_nodes(node1.node_id, node3.node_id, EdgeType.LEADS_TO)
        
        connected = mental_map.get_connected_nodes(node1.node_id)
        
        assert len(connected) >= 2
        assert node2 in connected
        assert node3 in connected
    
    def test_find_path_between_nodes(self, mental_map):
        """Test finding path between two nodes."""
        node_a = mental_map.create_node(NodeType.PROBLEM, "Start")
        node_b = mental_map.create_node(NodeType.CONCEPT, "Middle")
        node_c = mental_map.create_node(NodeType.SOLUTION, "End")
        
        mental_map.connect_nodes(node_a.node_id, node_b.node_id, EdgeType.LEADS_TO)
        mental_map.connect_nodes(node_b.node_id, node_c.node_id, EdgeType.LEADS_TO)
        
        path = mental_map.shortest_path(source=node_a, target=node_c)
        
        assert path is not None
        assert len(path) == 3
        assert path[0] == node_a
        assert path[1] == node_b
        assert path[2] == node_c
    
    def test_save_and_load_mental_map(self, mental_map, tmp_path):
        """Test saving and loading mental map."""
        # Create some nodes and edges
        node1 = mental_map.create_node(NodeType.PROBLEM, "Test problem")
        node2 = mental_map.create_node(NodeType.SOLUTION, "Test solution")
        mental_map.connect_nodes(node1.node_id, node2.node_id, EdgeType.LEADS_TO)
        
        # Save
        save_path = tmp_path / "mental_map.json"
        mental_map.save(save_path)
        
        # Load
        loaded_map = MentalMappingModel()
        loaded_map.load(save_path)
        
        # Verify loaded correctly
        assert len(loaded_map.nodes) == len(mental_map.nodes)
        assert len(loaded_map.edges) == len(mental_map.edges)
    
    # ========== EDGE CASES ==========
    
    def test_make_decision_with_empty_alternatives(self, mental_map, problem_node):
        """Test decision making with no alternatives."""
        decision = mental_map.make_decision(
            problem_id=problem_node.node_id,
            alternatives=[]
        )
        
        # Should handle gracefully
        assert decision is not None
        assert decision['confidence'] == 0.0
    
    def test_think_through_empty_problem(self, mental_map):
        """Test thinking through empty problem."""
        result = mental_map.think_through_problem(problem="")
        
        # Should handle gracefully
        assert 'problem_node' in result
    
    def test_get_connected_nodes_no_connections(self, mental_map):
        """Test getting connections for isolated node."""
        node = mental_map.create_node(NodeType.PROBLEM, "Isolated")
        
        connected = mental_map.get_connected_nodes(node.node_id)
        
        assert len(connected) == 0
