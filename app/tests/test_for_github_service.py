from unittest.mock import AsyncMock, patch

import fastapi
import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from pydantic_core import Url

from app.services.github_service import GitHubService


@pytest.mark.asyncio
async def test_validate_url_valid():
    url = "https://github.com/owner/repo"
    result = GitHubService._validate_url(url)
    assert result == Url("https://github.com/owner/repo")


@pytest.mark.asyncio
async def test_validate_url_invalid_host():
    url = "https://gitlab.com/owner/repo"
    with pytest.raises(HTTPException) as exc:
        GitHubService._validate_url(url)
    assert exc.value.status_code == 400
    assert "Unsupported host" in exc.value.detail


@pytest.mark.asyncio
async def test_validate_url_invalid_path():
    url = "https://github.com/owner"
    with pytest.raises(HTTPException) as exc:
        GitHubService._validate_url(url)
    assert exc.value.status_code == 400
    assert "Invalid path" in exc.value.detail


@pytest.mark.asyncio
async def test_get_owner_and_repo():
    url = "https://github.com/owner/repo"
    valid_url = GitHubService._validate_url(url)
    owner, repo = GitHubService._get_owner_and_repo(valid_url)
    assert owner == "owner"
    assert repo == "repo"


@pytest.mark.asyncio
async def test_get_owner_and_repo_invalid_path():
    url = "https://github.com/owner"
    with pytest.raises(fastapi.HTTPException) as exc:
        GitHubService._validate_url(url)
    assert exc.value.status_code == 400
    assert "Invalid path" in exc.value.detail


@pytest.mark.asyncio
async def test_make_request_not_found():
    url = "https://api.github.com/repos/owner/repo/contents"

    async with AsyncMock() as client:
        client.get = AsyncMock(
            return_value=AsyncMock(status_code=404, text="Not Found")
        )

        with pytest.raises(HTTPException) as exc:
            await GitHubService._make_request(url, client)
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_fetch_repo_contents(mocker):
    response_data = [
        {
            "name": "file1.txt",
            "type": "file",
            "url":
                "https://api.github.com/repos/owner/repo/contents/file1.txt",
        }
    ]

    mock_fetch = mocker.patch.object(
        GitHubService, "_fetch_repo_contents", return_value=response_data
    )

    service = GitHubService()
    async with AsyncClient() as client:
        result = await service._fetch_repo_contents("owner", "repo", client)

    assert result == response_data
    mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_main():
    url = "https://github.com/owner/repo"
    service = GitHubService()

    mock_validate_url = patch.object(
        service, "_validate_url", return_value=url
    )
    mock_get_owner_repo = patch.object(
        service, "_get_owner_and_repo", return_value=("owner", "repo")
    )
    mock_fetch_contents = patch.object(
        service,
        "_fetch_repo_contents",
        return_value=[
            {"name": "file.txt", "type": "file", "content": "Hello World!"}
        ],
    )
    mock_receive_data = patch.object(
        service,
        "_receive_repo_data",
        return_value=[
            {"name": "file.txt", "type": "file", "content": "Hello World!"}
        ],
    )

    with (
        mock_validate_url
    ), mock_get_owner_repo, mock_fetch_contents, mock_receive_data:
        result = await service.main(url)

    assert len(result) == 1
    assert result[0]["name"] == "file.txt"
    assert result[0]["content"] == "Hello World!"
