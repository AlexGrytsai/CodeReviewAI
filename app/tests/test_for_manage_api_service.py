from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.services.github_service import GitHubService
from app.services.manage_api_service import ManageAPIService


@pytest.fixture
def manage_api_service():
    return ManageAPIService()


@pytest.mark.asyncio
async def test_validate_candidate_level_success(manage_api_service):
    assert manage_api_service._validate_candidate_level("junior")
    assert manage_api_service._validate_candidate_level("middle")
    assert manage_api_service._validate_candidate_level("senior")


@pytest.mark.asyncio
async def test_validate_candidate_level_failure(manage_api_service):
    with pytest.raises(HTTPException) as exc_info:
        manage_api_service._validate_candidate_level("invalid_level")
    assert exc_info.value.status_code == 400
    assert "Invalid candidate level" in exc_info.value.detail


@pytest.mark.asyncio
@patch.object(GitHubService, 'main', new_callable=AsyncMock)
async def test_main_github_failure(mock_github_service, manage_api_service):
    mock_github_service.side_effect = HTTPException(status_code=404,
                                                    detail="Repo not found")

    with pytest.raises(HTTPException) as exc_info:
        await manage_api_service.main(
            repo_url="https://github.com/user/repo",
            candidate_level="junior",
            assignment_description="Code review assignment"
        )
    assert exc_info.value.status_code == 404
    assert "Repo not found" in exc_info.value.detail
