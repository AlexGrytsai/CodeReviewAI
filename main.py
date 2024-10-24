from typing import Any

from fastapi import FastAPI
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.services.manage_api_service import ManageAPIService
from settings import setup_logger

logger = setup_logger()

app = FastAPI()


class ReviewRequest(BaseModel):
    assignment_description: str
    github_repo_url: str
    candidate_level: str


@app.post("/review")
async def review(request: ReviewRequest) -> dict[str, Any]:
    try:
        logger.info(
            f"Trying to fetch repo contents for '{request.github_repo_url}'"
        )

        return await ManageAPIService().main(
            request.github_repo_url,
            request.candidate_level,
            request.assignment_description
        )
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
