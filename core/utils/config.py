import json
import os
import threading

lock = threading.Lock()

# Runtime config for worker threads (set before pipeline starts)
RUNTIME_CONFIG = {}

# -----------------------
# Import constants
# -----------------------
from core.constants import (
    DEFAULT_DISPLAY_LANGUAGE,
    DEFAULT_API_KEY,
    DEFAULT_API_BASE_URL,
    DEFAULT_API_MODEL,
    DEFAULT_API_FORMAT,
    DEFAULT_API_LLM_SUPPORT_JSON,
    DEFAULT_MAX_WORKERS,
    DEFAULT_SUMMARY_LENGTH,
    DEFAULT_REFLECT_TRANSLATE,
    DEFAULT_PAUSE_BEFORE_TRANSLATE,
    DEFAULT_ASR_LANGUAGE,
    DEFAULT_ASR_DETECTED_LANGUAGE,
    DEFAULT_ASR_RUNTIME,
    DEFAULT_ASR_ELEVENLABS_API_KEY,
    DEFAULT_ASR_OPENAI_API_KEY,
    DEFAULT_ASR_OPENAI_BASE_URL,
    DEFAULT_DEMUCS_ENABLED,
    DEFAULT_DEMUCS_MODEL,
    DEFAULT_TARGET_LANGUAGE,
    DEFAULT_BURN_SUBTITLES,
    DEFAULT_SUBTITLE_MAX_LENGTH,
    DEFAULT_SUBTITLE_TARGET_MULTIPLIER,
    DEFAULT_MAX_SPLIT_LENGTH,
    DEFAULT_FFMPEG_GPU,
    DEFAULT_YOUTUBE_COOKIES_PATH,
    DEFAULT_YTB_RESOLUTION,
    DEFAULT_TTS_METHOD,
    DEFAULT_OPENAI_TTS_API_KEY,
    DEFAULT_OPENAI_TTS_BASE_URL,
    DEFAULT_OPENAI_TTS_VOICE,
    DEFAULT_OPENAI_TTS_MODEL,
    DEFAULT_EDGE_TTS_VOICE,
    DEFAULT_SPEED_FACTOR_MIN,
    DEFAULT_SPEED_FACTOR_ACCEPT,
    DEFAULT_SPEED_FACTOR_MAX,
    DEFAULT_MIN_SUBTITLE_DURATION,
    DEFAULT_MIN_TRIM_DURATION,
    DEFAULT_TOLERANCE,
    DEFAULT_MODEL_DIR,
    DEFAULT_CONFIG_FILE_PATH,
    ALLOWED_VIDEO_FORMATS,
    ALLOWED_AUDIO_FORMATS,
    LANGUAGE_SPLIT_WITH_SPACE,
    LANGUAGE_SPLIT_WITHOUT_SPACE,
)

# -----------------------
# Default Configuration
# -----------------------

