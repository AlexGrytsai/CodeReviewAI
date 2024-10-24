import asyncio
import base64
import os
from datetime import datetime
from typing import Any, Dict, List

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi import status
from pydantic import HttpUrl

from settings import setup_logger

logger = setup_logger()

load_dotenv()


class GitHubService:
    API_HOST = "https://api.github.com"

    @staticmethod
    def _validate_url(url: str) -> HttpUrl:
        try:
            valid_url = HttpUrl(url)
            host = valid_url.host
            if host != "github.com":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported host: {host}",
                )

            path = valid_url.path
            if path:
                split_path = path.split("/")[1:]
                if len(split_path) != 2:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid path: {path}",
                    )
                return valid_url
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid path: {path} in {url}",
                )

        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error validating repo url: {exc}",
            )

    @staticmethod
    def _get_owner_and_repo(repo_url: HttpUrl) -> tuple[str, str]:
        if repo_url.path:
            owner, repo = repo_url.path.split("/")[1:]

            return owner, repo

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid path: {repo_url.path} in {repo_url}",
        )

    @staticmethod
    async def _make_request(
        url: str, client: httpx.AsyncClient
    ) -> list[dict] | dict:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        logger.info(f"Making request to: {url}")
        number_retry = 10
        while True:
            try:
                logger.info(f"Trying to fetch repo contents: {url}")
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    logger.info(
                        f"Repo contents fetched successfully. "
                        f"Status code: {response.status_code}. "
                    )
                    return response.json()
                elif response.status_code == 403:
                    logger.info(
                        f"Status code: {response.status_code}, "
                        f"Message: {response.text}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={response.text},
                    )
                elif response.status_code == 404:
                    logger.info(f"Repo contents not found for url: {url}.")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Repo contents not found for url: {url}",
                    )
                elif response.status_code == 429:
                    logger.info(
                        f"Status code: {response.status_code}, "
                        f"Message: {response.text}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail={response.text},
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error fetching repo contents: "
                               f"{response}, status code: "
                               f"{response.status_code}",
                    )
            except httpx.ConnectTimeout:
                logger.info("Connect timeout to GitHub. Retry...")
                if number_retry == 0:
                    logger.warning(
                        "Connect timeout. Cannot fetch repo contents"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                        detail="Connect timeout. "
                               "Cannot fetch repo contents",
                    )
                number_retry -= 1

    async def _fetch_repo_contents(
        self, owner: str, repo: str, client: httpx.AsyncClient
    ) -> list[dict[Any, Any]] | dict[Any, Any]:

        url = f"{GitHubService.API_HOST}/repos/{owner}/{repo}/contents"

        return await self._make_request(url, client)

    @staticmethod
    def _decode_content(content: str) -> str:
        return base64.b64decode(content).decode("utf-8")

    async def _get_file_content(
        self, item: dict, client: httpx.AsyncClient
    ) -> dict[str, str | Any]:
        if item.get("url"):
            self_data = await self._make_request(item["url"], client)

            if isinstance(self_data, dict) and self_data.get("content"):
                content = self._decode_content(self_data["content"])
                name = item["name"]
                type_content = item["type"]
                return {"name": name, "type": type_content, "content": content}

        return {}

    async def _get_dir_content(
        self, item: dict, client: httpx.AsyncClient
    ) -> List[Dict[str, Any]]:

        if item.get("url"):
            dir_data = await self._make_request(item["url"], client)
            return await self._receive_repo_data(dir_data, client)

        return [{"name": item["name"], "type": "dir", "content": []}]

    async def _receive_repo_data(
        self,
        repo_data: list[dict[Any, Any]] | dict[Any, Any],
        client: httpx.AsyncClient,
    ) -> list[dict[Any, Any]]:
        structure_data = []

        tasks = []
        directories = []
        for item in repo_data:
            if item["type"] == "file":
                tasks.append(self._get_file_content(item, client))
            elif item["type"] == "dir":
                directories.append(item)
                tasks.append(self._get_dir_content(item, client))

        results = await asyncio.gather(*tasks)

        result_idx = 0
        for item in repo_data:
            if item["type"] == "file":
                structure_data.append(results[result_idx])
                result_idx += 1
            elif item["type"] == "dir":
                directory_structure = {
                    "name": item["name"],
                    "type": item["type"],
                    "content": results[result_idx],
                }
                structure_data.append(directory_structure)
                result_idx += 1

        return structure_data

    async def main(self, repo_url: str) -> list[dict]:
        valid_url = self._validate_url(repo_url)
        if valid_url:
            start_time = datetime.now()

            owner, repo = self._get_owner_and_repo(valid_url)

            try:
                async with httpx.AsyncClient() as client:
                    raw_repo_data = await self._fetch_repo_contents(
                        owner, repo, client
                    )
                    clean_repo_data = await self._receive_repo_data(
                        raw_repo_data, client
                    )

                    end_time = datetime.now()
                    time_taken = end_time - start_time

                    logger.info(
                        f"Time taken to fetch repo contents: {time_taken}"
                    )
                    return clean_repo_data

            except Exception as exc:
                raise exc

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid repo url: {repo_url}. "
                       f"Cannot fetch repo contents",
            )
