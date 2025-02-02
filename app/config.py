import os


class Config:
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
    MODEL_NAME = os.getenv("MODEL_NAME", None)

