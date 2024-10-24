import logging


OPENAI_MODEL = "gpt-4-turbo"

MODEL_TOKEN_LIMITS = {
    "gpt-4": 10000,
    "gpt-4o-realtime-preview": 20000,
    "gpt-4-turbo": 30000,
    "gpt-3.5-turbo": 200000,
}

def setup_logger() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    logger = logging.getLogger(__name__)

    return logger
