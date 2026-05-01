import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt as pyjwt


class JWTError(Exception):
    """Raised when a JWT token is invalid, expired, or tampered with."""


class JWTHandler:
    """Generate and verify JWT tokens.

    The secret is read from the JWT_SECRET environment variable — never
    hardcoded. Raises ValueError at construction time if the variable is unset.
    """

    _ALGORITHM = "HS256"

    def __init__(self, expiry_minutes: int = 60) -> None:
        secret = os.environ.get("JWT_SECRET")
        if not secret:
            raise ValueError("JWT_SECRET environment variable is not set")
        self._secret = secret
        self._expiry = timedelta(minutes=expiry_minutes)

    def create_token(self, email: str) -> str:
        """Generate a signed JWT for the given email address.

        Args:
            email: Subject of the token (user identifier).

        Returns:
            Encoded JWT string.
        """
        now = datetime.now(tz=timezone.utc)
        payload = {
            "sub": email,
            "iat": now,
            "exp": now + self._expiry,
            "jti": str(uuid.uuid4()),
        }
        return pyjwt.encode(payload, self._secret, algorithm=self._ALGORITHM)

    def verify_token(self, token: str) -> str:
        """Verify a JWT and return the subject (email).

        Args:
            token: JWT string to verify.

        Returns:
            Email address from the token subject claim.

        Raises:
            JWTError: if the token is invalid, expired, or tampered with.
        """
        try:
            payload = pyjwt.decode(
                token, self._secret, algorithms=[self._ALGORITHM]
            )
            return str(payload["sub"])
        except pyjwt.PyJWTError as exc:
            raise JWTError(str(exc)) from exc
