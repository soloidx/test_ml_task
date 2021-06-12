from typing import Optional
from pydantic import BaseSettings, HttpUrl, Field, RedisDsn


class Settings(BaseSettings):
    model_URL: HttpUrl = Field(..., env="TEST_ML_MODEL_URL")
    labels_URL: HttpUrl = Field(..., env="TEST_ML_LABELS_URL")
    redis_DSN: Optional[RedisDsn] = Field(env="TEST_ML_REDIS_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
