from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    model_dir: str = "/app/data/models"
    whisper_model: str = "small"
    use_gpu: bool = True
    bert_model: str = "dccuchile/bert-base-spanish-wwm-cased"
    backend_url: str = "http://localhost:8000"
    redis_url: str = "redis://localhost:6379"
    internal_api_key: str = "usfx-internal-ai-key-2024"
    claude_api_key: str = ""

    @property
    def classifier_path(self) -> Path:
        return Path(self.model_dir) / "classifier"

    @property
    def classifier_active_path(self) -> Path:
        return Path(self.model_dir) / "classifier" / "active"

    class Config:
        env_file = ".env"


settings = Settings()
