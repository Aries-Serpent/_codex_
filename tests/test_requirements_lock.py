from pathlib import Path

def test_requirements_lock_exists():
    assert Path('requirements.lock').is_file()
