import os

from fastapi import APIRouter, Depends, HTTPException, status

from finstream.api.dependencies import get_jwt_handler
from finstream.api.schemas import TokenRequest, TokenResponse
from finstream.api.security.jwt_handler import JWTHandler

router = APIRouter(prefix="/auth", tags=["auth"])

# In production, validate against a real user store.
# This demo reads credentials from environment variables.
_DEMO_EMAIL = os.environ.get("DEMO_EMAIL", "admin@finstream.io")
_DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "changeme")


@router.post("/token", response_model=TokenResponse)
def login(
    body: TokenRequest,
    handler: JWTHandler = Depends(get_jwt_handler),
) -> TokenResponse:
    """Issue a JWT token for valid credentials.

    Args:
        body: JSON body with email and password fields.
        handler: Injected JWT handler.

    Returns:
        TokenResponse with access_token and token_type.

    Raises:
        HTTPException 401: if credentials are invalid.
    """
    if body.email != _DEMO_EMAIL or body.password != _DEMO_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return TokenResponse(access_token=handler.create_token(body.email))
