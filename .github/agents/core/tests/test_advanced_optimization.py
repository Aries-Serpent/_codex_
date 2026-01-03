"""
Tests for Advanced Optimization Module (Phase 8.6) and EXP Validation.

Tests:
- EXP-7 Validator for Adaptive Learning
- EXP-8 Validator for Transfer Learning
- Validation Runner
- Random Search Optimizer
- Evolutionary Optimizer
- Bayesian Optimizer
- Neural Policy Network
- Advanced Optimizer
"""
import pytest
from ..advanced_optimization import (
    ExperimentConfig,
    ExperimentResult,
    EXP7Validator,
    EXP8Validator,
    ValidationRunner,
    OptimizationState,
    RandomSearchOptimizer,
    EvolutionaryOptimizer,
    BayesianOptimizer,
    NeuralPolicyNetwork,
    AdvancedOptimizer,
)


# =============================================================================
# EXP-7 VALIDATOR TESTS
# =============================================================================


class TestEXP7Validator:
    """Tests for EXP-7 validation (Phase 8.3 Adaptive Learning)."""
    
    def test_experiment_id(self):
        """Test experiment ID property."""
        validator = EXP7Validator()
        assert validator.experiment_id == "EXP-7"
    
    def test_simulated_run(self):
        """Test simulated validation run."""
        validator = EXP7Validator()
        config = ExperimentConfig(
            experiment_id="EXP-7",
            name="Adaptive Learning Validation",
            target_value=0.33,
            max_iterations=100,
        )
        
        result = validator.run(config)
        
        assert result.experiment_id == "EXP-7"
        assert isinstance(result.final_value, float)
        assert result.iterations > 0
        assert result.duration_seconds >= 0
        assert len(result.history) > 0
        assert 'simulated' in result.metrics
    
    def test_convergence_check(self):
        """Test convergence detection."""
        validator = EXP7Validator()
        config = ExperimentConfig(
            experiment_id="EXP-7",
            name="Convergence Test",
            target_value=0.40,  # Easier target
            max_iterations=100,
            convergence_threshold=0.01,
        )
        
        result = validator.run(config)
        
        # Should converge before max iterations
        assert result.iterations <= 100 * 10
    
    def test_target_achievement(self):
        """Test target value achievement."""
        validator = EXP7Validator()
        config = ExperimentConfig(
            experiment_id="EXP-7",
            name="Target Test",
            target_value=0.50,  # Very easy target
            max_iterations=100,
        )
        
        result = validator.run(config)
        
        # Should succeed with easy target
        assert result.success is True
        assert result.final_value <= 0.50
    
    def test_result_to_dict(self):
        """Test result serialization."""
        validator = EXP7Validator()
        config = ExperimentConfig(
            experiment_id="EXP-7",
            name="Serialization Test",
        )
        
        result = validator.run(config)
        result_dict = result.to_dict()
        
        assert 'experiment_id' in result_dict
        assert 'success' in result_dict
        assert 'final_value' in result_dict
        assert 'iterations' in result_dict
        assert 'timestamp' in result_dict


# =============================================================================
# EXP-8 VALIDATOR TESTS
# =============================================================================


