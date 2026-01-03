import logging

from async_oauthlib import OAuth2Session
from litestar import Controller, post, get, Request

from config.zitadel import zitadel_settings

logger = logging.getLogger("_granian")


class AuthController(Controller):
    tags = ["auth"]

    @post("/authorization-url")
    async def get_authorization_url(self) -> dict:
        zitadel_client = OAuth2Session(
            zitadel_settings.web_client_id,
            redirect_uri=zitadel_settings.web_redirect_uri,
            scope=["openid", "profile", "email"],
        )
        authorization_url, state = zitadel_client.authorization_url(
            zitadel_settings.authorization_endpoint
        )

        # State is used to prevent CSRF, keep this for later.
        logger.info("state", state)
        return {"authorization_url": authorization_url}

    @get("/callback")
    async def callback(self, request: Request) -> dict:
        code = request.query_params.get("code")
        state = request.query_params.get("state")

        if not code:
            return {"error": "No code provided"}

        async with OAuth2Session(
            client_id=zitadel_settings.web_client_id,
            state=state,
            redirect_uri=zitadel_settings.web_redirect_uri,
        ) as zitadel_client:
            token = await zitadel_client.fetch_token(
                token_url=zitadel_settings.token_endpoint,
                code=code,
                client_secret=zitadel_settings.web_client_secret,
            )

        return {"token": token}
