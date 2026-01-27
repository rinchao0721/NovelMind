"""
Secure settings service for API key management
"""

import json
import base64
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config import settings


class SecureSettingsService:
    """Service for securely storing and retrieving settings including API keys"""

    def __init__(self):
        self.settings_file = settings.DATA_DIR / "settings.json"
        self.secure_file = settings.DATA_DIR / "secure.enc"
        self._cipher: Optional[Fernet] = None
        self._init_cipher()

    def _init_cipher(self):
        """Initialize the encryption cipher"""
        try:
            from cryptography.fernet import Fernet

            # Use machine-specific key derivation
            key_material = (settings.APP_SECRET_KEY + "novelmind").encode()
            salt = b"novelmind_salt_v1"

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(key_material))
            self._cipher = Fernet(key)
        except ImportError:
            # Fallback to base64 encoding if cryptography not available
            self._cipher = None

    def _encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        if self._cipher:
            return self._cipher.encrypt(data.encode()).decode()
        else:
            # Fallback to base64 (less secure)
            return base64.b64encode(data.encode()).decode()

    def _decrypt(self, data: str) -> str:
        """Decrypt sensitive data"""
        if self._cipher:
            return self._cipher.decrypt(data.encode()).decode()
        else:
            return base64.b64decode(data.encode()).decode()

    async def save_settings(self, data: Dict[str, Any]) -> None:
        """Save settings, encrypting sensitive data"""
        # Separate sensitive and non-sensitive data
        secure_data = {}
        public_data = {}

        sensitive_keys = [
            "openai",
            "claude",
            "gemini",
            "deepseek",
            "qwen",
            "zhipu",
            "baidu",
            "custom",
            "neo4j",
            "aihubmix",
            "siliconflow",
            "openrouter",
            "ollama",
        ]

        for key, value in data.items():
            if key in sensitive_keys and isinstance(value, dict):
                # Extract and encrypt API keys
                secure_data[key] = {}
                public_data[key] = {}

                for k, v in value.items():
                    if "key" in k.lower() or "password" in k.lower() or "secret" in k.lower():
                        if v:  # Only store non-empty values
                            secure_data[key][k] = self._encrypt(str(v))
                    else:
                        public_data[key][k] = v
            else:
                public_data[key] = value

        # Ensure directory exists
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Save public settings
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(public_data, f, indent=2, ensure_ascii=False)

        # Save encrypted settings
        if secure_data:
            with open(self.secure_file, "w", encoding="utf-8") as f:
                json.dump(secure_data, f, indent=2)

    async def load_settings(self) -> Dict[str, Any]:
        """Load settings, decrypting sensitive data"""
        result = {}

        # Load public settings
        if self.settings_file.exists():
            with open(self.settings_file, "r", encoding="utf-8") as f:
                result = json.load(f)

        # Load and decrypt secure settings
        if self.secure_file.exists():
            try:
                with open(self.secure_file, "r", encoding="utf-8") as f:
                    secure_data = json.load(f)

                for key, value in secure_data.items():
                    if key not in result:
                        result[key] = {}

                    if isinstance(value, dict):
                        for k, v in value.items():
                            try:
                                result[key][k] = self._decrypt(v)
                            except Exception:
                                result[key][k] = ""
            except Exception as e:
                print(f"Error loading secure settings: {e}")

        return result

    async def get_api_key(self, provider: str, key_name: str = "apiKey") -> Optional[str]:
        """Get a specific API key"""
        settings_data = await self.load_settings()
        provider_config = settings_data.get(provider, {})
        return provider_config.get(key_name) or provider_config.get("api_key")

    async def test_provider(self, provider: str, config: Dict[str, Any]) -> bool:
        """Test a provider connection"""
        from llm.providers import create_provider

        try:
            llm_provider = create_provider(provider, config)
            return await llm_provider.test_connection()
        except Exception as e:
            print(f"Provider test failed: {e}")
            return False


# Singleton instance
_settings_service: Optional[SecureSettingsService] = None


def get_settings_service() -> SecureSettingsService:
    """Get the settings service singleton"""
    global _settings_service
    if _settings_service is None:
        _settings_service = SecureSettingsService()
    return _settings_service
