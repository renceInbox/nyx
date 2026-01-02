import time
import uuid

import httpx
import jwt
from litestar import Controller, post
from litestar.exceptions import HTTPException, InternalServerException

from config.zitadel import zitadel_settings
from src.auth import OAuth2Login


class AuthController(Controller):
    tags = ["auth"]

    def _create_client_assertion(self) -> str:
        """
        Create a JWT for Private Key JWT authentication with Zitadel.
        """
        if not zitadel_settings.private_key:
            raise InternalServerException("ZITADEL_PRIVATE_KEY is not configured")
        private_key = zitadel_settings.private_key.replace("\\n", "\n")

        now = int(time.time())
        payload = {
            "iss": zitadel_settings.client_id,
            "sub": zitadel_settings.client_id,
            "aud": zitadel_settings.issuer,
            "iat": now,
            "exp": now + 3600,
            "jti": str(uuid.uuid4()),
        }

        headers = {}
        if zitadel_settings.key_id:
            headers["kid"] = zitadel_settings.key_id

        return jwt.encode(
            payload,
            private_key,
            algorithm="RS256",
            headers=headers,
        )

    @post("/login")
    async def login(self) -> OAuth2Login:
        """
        Login with Private Key JWT to get a Zitadel token.
        """
        client_assertion = self._create_client_assertion()

        async with httpx.AsyncClient() as client:
            payload = {
                "grant_type": "client_credentials",
                "scope": "openid profile email",
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "client_assertion": client_assertion,
            }

            try:
                response = await client.post(
                    f"{zitadel_settings.issuer}/oauth/v2/token",
                    data=payload,
                    timeout=10,
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=e.response.json(),
                ) from e
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error connecting to Zitadel: {e}",
                ) from e

            res_data = response.json()
            return OAuth2Login(
                access_token=res_data["access_token"],
                token_type=res_data["token_type"],
                refresh_token=res_data.get("refresh_token"),
                expires_in=res_data.get("expires_in"),
            )
