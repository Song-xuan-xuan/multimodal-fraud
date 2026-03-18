import json
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    SECRET_KEY: str = "dev-secret-key"

    JWT_SECRET_KEY: str = "change-this-to-a-secure-random-string"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    DATABASE_URL: str = "sqlite+aiosqlite:///./data/app.db"

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    OPENAI_MODEL: str = ""
    OPENAI_TEMPERATURE: float = 0.2

    ZHIPU_AUDIO_API_KEY: str = ""
    ZHIPU_AUDIO_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    ZHIPU_AUDIO_MODEL: str = "glm-asr-2512"

    SERPAPI_API_KEY: str = ""
    SEARCH_API_KEY: str = ""
    SEARCH_ENGINE_ID: str = ""
    IMAGE_API_KEY: str = ""

    VISION_API_KEY: str = ""
    VISION_BASE_URL: str = ""
    VISION_MODEL: str = ""
    VISION_TEMPERATURE: float = 0.1

    EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"
    EMBEDDING_DEVICE: str = "cuda"
    LOCAL_MODEL_NAME: str = "gpt-neo-2.7B"
    LOCAL_MODEL_REF_PATH: str = "text_aigc/local_infer_ref"
    LOCAL_MODEL_CACHE_DIR: str = "../cache"

    SIMILARITY_TOP_K: int = 3
    CHUNK_SIZE: int = 512

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    MAX_WORKERS: int = 4
    REQUEST_TIMEOUT: int = 30

    USE_OPENAI_API: bool = True
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024

    CORS_ORIGINS: str = '["http://localhost:5173","http://localhost:5174","http://localhost:3000"]'

    BASE_DIR: Path = Path(__file__).parent.parent.parent
    UPLOAD_FOLDER: str = "uploads"
    DATA_DIR: str = "data"
    STORAGE_DIR: str = "storage"

    @property
    def cors_origins_list(self) -> List[str]:
        try:
            return json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            return ["http://localhost:5173"]

    @property
    def upload_path(self) -> Path:
        return self.BASE_DIR / self.UPLOAD_FOLDER

    @property
    def data_path(self) -> Path:
        return self.BASE_DIR / self.DATA_DIR

    @property
    def storage_path(self) -> Path:
        return self.BASE_DIR / self.STORAGE_DIR


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
