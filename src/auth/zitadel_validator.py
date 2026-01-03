import time
from typing import Dict

from authlib.oauth2.rfc7662 import IntrospectTokenValidator
import requests
from requests.auth import HTTPBasicAuth

from config.zitadel import zitadel_settings


class ValidatorError(Exception):
    def __init__(self, error: Dict[str, str], status_code: int):
        super().__init__()
        self.error = error
        self.status_code = status_code


# Use Introspection in Resource Server
# https://docs.authlib.org/en/latest/specs/rfc7662.html#require-oauth-introspection


class ZitadelIntrospectTokenValidator(IntrospectTokenValidator):
    def introspect_token(self, token_string):
        url = f"{zitadel_settings.issuer}/oauth/v2/introspect"
        data = {
            "token": token_string,
            "token_type_hint": "access_token",
            "scope": "openid",
        }
        auth = HTTPBasicAuth(zitadel_settings.client_id, zitadel_settings.client_secret)
        resp = requests.post(url, data=data, auth=auth, timeout=60)
        resp.raise_for_status()
        return resp.json()

    def match_token_scopes(self, token, or_scopes):
        if or_scopes is None:
            return True
        roles = token["urn:zitadel:iam:org:project:roles"].keys()
        for and_scopes in or_scopes:
            scopes = and_scopes.split()
            """print(f"Check if all {scopes} are in {roles}")"""
            if all(key in roles for key in scopes):
                return True
        return False

    def validate_token(self, token, scopes, request):
        print(f"Token: {token}\n")
        now = int(time.time())
        if not token:
            raise ValidatorError(
                {"code": "invalid_token", "description": "Invalid Token."}, 401
            )
        """Revoked"""
        if not token["active"]:
            raise ValidatorError(
                {
                    "code": "invalid_token",
                    "description": "Invalid token (active: false)",
                },
                401,
            )
        """Expired"""
        if token["exp"] < now:
            raise ValidatorError(
                {"code": "invalid_token_expired", "description": "Token has expired."},
                401,
            )
        """Insufficient Scope"""
        if not self.match_token_scopes(token, scopes):
            raise ValidatorError(
                {
                    "code": "insufficient_scope",
                    "description": f"Token has insufficient scope. Route requires: {scopes}",
                },
                401,
            )

    def __call__(self, *args, **kwargs):
        res = self.introspect_token(*args, **kwargs)
        return res


async def introspect_token_async(token_string: str) -> dict:
    """
    Asynchronous version of token introspection.
    """
    from config.zitadel import zitadel_settings
    import httpx

    url = f"{zitadel_settings.issuer}/oauth/v2/introspect"
    data = {
        "token": token_string,
        "token_type_hint": "access_token",
        "scope": "openid",
    }
    auth = (zitadel_settings.client_id, zitadel_settings.client_secret)

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=data, auth=auth)
        resp.raise_for_status()
        return resp.json()
