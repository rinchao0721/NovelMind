"""
LLM Service - Unified interface for multiple LLM providers
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List, Type
from pydantic import BaseModel, ValidationError

from llm.providers import (
    BaseLLMProvider,
    create_provider,
)
from config import settings
from utils.logger import logger


class CharacterExtraction(BaseModel):
    name: str
    aliases: List[str] = []
    description: Optional[str] = ""
    personality: Optional[str] = ""
    importance: float = 0.5


class RelationshipExtraction(BaseModel):
    source: str
    target: str
    type: str
    subtype: Optional[str] = None
    strength: float = 0.5
    description: Optional[str] = ""


class PlotEventExtraction(BaseModel):
    title: str
    description: str
    characters: List[str] = []
    type: str
    importance: float = 0.5


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
        self._clients: Dict[str, BaseLLMProvider] = {}

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

        return configs.get(provider, {})

    def _create_client(
        self, provider: Optional[str] = None, config: Optional[Dict[str, Any]] = None
    ) -> BaseLLMProvider:
        """Create LLM client for the specified provider"""
        provider_name = provider or self.provider

        # Generate cache key based on provider and config
        config_key = json.dumps(config, sort_keys=True) if config else "default"
        cache_key = f"{provider_name}:{config_key}"

        # Return cached client if exists
        if cache_key in self._clients:
            return self._clients[cache_key]

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

            client = create_provider(
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
            client = create_provider(provider_name, cfg)

        # Cache the new client
        self._clients[cache_key] = client
        return client

    async def complete(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate completion (using streaming for robustness)"""
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
        max_retries = 3
        base_delay = 1

        for attempt in range(max_retries):
            try:
                # Use stream_complete to accumulate response
                # This helps with debugging progress and prevents silent timeouts on large payloads
                full_response = ""
                chunk_count = 0

                async for chunk in client.stream_complete(prompt, **kwargs):
                    full_response += chunk
                    chunk_count += 1
                    if chunk_count % 50 == 0:
                        logger.debug(f"Streaming... {len(full_response)} chars received")

                duration = time.time() - start_time
                logger.info(
                    f"LLM Response | Duration: {duration:.2f}s | Length: {len(full_response)} chars"
                )
                return full_response

            except Exception as e:
                duration = time.time() - start_time
                is_last_attempt = attempt == max_retries - 1
                error_msg = f"LLM Error [Complete] (Attempt {attempt + 1}/{max_retries}) | Provider: {provider_name} | Error: {str(e)}"

                if is_last_attempt:
                    logger.error(error_msg)
                    logger.exception("Full traceback:")
                    raise
                else:
                    logger.warning(f"{error_msg} - Retrying in {base_delay * (2**attempt)}s...")
                    await asyncio.sleep(base_delay * (2**attempt))

        # Should not be reached due to raise above
        raise Exception("Max retries exceeded")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate chat completion"""
        # Similar to complete but calls client.stream_chat directly
        # For brevity, implementing similar retry logic as complete if needed,
        # but complete() covers most extraction cases here.
        # This implementation falls back to non-streaming client.chat() for simplicity unless changed.
        # But to be consistent with robustness plan:

        provider_name = provider or self.provider
        # ... (config loading same as complete) ...
        # Simplified config loading for brevity in this snippet

        from services.settings_service import get_settings_service

        settings_service = get_settings_service()
        all_settings = await settings_service.load_settings()

        config = None
        if provider_name in all_settings:
            p_settings = all_settings[provider_name]
            config = {
                "api_key": p_settings.get("apiKey", ""),
                "model": p_settings.get("model", ""),
                "base_url": p_settings.get("baseUrl", ""),
                "secret_key": p_settings.get("secretKey", ""),
            }

        if model and config:
            config["model"] = model
        elif model and not config:
            base_config = self._get_provider_config(provider_name)
            if base_config:
                config = base_config
                config["model"] = model

        client = self._create_client(provider_name, config)

        logger.info(
            f"LLM Request [Chat] | Provider: {provider_name} | Model: {config.get('model') if config else 'default'}"
        )

        start_time = time.time()
        max_retries = 3
        base_delay = 1

        for attempt in range(max_retries):
            try:
                full_response = ""
                async for chunk in client.stream_chat(messages, **kwargs):
                    full_response += chunk

                duration = time.time() - start_time
                logger.info(
                    f"LLM Response | Duration: {duration:.2f}s | Length: {len(full_response)} chars"
                )
                return full_response
            except Exception as e:
                # Retry logic same as above
                duration = time.time() - start_time
                is_last_attempt = attempt == max_retries - 1
                error_msg = f"LLM Error [Chat] (Attempt {attempt + 1}/{max_retries}) | Provider: {provider_name} | Error: {str(e)}"

                if is_last_attempt:
                    logger.error(error_msg)
                    logger.exception("Full traceback:")
                    raise
                else:
                    logger.warning(f"{error_msg} - Retrying in {base_delay * (2**attempt)}s...")
                    await asyncio.sleep(base_delay * (2**attempt))
        raise Exception("Max retries exceeded")

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

    def _extract_json_from_response(self, response: str) -> Optional[Any]:
        """Helper to extract and parse JSON from LLM response safely"""
        try:
            # Clean up potential markdown formatting
            text = response.strip()
            if text.startswith("```"):
                # Remove first line (```json or just ```)
                text = text.split("\n", 1)[1]
                # Remove last line if it is ```
                if text.strip().endswith("```"):
                    text = text.strip()[:-3]

            # Try to find array brackets if not already clean
            # This logic is good for lists, but what if it's a dict?
            # We'll just look for the first [ or {
            start_list = text.find("[")
            start_dict = text.find("{")

            start = -1
            if start_list != -1 and start_dict != -1:
                start = min(start_list, start_dict)
            elif start_list != -1:
                start = start_list
            elif start_dict != -1:
                start = start_dict

            if start >= 0:
                # Find matching end? Or just take from start
                # Simple heuristic: look for last ] or }
                end_list = text.rfind("]")
                end_dict = text.rfind("}")
                end = max(end_list, end_dict) + 1

                if end > start:
                    text = text[start:end]

            return json.loads(text)
        except (json.JSONDecodeError, IndexError, AttributeError) as e:
            # We don't log warning here because complete_with_validation handles it
            return None

    async def complete_with_validation(
        self,
        prompt: str,
        validation_model: Type[BaseModel],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 2,
    ) -> Any:
        """
        Generate completion with Pydantic validation and auto-retry mechanism.
        If JSON parsing or validation fails, it feeds the error back to the LLM.
        """
        current_prompt = prompt

        for attempt in range(max_retries + 1):
            try:
                response_text = await self.complete(current_prompt, provider=provider, model=model)

                # 1. Try to parse JSON
                parsed_data = self._extract_json_from_response(response_text)
                if parsed_data is None:
                    raise ValueError("Could not extract valid JSON from response")

                # 2. Validate with Pydantic
                # If validation_model is a List type (e.g. List[Character]), we need to handle it.
                # Pydantic doesn't validate List[Model] directly with model_validate for the list itself easily without a wrapper or TypeAdapter.
                # Since we passed a specific class (like CharacterExtraction), we expect a list of those or a single one?
                # The caller usually expects a List. Let's check usage.
                # analyze_characters returns List[Dict].
                # So validation_model passed should probably be the Item model, and we iterate?
                # Or we use TypeAdapter(List[validation_model]).

                from pydantic import TypeAdapter

                # Assume input is a list of items
                adapter = TypeAdapter(List[validation_model])
                validated_data = adapter.validate_python(parsed_data)

                # Convert back to dicts for compatibility with existing code
                return [item.model_dump() for item in validated_data]

            except (ValidationError, ValueError) as e:
                logger.warning(f"Validation failed (Attempt {attempt + 1}/{max_retries + 1}): {e}")

                if attempt == max_retries:
                    logger.error("Max retries reached for validation.")
                    return []  # Or raise error

                # Construct retry prompt with hint
                current_prompt = f"""
{prompt}

