"""
LLM Service - Unified interface for multiple LLM providers
"""

import json
from typing import Dict, Any, Optional, List

from llm.providers import (
    BaseLLMProvider,
    create_provider,
    OpenAIProvider,
    ClaudeProvider,
    GeminiProvider,
    DeepSeekProvider,
    QwenProvider,
    ZhipuProvider,
    BaiduProvider,
)
from config import settings


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
        }
        return configs.get(provider, configs["openai"])

    def _create_client(
        self, provider: Optional[str] = None, config: Optional[Dict[str, Any]] = None
    ) -> BaseLLMProvider:
        """Create LLM client for the specified provider"""
        provider_name = provider or self.provider

        if config:
            # Use provided config (from frontend settings)
            return create_provider(
                provider_name,
                {
                    "api_key": config.get("apiKey") or config.get("api_key", ""),
                    "model": config.get("model", "gpt-4o"),
                    "base_url": config.get("baseUrl") or config.get("base_url"),
                    "secret_key": config.get("secretKey") or config.get("secret_key"),
                },
            )
        else:
            # Use settings config
            cfg = self._get_provider_config(provider_name)
            return create_provider(provider_name, cfg)

    async def complete(self, prompt: str, provider: Optional[str] = None, **kwargs: Any) -> str:
        """Generate completion"""
        client = self._create_client(provider)
        return await client.complete(prompt, **kwargs)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate chat completion"""
        client = self._create_client(provider)
        return await client.chat(messages, **kwargs)

    async def test_connection(
        self, provider: Optional[str] = None, config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Test connection to the LLM provider"""
        try:
            client = self._create_client(provider, config)
            return await client.test_connection()
        except Exception:
            return False

    async def analyze_characters(
        self, text: str, provider: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Use LLM to extract characters from text"""
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

        response = await self.complete(prompt, provider)

        # Parse JSON response
        try:
            # Try to extract JSON from response
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass

        return []

    async def analyze_relationships(
        self,
        characters: List[Dict[str, Any]],
        text: str,
        provider: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Use LLM to analyze relationships between characters"""
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

        response = await self.complete(prompt, provider)

        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass

        return []

    async def generate_summary(self, text: str, provider: Optional[str] = None) -> str:
        """Generate summary for text"""
        text_sample = text[:6000]

        prompt = f"""请为以下小说章节生成一个简洁的摘要（100-200字）：

{text_sample}

摘要："""

        return await self.complete(prompt, provider)

    async def analyze_plot_events(
        self, text: str, provider: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract key plot events from text"""
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

        response = await self.complete(prompt, provider)

        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
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
