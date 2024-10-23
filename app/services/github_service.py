import os

import httpx
from dotenv import load_dotenv
from pydantic import HttpUrl, BaseModel

from logger_config import setup_logger

logger = setup_logger()

load_dotenv()


class RepoUrlValidator(BaseModel):
    repo_url: HttpUrl


class GitHubService:
    API_HOST = "https://api.github.com"

    @staticmethod
    def _validate_url(url: str) -> HttpUrl:
        try:
            valid_url = RepoUrlValidator(repo_url=url).repo_url
            host = valid_url.host
            if host != "github.com":
                logger.error(f"Unsupported host: {host}")
                raise Exception(f"Unsupported host: {host}")

            path = valid_url.path
            split_path = valid_url.path.split("/")[1:]
            if len(split_path) != 2:
                logger.error(f"Invalid path: {path}")
                raise Exception(f"Invalid path: {path}")
            return valid_url

        except Exception as e:
            logger.error(f"Error validating repo url: {e}")
            raise Exception(f"Error validating repo url: {e}")

    @staticmethod
    def _get_owner_and_repo(repo_url: HttpUrl) -> tuple[str, str]:
        owner, repo = repo_url.path.split("/")[1:]

        return owner, repo

    @staticmethod
    async def _fetch_repo_contents(owner: str, repo: str) -> list[dict]:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        url = f"{GitHubService.API_HOST}/repos/{owner}/{repo}/contents"

        async with httpx.AsyncClient() as client:
            number_retry = 10
            while True:
                try:
                    response = await client.get(url, headers=headers)
                    if response.status_code == 200:
                        logger.info(
                            f"Repo contents fetched successfully. "
                            f"Status code: {response.status_code}. "
                        )
                        return response.json()
                    else:
                        raise Exception(
                            f"Error fetching repo contents: {response}"
                        )
                except httpx.ConnectTimeout:
                    if number_retry == 0:
                        raise Exception(
                            "Connect timeout. Cannot fetch repo contents"
                        )
                    number_retry -= 1

    async def main(self, repo_url: str) -> list[dict]:
        valid_url = self._validate_url(repo_url)
        if valid_url:
            owner, repo = self._get_owner_and_repo(valid_url)

            try:
                repo_data = await self._fetch_repo_contents(owner, repo)
                return repo_data

            except Exception as e:
                raise Exception(f"Error fetching repo contents: {e}")

        else:
            raise Exception(
                f"Invalid repo url: {repo_url}. Cannot fetch repo contents"
            )