IMPORTANT: Your previous response format was incorrect.
Error: {str(e)}

Please fix the format and return ONLY the valid JSON.
"""
        return []

    async def analyze_characters(
        self, text: str, provider: Optional[str] = None, model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Use LLM to extract characters from text"""
        logger.info("Starting character extraction...")
        # Limit text to avoid token limits
        text_sample = text[:8000]

        prompt = f"""请分析以下小说文本，提取所有出现的人物角色。
对于每个人物，请提供：
1. 姓名 (name)
2. 别名/称呼 (aliases) - 列表
3. 简短描述 (description)
4. 性格特点 (personality)
5. 重要性评分 (importance) - 0.0到1.0

请以JSON数组格式返回结果。

文本内容：
{text_sample}

请返回JSON格式：
[{{
    "name": "...",
    "aliases": ["..."],
    "description": "...",
    "personality": "...",
    "importance": 0.8
}}]
"""
        return await self.complete_with_validation(
            prompt, CharacterExtraction, provider=provider, model=model
        )

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
1. source: 人物A姓名
2. target: 人物B姓名
3. type: 关系类型 (family/friend/enemy/lover/colleague/other)
4. subtype: 具体关系 (如：父子、夫妻、死敌等)
5. strength: 关系强度 (0.0-1.0)
6. description: 关系描述

文本内容：
{text_sample}

请返回JSON格式：
[{{
    "source": "人物A", 
    "target": "人物B", 
    "type": "family", 
    "subtype": "父子", 
    "strength": 0.9, 
    "description": "..."
}}]
"""
        return await self.complete_with_validation(
            prompt, RelationshipExtraction, provider=provider, model=model
        )

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
1. title: 事件名称（简短标题）
2. description: 事件描述
3. characters: 涉及人物列表
4. type: 事件类型 (conflict/revelation/turning_point/climax/resolution)
5. importance: 重要性 (0.0-1.0)

文本内容：
{text_sample}

请返回JSON格式：
[{{
    "title": "...", 
    "description": "...", 
    "characters": ["..."], 
    "type": "conflict", 
    "importance": 0.8
}}]
"""
        return await self.complete_with_validation(
            prompt, PlotEventExtraction, provider=provider, model=model
        )


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get the LLM service singleton"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
