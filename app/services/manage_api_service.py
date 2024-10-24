from datetime import datetime
from typing import Dict, Any

from fastapi import HTTPException
from fastapi import status

from app.services.github_service import GitHubService
from app.services.openai_services import OpenAIService
from settings import setup_logger

logger = setup_logger()


class ManageAPIService:
    def __init__(self):
        self.github_service = GitHubService()
        self.openai_service = OpenAIService()

    @staticmethod
    def _validate_candidate_level(candidate_level: str) -> bool:
        if candidate_level.lower() not in ("junior", "middle", "senior"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid candidate level. "
                       "Must be 'junior', 'middle', or 'senior'",
            )
        return True

    async def main(
        self, repo_url: str, candidate_level: str, assignment_description: str
    ) -> Dict[str, Any]:
        try:
            start_time = datetime.now()
            logger.info(
                f"Trying to validate candidate level: {candidate_level}"
            )
            self._validate_candidate_level(candidate_level)

            logger.info(f"Trying to fetch repo contents for '{repo_url}'")

            repo_data = await self.github_service.main(repo_url)

            end_time_fetching_repo = datetime.now()

            logger.info(f"Trying to analyze code with OpenAI for '{repo_url}'")

            code_review = await self.openai_service.analyze_code_with_openai(
                repo_data, candidate_level, assignment_description, repo_url
            )

            end_time_analyzing_code = datetime.now()

            time_for_fetching_repo = end_time_fetching_repo - start_time
            time_for_analyzing_code = (
                end_time_analyzing_code - end_time_fetching_repo
            )
            total_time = end_time_analyzing_code - start_time

            logger.info(
                f"Finished analyzing code with OpenAI for '{repo_url}'.\n"
                f"Time for fetching repo contents: {time_for_fetching_repo}.\n"
                f"Time for analyzing code: {time_for_analyzing_code}.\n"
                f"Total time: {total_time}"
            )

            return code_review

        except HTTPException as exc:
            raise exc
