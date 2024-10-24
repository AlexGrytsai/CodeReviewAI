import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app, ReviewRequest


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_review_success(client):
    request_data = {
        "assignment_description": "Analyze this code.",
        "github_repo_url": "http://github.com/owner/repo",
        "candidate_level": "junior",
    }

    with patch(
        "app.services.manage_api_service.ManageAPIService.main",
        new_callable=AsyncMock,
    ) as mock_main:
        mock_main.return_value = {"result": "success"}

        response = client.post("/review", json=request_data)

        assert response.status_code == 200
        assert response.json() == {"result": "success"}
        mock_main.assert_awaited_once_with(
            request_data["github_repo_url"],
            request_data["candidate_level"],
            request_data["assignment_description"],
        )


@pytest.mark.asyncio
async def test_review_http_exception(client):
    request_data = {
        "assignment_description": "Analyze this code.",
        "github_repo_url": "http://github.com/owner",
        "candidate_level": "junior",
    }

    with patch(
        "app.services.manage_api_service.ManageAPIService.main",
        new_callable=AsyncMock,
    ) as mock_main:
        mock_main.side_effect = HTTPException(
            status_code=400, detail="Bad Request"
        )

        response = client.post("/review", json=request_data)

        assert response.status_code == 400
        assert response.json() == {"detail": "Bad Request"}


@pytest.mark.asyncio
async def test_review_general_exception(client):
    request_data = {
        "assignment_description": "Analyze this code.",
        "github_repo_url": "http://example.com/repo",
        "candidate_level": "junior",
    }

    with patch(
        "app.services.manage_api_service.ManageAPIService.main",
        new_callable=AsyncMock,
    ) as mock_main:
        mock_main.side_effect = Exception("An unexpected error occurred")

        response = client.post("/review", json=request_data)

        assert response.status_code == 500
        assert response.json() == {"detail": "An unexpected error occurred"}