DEFAULT_CONFIG = {
    # Display
    "display_language": DEFAULT_DISPLAY_LANGUAGE,

    # API
    "api.key": DEFAULT_API_KEY,
    "api.base_url": DEFAULT_API_BASE_URL,
    "api.model": DEFAULT_API_MODEL,
    "api.format": DEFAULT_API_FORMAT,
    "api.llm_support_json": DEFAULT_API_LLM_SUPPORT_JSON,

    # LLM Processing
    "max_workers": DEFAULT_MAX_WORKERS,
    "summary_length": DEFAULT_SUMMARY_LENGTH,
    "reflect_translate": DEFAULT_REFLECT_TRANSLATE,
    "pause_before_translate": DEFAULT_PAUSE_BEFORE_TRANSLATE,

    # ASR (cloud services only)
    "asr.language": DEFAULT_ASR_LANGUAGE,
    "asr.detected_language": DEFAULT_ASR_DETECTED_LANGUAGE,
    "asr.runtime": DEFAULT_ASR_RUNTIME,
    "asr.elevenlabs_api_key": DEFAULT_ASR_ELEVENLABS_API_KEY,
    "asr.openai_api_key": DEFAULT_ASR_OPENAI_API_KEY,
    "asr.openai_base_url": DEFAULT_ASR_OPENAI_BASE_URL,

    # Demucs
    "demucs.enabled": DEFAULT_DEMUCS_ENABLED,
    "demucs.model": DEFAULT_DEMUCS_MODEL,

    # Subtitle
    "target_language": DEFAULT_TARGET_LANGUAGE,
    "burn_subtitles": DEFAULT_BURN_SUBTITLES,
    "subtitle.max_length": DEFAULT_SUBTITLE_MAX_LENGTH,
    "subtitle.target_multiplier": DEFAULT_SUBTITLE_TARGET_MULTIPLIER,
    "max_split_length": DEFAULT_MAX_SPLIT_LENGTH,

    # Video
    "ffmpeg_gpu": DEFAULT_FFMPEG_GPU,
    "youtube.cookies_path": DEFAULT_YOUTUBE_COOKIES_PATH,
    "ytb_resolution": DEFAULT_YTB_RESOLUTION,

    # TTS
    "tts_method": DEFAULT_TTS_METHOD,
    "openai_tts.api_key": DEFAULT_OPENAI_TTS_API_KEY,
    "openai_tts.base_url": DEFAULT_OPENAI_TTS_BASE_URL,
    "openai_tts.voice": DEFAULT_OPENAI_TTS_VOICE,
    "openai_tts.model": DEFAULT_OPENAI_TTS_MODEL,
    "edge_tts.voice": DEFAULT_EDGE_TTS_VOICE,

    # Audio
    "speed_factor.min": DEFAULT_SPEED_FACTOR_MIN,
    "speed_factor.accept": DEFAULT_SPEED_FACTOR_ACCEPT,
    "speed_factor.max": DEFAULT_SPEED_FACTOR_MAX,
    "min_subtitle_duration": DEFAULT_MIN_SUBTITLE_DURATION,
    "min_trim_duration": DEFAULT_MIN_TRIM_DURATION,
    "tolerance": DEFAULT_TOLERANCE,

    # Additional
    "model_dir": DEFAULT_MODEL_DIR,
    "config_file_path": DEFAULT_CONFIG_FILE_PATH,
    "allowed_video_formats": ALLOWED_VIDEO_FORMATS,
    "allowed_audio_formats": ALLOWED_AUDIO_FORMATS,
    "language_split_with_space": LANGUAGE_SPLIT_WITH_SPACE,
    "language_split_without_space": LANGUAGE_SPLIT_WITHOUT_SPACE,
}

# -----------------------
# Pure config functions (no Streamlit)
# -----------------------

# Cache for config file to avoid repeated file I/O
_config_file_cache = None


def _load_config_from_file_pure():
    """Load config from file (cached, no Streamlit)"""
    global _config_file_cache
    if _config_file_cache is None:
        config_path = DEFAULT_CONFIG.get("config_file_path", "./videolingo_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    _config_file_cache = json.load(f)
            except Exception:
                _config_file_cache = None
    return _config_file_cache


def load_key(key):
    """Load config value from RUNTIME_CONFIG, config file, or DEFAULT_CONFIG (no Streamlit)"""
    # First try RUNTIME_CONFIG (for worker threads or explicit overrides)
    if key in RUNTIME_CONFIG and RUNTIME_CONFIG[key] is not None:
        return RUNTIME_CONFIG[key]

    # Then try config file
    file_config = _load_config_from_file_pure()
    if file_config and key in file_config and file_config[key] is not None:
        return file_config[key]

    # Fallback to DEFAULT_CONFIG
    return DEFAULT_CONFIG.get(key)


def set_runtime_key(key, value):
    """Set a value in RUNTIME_CONFIG (for worker threads or temporary overrides)"""
    with lock:
        RUNTIME_CONFIG[key] = value


def clear_runtime_config():
    """Clear all runtime config values"""
    with lock:
        RUNTIME_CONFIG.clear()


# basic utils
def get_joiner(language):
    if language in load_key('language_split_with_space'):
        return " "
    elif language in load_key('language_split_without_space'):
        return ""
    else:
        raise ValueError(f"Unsupported language code: {language}")

