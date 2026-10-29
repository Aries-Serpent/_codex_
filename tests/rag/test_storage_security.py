"""Regression tests for tenant storage containment without model downloads."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from aries_serpent_core.rag import indexer


@pytest.fixture
def np():
    pytest.importorskip("faiss")
    return pytest.importorskip("numpy")


@pytest.mark.parametrize(
    "name",
    ["", " ", ".", "..", "../escape", "/absolute", "a/b", r"a\b", "\x00", "C:escape"],
)
@pytest.mark.parametrize("field", ["tenant_id", "index_name"])
def test_persist_and_load_reject_unsafe_names(tmp_path, name, field, np):
    kwargs = {"index_dir": str(tmp_path), "tenant_id": "tenant", "index_name": "docs"}
    kwargs[field] = name
    with pytest.raises(ValueError):
        indexer.persist_index(
            embeddings=np.ones((1, 2), dtype=np.float32), chunks=[(0, 4, "text")], **kwargs
        )
    with pytest.raises(ValueError):
        indexer.load_index(**kwargs)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("operation", ["create", "update", "delete", "merge", "list"])
def test_management_rejects_traversal_before_side_effects(tmp_path, operation):
    victim = tmp_path / "victim"
    victim.mkdir()
    with pytest.raises(ValueError):
        indexer.manage_tenant_indices(
            "tenant", operation, ["../victim"], index_dir=str(tmp_path), files=["unused"]
        )
    assert victim.is_dir()
    assert not (tmp_path / "tenant").exists()


@pytest.mark.parametrize(
    "component", ["tenant", "docs", "index.faiss", "chunks.json", "metadata.json"]
)
def test_persist_and_load_reject_symlinks(tmp_path, component, np):
    storage = tmp_path / "storage"
    target = tmp_path / "target"
    target.mkdir()
    (target / "sentinel").write_text("unchanged")
    index_path = storage / "tenant" / "docs"
    link = {
        "tenant": storage / "tenant",
        "docs": index_path,
    }.get(component, index_path / component)
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(target, target_is_directory=True)
    kwargs = {"index_dir": str(storage), "tenant_id": "tenant", "index_name": "docs"}
    with pytest.raises(ValueError):
        indexer.persist_index(
            embeddings=np.ones((1, 2), dtype=np.float32), chunks=[(0, 4, "text")], **kwargs
        )
    with pytest.raises(ValueError):
        indexer.load_index(**kwargs)
    assert (target / "sentinel").read_text() == "unchanged"
    assert list(target.iterdir()) == [target / "sentinel"]


def test_index_lifecycle_preserves_metadata_and_tenant_isolation(tmp_path, np):
    embeddings = np.eye(2, dtype=np.float32)
    chunks = [(0, 5, "alpha"), (5, 9, "beta")]
    for tenant in ("first", "second"):
        indexer.persist_index("docs", embeddings, chunks, tenant_id=tenant, index_dir=tmp_path)
    path = tmp_path / "first" / "docs"
    original_metadata = (path / "metadata.json").read_bytes()
    original_chunks = (path / "chunks.json").read_bytes()
    loaded, loaded_chunks, metadata = indexer.load_index("docs", "first", tmp_path)
    np.testing.assert_allclose(loaded.reconstruct_n(0, 2), embeddings)
    assert [chunk["text"] for chunk in loaded_chunks] == ["alpha", "beta"]
    assert metadata == json.loads(original_metadata)
    assert (path / "metadata.json").read_bytes() == original_metadata
    assert (path / "chunks.json").read_bytes() == original_chunks
    listed = indexer.manage_tenant_indices("first", "list", [], index_dir=tmp_path)
    assert listed.success and listed.index_names == ["docs"]
    deleted = indexer.manage_tenant_indices("first", "delete", ["docs"], index_dir=tmp_path)
    assert deleted.success
    assert not path.exists()
    assert (tmp_path / "second" / "docs" / "index.faiss").is_file()


def test_list_does_not_follow_index_symlink(tmp_path):
    tenant = tmp_path / "tenant"
    tenant.mkdir()
    external = tmp_path / "external"
    external.mkdir()
    (external / "index.faiss").touch()
    (external / "metadata.json").write_text('{"num_vectors": 999}')
    (tenant / "alias").symlink_to(external, target_is_directory=True)
    result = indexer.manage_tenant_indices("tenant", "list", [], index_dir=tmp_path)
    assert result.success and result.index_names == []


@pytest.mark.parametrize(
    "parts",
    [
        (),
        ("",),
        (".",),
        ("..",),
        ("../escape",),
        ("/absolute",),
        (r"C:\escape",),
        (r"\\host\share",),
    ],
)
def test_helper_rejects_unsafe_components_before_inspection(tmp_path, parts):
    with patch.object(indexer.os.path, "islink") as islink:
        with pytest.raises(ValueError):
            indexer._resolve_safe_subpath(tmp_path, *parts)
    islink.assert_not_called()


@pytest.mark.parametrize("base_as_string", [True, False])
def test_helper_accepts_custom_root_and_nonexistent_descendants(tmp_path, base_as_string):
    root = tmp_path / "custom storage"
    base = str(root) if base_as_string else root
    assert indexer._resolve_safe_subpath(base, "tenant", "docs") == root / "tenant" / "docs"
    assert not root.exists()


@pytest.mark.parametrize("target_kind", ["external", "internal", "missing"])
def test_helper_rejects_symlink_aliases(tmp_path, target_kind):
    root = tmp_path / "storage"
    root.mkdir()
    target = tmp_path / "external"
    if target_kind == "internal":
        target = root / "internal"
    if target_kind != "missing":
        target.mkdir()
    (root / "alias").symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError, match="Symlinks"):
        indexer._resolve_safe_subpath(root, "alias", "docs")


def test_helper_rejects_sibling_prefix_before_inspection(tmp_path):
    root = tmp_path / "storage"
    sibling = str(tmp_path / "storage-other" / "docs")
    with (
        patch.object(indexer.os.path, "abspath", return_value=sibling),
        patch.object(indexer.os.path, "islink") as islink,
    ):
        with pytest.raises(ValueError, match="strictly inside"):
            indexer._resolve_safe_subpath(root, "docs")
    islink.assert_not_called()


def test_helper_rechecks_resolved_containment(tmp_path):
    root = tmp_path / "storage"
    external = tmp_path / "external"
    with patch.object(indexer.os.path, "realpath", side_effect=[str(root), str(external)]):
        with pytest.raises(ValueError, match="strictly inside"):
            indexer._resolve_safe_subpath(root, "docs")


def test_helper_supports_filesystem_root():
    root = Path(Path.cwd().anchor)
    assert indexer._resolve_safe_subpath(root, "nonexistent-storage-component") == (
        root / "nonexistent-storage-component"
    )
