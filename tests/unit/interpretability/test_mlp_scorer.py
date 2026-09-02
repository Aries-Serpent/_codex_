"""
Unit tests for MLPScorer class.

Tests MLP activation extraction, neuron importance scoring, and activation analysis.
"""

import sys

import pytest

pytest.importorskip("torch")

# Graceful import handling for optional dependencies
try:
    import numpy as np
    import torch

    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    torch = None
    np = None
    pytestmark = pytest.mark.skip("Required dependencies (torch, numpy) not available")

# PyTorch 2.x + Python 3.12 isinstance() union-type bug guard
# Fixed in PyTorch 2.2.0 (DR-003). Skip affected tests until upgrade.
try:
    import torch as _torch_ver

    _TORCH_312_BUG = sys.version_info >= (3, 12) and _torch_ver.__version__.startswith("2.")
except ImportError:
    _TORCH_312_BUG = False

# Only import if dependencies are available
if HAS_DEPS:
    from codex.interpretability.mlp_scorer import MLPAnalysis, MLPScorer
else:
    MLPAnalysis = None
    MLPScorer = None


# Conditional class definition - only define if torch is available
if HAS_DEPS and torch is not None:

    class MockTransformerWithMLP(torch.nn.Module):
        """Mock transformer model with MLP layers for testing."""

        def __init__(self, num_layers=2, hidden_dim=64, intermediate_dim=256):
            super().__init__()
            self.num_layers = num_layers
            self.hidden_dim = hidden_dim
            self.intermediate_dim = intermediate_dim

            # Create mock MLP layers
            self.layers = torch.nn.ModuleList(
                [
                    torch.nn.ModuleDict(
                        {
                            "mlp": torch.nn.Sequential(
                                torch.nn.Linear(hidden_dim, intermediate_dim),
                                torch.nn.GELU(),
                                torch.nn.Linear(intermediate_dim, hidden_dim),
                            )
                        }
                    )
                    for _ in range(num_layers)
                ]
            )

        def forward(self, input_ids, attention_mask=None):
            batch_size = input_ids.size(0)
            seq_len = input_ids.size(1)

            # Generate mock hidden states
            hidden = torch.randn(batch_size, seq_len, self.hidden_dim)

            # Pass through MLP layers
            for layer in self.layers:
                hidden = layer["mlp"](hidden)

            return hidden

else:
    # Dummy class when torch is not available
    class MockTransformerWithMLP:
        pass


