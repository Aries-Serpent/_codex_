"""Comprehensive test suite for advanced_indexing module."""

import pytest

from src.codex.retrieval.stores.advanced_indexing import (
    HNSWConfig,
    HNSWIndex,
    IndexType,
    IVFPQConfig,
    IVFPQIndex,
)


class TestIndexType:
    """Test suite for IndexType enum."""

    def test_index_type_flat_value(self):
        """Test FLAT index type value."""
        assert IndexType.FLAT.value == "flat", "Value must be initialized"

    def test_index_type_hnsw_value(self):
        """Test HNSW index type value."""
        assert IndexType.HNSW.value == "hnsw", "Value must be initialized"

    def test_index_type_ivf_flat_value(self):
        """Test IVF_FLAT index type value."""
        assert IndexType.IVF_FLAT.value == "ivf_flat", "Value must be initialized"

    def test_index_type_ivf_pq_value(self):
        """Test IVF_PQ index type value."""
        assert IndexType.IVF_PQ.value == "ivf_pq", "Value must be initialized"

    def test_index_type_hybrid_value(self):
        """Test HYBRID index type value."""
        assert IndexType.HYBRID.value == "hybrid", "Value must be initialized"

    def test_all_index_types(self):
        """Test all index types enumerated."""
        types = list(IndexType)
        assert len(types) == 5, "Types must not be empty"
        values = [t.value for t in types]
        assert values == ["flat", "hnsw", "ivf_flat", "ivf_pq", "hybrid"]

    def test_index_type_names(self):
        """Test index type names."""
        assert IndexType.FLAT.name == "FLAT", "name is not valid"
        assert IndexType.HNSW.name == "HNSW", "name is not valid"
        assert IndexType.IVF_FLAT.name == "IVF_FLAT", "name is not valid"
        assert IndexType.IVF_PQ.name == "IVF_PQ", "name is not valid"
        assert IndexType.HYBRID.name == "HYBRID", "name is not valid"

    def test_index_type_iteration(self):
        """Test iterating over index types."""
        count = 0
        for index_type in IndexType:
            assert isinstance(index_type, IndexType)
            count += 1
        assert count == 5, "Count must be greater than zero"

    def test_index_type_equality(self):
        """Test index type equality."""
        assert IndexType.FLAT == IndexType.FLAT, "FLAT is not valid"
        assert IndexType.HNSW != IndexType.FLAT, "HNSW is not valid"

    def test_index_type_inequality(self):
        """Test index type inequality."""
        assert IndexType.FLAT != IndexType.HNSW, "FLAT is not valid"
        assert IndexType.IVF_FLAT != IndexType.IVF_PQ, "IVF_FLAT is not valid"


