import pytest
from unittest.mock import AsyncMock, patch
from litestar.status_codes import HTTP_201_CREATED
from litestar.testing import TestClient
from src.main import app


@pytest.fixture
def client():
    with TestClient(app=app) as client:
        yield client


def test_login_success(client):
    """
    Test that the login endpoint returns a 201 Created and a valid token response.
    Mocks the external call to Zitadel.
    """
    mock_response = {
        "access_token": "mock-access-token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "mock-refresh-token",
    }

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200, json=lambda: mock_response, raise_for_status=lambda: None
        )

        response = client.post("/login")

        assert response.status_code == HTTP_201_CREATED

        data = response.json()
        assert data["access_token"] == "mock-access-token"
        assert data["token_type"] == "Bearer"
        assert data["expires_in"] == 3600
        assert data["refresh_token"] == "mock-refresh-token"