class TestMLPScorer:
    """Test suite for MLPScorer."""

    @pytest.fixture(scope="function")
    def mock_model(self):
        """Create a mock transformer model with MLP layers."""
        return MockTransformerWithMLP(num_layers=2, hidden_dim=64, intermediate_dim=256)

    @pytest.fixture(scope="function")
    def scorer(self, mock_model):
        """Create an MLPScorer instance."""
        return MLPScorer(mock_model, device="cpu")

    @pytest.fixture(scope="function")
    def sample_input(self):
        """Create sample input tensors."""
        batch_size = 1
        seq_len = 10
        input_ids = torch.randint(0, 1000, (batch_size, seq_len))
        attention_mask = torch.ones(batch_size, seq_len)
        return input_ids, attention_mask

    def test_initialization(self, mock_model):
        """Test MLPScorer initialization."""
        scorer = MLPScorer(mock_model)
        assert scorer.model == mock_model, "model is not valid"
        assert scorer.normalize is True, "normalize is not valid"
        assert isinstance(scorer.device, torch.device)

    def test_initialization_custom_device(self, mock_model):
        """Test initialization with custom device."""
        scorer = MLPScorer(mock_model, device="cpu")
        assert scorer.device == torch.device("cpu"), "device is not valid"

    def test_extract_mlp_activations(self, scorer, sample_input):
        """Test extraction of MLP activations."""
        input_ids, attention_mask = sample_input

        mlp_acts, layer_names = scorer.extract_mlp_activations(input_ids, attention_mask)

        assert isinstance(mlp_acts, list)
        assert isinstance(layer_names, list)
        assert len(mlp_acts) > 0, "Mlp_acts must not be empty"
        assert len(layer_names) == len(mlp_acts), "Layer_names must not be empty"

        # Check shape of MLP activations
        for act in mlp_acts:
            assert act.dim() in [2, 3]  # (batch, hidden) or (batch, seq, hidden)

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug on Python 3.12 (fixed in 2.2.0 — DR-003)"
    )
    def test_compute_neuron_importance_mean_abs(self, scorer):
        """Test neuron importance computation with mean_abs method."""
        # Create mock MLP activations
        batch_size, seq_len, hidden_dim = 1, 10, 64
        mlp_acts = [torch.randn(batch_size, seq_len, hidden_dim) for _ in range(2)]

        importance = scorer.compute_neuron_importance(mlp_acts, method="mean_abs")

        assert isinstance(importance, np.ndarray)
        assert importance.shape == (2, hidden_dim)  # (num_layers, hidden_dim)
        assert np.all(importance >= 0), "importance must be greater than zero"
        # Check normalization per layer
        for layer_importance in importance:
            assert np.abs(layer_importance.sum() - 1.0) < 1e-5, "Condition must be true"

    def test_compute_neuron_importance_max(self, scorer):
        """Test neuron importance with max method."""
        batch_size, seq_len, hidden_dim = 1, 10, 64
        mlp_acts = [torch.randn(batch_size, seq_len, hidden_dim) for _ in range(2)]

        importance = scorer.compute_neuron_importance(mlp_acts, method="max")

        assert isinstance(importance, np.ndarray)
        assert importance.shape == (2, hidden_dim)
        assert np.all(importance >= 0), "importance must be greater than zero"

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug on Python 3.12 (fixed in 2.2.0 — DR-003)"
    )
    def test_compute_neuron_importance_variance(self, scorer):
        """Test neuron importance with variance method."""
        batch_size, seq_len, hidden_dim = 1, 10, 64
        mlp_acts = [torch.randn(batch_size, seq_len, hidden_dim) for _ in range(2)]

        importance = scorer.compute_neuron_importance(mlp_acts, method="variance")

        assert isinstance(importance, np.ndarray)
        assert importance.shape == (2, hidden_dim)
        assert np.all(importance >= 0), "importance must be greater than zero"

    def test_compute_neuron_importance_invalid_method(self, scorer):
        """Test that invalid method raises error."""
        mlp_acts = [torch.randn(1, 10, 64)]

        with pytest.raises(ValueError, match="Unknown method"):
            scorer.compute_neuron_importance(mlp_acts, method="invalid")

    def test_compute_neuron_importance_empty_activations(self, scorer):
        """Test that empty activations raises error."""
        with pytest.raises(ValueError, match="No MLP activations"):
            scorer.compute_neuron_importance([])

    def test_compute_activation_statistics(self, scorer):
        """Test activation statistics computation."""
        batch_size, seq_len, hidden_dim = 1, 10, 64
        mlp_acts = [torch.randn(batch_size, seq_len, hidden_dim) for _ in range(2)]

        stats = scorer.compute_activation_statistics(mlp_acts)

        assert isinstance(stats, dict)
        assert "mean" in stats, "Condition must be true"
        assert "std" in stats, "Condition must be true"
        assert "min" in stats, "Condition must be true"
        assert "max" in stats, "Condition must be true"
        assert "sparsity" in stats, "Condition must be true"

        # Check shapes
        for key, value in stats.items():
            assert isinstance(value, np.ndarray)
            assert value.shape == (2, hidden_dim)  # (num_layers, hidden_dim)

    def test_analyze_mlp(self, scorer, sample_input):
        """Test complete MLP analysis."""
        input_ids, attention_mask = sample_input

        analysis = scorer.analyze_mlp(input_ids=input_ids, attention_mask=attention_mask)

        assert isinstance(analysis, MLPAnalysis)
        assert isinstance(analysis.activations, np.ndarray)
        assert isinstance(analysis.neuron_importance, np.ndarray)
        assert isinstance(analysis.layer_stats, dict)
        assert isinstance(analysis.layer_names, list)
        assert analysis.input_shape == input_ids.shape, "input_shape is not valid"

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug on Python 3.12 (fixed in 2.2.0 — DR-003)"
    )
    def test_get_top_neurons(self, scorer):
        """Test getting top neurons per layer."""
        # Create mock analysis
        num_layers, hidden_dim = 2, 64
        analysis = MLPAnalysis(
            activations=np.random.rand(num_layers, hidden_dim),
            neuron_importance=np.random.rand(num_layers, hidden_dim),
            layer_stats={
                "mean": np.random.rand(num_layers, hidden_dim),
                "std": np.random.rand(num_layers, hidden_dim),
                "min": np.random.rand(num_layers, hidden_dim),
                "max": np.random.rand(num_layers, hidden_dim),
                "sparsity": np.random.rand(num_layers, hidden_dim),
            },
            layer_names=["layer_0", "layer_1"],
            input_shape=(1, 10),
        )

        top_neurons = scorer.get_top_neurons(analysis, top_k=10)

        assert isinstance(top_neurons, dict)
        assert len(top_neurons) == num_layers, "Top_neurons must not be empty"

        for layer_idx, neurons in top_neurons.items():
            assert len(neurons) == 10, "Neurons must not be empty"
            for neuron_idx, importance in neurons:
                assert isinstance(neuron_idx, int)
                assert isinstance(importance, float)
                assert 0 <= neuron_idx < hidden_dim, "0 is not valid"

    def test_get_dead_neurons(self, scorer):
        """Test identification of dead neurons."""
        # Create mock analysis with some dead neurons
        num_layers, hidden_dim = 2, 64
        sparsity = np.random.rand(num_layers, hidden_dim)
        sparsity[0, :5] = 0.995  # Make first 5 neurons in layer 0 dead

        analysis = MLPAnalysis(
            activations=np.random.rand(num_layers, hidden_dim),
            neuron_importance=np.random.rand(num_layers, hidden_dim),
            layer_stats={
                "mean": np.random.rand(num_layers, hidden_dim),
                "std": np.random.rand(num_layers, hidden_dim),
                "min": np.random.rand(num_layers, hidden_dim),
                "max": np.random.rand(num_layers, hidden_dim),
                "sparsity": sparsity,
            },
            layer_names=["layer_0", "layer_1"],
            input_shape=(1, 10),
        )

        dead_neurons = scorer.get_dead_neurons(analysis, threshold=0.99)

        assert isinstance(dead_neurons, dict)
        assert 0 in dead_neurons, "Condition must be true"
        assert len(dead_neurons[0]) >= 5, "Collection must not be empty"

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug on Python 3.12 (fixed in 2.2.0 — DR-003)"
    )
    def test_compare_inputs(self, scorer, sample_input):
        """Test comparison of MLP activations between two inputs."""
        input_ids_1, attention_mask_1 = sample_input
        input_ids_2 = torch.randint(0, 1000, input_ids_1.shape)
        attention_mask_2 = attention_mask_1.clone()

        comparison = scorer.compare_inputs(
            input_ids_1, input_ids_2, attention_mask_1, attention_mask_2
        )

        assert isinstance(comparison, dict)
        assert "diff" in comparison, "Condition must be true"
        assert "correlation" in comparison, "Condition must be true"
        assert "l2_distance" in comparison, "Condition must be true"

        assert isinstance(comparison["diff"], np.ndarray)
        assert isinstance(comparison["correlation"], np.ndarray)
        assert isinstance(comparison["l2_distance"], np.ndarray)

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug on Python 3.12 (fixed in 2.2.0 — DR-003)"
    )
    def test_scorer_with_normalization_disabled(self, mock_model):
        """Test scorer with normalization disabled."""
        scorer = MLPScorer(mock_model, normalize=False)

        batch_size, seq_len, hidden_dim = 1, 10, 64
        mlp_acts = [torch.randn(batch_size, seq_len, hidden_dim) for _ in range(2)]

        importance = scorer.compute_neuron_importance(mlp_acts)

        # Without normalization, sum might not be 1
        assert isinstance(importance, np.ndarray)
        assert importance.shape == (2, hidden_dim)
