import json
import os

import tiktoken
from dotenv import load_dotenv
from openai import AsyncOpenAI
from fastapi.exceptions import HTTPException
from fastapi import status

from settings import setup_logger, OPENAI_MODEL, MODEL_TOKEN_LIMITS

load_dotenv()

logger = setup_logger()


class OpenAIService:

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    @staticmethod
    def _validate_length_prompt(prompt: str) -> None:
        encoding = tiktoken.encoding_for_model(OPENAI_MODEL)

        tokens = encoding.encode(prompt)
        length_tokens_prompt = len(tokens)

        model_max_tokens = MODEL_TOKEN_LIMITS[OPENAI_MODEL]

        if length_tokens_prompt > model_max_tokens:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Prompt is too long: {length_tokens_prompt} tokens. "
                f"Max tokens: {MODEL_TOKEN_LIMITS[OPENAI_MODEL]}",
            )

    def _format_repo_data_for_prompt(
        self, repo_data: list[dict], indent=0
    ) -> str:
        formatted_data = ""
        for item in repo_data:
            if item.get("type") == "file":
                formatted_data += " " * indent + (
                    f"File: {item['name']}\n"
                    f"Content:\n"
                    f"{item['content']}\n\n"
                )
            elif item.get("type") == "dir":
                formatted_data += " " * indent + f"Directory: {item['name']}\n"
                formatted_data += self._format_repo_data_for_prompt(
                    item["content"], indent + 2
                )
        return formatted_data

    async def analyze_code_with_openai(
        self,
        repo_data: list[dict],
        candidate_level: str,
        assignment_description: str,
        repo_url: str,
    ) -> None:
        logger.info(f"Starting code review with OpenAI for '{repo_url}'")
        logger.info(
            f"Starting formatting repo data for prompt for '{repo_url}'"
        )

        formatted_data_from_github = self._format_repo_data_for_prompt(
            repo_data
        )

        logger.info(f"Finished formatting repo data for prompt ({repo_url})")

        try:
            self._validate_length_prompt(formatted_data_from_github)

            prompt = (
                f"Here is a repository with the following files: "
                f"{formatted_data_from_github}. "
                f"Description: {assignment_description}. "
                f"Analyze the code for a {candidate_level} developer, "
                f"and provide feedback."
                f"Return the review result (text) in the following format: "
                f"Found files, Downsides/Comments, Rating (from 0 to 10), "
                f"Conclusion. "
                f"It must be dictionary. "
                f"Return data without special characters or formatting."
            )

            try:
                logger.info(
                    f"Trying to analyze code with OpenAI for '{repo_url}'"
                )
                response = await self.client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a code review assistant.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                )

                review = response.choices[0].message.content
                review_json = json.loads(review)

                logger.info(
                    f"Finished analyzing code with OpenAI for {repo_url}"
                )
                return review_json

            except Exception as e:
                raise Exception(f"Error analyzing code: {e}")

        except HTTPException as exc:
            raise exc