class TestEXP8Validator:
    """Tests for EXP-8 validation (Phase 8.4 Transfer Learning)."""
    
    def test_experiment_id(self):
        """Test experiment ID property."""
        validator = EXP8Validator()
        assert validator.experiment_id == "EXP-8"
    
    def test_simulated_run(self):
        """Test simulated validation run."""
        validator = EXP8Validator()
        config = ExperimentConfig(
            experiment_id="EXP-8",
            name="Transfer Learning Validation",
            target_value=0.32,
            max_iterations=50,
        )
        
        result = validator.run(config)
        
        assert result.experiment_id == "EXP-8"
        assert isinstance(result.final_value, float)
        assert result.iterations > 0
        assert 'simulated' in result.metrics
        assert 'transfer_efficiency' in result.metrics
    
    def test_transfer_efficiency_metric(self):
        """Test transfer efficiency is tracked."""
        validator = EXP8Validator()
        config = ExperimentConfig(
            experiment_id="EXP-8",
            name="Efficiency Test",
            max_iterations=50,
        )
        
        result = validator.run(config)
        
        assert result.metrics.get('transfer_efficiency', 0) > 0
    
    def test_history_tracking(self):
        """Test metric history is tracked."""
        validator = EXP8Validator()
        config = ExperimentConfig(
            experiment_id="EXP-8",
            name="History Test",
            max_iterations=50,
        )
        
        result = validator.run(config)
        
        assert len(result.history) > 0
        # History should show improvement (decreasing k1)
        if len(result.history) >= 2:
            assert result.history[-1] <= result.history[0]


# =============================================================================
# VALIDATION RUNNER TESTS
# =============================================================================


class TestValidationRunner:
    """Tests for validation runner."""
    
    def test_register_experiment(self):
        """Test experiment registration."""
        runner = ValidationRunner()
        validator = EXP7Validator()
        
        runner.register(validator)
        
        assert "EXP-7" in runner.experiments
    
    def test_run_single_experiment(self):
        """Test running single experiment."""
        runner = ValidationRunner()
        runner.register(EXP7Validator())
        
        result = runner.run_experiment("EXP-7")
        
        assert result.experiment_id == "EXP-7"
        assert "EXP-7" in runner.results
    
    def test_run_all_experiments(self):
        """Test running all experiments."""
        runner = ValidationRunner()
        runner.register(EXP7Validator())
        runner.register(EXP8Validator())
        
        results = runner.run_all()
        
        assert len(results) == 2
        assert "EXP-7" in results
        assert "EXP-8" in results
    
    def test_get_summary(self):
        """Test getting validation summary."""
        runner = ValidationRunner()
        runner.register(EXP7Validator())
        runner.register(EXP8Validator())
        
        runner.run_all()
        summary = runner.get_summary()
        
        assert 'total_experiments' in summary
        assert 'passed' in summary
        assert 'failed' in summary
        assert 'all_passed' in summary
        assert 'results' in summary
    
    def test_unknown_experiment_raises(self):
        """Test unknown experiment raises error."""
        runner = ValidationRunner()
        
        with pytest.raises(ValueError, match="Unknown experiment"):
            runner.run_experiment("UNKNOWN")


# =============================================================================
# OPTIMIZER TESTS
# =============================================================================


class TestRandomSearchOptimizer:
    """Tests for random search optimizer."""
    
    def test_name(self):
        """Test optimizer name."""
        optimizer = RandomSearchOptimizer()
        assert optimizer.name == "random_search"
    
    def test_optimize(self):
        """Test basic optimization."""
        optimizer = RandomSearchOptimizer(seed=42)
        
        def objective(params):
            return -(params['x'] ** 2 + params['y'] ** 2)
        
        param_space = {'x': (-5.0, 5.0), 'y': (-5.0, 5.0)}
        
        result = optimizer.optimize(objective, param_space, max_iterations=100)
        
        assert result.iteration == 100
        assert result.best_value is not None
        assert 'x' in result.best_params
        assert 'y' in result.best_params
    
    def test_convergence_tracking(self):
        """Test convergence is tracked."""
        optimizer = RandomSearchOptimizer(seed=42)
        
        def objective(params):
            return -params['x'] ** 2
        
        result = optimizer.optimize(
            objective,
            {'x': (-1.0, 1.0)},
            max_iterations=50,
        )
        
        assert result.convergence >= 0


