import json
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from logger_config import setup_logger

load_dotenv()

logger = setup_logger()


class OpenAIService:

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    def _format_repo_data_for_prompt(
        self, repo_data: list[dict], indent=0
    ) -> str:
        formatted_data = ""
        for item in repo_data:
            if item["type"] == "file":
                formatted_data += " " * indent + (
                    f"File: {item['name']}\n"
                    f"Content:\n"
                    f"{item['content']}\n\n"
                )
            elif item["type"] == "dir":
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
    ) -> None:
        logger.info("Starting code review with OpenAI")
        logger.info("Starting formatting repo data for prompt")

        formatted_data_from_github = self._format_repo_data_for_prompt(
            repo_data
        )

        logger.info("Finished formatting repo data for prompt")

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
            logger.info("Trying to analyze code with OpenAI")
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo",
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

            logger.info("Finished analyzing code with OpenAI")
            return review_json

        except Exception as e:
            raise Exception(f"Error analyzing code: {e}")
