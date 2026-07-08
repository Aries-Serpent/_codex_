"""
Test: Vector Store Stubs (S-vector)

Validates that vector store stubs raise informative errors.
"""

import pytest

from codex_addons.vector_stores import PGVectorStore, WeaviateStore


@pytest.mark.parametrize("cls,args", [(PGVectorStore, ()), (WeaviateStore, ())])
def test_stub_raises_informative_importerror(cls, args):
    """Test that stubs raise informative ImportError on connect."""
    vs = cls(*args)
    with pytest.raises(ImportError):
        vs.connect()
