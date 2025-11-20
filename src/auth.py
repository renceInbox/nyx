import time
import httpx
from jose import jwt
from litestar.exceptions import NotAuthorizedException
from typing import Any, Dict

from config.zitadel import zitadel_settings

JWKS_CACHE: Dict[str, Any] = {}
JWKS_LAST_FETCH: float = 0.0


async def fetch_jwks() -> Dict[str, Any]:
    """Fetch Zitadel JWKS."""
    async with httpx.AsyncClient() as client:
        response = await client.get(zitadel_settings.jwks_url, timeout=10)
        response.raise_for_status()
        return response.json()


async def get_jwks() -> Dict[str, Any]:
    """Return cached JWKS, refreshing if needed."""
    global JWKS_CACHE, JWKS_LAST_FETCH
    now = time.time()
    if not JWKS_CACHE or (
        now - JWKS_LAST_FETCH > zitadel_settings.jwks_refresh_interval
    ):
        JWKS_CACHE = await fetch_jwks()
        JWKS_LAST_FETCH = now
    return JWKS_CACHE


async def verify_jwt(token: str) -> Dict[str, Any]:
    """Verify JWT locally using cached Zitadel JWKS."""
    jwks = await get_jwks()

    try:
        return jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=zitadel_settings.audience,
            issuer=zitadel_settings.issuer,
            options={"verify_aud": True, "verify_iss": True},
        )
    except Exception as e:
        raise NotAuthorizedException(detail=f"Invalid token: {e}")
