import asyncio

from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from starlette.responses import JSONResponse

from app.services.github_services import fetch_repo_contents
from logger_config import setup_logger

logger = setup_logger()

app = FastAPI()


class ReviewRequest(BaseModel):
    assignment_description: str
    github_repo_url: HttpUrl
    candidate_level: str


@app.post("/review")
async def review(request: ReviewRequest) -> JSONResponse:
    try:
        logger.info(
            f"Trying to fetch repo contents for {request.github_repo_url}"
        )

        repo_data = await fetch_repo_contents(request.github_repo_url)
    except Exception as e:
        logger.error(f"Error fetching repo contents: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": "Error fetching repo contents"}
        )


request_sample = ReviewRequest(assignment_description="some description",
                               github_repo_url="https://errors.pydantic.dev/2.9/v/url_parsing",
                               candidate_level="1")
asyncio.run(review(request_sample))
