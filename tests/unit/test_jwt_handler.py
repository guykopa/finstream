import time

import pytest

from finstream.api.security.jwt_handler import JWTHandler, JWTError


@pytest.fixture(autouse=True)
def set_jwt_secret(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret-key-for-tests-minimum-32-chars!!")


class TestJWTHandler:
    """Unit tests for JWTHandler."""

    def test_create_token_returns_string(self) -> None:
        token = JWTHandler().create_token("user@example.com")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_returns_email(self) -> None:
        handler = JWTHandler()
        token = handler.create_token("user@example.com")
        email = handler.verify_token(token)
        assert email == "user@example.com"

    def test_tampered_token_raises_jwt_error(self) -> None:
        handler = JWTHandler()
        token = handler.create_token("user@example.com")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(JWTError):
            handler.verify_token(tampered)

    def test_invalid_token_raises_jwt_error(self) -> None:
        with pytest.raises(JWTError):
            JWTHandler().verify_token("not.a.token")

    def test_expired_token_raises_jwt_error(self) -> None:
        handler = JWTHandler(expiry_minutes=0)
        token = handler.create_token("user@example.com")
        time.sleep(1)
        with pytest.raises(JWTError):
            handler.verify_token(token)

    def test_missing_secret_raises_value_error(self, monkeypatch) -> None:
        monkeypatch.delenv("JWT_SECRET", raising=False)
        with pytest.raises(ValueError):
            JWTHandler()

    def test_two_tokens_for_same_email_are_different(self) -> None:
        handler = JWTHandler()
        t1 = handler.create_token("user@example.com")
        time.sleep(1)
        t2 = handler.create_token("user@example.com")
        assert t1 != t2
