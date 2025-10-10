from src.security import check_secret_entropy


def test_weak_password_rejected() -> None:
    assert check_secret_entropy("12345") is False
    assert check_secret_entropy("aB3$xY9@qW") is True