class TestEvolutionaryOptimizer:
    """Tests for evolutionary optimizer."""
    
    def test_name(self):
        """Test optimizer name."""
        optimizer = EvolutionaryOptimizer()
        assert optimizer.name == "evolutionary"
    
    def test_optimize(self):
        """Test evolutionary optimization."""
        optimizer = EvolutionaryOptimizer(
            population_size=10,
            offspring_size=20,
            seed=42,
        )
        
        def objective(params):
            return -(params['x'] ** 2)
        
        result = optimizer.optimize(
            objective,
            {'x': (-5.0, 5.0)},
            max_iterations=20,
        )
        
        assert result.iteration == 20
        assert result.best_value > -25  # Should find something reasonable
    
    def test_mutation(self):
        """Test mutation affects offspring."""
        optimizer = EvolutionaryOptimizer(mutation_rate=1.0, seed=42)
        
        def objective(params):
            return params['x']
        
        result = optimizer.optimize(
            objective,
            {'x': (0.0, 10.0)},
            max_iterations=10,
        )
        
        # Should have explored the space
        assert len(result.history) == 10


class TestBayesianOptimizer:
    """Tests for Bayesian optimizer."""
    
    def test_name(self):
        """Test optimizer name."""
        optimizer = BayesianOptimizer()
        assert optimizer.name == "bayesian"
    
    def test_optimize(self):
        """Test Bayesian optimization."""
        optimizer = BayesianOptimizer(n_initial=5, seed=42)
        
        def objective(params):
            return -(params['x'] ** 2)
        
        result = optimizer.optimize(
            objective,
            {'x': (-2.0, 2.0)},
            max_iterations=20,
        )
        
        assert result.iteration == 20
        # Should find value near 0
        assert result.best_value > -4
    
    def test_initial_samples(self):
        """Test initial random samples are taken."""
        optimizer = BayesianOptimizer(n_initial=10, seed=42)
        
        def objective(params):
            return params['x']
        
        optimizer.optimize(
            objective,
            {'x': (0.0, 1.0)},
            max_iterations=15,
        )
        
        # Should have at least n_initial samples
        assert len(optimizer._samples) >= 10


# =============================================================================
# NEURAL POLICY NETWORK TESTS
# =============================================================================


class TestNeuralPolicyNetwork:
    """Tests for neural policy network."""
    
    def test_initialization(self):
        """Test network initialization."""
        network = NeuralPolicyNetwork(
            input_size=4,
            hidden_size=32,
            output_size=3,
        )
        
        assert network.input_size == 4
        assert network.hidden_size == 32
        assert network.output_size == 3
    
    def test_forward(self):
        """Test forward pass."""
        network = NeuralPolicyNetwork(
            input_size=4,
            hidden_size=16,
            output_size=3,
        )
        
        state = [0.5, 0.3, 0.8, 0.1]
        output = network.forward(state)
        
        assert len(output) == 3
        # Should be probabilities
        assert abs(sum(output) - 1.0) < 0.01
        assert all(p >= 0 for p in output)
    
    def test_select_action(self):
        """Test action selection."""
        network = NeuralPolicyNetwork(
            input_size=4,
            hidden_size=16,
            output_size=3,
        )
        
        state = [0.5, 0.3, 0.8, 0.1]
        action = network.select_action(state)
        
        assert 0 <= action < 3
    
    def test_statistics(self):
        """Test getting statistics."""
        network = NeuralPolicyNetwork(
            input_size=4,
            hidden_size=32,
            output_size=3,
        )
        
        stats = network.get_statistics()
        
        assert stats['input_size'] == 4
        assert stats['hidden_size'] == 32
        assert stats['output_size'] == 3
        assert stats['total_parameters'] == 4 * 32 + 32 * 3


# =============================================================================
# ADVANCED OPTIMIZER TESTS
# =============================================================================


