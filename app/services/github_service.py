import base64
import os
from typing import Any

import httpx
from dotenv import load_dotenv
from pydantic import HttpUrl

from logger_config import setup_logger

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
                raise Exception(f"Unsupported host: {host}")

            path = valid_url.path
            if path:
                split_path = path.split("/")[1:]
                if len(split_path) != 2:
                    raise Exception(f"Invalid path: {path}")
                return valid_url
            raise Exception(f"Invalid path: {path} in {url}")

        except Exception as e:
            raise Exception(f"Error validating repo url: {e}")

    @staticmethod
    def _get_owner_and_repo(repo_url: HttpUrl) -> tuple[str, str]:
        if repo_url.path:
            owner, repo = repo_url.path.split("/")[1:]

            return owner, repo
        raise Exception(f"Invalid path: {repo_url.path} in {repo_url}")

    @staticmethod
    async def _make_request(url: str) -> list[dict] | dict:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        logger.info(f"Making request to: {url}")
        async with httpx.AsyncClient() as client:
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
                    else:
                        raise Exception(
                            f"Error fetching repo contents: "
                            f"{response}, status code: {response.status_code}"
                        )
                except httpx.ConnectTimeout:
                    if number_retry == 0:
                        raise Exception(
                            "Connect timeout. Cannot fetch repo contents"
                        )
                    number_retry -= 1

    async def _fetch_repo_contents(
        self, owner: str, repo: str
    ) -> list[dict[Any, Any]] | dict[Any, Any]:

        url = f"{GitHubService.API_HOST}/repos/{owner}/{repo}/contents"

        return await self._make_request(url)

    @staticmethod
    def _decode_content(content: str) -> str:
        return base64.b64decode(content).decode("utf-8")

    async def _get_file_content(self, item: dict) -> dict[str, str | Any]:
        if item.get("url"):
            self_data = await self._make_request(item["url"])

            if isinstance(self_data, dict) and self_data.get("content"):
                content = self._decode_content(self_data["content"])
                name = item["name"]
                type_content = item["type"]
                return {"name": name, "type": type_content, "content": content}

        return {}

    async def _get_dir_content(
        self, item: dict
    ) -> list[dict[str, str]] | dict[Any, Any]:

        if item.get("url"):
            dir_data = await self._make_request(item["url"])
            return await self._receive_repo_data(dir_data)

        return []

    async def _receive_repo_data(
        self, repo_data: list[dict[Any, Any]] | dict[Any, Any]
    ) -> list[dict[Any, Any]]:

        structure_data = []
        for item in repo_data:
            logger.info(f"Processing item: {item}")
            if item["type"] == "file":
                structure_data.append(await self._get_file_content(item))
            elif item["type"] == "dir":
                dir_content = await self._get_dir_content(item)
                directory_structure = {
                    "name": item["name"],
                    "type": item["type"],
                    "content": [],
                }
                structure_data.append(directory_structure)
                for content in dir_content:
                    if content["type"] == "file":
                        directory_structure["content"].append(content)
                    elif content["type"] == "dir":
                        directory_structure["content"].append(content)
        return structure_data

    async def main(self, repo_url: str) -> list[dict]:
        valid_url = self._validate_url(repo_url)
        if valid_url:
            owner, repo = self._get_owner_and_repo(valid_url)

            try:
                raw_repo_data = await self._fetch_repo_contents(owner, repo)
                clean_repo_data = await self._receive_repo_data(raw_repo_data)
                return clean_repo_data

            except Exception as e:
                raise Exception(f"Error fetching repo contents: {e}")

        else:
            raise Exception(
                f"Invalid repo url: {repo_url}. Cannot fetch repo contents"
            )
