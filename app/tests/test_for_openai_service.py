import os
from unittest.mock import patch

import fastapi
import pytest

from app.services.openai_services import (
    OpenAIService,
    OPENAI_MODEL,
    MODEL_TOKEN_LIMITS,
)


@pytest.fixture
def openai_service():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "fake_api_key"}):
        return OpenAIService()


def test_validate_length_prompt_valid(openai_service):
    prompt = "Short prompt."
    MODEL_TOKEN_LIMITS[OPENAI_MODEL] = 100
    try:
        openai_service._validate_length_prompt(prompt)
    except fastapi.HTTPException:
        pytest.fail("HTTPException was raised unexpectedly")


def test_validate_length_prompt_too_long(openai_service):
    prompt = "a" * 101
    MODEL_TOKEN_LIMITS[OPENAI_MODEL] = 100
    try:
        openai_service._validate_length_prompt(prompt)
    except fastapi.HTTPException:
        pytest.fail("HTTPException was raised unexpectedly")
