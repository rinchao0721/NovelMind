"""
LLM Provider implementations for different API services
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx
import logging

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""

    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.kwargs = kwargs

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate chat completion"""
        pass

    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion from a single prompt"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, **kwargs)

    async def test_connection(self) -> bool:
        """Test if the connection works"""
        try:
            response = await self.complete("Say 'OK' in one word.")
            return bool(response and len(response) > 0)
        except Exception as e:
            logger.error(
                f"Connection test failed for {self.__class__.__name__}: {str(e)}", exc_info=True
            )
            return False


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider (also compatible with OpenAI-format APIs)"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        base_url: str = "https://api.openai.com/v1",
        **kwargs,
    ):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url.rstrip("/")

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate chat completion using OpenAI API"""
        url = f"{self.base_url}/chat/completions"

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4096),
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class AIHubMixProvider(OpenAIProvider):
    """AIHubMix Provider (OpenAI Compatible)"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        base_url: str = "https://aihubmix.com/v1",
        **kwargs,
    ):
        # Auto-fix URL if /v1 is missing but domain is correct
        if "aihubmix.com" in base_url and not base_url.endswith("/v1"):
            base_url = f"{base_url.rstrip('/')}/v1"
        super().__init__(api_key, model, base_url, **kwargs)


class SiliconFlowProvider(OpenAIProvider):
    """SiliconFlow (SiliconCloud) Provider"""

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-ai/DeepSeek-V3",
        base_url: str = "https://api.siliconflow.cn/v1",
        **kwargs,
    ):
        super().__init__(api_key, model, base_url, **kwargs)


class OpenRouterProvider(OpenAIProvider):
    """OpenRouter Provider"""

    def __init__(
        self,
        api_key: str,
        model: str = "openai/gpt-4o",
        base_url: str = "https://openrouter.ai/api/v1",
        **kwargs,
    ):
        super().__init__(api_key, model, base_url, **kwargs)


class OllamaProvider(OpenAIProvider):
    """Ollama Local Provider"""

    def __init__(
        self,
        api_key: str = "ollama",
        model: str = "llama3",
        base_url: str = "http://localhost:11434/v1",
        **kwargs,
    ):
        super().__init__(api_key, model, base_url, **kwargs)


class DeepSeekProvider(OpenAIProvider):
    """DeepSeek API provider (OpenAI compatible)"""

    def __init__(self, api_key: str, model: str = "deepseek-chat", **kwargs):
        super().__init__(
            api_key=api_key, model=model, base_url="https://api.deepseek.com/v1", **kwargs
        )


class QwenProvider(OpenAIProvider):
    """Alibaba Qwen API provider (OpenAI compatible)"""

    def __init__(self, api_key: str, model: str = "qwen-plus", **kwargs):
        super().__init__(
            api_key=api_key,
            model=model,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            **kwargs,
        )


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude API provider"""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = "https://api.anthropic.com/v1"

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate chat completion using Claude API"""
        url = f"{self.base_url}/messages"

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        # Convert messages to Claude format
        system_message = ""
        claude_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                claude_messages.append({"role": msg["role"], "content": msg["content"]})

        payload = {
            "model": self.model,
            "messages": claude_messages,
            "max_tokens": kwargs.get("max_tokens", 4096),
        }

        if system_message:
            payload["system"] = system_message

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider"""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate chat completion using Gemini API"""
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": kwargs.get("max_tokens", 4096),
            },
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]


class ZhipuProvider(BaseLLMProvider):
    """Zhipu AI (GLM) API provider"""

    def __init__(self, api_key: str, model: str = "glm-4", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate chat completion using Zhipu API"""
        url = f"{self.base_url}/chat/completions"

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4096),
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class BaiduProvider(BaseLLMProvider):
    """Baidu Wenxin API provider"""

    def __init__(self, api_key: str, secret_key: str, model: str = "ernie-4.0-8k", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.secret_key = secret_key
        self._access_token: Optional[str] = None

    async def _get_access_token(self) -> str:
        """Get access token from Baidu API"""
        if self._access_token:
            return self._access_token

        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params)
            response.raise_for_status()
            data = response.json()
            access_token: str = data["access_token"]
            self._access_token = access_token
            return access_token

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate chat completion using Baidu API"""
        access_token = await self._get_access_token()

        # Model endpoint mapping
        model_endpoints = {
            "ernie-4.0-8k": "completions_pro",
            "ernie-3.5-8k": "completions",
            "ernie-speed": "ernie_speed",
        }

        endpoint = model_endpoints.get(self.model, "completions_pro")
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{endpoint}?access_token={access_token}"

        payload = {
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["result"]


# Provider factory
def create_provider(provider_name: str, config: Dict[str, Any]) -> BaseLLMProvider:
    """Factory function to create LLM provider instances"""

    providers = {
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
        "gemini": GeminiProvider,
        "deepseek": DeepSeekProvider,
        "qwen": QwenProvider,
        "zhipu": ZhipuProvider,
        "baidu": BaiduProvider,
        "custom": OpenAIProvider,
        "aihubmix": AIHubMixProvider,
        "siliconflow": SiliconFlowProvider,
        "openrouter": OpenRouterProvider,
        "ollama": OllamaProvider,
    }

    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}")

    return provider_class(**config)