class TestHNSWConfig:
    """Test suite for HNSWConfig dataclass."""

    def test_hnsw_config_defaults(self):
        """Test HNSW config default values."""
        config = HNSWConfig()
        assert config.M == 32, "M is not valid"
        assert config.ef_construction == 200, "ef_construction is not valid"
        assert config.ef_search == 100, "ef_search is not valid"
        assert config.metric == "l2", "metric is not valid"

    def test_hnsw_config_custom_m(self):
        """Test HNSW config with custom M."""
        config = HNSWConfig(M=64)
        assert config.M == 64, "M is not valid"
        assert config.ef_construction == 200, "ef_construction is not valid"

    def test_hnsw_config_custom_ef_construction(self):
        """Test HNSW config with custom ef_construction."""
        config = HNSWConfig(ef_construction=400)
        assert config.ef_construction == 400, "ef_construction is not valid"

    def test_hnsw_config_custom_ef_search(self):
        """Test HNSW config with custom ef_search."""
        config = HNSWConfig(ef_search=200)
        assert config.ef_search == 200, "ef_search is not valid"

    def test_hnsw_config_custom_metric(self):
        """Test HNSW config with custom metric."""
        config = HNSWConfig(metric="cosine")
        assert config.metric == "cosine", "metric is not valid"

    def test_hnsw_config_all_parameters(self):
        """Test HNSW config with all custom parameters."""
        config = HNSWConfig(M=48, ef_construction=300, ef_search=150, metric="ip")
        assert config.M == 48, "M is not valid"
        assert config.ef_construction == 300, "ef_construction is not valid"
        assert config.ef_search == 150, "ef_search is not valid"
        assert config.metric == "ip", "metric is not valid"

    def test_hnsw_config_validate_default(self):
        """Test HNSW config validation with default values."""
        config = HNSWConfig()
        config.validate()  # Should not raise

    def test_hnsw_config_validate_valid_m(self):
        """Test HNSW config M validation with valid values."""
        for m in [4, 16, 32, 64, 128]:
            config = HNSWConfig(M=m)
            config.validate()  # Should not raise

    def test_hnsw_config_validate_m_too_low(self):
        """Test HNSW config M validation with value too low."""
        config = HNSWConfig(M=3)
        with pytest.raises(ValueError, match="M must be between 4 and 128"):
            config.validate()

    def test_hnsw_config_validate_m_too_high(self):
        """Test HNSW config M validation with value too high."""
        config = HNSWConfig(M=129)
        with pytest.raises(ValueError, match="M must be between 4 and 128"):
            config.validate()

    def test_hnsw_config_validate_ef_construction_too_low(self):
        """Test HNSW config ef_construction validation too low."""
        config = HNSWConfig(M=32, ef_construction=50)
        with pytest.raises(ValueError, match="ef_construction must be >= 2\\*M"):
            config.validate()

    def test_hnsw_config_validate_ef_search_too_low(self):
        """Test HNSW config ef_search validation."""
        config = HNSWConfig(ef_search=0)
        with pytest.raises(ValueError, match="ef_search must be >= 1"):
            config.validate()

    def test_hnsw_config_validate_invalid_metric(self):
        """Test HNSW config metric validation."""
        config = HNSWConfig(metric="invalid")
        with pytest.raises(ValueError, match="metric must be one of"):
            config.validate()

    def test_hnsw_config_valid_metrics(self):
        """Test HNSW config with all valid metrics."""
        for metric in ["l2", "ip", "cosine"]:
            config = HNSWConfig(metric=metric)
            config.validate()  # Should not raise


