import json
from typing import Any

from fastapi import FastAPI
from fastapi import HTTPException, status
from pydantic import BaseModel
from redis.asyncio import Redis

from app.services.manage_api_service import ManageAPIService
from settings import setup_logger, REDIS_URL

logger = setup_logger()

app = FastAPI()

redis_client = Redis.from_url(REDIS_URL)


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
        cache_key = f"{request.github_repo_url}_{request.candidate_level}"

        try:
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info(
                    f"Found cached result for '{request.github_repo_url}'"
                )
                return json.loads(cached_result)
        except Exception as exc:
            logger.info(
                f"Failed to fetch cached result. Error: '{exc}'"
            )

        result = await ManageAPIService().main(
            request.github_repo_url,
            request.candidate_level,
            request.assignment_description
        )

        try:
            await redis_client.set(cache_key, json.dumps(result), ex=300)
        except Exception as exc:
            logger.info(
                f"Failed to adding a result to cache. Error: '{exc}'"
            )

        return result
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
