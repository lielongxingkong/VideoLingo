from dataclasses import dataclass, field
from typing import List, Optional
from core.utils.config_utils import load_key, update_key
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
    ALLOWED_VIDEO_FORMATS,
    ALLOWED_AUDIO_FORMATS,
    LANGUAGE_SPLIT_WITH_SPACE,
    LANGUAGE_SPLIT_WITHOUT_SPACE,
)
import threading

# -----------------------
# Nested Configuration Classes
# -----------------------

@dataclass
class ApiConfig:
    key: str = DEFAULT_API_KEY
    base_url: str = DEFAULT_API_BASE_URL
    model: str = DEFAULT_API_MODEL
    llm_support_json: bool = DEFAULT_API_LLM_SUPPORT_JSON
    format: str = DEFAULT_API_FORMAT

@dataclass
class AsrConfig:
    language: str = DEFAULT_ASR_LANGUAGE
    detected_language: str = DEFAULT_ASR_DETECTED_LANGUAGE
    runtime: str = DEFAULT_ASR_RUNTIME
    elevenlabs_api_key: str = DEFAULT_ASR_ELEVENLABS_API_KEY
    openai_api_key: str = DEFAULT_ASR_OPENAI_API_KEY
    openai_base_url: str = DEFAULT_ASR_OPENAI_BASE_URL

@dataclass
class OpenAITTSConfig:
    api_key: str = DEFAULT_OPENAI_TTS_API_KEY
    base_url: str = DEFAULT_OPENAI_TTS_BASE_URL
    voice: str = DEFAULT_OPENAI_TTS_VOICE
    model: str = DEFAULT_OPENAI_TTS_MODEL

@dataclass
class EdgeTTSConfig:
    voice: str = DEFAULT_EDGE_TTS_VOICE

@dataclass
class SubtitleConfig:
    max_length: int = DEFAULT_SUBTITLE_MAX_LENGTH
    target_multiplier: float = DEFAULT_SUBTITLE_TARGET_MULTIPLIER

@dataclass
class SpeedFactorConfig:
    min: float = DEFAULT_SPEED_FACTOR_MIN
    accept: float = DEFAULT_SPEED_FACTOR_ACCEPT
    max: float = DEFAULT_SPEED_FACTOR_MAX

@dataclass
class YouTubeConfig:
    cookies_path: str = DEFAULT_YOUTUBE_COOKIES_PATH

# -----------------------
# Main Configuration Class
# -----------------------

