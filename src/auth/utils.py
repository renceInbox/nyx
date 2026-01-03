import time
from datetime import timedelta

import httpx
import msgspec
from advanced_alchemy.config import TypeEncodersMap
from jose import jwt
from litestar import MediaType, Response
from litestar.connection import ASGIConnection
from litestar.datastructures import Cookie
from litestar.di import Provide
from litestar.exceptions import NotAuthorizedException
from typing import Any, Dict, Generic, Callable, Iterable, Sequence, cast, Literal

from litestar.middleware import DefineMiddleware
from litestar.openapi.spec import OAuthFlow, Components, SecurityScheme, OAuthFlows
from litestar.security.base import UserType
from litestar.security.jwt import (
    OAuth2PasswordBearerAuth,
    JWTCookieAuthenticationMiddleware,
    Token,
)
from litestar.security.jwt.auth import TokenT, BaseJWTAuth
from litestar.status_codes import HTTP_201_CREATED
from litestar.types import (
    SyncOrAsyncUnion,
    Guard,
    Method,
    Scopes,
    ControllerRouterHandler,
    Empty,
)
from msgspec.structs import asdict

from config.zitadel import zitadel_settings
from src.schemas import CurrentUser

JWKS_CACHE: Dict[str, Any] = {}
JWKS_LAST_FETCH: float = 0.0


async def retrieve_user_handler(token: str) -> CurrentUser:
    """Verify JWT and return user from token claims"""
    payload = await verify_jwt(token)  # You already have this!

    return CurrentUser(
        sub=payload.get("sub"),
        email=payload.get("email"),
        preferred_username=payload.get("preferred_username"),
        roles=payload.get("roles", []),
        exp=payload.get("exp"),
    )


oauth2_auth = OAuth2PasswordBearerAuth[CurrentUser](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=zitadel_settings.jwt_secret,
    token_url="/login",  # nosec
    exclude=["/login", "/schema"],
)


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


class OAuth2Login(msgspec.Struct):
    """OAuth2 Login DTO"""

    access_token: str
    """Valid JWT access token"""
    token_type: str
    """Type of the OAuth token used"""
    refresh_token: str | None = None
    """Optional valid refresh token JWT"""
    expires_in: int | None = None
    """Expiration time of the token in seconds. """


