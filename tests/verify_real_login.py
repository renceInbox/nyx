import asyncio
from litestar.testing import AsyncTestClient
from src.main import app
from litestar.status_codes import HTTP_201_CREATED


async def verify_login():
    async with AsyncTestClient(app=app) as client:
        print("Attempting real login...")
        response = await client.post("/login")

        print(f"Status Code: {response.status_code}")
        if response.status_code == HTTP_201_CREATED:
            print("Login successful!")
            print(f"Response: {response.json()}")
        else:
            print("Login failed.")
            print(f"Response: {response.text}")


if __name__ == "__main__":
    asyncio.run(verify_login())