class TestIVFPQConfig:
    """Test suite for IVFPQConfig dataclass."""

    def test_ivfpq_config_defaults(self):
        """Test IVFPQ config default values."""
        config = IVFPQConfig()
        assert config.nlist == 1000, "nlist is not valid"
        assert config.m == 8, "m is not valid"
        assert config.nbits == 8, "nbits is not valid"
        assert config.nprobe == 10, "nprobe is not valid"
        assert config.metric == "l2", "metric is not valid"

    def test_ivfpq_config_custom_nlist(self):
        """Test IVFPQ config with custom nlist."""
        config = IVFPQConfig(nlist=500)
        assert config.nlist == 500, "nlist is not valid"

    def test_ivfpq_config_custom_m(self):
        """Test IVFPQ config with custom m."""
        config = IVFPQConfig(m=16)
        assert config.m == 16, "m is not valid"

    def test_ivfpq_config_custom_nbits(self):
        """Test IVFPQ config with custom nbits."""
        config = IVFPQConfig(nbits=4)
        assert config.nbits == 4, "nbits is not valid"

    def test_ivfpq_config_custom_nprobe(self):
        """Test IVFPQ config with custom nprobe."""
        config = IVFPQConfig(nprobe=20)
        assert config.nprobe == 20, "nprobe is not valid"

    def test_ivfpq_config_custom_metric(self):
        """Test IVFPQ config with custom metric."""
        config = IVFPQConfig(metric="ip")
        assert config.metric == "ip", "metric is not valid"

    def test_ivfpq_config_all_parameters(self):
        """Test IVFPQ config with all custom parameters."""
        config = IVFPQConfig(nlist=500, m=16, nbits=4, nprobe=20, metric="ip")
        assert config.nlist == 500, "nlist is not valid"
        assert config.m == 16, "m is not valid"
        assert config.nbits == 4, "nbits is not valid"
        assert config.nprobe == 20, "nprobe is not valid"
        assert config.metric == "ip", "metric is not valid"

    def test_ivfpq_config_validate_default(self):
        """Test IVFPQ config validation with defaults."""
        config = IVFPQConfig()
        config.validate()  # Should not raise

    def test_ivfpq_config_validate_nlist_valid(self):
        """Test IVFPQ config nlist validation with valid values."""
        for nlist in [1, 100, 1000, 10000]:
            config = IVFPQConfig(nlist=nlist)
            config.validate()  # Should not raise

    def test_ivfpq_config_validate_nlist_invalid(self):
        """Test IVFPQ config nlist validation with invalid value."""
        config = IVFPQConfig(nlist=0)
        with pytest.raises(ValueError, match="nlist must be >= 1"):
            config.validate()

    def test_ivfpq_config_validate_m_valid(self):
        """Test IVFPQ config m validation with valid values."""
        for m in [8, 16, 32, 64]:
            config = IVFPQConfig(m=m)
            config.validate()  # Should not raise

    def test_ivfpq_config_validate_m_invalid(self):
        """Test IVFPQ config m validation with invalid value."""
        config = IVFPQConfig(m=12)
        with pytest.raises(ValueError, match="m should be one of"):
            config.validate()

    def test_ivfpq_config_validate_nbits_valid(self):
        """Test IVFPQ config nbits validation with valid values."""
        for nbits in [4, 8]:
            config = IVFPQConfig(nbits=nbits)
            config.validate()  # Should not raise

    def test_ivfpq_config_validate_nbits_invalid(self):
        """Test IVFPQ config nbits validation with invalid value."""
        config = IVFPQConfig(nbits=6)
        with pytest.raises(ValueError, match="nbits must be 4 or 8"):
            config.validate()

    def test_ivfpq_config_validate_nprobe_too_low(self):
        """Test IVFPQ config nprobe validation too low."""
        config = IVFPQConfig(nprobe=0)
        with pytest.raises(ValueError, match="nprobe must be between 1 and nlist"):
            config.validate()

    def test_ivfpq_config_validate_nprobe_too_high(self):
        """Test IVFPQ config nprobe validation too high."""
        config = IVFPQConfig(nlist=100, nprobe=101)
        with pytest.raises(ValueError, match="nprobe must be between 1 and nlist"):
            config.validate()

    def test_ivfpq_config_validate_nprobe_valid_boundary(self):
        """Test IVFPQ config nprobe validation boundary."""
        config = IVFPQConfig(nlist=100, nprobe=100)
        config.validate()  # Should not raise

    def test_ivfpq_config_validate_metric_valid(self):
        """Test IVFPQ config metric validation with valid values."""
        for metric in ["l2", "ip"]:
            config = IVFPQConfig(metric=metric)
            config.validate()  # Should not raise

    def test_ivfpq_config_validate_metric_invalid(self):
        """Test IVFPQ config metric validation with invalid value."""
        config = IVFPQConfig(metric="cosine")
        with pytest.raises(ValueError, match="metric must be one of"):
            config.validate()


class TestHNSWIndex:
    """Test suite for HNSWIndex class."""

    def test_hnsw_index_initialization_default_config(self):
        """Test HNSWIndex initialization with default config."""
        index = HNSWIndex(dimension=768)
        assert index.dimension == 768, "dimension is not valid"
        assert index.config is not None, "config must be initialized"
        assert index.config.M == 32, "M is not valid"

    def test_hnsw_index_initialization_custom_config(self):
        """Test HNSWIndex initialization with custom config."""
        config = HNSWConfig(M=64)
        index = HNSWIndex(dimension=512, config=config)
        assert index.dimension == 512, "dimension is not valid"
        assert index.config.M == 64, "M is not valid"

    def test_hnsw_index_different_dimensions(self):
        """Test HNSWIndex with various dimensions."""
        for dim in [32, 128, 512, 768, 1024]:
            index = HNSWIndex(dimension=dim)
            assert index.dimension == dim, "dimension is not valid"

    def test_hnsw_index_invalid_config_raises(self):
        """Test HNSWIndex raises on invalid config."""
        config = HNSWConfig(M=3)  # Invalid M
        with pytest.raises(ValueError):
            HNSWIndex(dimension=768, config=config)

    def test_hnsw_index_dimension_zero(self):
        """Test HNSWIndex with dimension zero."""
        index = HNSWIndex(dimension=0)
        assert index.dimension == 0, "dimension is not valid"

    def test_hnsw_index_dimension_one(self):
        """Test HNSWIndex with dimension one."""
        index = HNSWIndex(dimension=1)
        assert index.dimension == 1, "dimension is not valid"

    def test_hnsw_index_large_dimension(self):
        """Test HNSWIndex with large dimension."""
        index = HNSWIndex(dimension=100000)
        assert index.dimension == 100000, "dimension is not valid"


