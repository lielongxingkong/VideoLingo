import streamlit as st
import json
import threading

lock = threading.Lock()

# -----------------------
# Default Configuration
# -----------------------

DEFAULT_CONFIG = {
    # Display
    "display_language": "zh-CN",

    # API
    "api.key": "",
    "api.base_url": "https://www.dmxapi.cn",
    "api.model": "gpt-4.1-2025-04-14",
    "api.format": "openai",
    "api.llm_support_json": False,

    # LLM Processing
    "max_workers": 4,
    "summary_length": 8000,
    "reflect_translate": True,
    "pause_before_translate": False,

    # ASR (cloud services only)
    "asr.language": "en",
    "asr.detected_language": "en",
    "asr.runtime": "openai",
    "asr.elevenlabs_api_key": "",
    "asr.openai_api_key": "",
    "asr.openai_base_url": "https://www.dmxapi.cn",

    # Subtitle
    "target_language": "简体中文",
    "burn_subtitles": True,
    "subtitle.max_length": 75,
    "subtitle.target_multiplier": 1.2,
    "max_split_length": 20,

    # Video
    "ffmpeg_gpu": False,
    "youtube.cookies_path": "",
    "ytb_resolution": "1080",

    # TTS
    "tts_method": "openai_tts",
    "openai_tts.api_key": "",
    "openai_tts.base_url": "https://www.dmxapi.cn",
    "openai_tts.voice": "alloy",
    "openai_tts.model": "tts-1",
    "edge_tts.voice": "zh-CN-XiaoxiaoNeural",

    # Audio
    "speed_factor.min": 1.0,
    "speed_factor.accept": 1.2,
    "speed_factor.max": 1.4,
    "min_subtitle_duration": 2.5,
    "min_trim_duration": 3.5,
    "tolerance": 1.5,

    # Additional
    "model_dir": "./_model_cache",
    "config_file_path": "./videolingo_config.json",
    "allowed_video_formats": ["mp4", "mov", "avi", "mkv", "flv", "wmv", "webm"],
    "allowed_audio_formats": ["wav", "mp3", "flac", "m4a"],
    "language_split_with_space": ["en", "es", "fr", "de", "it", "ru"],
    "language_split_without_space": ["zh", "ja"],
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

def load_key(key):
    """Load config value from session_state or DEFAULT_CONFIG"""
    # First try to get from session_state (Streamlit context)
    if hasattr(st, 'session_state') and st.session_state:
        config = st.session_state.get("config", {})
        if config is not None:
            # Use key directly (flat key structure, not nested)
            if key in config:
                return config[key]

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
