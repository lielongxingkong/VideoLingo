"""
TTS Backend Factory

Factory for creating TTS backend instances based on configuration.
"""

from typing import Optional
from core.utils.config import load_key


def get_tts_backend(method: Optional[str] = None):
    """
    Get a TTS backend function based on the configured method.

    Args:
        method: Optional method override (defaults to config)

    Returns:
        TTS backend function (maintaining backward compatibility)
    """
    if method is None:
        method = load_key("tts_method")

    if method == "edge_tts":
        from core.tts_backend.edge_tts import edge_tts
        return edge_tts
    elif method == "openai_tts":
        from core.tts_backend.openai_tts import openai_tts_for_videolingo
        return openai_tts_for_videolingo
    else:
        raise ValueError(f"Unknown TTS method: {method}")


__all__ = ["get_tts_backend"]
