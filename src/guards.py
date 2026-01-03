import msgspec
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
import httpx
import jwt
import time
from litestar.handlers import BaseRouteHandler

from config.zitadel import zitadel_settings
from src.schemas import CurrentUser
from src.auth.zitadel_validator import introspect_token_async


class JWKSCache:
    _keys: list[dict] | None = None
    _last_fetch = 0
    _ttl = 3600  # refresh every 1 hour

    @classmethod
    async def get_keys(cls) -> list[dict]:
        if cls._keys is None or (time.time() - cls._last_fetch) > cls._ttl:
            async with httpx.AsyncClient() as client:
                resp = await client.get(zitadel_settings.jwks_url)
                resp.raise_for_status()
                cls._keys = resp.json()["keys"]
                cls._last_fetch = time.time()
        return cls._keys


async def jwt_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    auth = connection.headers.get("authorization")
    if not auth or not auth.startswith("Bearer "):
        raise NotAuthorizedException("Missing Authorization header")

    token = auth.removeprefix("Bearer ").strip()
    jwks = await JWKSCache.get_keys()
    header = jwt.get_unverified_header(token)

    key = next((k for k in jwks if k["kid"] == header.get("kid")), None)
    if not key:
        raise NotAuthorizedException("Invalid key ID")

    try:
        payload = jwt.decode(
            token,
            jwt.algorithms.RSAAlgorithm.from_jwk(key),
            algorithms=["RS256"],
            audience=zitadel_settings.audience,
        )
    except jwt.PyJWTError as e:
        raise NotAuthorizedException(str(e))

    # ⚡ Convert to typed msgspec.Struct
    connection.state.current_user = msgspec.convert(payload, type=CurrentUser)


async def introspect_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    auth = connection.headers.get("authorization")
    if not auth or not auth.startswith("Bearer "):
        raise NotAuthorizedException("Missing Authorization header")

    token_string = auth.removeprefix("Bearer ").strip()

    try:
        token = await introspect_token_async(token_string)
    except httpx.HTTPStatusError as e:
        raise NotAuthorizedException(f"Introspection failed: {e.response.text}")
    except httpx.RequestError as e:
        raise NotAuthorizedException(f"Introspection request error: {e}")

    if not token.get("active"):
        raise NotAuthorizedException("Invalid token (active: false)")

    # Map Zitadel introspection response to CurrentUser
    # Note: Zitadel introspection response might have different keys than JWT payload
    # but CurrentUser fields (sub, email, preferred_username) are usually common.

    # Roles in Zitadel introspection are often in 'urn:zitadel:iam:org:project:roles'
    roles_key = "urn:zitadel:iam:org:project:roles"
    roles = list(token.get(roles_key, {}).keys())

    user_data = {
        "sub": token.get("sub"),
        "email": token.get("email"),
        "preferred_username": token.get("preferred_username"),
        "roles": roles,
        "exp": token.get("exp"),
    }

    connection.state.current_user = msgspec.convert(user_data, type=CurrentUser)


async def auth_guard(
    connection: ASGIConnection, route_handler: BaseRouteHandler
) -> None:
    if zitadel_settings.use_introspection:
        await introspect_guard(connection, route_handler)
    else:
        await jwt_guard(connection, route_handler)
