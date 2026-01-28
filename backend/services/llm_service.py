"""
LLM Service - Unified interface for multiple LLM providers
"""

import json
import time
from typing import Dict, Any, Optional, List

from llm.providers import (
    BaseLLMProvider,
    create_provider,
)
from config import settings
from utils.logger import logger


class LLMService:
    """Main LLM service class using our custom providers"""

    # Model mappings for different providers
    PROVIDER_MODELS: Dict[str, Dict[str, Any]] = {
        "openai": {
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
            "default": "gpt-4o",
        },
        "claude": {
            "models": [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
                "claude-3-opus-20240229",
            ],
            "default": "claude-3-5-sonnet-20241022",
        },
        "gemini": {
            "models": ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"],
            "default": "gemini-1.5-flash",
        },
        "deepseek": {
            "models": ["deepseek-chat", "deepseek-reasoner"],
            "default": "deepseek-chat",
        },
        "qwen": {
            "models": ["qwen-max", "qwen-plus", "qwen-turbo"],
            "default": "qwen-plus",
        },
        "zhipu": {
            "models": ["glm-4", "glm-4-flash", "glm-3-turbo"],
            "default": "glm-4",
        },
        "baidu": {
            "models": ["ernie-4.0-8k", "ernie-3.5-8k", "ernie-speed"],
            "default": "ernie-4.0-8k",
        },
        "aihubmix": {
            "models": ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-pro-latest"],
            "default": "gpt-4o",
        },
        "siliconflow": {
            "models": [
                "deepseek-ai/DeepSeek-V3",
                "deepseek-ai/DeepSeek-R1",
                "Qwen/Qwen2.5-72B-Instruct",
            ],
            "default": "deepseek-ai/DeepSeek-V3",
        },
        "openrouter": {
            "models": ["openai/gpt-4o", "anthropic/claude-3.5-sonnet", "google/gemini-pro-1.5"],
            "default": "openai/gpt-4o",
        },
        "ollama": {
            "models": ["llama3", "mistral", "qwen2"],
            "default": "llama3",
        },
    }

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        self._client: Optional[BaseLLMProvider] = None

    def _get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get configuration for a specific provider from settings"""
        configs: Dict[str, Dict[str, Any]] = {
            "openai": {
                "api_key": settings.OPENAI_API_KEY or "",
                "model": settings.OPENAI_MODEL or "gpt-4o",
                "base_url": settings.OPENAI_BASE_URL or "https://api.openai.com/v1",
            },
            "claude": {
                "api_key": settings.ANTHROPIC_API_KEY or "",
                "model": settings.CLAUDE_MODEL or "claude-3-5-sonnet-20241022",
            },
            "gemini": {
                "api_key": settings.GOOGLE_API_KEY or "",
                "model": settings.GEMINI_MODEL or "gemini-1.5-flash",
            },
            "deepseek": {
                "api_key": settings.DEEPSEEK_API_KEY or "",
                "model": settings.DEEPSEEK_MODEL or "deepseek-chat",
            },
            "qwen": {
                "api_key": settings.QWEN_API_KEY or "",
                "model": settings.QWEN_MODEL or "qwen-plus",
            },
            "zhipu": {
                "api_key": settings.ZHIPU_API_KEY or "",
                "model": settings.ZHIPU_MODEL or "glm-4",
            },
            "baidu": {
                "api_key": settings.BAIDU_API_KEY or "",
                "secret_key": settings.BAIDU_SECRET_KEY or "",
                "model": settings.BAIDU_MODEL or "ernie-4.0-8k",
            },
            "custom": {
                "api_key": settings.CUSTOM_API_KEY or "",
                "model": settings.CUSTOM_MODEL_NAME or "gpt-4o",
                "base_url": settings.CUSTOM_BASE_URL or "https://api.openai.com/v1",
            },
            # New Providers - Configs will be loaded dynamically from settings_service primarily
            # These are defaults if ENV vars were used, but we rely on settings_service for new ones mostly
            "aihubmix": {},
            "siliconflow": {},
            "openrouter": {},
            "ollama": {},
        }

        # Merge with dynamically loaded settings if available via config.settings
        # Note: settings.py currently only has env vars.
        # The SettingsService loads from JSON.
        # This method is primarily used when initializing from ENV or default config.
        # When called from UI context, we often pass specific config.

        return configs.get(provider, {})

    def _create_client(
        self, provider: Optional[str] = None, config: Optional[Dict[str, Any]] = None
    ) -> BaseLLMProvider:
        """Create LLM client for the specified provider"""
        provider_name = provider or self.provider

        if config:
            # Use provided config (from frontend settings)
            api_key = config.get("apiKey") or config.get("api_key", "")
            # Mask key for logging
            masked_key = (
                api_key[:4] + "***" + api_key[-4:] if api_key and len(api_key) > 8 else "***"
            )
            logger.info(
                f"Initializing {provider_name} provider with model: {config.get('model')} (Key: {masked_key})"
            )

            return create_provider(
                provider_name,
                {
                    "api_key": api_key,
                    "model": config.get("model", "gpt-4o"),
                    "base_url": config.get("baseUrl") or config.get("base_url"),
                    "secret_key": config.get("secretKey") or config.get("secret_key"),
                },
            )
        else:
            # Use settings config
            logger.info(f"Initializing {provider_name} provider from default settings")
            cfg = self._get_provider_config(provider_name)
            return create_provider(provider_name, cfg)

    async def complete(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate completion"""
        provider_name = provider or self.provider
        config = None

        # Load full settings to get keys for new providers
        from services.settings_service import get_settings_service

        settings_service = get_settings_service()
        all_settings = await settings_service.load_settings()

        if provider_name in all_settings:
            p_settings = all_settings[provider_name]
            config = {
                "api_key": p_settings.get("apiKey", ""),
                "model": p_settings.get("model", ""),
                "base_url": p_settings.get("baseUrl", ""),
                "secret_key": p_settings.get("secretKey", ""),
            }

        # Override model if provided
        if model and config:
            config["model"] = model
        elif model and not config:
            # Fallback if config not found (e.g. env vars only)
            base_config = self._get_provider_config(provider_name)
            if base_config:
                config = base_config
                config["model"] = model

        client = self._create_client(provider_name, config)

        # Log request
        logger.info(
            f"LLM Request [Complete] | Provider: {provider_name} | Model: {config.get('model') if config else 'default'}"
        )
        logger.debug(f"Prompt: {prompt[:100]}...")

        start_time = time.time()
        try:
            response = await client.complete(prompt, **kwargs)
            duration = time.time() - start_time
            logger.info(f"LLM Response | Duration: {duration:.2f}s | Length: {len(response)} chars")
            return response
        except Exception as e:
            logger.error(f"LLM Error [Complete] | Provider: {provider_name} | Error: {str(e)}")
            raise

    async def chat(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate chat completion"""
        provider_name = provider or self.provider
        config = None

        # Load full settings to get keys for new providers
        from services.settings_service import get_settings_service

        settings_service = get_settings_service()
        all_settings = await settings_service.load_settings()

        if provider_name in all_settings:
            p_settings = all_settings[provider_name]
            config = {
                "api_key": p_settings.get("apiKey", ""),
                "model": p_settings.get("model", ""),
                "base_url": p_settings.get("baseUrl", ""),
                "secret_key": p_settings.get("secretKey", ""),
            }

        # Override model if provided
        if model and config:
            config["model"] = model
        elif model and not config:
            base_config = self._get_provider_config(provider_name)
            if base_config:
                config = base_config
                config["model"] = model

        client = self._create_client(provider_name, config)

        # Log request
        logger.info(
            f"LLM Request [Chat] | Provider: {provider_name} | Model: {config.get('model') if config else 'default'}"
        )

        start_time = time.time()
        try:
            response = await client.chat(messages, **kwargs)
            duration = time.time() - start_time
            logger.info(f"LLM Response | Duration: {duration:.2f}s | Length: {len(response)} chars")
            return response
        except Exception as e:
            logger.error(f"LLM Error [Chat] | Provider: {provider_name} | Error: {str(e)}")
            raise

    async def test_connection(
        self, provider: Optional[str] = None, config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Test connection to the LLM provider"""
        try:
            client = self._create_client(provider, config)
            if config and (config.get("baseUrl") or config.get("base_url")):
                logger.info(
                    f"Testing connection to {provider} at {config.get('baseUrl') or config.get('base_url')}"
                )

            return await client.test_connection()
        except Exception as e:
            logger.error(f"Connection test failed for {provider}: {e}")
            logger.exception("Full traceback:")  # Log full traceback
            return False

    async def analyze_characters(
        self, text: str, provider: Optional[str] = None, model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Use LLM to extract characters from text"""
        logger.info("Starting character extraction...")
        # Limit text to avoid token limits
        text_sample = text[:8000]

        prompt = f"""请分析以下小说文本，提取所有出现的人物角色。
对于每个人物，请提供：
1. 姓名
2. 别名/称呼（如果有）
3. 简短描述
4. 性格特点
5. 重要性评分（0-1，1为最重要）

请以JSON数组格式返回结果。

文本内容：
{text_sample}

请返回JSON格式：
[{{"name": "...", "aliases": [...], "description": "...", "personality": "...", "importance": 0.8}}]
"""

        response = await self.complete(prompt, provider, model)

        # Parse JSON response
        try:
            # Try to extract JSON from response
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                logger.info(f"Extracted {len(data)} characters")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse character JSON: {e}")
            pass

        return []

    async def analyze_relationships(
        self,
        characters: List[Dict[str, Any]],
        text: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Use LLM to analyze relationships between characters"""
        logger.info(f"Starting relationship analysis for {len(characters)} characters...")
        char_names = [c.get("name", "") for c in characters if c.get("name")]
        text_sample = text[:8000]

        prompt = f"""请分析以下小说文本中人物之间的关系。

已识别的人物：{", ".join(char_names)}

对于每对有关系的人物，请提供：
1. 关系类型（family/friend/enemy/lover/colleague/other）
2. 具体关系（如：父子、夫妻、死敌等）
3. 关系强度（0-1）
4. 关系描述

文本内容：
{text_sample}

请返回JSON格式：
[{{"source": "人物A", "target": "人物B", "type": "family", "subtype": "父子", "strength": 0.9, "description": "..."}}]
"""

        response = await self.complete(prompt, provider, model)

        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                logger.info(f"Extracted {len(data)} relationships")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse relationship JSON: {e}")
            pass

        return []

    async def generate_summary(
        self, text: str, provider: Optional[str] = None, model: Optional[str] = None
    ) -> str:
        """Generate summary for text"""
        logger.info("Generating summary...")
        text_sample = text[:6000]

        prompt = f"""请为以下小说章节生成一个简洁的摘要（100-200字）：

{text_sample}

摘要："""

        return await self.complete(prompt, provider, model)

    async def analyze_plot_events(
        self, text: str, provider: Optional[str] = None, model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract key plot events from text"""
        logger.info("Starting plot analysis...")
        text_sample = text[:8000]

        prompt = f"""请分析以下小说文本，提取关键剧情事件。

对于每个事件，请提供：
1. 事件名称（简短标题）
2. 事件描述
3. 涉及人物
4. 事件类型（conflict/revelation/turning_point/climax/resolution）
5. 重要性（0-1）

文本内容：
{text_sample}

请返回JSON格式：
[{{"title": "...", "description": "...", "characters": [...], "type": "conflict", "importance": 0.8}}]
"""

        response = await self.complete(prompt, provider, model)

        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                logger.info(f"Extracted {len(data)} plot events")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse plot JSON: {e}")
            pass

        return []


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get the LLM service singleton"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
