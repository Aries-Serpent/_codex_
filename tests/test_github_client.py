from src.codex_bridge.github_client import list_branches

def test_list_branches_returns_list():
    out = list_branches()
    assert isinstance(out, list)
