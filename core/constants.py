# -*- coding: utf-8 -*-
"""
Centralized constants for VideoLingo
All default values are defined here for easy configuration
"""

# ==================== API Settings ====================
DEFAULT_API_KEY = ""
DEFAULT_API_BASE_URL = "https://www.dmxapi.cn"
DEFAULT_API_MODEL = "gpt-4.1-2025-04-14"
DEFAULT_API_FORMAT = "openai"  # "openai" or "anthropic"
DEFAULT_API_LLM_SUPPORT_JSON = False

# ==================== ASR Settings ====================
DEFAULT_ASR_LANGUAGE = "en"
DEFAULT_ASR_DETECTED_LANGUAGE = "en"
DEFAULT_ASR_RUNTIME = "openai"  # "openai" or "elevenlabs"
DEFAULT_ASR_ELEVENLABS_API_KEY = ""
DEFAULT_ASR_OPENAI_API_KEY = ""
DEFAULT_ASR_OPENAI_BASE_URL = "https://www.dmxapi.cn"

# ==================== Demucs Settings ====================
DEFAULT_DEMUCS_ENABLED = False
DEFAULT_DEMUCS_MODEL = "htdemucs"

# ==================== Subtitle Settings ====================
DEFAULT_TARGET_LANGUAGE = "简体中文"
DEFAULT_BURN_SUBTITLES = True
DEFAULT_SUBTITLE_MAX_LENGTH = 75
DEFAULT_SUBTITLE_TARGET_MULTIPLIER = 1.2

# ==================== LLM Processing ====================
DEFAULT_MAX_WORKERS = 4
DEFAULT_SUMMARY_LENGTH = 8000
DEFAULT_REFLECT_TRANSLATE = True
DEFAULT_PAUSE_BEFORE_TRANSLATE = False
DEFAULT_MAX_SPLIT_LENGTH = 20

# ==================== Video Settings ====================
DEFAULT_FFMPEG_GPU = False
DEFAULT_YTB_RESOLUTION = "1080"
DEFAULT_YOUTUBE_COOKIES_PATH = ""

# ==================== TTS Settings ====================
DEFAULT_TTS_METHOD = "openai_tts"  # "openai_tts" or "edge_tts"

# OpenAI TTS
DEFAULT_OPENAI_TTS_API_KEY = ""
DEFAULT_OPENAI_TTS_BASE_URL = "https://www.dmxapi.cn"
DEFAULT_OPENAI_TTS_VOICE = "alloy"  # alloy, echo, fable, onyx, nova, shimmer
DEFAULT_OPENAI_TTS_MODEL = "tts-1"  # tts-1, tts-1-hd

# Edge TTS
DEFAULT_EDGE_TTS_VOICE = "zh-CN-XiaoxiaoNeural"

# ==================== Audio/Dubbing Settings ====================
DEFAULT_SPEED_FACTOR_MIN = 1.0
DEFAULT_SPEED_FACTOR_ACCEPT = 1.2
DEFAULT_SPEED_FACTOR_MAX = 1.4
DEFAULT_MIN_SUBTITLE_DURATION = 2.5
DEFAULT_MIN_TRIM_DURATION = 3.5
DEFAULT_TOLERANCE = 1.5

# ==================== Display Settings ====================
DEFAULT_DISPLAY_LANGUAGE = "zh-CN"

# ==================== Additional Settings ====================
DEFAULT_MODEL_DIR = "./_model_cache"
DEFAULT_CONFIG_FILE_PATH = "./videolingo_config.json"

ALLOWED_VIDEO_FORMATS = ["mp4", "mov", "avi", "mkv", "flv", "wmv", "webm"]
ALLOWED_AUDIO_FORMATS = ["wav", "mp3", "flac", "m4a"]
LANGUAGE_SPLIT_WITH_SPACE = ["en", "es", "fr", "de", "it", "ru"]
LANGUAGE_SPLIT_WITHOUT_SPACE = ["zh", "ja"]

# ==================== UI Options (for dropdowns) ====================
# API Format options
API_FORMAT_OPTIONS = ["openai", "anthropic"]

# ASR Runtime options
ASR_RUNTIME_OPTIONS = ["elevenlabs", "openai"]

# TTS Method options
TTS_METHOD_OPTIONS = ["edge_tts", "openai_tts"]

# OpenAI TTS Voice options
OPENAI_TTS_VOICE_OPTIONS = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

# OpenAI TTS Model options
OPENAI_TTS_MODEL_OPTIONS = ["tts-1", "tts-1-hd"]

# Language options for ASR
ASR_LANGUAGE_OPTIONS = {
    "🇺🇸 English": "en",
    "🇨🇳 简体中文": "zh",
    "🇪🇸 Español": "es",
    "🇷🇺 Русский": "ru",
    "🇫🇷 Français": "fr",
    "🇩🇪 Deutsch": "de",
    "🇮🇹 Italiano": "it",
    "🇯🇵 日本語": "ja"
}
