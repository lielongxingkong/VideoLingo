"""
ASR Backend Factory

Factory for creating ASR backend instances based on configuration.
"""

from typing import Optional
from core.utils.config import load_key


def get_asr_backend(runtime: Optional[str] = None):
    """
    Get an ASR backend instance based on the configured runtime.

    Args:
        runtime: Optional runtime override (defaults to config)

    Returns:
        ASR backend function (maintaining backward compatibility)
    """
    if runtime is None:
        runtime = load_key("asr.runtime")

    if runtime == "openai":
        from core.asr_backend.openai_asr import transcribe_audio_openai
        return transcribe_audio_openai
    elif runtime == "elevenlabs":
        from core.asr_backend.elevenlabs_asr import transcribe_audio_elevenlabs
        return transcribe_audio_elevenlabs
    else:
        raise ValueError(f"Unknown ASR runtime: {runtime}")


__all__ = ["get_asr_backend"]