@dataclass
class Config:
    # Basic Settings
    display_language: str = DEFAULT_DISPLAY_LANGUAGE
    api: ApiConfig = field(default_factory=ApiConfig)
    max_workers: int = DEFAULT_MAX_WORKERS
    target_language: str = DEFAULT_TARGET_LANGUAGE
    asr: AsrConfig = field(default_factory=AsrConfig)
    burn_subtitles: bool = DEFAULT_BURN_SUBTITLES

    # Advanced Settings
    ffmpeg_gpu: bool = DEFAULT_FFMPEG_GPU
    youtube: YouTubeConfig = field(default_factory=YouTubeConfig)
    ytb_resolution: str = DEFAULT_YTB_RESOLUTION
    subtitle: SubtitleConfig = field(default_factory=SubtitleConfig)
    summary_length: int = DEFAULT_SUMMARY_LENGTH
    max_split_length: int = DEFAULT_MAX_SPLIT_LENGTH
    reflect_translate: bool = DEFAULT_REFLECT_TRANSLATE
    pause_before_translate: bool = DEFAULT_PAUSE_BEFORE_TRANSLATE

    # Dubbing Settings
    tts_method: str = DEFAULT_TTS_METHOD
    openai_tts: OpenAITTSConfig = field(default_factory=OpenAITTSConfig)
    edge_tts: EdgeTTSConfig = field(default_factory=EdgeTTSConfig)
    speed_factor: SpeedFactorConfig = field(default_factory=SpeedFactorConfig)
    min_subtitle_duration: float = DEFAULT_MIN_SUBTITLE_DURATION
    min_trim_duration: float = DEFAULT_MIN_TRIM_DURATION
    tolerance: float = DEFAULT_TOLERANCE

    # Additional Settings
    model_dir: str = DEFAULT_MODEL_DIR
    allowed_video_formats: List[str] = field(default_factory=lambda: ALLOWED_VIDEO_FORMATS.copy())
    allowed_audio_formats: List[str] = field(default_factory=lambda: ALLOWED_AUDIO_FORMATS.copy())
    language_split_with_space: List[str] = field(default_factory=lambda: LANGUAGE_SPLIT_WITH_SPACE.copy())
    language_split_without_space: List[str] = field(default_factory=lambda: LANGUAGE_SPLIT_WITHOUT_SPACE.copy())

    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate()

    def _validate(self):
        """Validate required fields and constraints"""
        # Validate API settings
        if not self.api.base_url:
            raise ValueError("API base URL is required")
        if self.api.format not in ["openai", "anthropic"]:
            raise ValueError("API format must be 'openai' or 'anthropic'")

        # Validate Whisper settings
        if self.asr.runtime not in ["elevenlabs", "openai"]:
            raise ValueError("Whisper runtime must be 'elevenlabs' or 'openai'")

        # Validate TTS settings
        allowed_tts_methods = ["edge_tts", "custom_tts", "openai_tts"]
        if self.tts_method not in allowed_tts_methods:
            raise ValueError(f"TTS method must be one of {allowed_tts_methods}")

        # Validate subtitle settings
        if self.subtitle.max_length <= 0:
            raise ValueError("Subtitle max length must be positive")
        if self.subtitle.target_multiplier <= 0:
            raise ValueError("Subtitle target multiplier must be positive")

        # Validate speed factor settings
        if self.speed_factor.min <= 0 or self.speed_factor.max <= 0:
            raise ValueError("Speed factor values must be positive")
        if self.speed_factor.min > self.speed_factor.accept or self.speed_factor.accept > self.speed_factor.max:
            raise ValueError("Speed factor must satisfy min ≤ accept ≤ max")

    def save(self) -> None:
        """Save configuration (no longer used, config is stored in session_state)"""
        with threading.Lock():
            # Load existing YAML structure to preserve comments
            with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
                existing_data = yaml.load(file)

            # Update existing data with current config values
            self._update_dict(existing_data, self._to_dict())

            # Save updated configuration
            with open(CONFIG_PATH, 'w', encoding='utf-8') as file:
                yaml.dump(existing_data, file)

    def _to_dict(self) -> dict:
        """Convert dataclass to dictionary (including nested classes)"""
        import dataclasses
        data = {}
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if dataclasses.is_dataclass(value):
                data[field.name] = self._to_dict_recursive(value)
            else:
                data[field.name] = value
        return data

    def _to_dict_recursive(self, obj) -> dict:
        """Recursively convert nested dataclasses to dictionaries"""
        import dataclasses
        if dataclasses.is_dataclass(obj):
            data = {}
            for field in dataclasses.fields(obj):
                value = getattr(obj, field.name)
                if dataclasses.is_dataclass(value):
                    data[field.name] = self._to_dict_recursive(value)
                else:
                    data[field.name] = value
            return data
        elif isinstance(obj, list):
            return [self._to_dict_recursive(item) for item in obj]
        else:
            return obj

    def _update_dict(self, existing: dict, new: dict) -> None:
        """Update existing dictionary with new values (preserving structure)"""
        for key, value in new.items():
            if key in existing:
                if isinstance(value, dict) and isinstance(existing[key], dict):
                    self._update_dict(existing[key], value)
                else:
                    existing[key] = value
            else:
                existing[key] = value

# -----------------------
# Singleton Pattern
# -----------------------

_config_instance: Optional[Config] = None
_config_lock = threading.Lock()

