import streamlit as st
import json
import os
import threading

lock = threading.Lock()

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
# load & update config
# -----------------------

def _get_nested_value(data, keys):
    """Helper to get nested value from dict"""
    value = data
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return None
    return value

def _set_nested_value(data, keys, new_value):
    """Helper to set nested value in dict"""
    current = data
    for k in keys[:-1]:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return False
    if isinstance(current, dict) and keys[-1] in current:
        current[keys[-1]] = new_value
        return True
    return False

# Cache for config file to avoid repeated file I/O
_config_file_cache = None

def _load_config_from_file():
    """Load config from file (cached)"""
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
    """Load config value from session_state, config file, or DEFAULT_CONFIG"""
    # First try to get from session_state (Streamlit context)
    if hasattr(st, 'session_state') and st.session_state:
        config = st.session_state.get("config", {})
        if config is not None:
            # Use key directly (flat key structure, not nested)
            if key in config and config[key]:
                return config[key]

    # Try to load from config file (for worker threads)
    file_config = _load_config_from_file()
    if file_config and key in file_config and file_config[key]:
        return file_config[key]

    # Fallback to DEFAULT_CONFIG
    return DEFAULT_CONFIG.get(key)

def update_key(key, value):
    """Update config value in session_state"""
    if hasattr(st, 'session_state') and st.session_state:
        if "config" not in st.session_state:
            st.session_state.config = DEFAULT_CONFIG.copy()

        # Use key directly (flat key structure, not nested)
        st.session_state.config[key] = value
        return True
    return False

# basic utils
def get_joiner(language):
    if language in load_key('language_split_with_space'):
        return " "
    elif language in load_key('language_split_without_space'):
        return ""
    else:
        raise ValueError(f"Unsupported language code: {language}")

# Save/Load config to/from file
def save_config_to_file():
    """Save current config to file"""
    config_path = load_key("config_file_path")
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.config, f, indent=2, ensure_ascii=False)
        return True, config_path
    except Exception as e:
        return False, str(e)

def load_config_from_file():
    """Load config from file"""
    config_path = load_key("config_file_path")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            imported_config = json.load(f)
        # Merge with DEFAULT_CONFIG to ensure all keys exist
        merged_config = DEFAULT_CONFIG.copy()
        merged_config.update(imported_config)
        st.session_state.config = merged_config
        return True, config_path
    except FileNotFoundError:
        return False, f"File not found: {config_path}"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    print(load_key('language_split_with_space'))