class OAuth2PasswordBearerAuth(
    Generic[UserType, TokenT], BaseJWTAuth[UserType, TokenT]
):
    """OAUTH2 Schema for Password Bearer Authentication.

    This class implements an OAUTH2 authentication flow entry point to the library, and it includes all the
    functionality of the :class:`JWTAuth` class and adds support for passing JWT tokens ``HttpOnly`` cookies.

    ``token_url`` is the only additional argument that is required, and it should point at your login route
    """

    token_secret: str
    """Key with which to generate the token hash.

    Notes:
        - This value should be kept as a secret and the standard practice is to inject it into the environment.
    """
    token_url: str
    """The URL for retrieving a new token."""
    retrieve_user_handler: Callable[[Any, ASGIConnection], SyncOrAsyncUnion[Any | None]]
    """Callable that receives the ``auth`` value from the authentication middleware and returns a ``user`` value.

    Notes:
        - User and Auth can be any arbitrary values specified by the security backend.
        - The User and Auth values will be set by the middleware as ``scope["user"]`` and ``scope["auth"]`` respectively.
          Once provided, they can access via the ``connection.user`` and ``connection.auth`` properties.
        - The callable can be sync or async. If it is sync, it will be wrapped to support async.

    """
    revoked_token_handler: (
        Callable[[Any, ASGIConnection], SyncOrAsyncUnion[bool]] | None
    ) = None
    """Callable that receives the auth value from the authentication middleware and checks whether the token has been revoked,
    returning True if revoked, False otherwise."""
    guards: Iterable[Guard] | None = None
    """An iterable of guards to call for requests, providing authorization functionalities."""
    exclude: str | list[str] | None = None
    """A pattern or list of patterns to skip in the authentication middleware."""
    exclude_opt_key: str = "exclude_from_auth"
    """An identifier to use on routes to disable authentication and authorization checks for a particular route."""
    exclude_http_methods: Sequence[Method] | None = lambda: cast(
        "Sequence[Method]", ["OPTIONS", "HEAD"]
    )
    """A sequence of http methods that do not require authentication. Defaults to ['OPTIONS', 'HEAD']"""
    scopes: Scopes = None
    """ASGI scopes processed by the authentication middleware, if ``None``, both ``http`` and ``websocket`` will be
    processed."""
    route_handlers: Iterable[ControllerRouterHandler] | None = None
    """An optional iterable of route handlers to register."""
    dependencies: dict[str, Provide] | None = None
    """An optional dictionary of dependency providers."""
    type_encoders: TypeEncodersMap | None = None
    """A mapping of types to callables that transform them into types supported for serialization."""
    algorithm: str = "HS256"
    """Algorithm to use for JWT hashing."""
    auth_header: str = "Authorization"
    """Request header key from which to retrieve the token.

    E.g. ``Authorization`` or 'X-Api-Key'.
    """
    default_token_expiration: timedelta = lambda: timedelta(days=1)
    """The default value for token expiration."""
    openapi_security_scheme_name: str = "BearerToken"
    """The value to use for the OpenAPI security scheme and security requirements."""
    oauth_scopes: dict[str, str] | None = None
    """Oauth Scopes available for the token."""
    key: str = "token"
    """Key for the cookie."""
    path: str = "/"
    """Path fragment that must exist in the request url for the cookie to be valid.

    Defaults to ``/``.
    """
    domain: str | None = None
    """Domain for which the cookie is valid."""
    secure: bool | None = None
    """Https is required for the cookie."""
    samesite: Literal["lax", "strict", "none"] = "lax"
    """Controls whether or not a cookie is sent with cross-site requests. Defaults to ``lax``. """
    description: str = "OAUTH2 password bearer authentication and authorization."
    """Description for the OpenAPI security scheme."""
    authentication_middleware_class: type[JWTCookieAuthenticationMiddleware] = (
        JWTCookieAuthenticationMiddleware
    )
    """The authentication middleware class to use.

    Must inherit from :class:`JWTCookieAuthenticationMiddleware`
    """
    token_cls: type[Token] = Token
    """Target type the JWT payload will be converted into"""
    accepted_audiences: Sequence[str] | None = None
    """Audiences to accept when verifying the token. If given, and the audience in the
    token does not match, a 401 response is returned
    """
    accepted_issuers: Sequence[str] | None = None
    """Issuers to accept when verifying the token. If given, and the issuer in the
    token does not match, a 401 response is returned
    """
    require_claims: Sequence[str] | None = None
    """Require these claims to be present in the JWT payload. If any of those claims
    is missing, a 401 response is returned
    """
    verify_expiry: bool = True
    """Verify that the value of the ``exp`` (*expiration*) claim is in the future"""
    verify_not_before: bool = True
    """Verify that the value of the ``nbf`` (*not before*) claim is in the past"""
    strict_audience: bool = False
    """Verify that the value of the ``aud`` (*audience*) claim is a single value, and
    not a list of values, and matches ``audience`` exactly. Requires that
    ``accepted_audiences`` is a sequence of length 1
    """

    @property
    def middleware(self) -> DefineMiddleware:
        """Create ``JWTCookieAuthenticationMiddleware`` wrapped in
            :class:`DefineMiddleware <.middleware.base.DefineMiddleware>`.

        Returns:
            An instance of :class:`DefineMiddleware <.middleware.base.DefineMiddleware>`.
        """
        return DefineMiddleware(
            self.authentication_middleware_class,
            algorithm=self.algorithm,
            auth_cookie_key=self.key,
            auth_header=self.auth_header,
            exclude=self.exclude,
            exclude_opt_key=self.exclude_opt_key,
            exclude_http_methods=self.exclude_http_methods,
            retrieve_user_handler=self.retrieve_user_handler,
            revoked_token_handler=self.revoked_token_handler,
            scopes=self.scopes,
            token_secret=self.token_secret,
            token_cls=self.token_cls,
            token_issuer=self.accepted_issuers,
            token_audience=self.accepted_audiences,
            require_claims=self.require_claims,
            verify_expiry=self.verify_expiry,
            verify_not_before=self.verify_not_before,
            strict_audience=self.strict_audience,
        )

    @property
    def oauth_flow(self) -> OAuthFlow:
        """Create an OpenAPI OAuth2 flow for the password bearer authentication scheme.

        Returns:
            An :class:`OAuthFlow <litestar.openapi.spec.oauth_flow.OAuthFlow>` instance.
        """
        return OAuthFlow(
            token_url=self.token_url,
            scopes=self.oauth_scopes,
        )

    @property
    def openapi_components(self) -> Components:
        """Create OpenAPI documentation for the OAUTH2 Password bearer auth scheme.

        Returns:
            An :class:`Components <litestar.openapi.spec.components.Components>` instance.
        """
        return Components(
            security_schemes={
                self.openapi_security_scheme_name: SecurityScheme(
                    type="oauth2",
                    scheme="Bearer",
                    name=self.auth_header,
                    security_scheme_in="header",
                    flows=OAuthFlows(password=self.oauth_flow),  # pyright: ignore[reportGeneralTypeIssues]
                    bearer_format="JWT",
                    description=self.description,
                )
            }
        )

    def login(
        self,
        identifier: str,
        *,
        response_body: Any = Empty,
        response_media_type: str | MediaType = MediaType.JSON,
        response_status_code: int = HTTP_201_CREATED,
        token_expiration: timedelta | None = None,
        token_issuer: str | None = None,
        token_audience: str | None = None,
        token_unique_jwt_id: str | None = None,
        token_extras: dict[str, Any] | None = None,
        send_token_as_response_body: bool = True,
    ) -> Response[Any]:
        """Create a response with a JWT header.

        Args:
            identifier: Unique identifier of the token subject. Usually this is a user ID or equivalent kind of value.
            response_body: An optional response body to send.
            response_media_type: An optional ``Content-Type``. Defaults to ``application/json``.
            response_status_code: An optional status code for the response. Defaults to ``201``.
            token_expiration: An optional timedelta for the token expiration.
            token_issuer: An optional value of the token ``iss`` field.
            token_audience: An optional value for the token ``aud`` field.
            token_unique_jwt_id: An optional value for the token ``jti`` field.
            token_extras: An optional dictionary to include in the token ``extras`` field.
            send_token_as_response_body: If ``True`` the response will be an oAuth2 token response dict.
                Note: if a response body is passed this setting will be ignored.

        Returns:
            A :class:`Response <.response.Response>` instance.
        """
        encoded_token = self.create_token(
            identifier=identifier,
            token_expiration=token_expiration,
            token_issuer=token_issuer,
            token_audience=token_audience,
            token_unique_jwt_id=token_unique_jwt_id,
            token_extras=token_extras,
        )
        expires_in = int(
            (token_expiration or self.default_token_expiration).total_seconds()
        )
        cookie = Cookie(
            key=self.key,
            path=self.path,
            httponly=True,
            value=self.format_auth_header(encoded_token),
            max_age=expires_in,
            secure=self.secure,
            samesite=self.samesite,
            domain=self.domain,
        )

        if response_body is not Empty:
            body = response_body
        elif send_token_as_response_body:
            token_dto = OAuth2Login(
                access_token=encoded_token,
                expires_in=expires_in,
                token_type="bearer",  # noqa: S106  # nosec
            )
            body = asdict(token_dto)
        else:
            body = None

        return self.create_response(
            content=body,
            headers={self.auth_header: self.format_auth_header(encoded_token)},
            cookies=[cookie],
            media_type=response_media_type,
            status_code=response_status_code,
        )
