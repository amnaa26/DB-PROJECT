import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Simple settings holder for secrets and configuration."""

    def __init__(self) -> None:
        self.database_url: str | None = os.getenv("DATABASE_URL")
        self.secret_key: str = os.getenv("SECRET_KEY", "change-me")
        self.algorithm: str = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        )

        if not self.database_url:
            raise ValueError(
                "DATABASE_URL is not set. Ensure it exists in your environment or .env file."
            )


settings = Settings()
