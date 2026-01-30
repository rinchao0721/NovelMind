"""
JSON processing utilities
"""

import json
from typing import Any, Optional
from utils.logger import logger


def safe_json_loads(data: Any, default: Any = None) -> Any:
    """
    Safely load JSON data with error handling

    Args:
        data: String or bytes to parse
        default: Default value to return on failure

    Returns:
        Parsed object or default value
    """
    if data is None:
        return default

    if not isinstance(data, (str, bytes)):
        return data

    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {str(e)[:100]}...")
        return default
