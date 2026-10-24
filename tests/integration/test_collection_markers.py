import pytest


@pytest.mark.slow
def test_slow_integration_test_is_marked_integration(request):
    assert request.node.get_closest_marker("integration") is not None
