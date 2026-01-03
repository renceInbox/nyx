import time
import uuid
import jwt
import httpx
import asyncio
from config.zitadel import zitadel_settings


async def test_combinations():
    private_key = zitadel_settings.private_key.replace("\\n", "\n")
    client_id = zitadel_settings.client_id
    issuer = zitadel_settings.issuer
    token_endpoint = f"{issuer}/oauth/v2/token"

    audiences = [issuer, token_endpoint]
    issuers = [
        client_id,
        "347527194265780227",
        "12345",
    ]  # Litestar, Management-API, Fake

    async with httpx.AsyncClient() as client:
        for aud in audiences:
            for iss in issuers:
                print(f"Testing aud={aud}, iss={iss}...")
                now = int(time.time()) - 60
                payload = {
                    "iss": iss,
                    "sub": iss,
                    "aud": aud,
                    "iat": now,
                    "exp": now + 3600,
                    "jti": str(uuid.uuid4()),
                }
                # headers = {"kid": zitadel_settings.key_id}
                headers = {}
                assertion = jwt.encode(
                    payload, private_key, algorithm="RS256", headers=headers
                )

                # Try without client_id in body
                data = {
                    "grant_type": "client_credentials",
                    "scope": "openid profile email",
                    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                    "client_assertion": assertion,
                }
                headers_post = {"x-zitadel-orgid": "347527192554569731"}
                resp = await client.post(
                    token_endpoint, data=data, headers=headers_post
                )
                print(
                    f"  Result (no client_id, with orgid header): {resp.status_code} {resp.text}"
                )

                # Try with client_id in body
                data["client_id"] = client_id
                resp = await client.post(
                    token_endpoint, data=data, headers=headers_post
                )
                print(
                    f"  Result (with client_id, with orgid header): {resp.status_code} {resp.text}"
                )
                print("-" * 20)


if __name__ == "__main__":
    asyncio.run(test_combinations())
