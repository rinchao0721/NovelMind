"""
Configuration management using Pydantic Settings
"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings"""

    # App settings
    APP_NAME: str = "NovelMind"
    APP_VERSION: str = "1.0.0"
    APP_PORT: int = 5001
    APP_DEBUG: bool = False
    APP_SECRET_KEY: str = "your-secret-key-change-in-production"

    # Database paths
    DATA_DIR: Path = Path.home() / ".novelmind"
    DATABASE_PATH: Path = DATA_DIR / "novelmind.db"

    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o"

    # Claude settings
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

    # Gemini settings
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-pro"

    # DeepSeek settings
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # Qwen settings
    QWEN_API_KEY: Optional[str] = None
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_MODEL: str = "qwen-plus"

    # Zhipu settings
    ZHIPU_API_KEY: Optional[str] = None
    ZHIPU_MODEL: str = "glm-4"

    # Baidu settings
    BAIDU_API_KEY: Optional[str] = None
    BAIDU_SECRET_KEY: Optional[str] = None
    BAIDU_MODEL: str = "ernie-4.0"

    # Custom API settings
    CUSTOM_API_KEY: Optional[str] = None
    CUSTOM_BASE_URL: Optional[str] = None
    CUSTOM_MODEL_NAME: Optional[str] = None

    # Default LLM provider
    DEFAULT_LLM_PROVIDER: str = "openai"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure data directory exists
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