def get_config() -> Config:
    """Get singleton configuration instance (loaded from DEFAULT_CONFIG or session_state)"""
    global _config_instance
    if _config_instance is None:
        with _config_lock:
            if _config_instance is None:
                _config_instance = Config.load()
    return _config_instance

@classmethod
def load(cls) -> "Config":
    """Load configuration from DEFAULT_CONFIG"""
    config = cls()

    # Load API settings
    config.api.key = load_key("api.key")
    config.api.base_url = load_key("api.base_url")
    config.api.model = load_key("api.model")
    config.api.llm_support_json = load_key("api.llm_support_json")
    config.api.format = load_key("api.format")

    # Load Whisper settings
    config.asr.language = load_key("asr.language")
    config.asr.detected_language = load_key("asr.detected_language")
    config.asr.runtime = load_key("asr.runtime")
    config.asr.elevenlabs_api_key = load_key("asr.elevenlabs_api_key")
    config.asr.openai_api_key = load_key("asr.openai_api_key")
    config.asr.openai_base_url = load_key("asr.openai_base_url")

    # Load OpenAI TTS settings
    config.openai_tts.api_key = load_key("openai_tts.api_key")
    config.openai_tts.base_url = load_key("openai_tts.base_url")
    config.openai_tts.voice = load_key("openai_tts.voice")
    config.openai_tts.model = load_key("openai_tts.model")

    # Load Edge TTS settings
    config.edge_tts.voice = load_key("edge_tts.voice")

    # Load YouTube settings
    config.youtube.cookies_path = load_key("youtube.cookies_path")

    # Load subtitle settings
    config.subtitle.max_length = load_key("subtitle.max_length")
    config.subtitle.target_multiplier = load_key("subtitle.target_multiplier")

    # Load speed factor settings
    config.speed_factor.min = load_key("speed_factor.min")
    config.speed_factor.accept = load_key("speed_factor.accept")
    config.speed_factor.max = load_key("speed_factor.max")

    # Load remaining settings
    config.display_language = load_key("display_language")
    config.max_workers = load_key("max_workers")
    config.target_language = load_key("target_language")
    config.burn_subtitles = load_key("burn_subtitles")
    config.ffmpeg_gpu = load_key("ffmpeg_gpu")
    config.ytb_resolution = load_key("ytb_resolution")
    config.summary_length = load_key("summary_length")
    config.max_split_length = load_key("max_split_length")
    config.reflect_translate = load_key("reflect_translate")
    config.pause_before_translate = load_key("pause_before_translate")
    config.tts_method = load_key("tts_method")
    config.min_subtitle_duration = load_key("min_subtitle_duration")
    config.min_trim_duration = load_key("min_trim_duration")
    config.tolerance = load_key("tolerance")
    config.model_dir = load_key("model_dir")
    config.allowed_video_formats = load_key("allowed_video_formats")
    config.allowed_audio_formats = load_key("allowed_audio_formats")
    config.language_split_with_space = load_key("language_split_with_space")
    config.language_split_without_space = load_key("language_split_without_space")

    return config

# Attach load class method
Config.load = load

# -----------------------
# Utility Functions
# -----------------------

def get_joiner(language: str) -> str:
    """Get word joiner based on language (space or empty string)"""
    config = get_config()
    if language in config.language_split_with_space:
        return " "
    elif language in config.language_split_without_space:
        return ""
    else:
        raise ValueError(f"Unsupported language code: {language}")

if __name__ == "__main__":
    # Test loading and usage
    try:
        config = get_config()
        print("Configuration loaded successfully!")
        print(f"API Key: {config.api.key}")
        print(f"ASR Language: {config.asr.language}")
        print(f"TTS Method: {config.tts_method}")
        print(f"Subtitle Max Length: {config.subtitle.max_length}")
        print(f"Language Split with Space: {config.language_split_with_space}")
    except Exception as e:
        print(f"Error loading configuration: {e}")
