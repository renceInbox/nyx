import asyncio

from src.auth import get_jwks


async def refresh_jwks_periodically():
    while True:
        await get_jwks()
        await asyncio.sleep(6 * 3600)
