"""配置管理系统 —— 使用 Pydantic Settings 管理所有环境变量和配置"""

from typing import List
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，自动从 .env 文件和环境变量加载"""

    # 应用
    app_name: str = "Week1 FullStack API"
    app_version: str = "1.0.0"
    debug: bool = True

    # 数据库
    database_url: str = "sqlite+aiosqlite:///./week1.db"

    # JWT
    secret_key: str = "week1-dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:5500", "http://localhost:5500"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """单例模式获取配置 —— 全局只实例化一次"""
    return Settings()