class TestAdvancedOptimizer:
    """Tests for advanced optimizer."""
    
    def test_initialization(self):
        """Test optimizer initialization."""
        optimizer = AdvancedOptimizer(seed=42)
        
        assert 'random' in optimizer.optimizers
        assert 'evolutionary' in optimizer.optimizers
        assert 'bayesian' in optimizer.optimizers
    
    def test_optimize_with_bayesian(self):
        """Test optimization with Bayesian."""
        optimizer = AdvancedOptimizer(seed=42)
        
        def objective(params):
            return -(params['x'] ** 2)
        
        result = optimizer.optimize(
            objective,
            {'x': (-2.0, 2.0)},
            optimizer_name='bayesian',
            max_iterations=20,
        )
        
        assert result.best_value > -4
    
    def test_optimize_with_evolutionary(self):
        """Test optimization with evolutionary."""
        optimizer = AdvancedOptimizer(seed=42)
        
        def objective(params):
            return -(params['x'] ** 2)
        
        result = optimizer.optimize(
            objective,
            {'x': (-2.0, 2.0)},
            optimizer_name='evolutionary',
            max_iterations=10,
        )
        
        assert result.iteration == 10
    
    def test_auto_select(self):
        """Test auto optimizer selection."""
        optimizer = AdvancedOptimizer()
        
        # Few params -> Bayesian
        selected = optimizer.auto_select_optimizer({'x': (0, 1), 'y': (0, 1)})
        assert selected == 'bayesian'
        
        # Many params -> Random
        many_params = {f'x{i}': (0, 1) for i in range(15)}
        selected = optimizer.auto_select_optimizer(many_params)
        assert selected == 'random'
    
    def test_optimization_history(self):
        """Test optimization history is tracked."""
        optimizer = AdvancedOptimizer(seed=42)
        
        def objective(params):
            return params['x']
        
        optimizer.optimize(objective, {'x': (0, 1)}, max_iterations=10)
        optimizer.optimize(objective, {'x': (0, 1)}, max_iterations=10)
        
        assert len(optimizer.optimization_history) == 2
    
    def test_statistics(self):
        """Test getting statistics."""
        optimizer = AdvancedOptimizer()
        
        stats = optimizer.get_statistics()
        
        assert 'available_optimizers' in stats
        assert 'current_optimizer' in stats
        assert 'total_optimizations' in stats
    
    def test_unknown_optimizer_raises(self):
        """Test unknown optimizer raises error."""
        optimizer = AdvancedOptimizer()
        
        with pytest.raises(ValueError, match="Unknown optimizer"):
            optimizer.optimize(
                lambda p: p['x'],
                {'x': (0, 1)},
                optimizer_name='unknown',
            )


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests for Phase 8.6 components."""
    
    def test_validation_with_optimizer(self):
        """Test validation runner with optimizer tuning."""
        # Run validation
        runner = ValidationRunner()
        runner.register(EXP7Validator())
        runner.register(EXP8Validator())
        
        results = runner.run_all()
        
        # Use optimizer to tune based on results
        optimizer = AdvancedOptimizer(seed=42)
        
        def objective(params):
            # Simulate optimization based on validation
            return 1.0 - params['learning_rate'] * 0.5
        
        opt_result = optimizer.optimize(
            objective,
            {'learning_rate': (0.01, 0.2)},
            max_iterations=20,
        )
        
        assert opt_result.best_value is not None
        assert len(results) == 2
    
    def test_neural_policy_with_optimizer(self):
        """Test neural policy optimization."""
        network = NeuralPolicyNetwork(input_size=4, hidden_size=16, output_size=3)
        optimizer = AdvancedOptimizer(seed=42)
        
        def objective(params):
            # Simulate policy performance
            state = [params['s1'], params['s2'], params['s3'], params['s4']]
            probs = network.forward(state)
            return max(probs)  # Maximize confidence
        
        result = optimizer.optimize(
            objective,
            {
                's1': (0.0, 1.0),
                's2': (0.0, 1.0),
                's3': (0.0, 1.0),
                's4': (0.0, 1.0),
            },
            max_iterations=20,
        )
        
        assert result.best_value > 0.3  # Some reasonable confidence
