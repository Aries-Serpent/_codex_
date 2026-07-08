"""
Extended tests for complete dataset loader suite

Author: mbaetiong
Generated: 2025-11-19 04:02:05
"""

import tempfile
from pathlib import Path

import pytest

pytest.importorskip("numpy")


from codex_ml.data import load_dataset


class TestParquetLoader:
    """Test Parquet loader"""

    @pytest.mark.skipif(not pytest.importorskip("pyarrow"), reason="Requires pyarrow")
    def test_load_parquet_basic(self):
        """Test basic Parquet loading"""
        import pandas as pd

        from src.codex_ml.data.loaders.parquet_loader import load_parquet

        # Create sample Parquet
        df = pd.DataFrame({"text": ["Sample 1", "Sample 2", "Sample 3"], "label": [0, 1, 0]})

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            df.to_parquet(f.name)
            path = Path(f.name)

        dataset = load_parquet(path)

        assert len(dataset) == 3, "Dataset must not be empty"
        assert dataset[0]["text"] == "Sample 1", "Data must not be empty"

    @pytest.mark.skipif(not pytest.importorskip("pyarrow"), reason="Requires pyarrow")
    def test_load_parquet_batched(self):
        """Test batched Parquet loading"""
        import pandas as pd

        from src.codex_ml.data.loaders.parquet_loader import load_parquet

        # Create larger dataset
        df = pd.DataFrame({"id": range(100), "value": range(100, 200)})

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            df.to_parquet(f.name)
            path = Path(f.name)

        batches = list(load_parquet(path, batch_size=20))

        assert len(batches) == 5, "Batches must not be empty"
        assert len(batches[0]) == 20, "Collection must not be empty"


class TestArrowLoader:
    """Test Arrow IPC loader"""

    @pytest.mark.skipif(not pytest.importorskip("pyarrow"), reason="Requires pyarrow")
    def test_load_arrow_basic(self):
        """Test basic Arrow loading"""
        import pyarrow as pa
        import pyarrow.ipc as ipc

        from src.codex_ml.data.loaders.arrow_loader import load_arrow

        # Create sample Arrow file
        schema = pa.schema([("text", pa.string()), ("label", pa.int64())])

        data = [pa.array(["Sample 1", "Sample 2"]), pa.array([0, 1])]

        batch = pa.record_batch(data, schema=schema)

        with tempfile.NamedTemporaryFile(suffix=".arrow", delete=False) as f:
            with ipc.new_file(f.name, schema) as writer:
                writer.write_batch(batch)
            path = Path(f.name)

        dataset = load_arrow(path)

        assert len(dataset) == 2, "Dataset must not be empty"
        assert dataset[0]["text"] == "Sample 1", "Data must not be empty"


class TestHDF5Loader:
    """Test HDF5 loader"""

    @pytest.mark.skipif(not pytest.importorskip("h5py"), reason="Requires h5py")
    def test_load_hdf5_basic(self):
        """Test basic HDF5 loading"""
        import h5py
        import numpy as np

        from src.codex_ml.data.loaders.hdf5_loader import load_hdf5

        # Create sample HDF5
        data = np.random.rand(100, 10)

        with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as f:
            with h5py.File(f.name, "w") as hf:
                hf.create_dataset("data", data=data)
            path = Path(f.name)

        loaded = load_hdf5(path, dataset_path="/data")

        assert loaded.shape == (100, 10)
        assert np.allclose(loaded, data)


class TestLoaderRegistry:
    """Test unified loader registry"""

    def test_unsupported_extension(self):
        """Test error on unsupported extension"""
        with tempfile.NamedTemporaryFile(suffix=".unknown", delete=False) as f:
            path = Path(f.name)

        with pytest.raises(ValueError, match="Unsupported file extension"):
            load_dataset(path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
