import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings with validation"""

    # API Keys
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")

    # Model Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "openai/gpt-oss-120b")
    MEMORY_LENGTH: int = int(os.getenv("MEMORY_LENGTH", "10"))

    # Limits
    MAX_MESSAGE_LENGTH: int = 2000
    REQUEST_TIMEOUT: int = 30

    # Paths
    CHROMA_DB_PATH: str = "./data/chroma_db"
    CUSTOMER_DATA_PATH: str = "./data/customer_profiles"

    # Debug
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    def validate(self) -> bool:
        """Validate critical settings"""
        if not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        if len(self.GROQ_API_KEY) < 10:
            raise ValueError("GROQ_API_KEY appears invalid")
        return True


settings = Settings()
