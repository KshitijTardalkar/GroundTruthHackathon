import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
    MODEL_NAME: str = "openai/gpt-oss-120b"
    MEMORY_LENGTH: int = 10


settings = Settings()