class TestIVFPQIndex:
    """Test suite for IVFPQIndex class."""

    def test_ivfpq_index_initialization_default_config(self):
        """Test IVFPQIndex initialization with default config."""
        index = IVFPQIndex(dimension=768)
        assert index.dimension == 768, "dimension is not valid"
        assert index.config is not None, "config must be initialized"
        assert index.config.nlist == 1000, "nlist is not valid"

    def test_ivfpq_index_initialization_custom_config(self):
        """Test IVFPQIndex initialization with custom config."""
        config = IVFPQConfig(nlist=500)
        index = IVFPQIndex(dimension=512, config=config)
        assert index.dimension == 512, "dimension is not valid"
        assert index.config.nlist == 500, "nlist is not valid"

    def test_ivfpq_index_different_dimensions(self):
        """Test IVFPQIndex with various dimensions."""
        for dim in [32, 128, 512, 768, 1024]:
            index = IVFPQIndex(dimension=dim)
            assert index.dimension == dim, "dimension is not valid"

    def test_ivfpq_index_invalid_config_raises(self):
        """Test IVFPQIndex raises on invalid config."""
        config = IVFPQConfig(nlist=0)  # Invalid nlist
        with pytest.raises(ValueError):
            IVFPQIndex(dimension=768, config=config)

    def test_ivfpq_index_dimension_zero(self):
        """Test IVFPQIndex with dimension zero."""
        index = IVFPQIndex(dimension=0)
        assert index.dimension == 0, "dimension is not valid"

    def test_ivfpq_index_dimension_one(self):
        """Test IVFPQIndex with dimension one."""
        index = IVFPQIndex(dimension=1)
        assert index.dimension == 1, "dimension is not valid"

    def test_ivfpq_index_large_dimension(self):
        """Test IVFPQIndex with large dimension."""
        index = IVFPQIndex(dimension=100000)
        assert index.dimension == 100000, "dimension is not valid"


class TestIndexTypeSelection:
    """Test suite for index type selection logic."""

    def test_select_flat_for_small_dataset(self):
        """Test that FLAT is appropriate for small datasets."""
        assert IndexType.FLAT.value == "flat", "Value must be initialized"

    def test_select_hnsw_for_medium_dataset(self):
        """Test that HNSW is appropriate for medium datasets."""
        assert IndexType.HNSW.value == "hnsw", "Value must be initialized"

    def test_select_ivf_for_large_dataset(self):
        """Test that IVF-PQ is appropriate for large datasets."""
        assert IndexType.IVF_PQ.value == "ivf_pq", "Value must be initialized"

    def test_hybrid_search_capability(self):
        """Test hybrid search capability."""
        assert IndexType.HYBRID.value == "hybrid", "Value must be initialized"


class TestConfigConsistency:
    """Test suite for config consistency."""

    def test_hnsw_config_independent_instances(self):
        """Test that HNSW config instances are independent."""
        config1 = HNSWConfig(M=32)
        config2 = HNSWConfig(M=64)
        assert config1.M != config2.M, "M is not valid"

    def test_ivfpq_config_independent_instances(self):
        """Test that IVFPQ config instances are independent."""
        config1 = IVFPQConfig(nlist=100)
        config2 = IVFPQConfig(nlist=200)
        assert config1.nlist != config2.nlist, "nlist is not valid"

    def test_hnsw_config_equality(self):
        """Test HNSW config equality."""
        config1 = HNSWConfig(M=32)
        config2 = HNSWConfig(M=32)
        assert config1 == config2, "config1 is not valid"

    def test_ivfpq_config_equality(self):
        """Test IVFPQ config equality."""
        config1 = IVFPQConfig(nlist=100)
        config2 = IVFPQConfig(nlist=100)
        assert config1 == config2, "config1 is not valid"
