from dataclasses import dataclass, field
from typing import List, Optional
from core.utils.config_utils import load_key, update_key, CONFIG_PATH
from ruamel.yaml import YAML
import threading

yaml = YAML()
yaml.preserve_quotes = True

# -----------------------
# Nested Configuration Classes
# -----------------------

@dataclass
class ApiConfig:
    key: str = ""
    base_url: str = "https://yunwu.ai"
    model: str = "gpt-4.1-2025-04-14"
    llm_support_json: bool = False
    format: str = "openai"

@dataclass
class WhisperConfig:
    model: str = "large-v3"
    language: str = "en"
    detected_language: str = "en"
    runtime: str = "elevenlabs"
    elevenlabs_api_key: str = ""
    openai_api_key: str = ""
    openai_base_url: str = ""

@dataclass
class OpenAITTSConfig:
    api_key: str = ""
    base_url: str = ""
    voice: str = "alloy"
    model: str = "tts-1"

@dataclass
class EdgeTTSConfig:
    voice: str = "zh-CN-XiaoxiaoNeural"

@dataclass
class SubtitleConfig:
    max_length: int = 75
    target_multiplier: float = 1.2

@dataclass
class SpeedFactorConfig:
    min: float = 1.0
    accept: float = 1.2
    max: float = 1.4

@dataclass
class YouTubeConfig:
    cookies_path: str = ""

# -----------------------
# Main Configuration Class
# -----------------------

@dataclass
class Config:
    # Basic Settings
    display_language: str = "zh-CN"
    api: ApiConfig = field(default_factory=ApiConfig)
    max_workers: int = 4
    target_language: str = "简体中文"
    demucs: bool = False
    whisper: WhisperConfig = field(default_factory=WhisperConfig)
    burn_subtitles: bool = True

    # Advanced Settings
    ffmpeg_gpu: bool = False
    youtube: YouTubeConfig = field(default_factory=YouTubeConfig)
    ytb_resolution: str = "1080"
    subtitle: SubtitleConfig = field(default_factory=SubtitleConfig)
    summary_length: int = 8000
    max_split_length: int = 20
    reflect_translate: bool = True
    pause_before_translate: bool = False

    # Dubbing Settings
    tts_method: str = "openai_tts"
    openai_tts: OpenAITTSConfig = field(default_factory=OpenAITTSConfig)
    edge_tts: EdgeTTSConfig = field(default_factory=EdgeTTSConfig)
    speed_factor: SpeedFactorConfig = field(default_factory=SpeedFactorConfig)
    min_subtitle_duration: float = 2.5
    min_trim_duration: float = 3.5
    tolerance: float = 1.5

    # Additional Settings
    model_dir: str = "./_model_cache"
    allowed_video_formats: List[str] = field(default_factory=lambda: [
        "mp4", "mov", "avi", "mkv", "flv", "wmv", "webm"
    ])
    allowed_audio_formats: List[str] = field(default_factory=lambda: [
        "wav", "mp3", "flac", "m4a"
    ])
    language_split_with_space: List[str] = field(default_factory=lambda: [
        "en", "es", "fr", "de", "it", "ru"
    ])
    language_split_without_space: List[str] = field(default_factory=lambda: [
        "zh", "ja"
    ])

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
        if self.whisper.model not in ["large-v3", "large-v3-turbo"]:
            raise ValueError("Whisper model must be 'large-v3' or 'large-v3-turbo'")
        if self.whisper.runtime not in ["elevenlabs", "openai"]:
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
        """Save configuration to config.yaml"""
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
    """Get singleton configuration instance (loaded from config.yaml)"""
    global _config_instance
    if _config_instance is None:
        with _config_lock:
            if _config_instance is None:
                _config_instance = Config.load()
    return _config_instance

@classmethod
def load(cls) -> "Config":
    """Load configuration from config.yaml"""
    config = cls()

    # Load API settings
    config.api.key = load_key("api.key")
    config.api.base_url = load_key("api.base_url")
    config.api.model = load_key("api.model")
    config.api.llm_support_json = load_key("api.llm_support_json")
    config.api.format = load_key("api.format")

    # Load Whisper settings
    config.whisper.model = load_key("whisper.model")
    config.whisper.language = load_key("whisper.language")
    config.whisper.detected_language = load_key("whisper.detected_language")
    config.whisper.runtime = load_key("whisper.runtime")
    config.whisper.elevenlabs_api_key = load_key("whisper.elevenlabs_api_key")
    config.whisper.openai_api_key = load_key("whisper.openai_api_key")
    config.whisper.openai_base_url = load_key("whisper.openai_base_url")

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
    config.demucs = load_key("demucs")
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
        print(f"Whisper Model: {config.whisper.model}")
        print(f"TTS Method: {config.tts_method}")
        print(f"Subtitle Max Length: {config.subtitle.max_length}")
        print(f"Language Split with Space: {config.language_split_with_space}")
    except Exception as e:
        print(f"Error loading configuration: {e}")
