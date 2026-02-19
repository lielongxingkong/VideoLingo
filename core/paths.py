"""
VideoLingo Paths Module - Centralized file path management

This module provides a structured, type-safe way to manage all file paths used in VideoLingo.
All paths are created using pathlib.Path for better type safety and automatic directory creation.
"""

from pathlib import Path
from typing import Optional


class Paths:
    """
    Centralized file path management for VideoLingo.

    This class provides static properties for all file paths used in the application,
    organized into logical categories for clarity. Directories are automatically
    created when accessed for the first time.
    """

    # ==========================================
    # Root Directories
    # ==========================================

    @staticmethod
    def output_dir() -> Path:
        """Root output directory"""
        path = Path("output")
        path.mkdir(exist_ok=True)
        return path

    @staticmethod
    def log_dir() -> Path:
        """Directory for log files and intermediate results"""
        path = Paths.output_dir() / "log"
        path.mkdir(exist_ok=True)
        return path

    @staticmethod
    def audio_dir() -> Path:
        """Directory for audio files"""
        path = Paths.output_dir() / "audio"
        path.mkdir(exist_ok=True)
        return path

    @staticmethod
    def gpt_log_dir() -> Path:
        """Directory for GPT response logs"""
        path = Paths.output_dir() / "gpt_log"
        path.mkdir(exist_ok=True)
        return path

    # ==========================================
    # Intermediate Output Files (Excel/JSON/TXT)
    # ==========================================

    @staticmethod
    def cleaned_chunks() -> Path:
        """Excel file with cleaned subtitle chunks from ASR"""
        return Paths.log_dir() / "cleaned_chunks.xlsx"

    @staticmethod
    def split_by_nlp() -> Path:
        """Text file with NLP-based sentence segmentation results"""
        return Paths.log_dir() / "split_by_nlp.txt"

    @staticmethod
    def split_by_meaning() -> Path:
        """Text file with meaning-based sentence segmentation results"""
        return Paths.log_dir() / "split_by_meaning.txt"

    @staticmethod
    def terminology() -> Path:
        """JSON file with custom and AI-generated terminology"""
        return Paths.log_dir() / "terminology.json"

    @staticmethod
    def translation_results() -> Path:
        """Excel file with translation results"""
        return Paths.log_dir() / "translation_results.xlsx"

    @staticmethod
    def translation_results_for_subtitles() -> Path:
        """Excel file with translation results optimized for subtitles"""
        return Paths.log_dir() / "translation_results_for_subtitles.xlsx"

    @staticmethod
    def translation_results_remerged() -> Path:
        """Excel file with remerged translation results"""
        return Paths.log_dir() / "translation_results_remerged.xlsx"

    @staticmethod
    def tts_tasks() -> Path:
        """Excel file with TTS dubbing tasks"""
        return Paths.audio_dir() / "tts_tasks.xlsx"

    # ==========================================
    # Audio Files
    # ==========================================

    @staticmethod
    def raw_audio() -> Path:
        """Raw audio extracted from video"""
        return Paths.audio_dir() / "raw.mp3"

    @staticmethod
    def vocal_audio() -> Path:
        """Vocal audio separated from background (Demucs)"""
        return Paths.audio_dir() / "vocal.mp3"

    @staticmethod
    def background_audio() -> Path:
        """Background audio separated from vocals (Demucs)"""
        return Paths.audio_dir() / "background.mp3"

    @staticmethod
    def dub_vocal() -> Path:
        """Final merged dub vocal file"""
        return Paths.output_dir() / "dub.mp3"

    @staticmethod
    def dub_subtitle() -> Path:
        """Final dub subtitle file (SRT)"""
        return Paths.output_dir() / "dub.srt"

    # ==========================================
    # Audio Subdirectories
    # ==========================================

    @staticmethod
    def audio_refers_dir() -> Path:
        """Directory for reference audio segments"""
        path = Paths.audio_dir() / "refers"
        path.mkdir(exist_ok=True)
        return path

    @staticmethod
    def audio_segs_dir() -> Path:
        """Directory for segmented audio chunks"""
        path = Paths.audio_dir() / "segs"
        path.mkdir(exist_ok=True)
        return path

    @staticmethod
    def audio_tmp_dir() -> Path:
        """Directory for temporary audio files"""
        path = Paths.audio_dir() / "tmp"
        path.mkdir(exist_ok=True)
        return path

    # ==========================================
    # Model and Cache Paths
    # ==========================================

    @staticmethod
    def model_cache_dir() -> Path:
        """Directory for downloaded models (WhisperX, Demucs, etc.)"""
        path = Path("models")
        path.mkdir(exist_ok=True)
        return path

    @staticmethod
    def whisperx_cache_dir() -> Path:
        """Cache directory for WhisperX models"""
        path = Paths.model_cache_dir() / "whisperx"
        path.mkdir(exist_ok=True)
        return path

    @staticmethod
    def demucs_cache_dir() -> Path:
        """Cache directory for Demucs models"""
        path = Paths.model_cache_dir() / "demucs"
        path.mkdir(exist_ok=True)
        return path

    # ==========================================
    # Helper Methods
    # ==========================================

    @staticmethod
    def create_audio_seg_file(number: int, line_index: int) -> Path:
        """
        Create a path for an audio segment file

        Args:
            number: The chunk number
            line_index: The line index within the chunk

        Returns:
            Path to the audio segment file
        """
        return Paths.audio_segs_dir() / f"{number}_{line_index}.wav"

    @staticmethod
    def create_gpt_log_file(log_title: str = "default") -> Path:
        """
        Create a path for a GPT log file

        Args:
            log_title: The title of the log file

        Returns:
            Path to the GPT log file
        """
        return Paths.gpt_log_dir() / f"{log_title}.json"

    @staticmethod
    def find_video_file() -> Optional[Path]:
        """
        Find the downloaded video file in the output directory

        Returns:
            Path to the video file if found, None otherwise
        """
        from core._1_ytdlp import find_video_files
        try:
            video_path = find_video_files(str(Paths.output_dir()))
            return Path(video_path)
        except Exception:
            return None


# ==========================================
# Backward Compatibility - Map old variable names to new Paths class
# ==========================================

# This section provides backward compatibility with existing code that uses
# the old variable names from core.utils.models

# Intermediate output files
_2_CLEANED_CHUNKS = str(Paths.cleaned_chunks())
_3_1_SPLIT_BY_NLP = str(Paths.split_by_nlp())
_3_2_SPLIT_BY_MEANING = str(Paths.split_by_meaning())
_4_1_TERMINOLOGY = str(Paths.terminology())
_4_2_TRANSLATION = str(Paths.translation_results())
_5_SPLIT_SUB = str(Paths.translation_results_for_subtitles())
_5_REMERGED = str(Paths.translation_results_remerged())
_8_1_AUDIO_TASK = str(Paths.tts_tasks())

# Audio files and directories
_OUTPUT_DIR = str(Paths.output_dir())
_AUDIO_DIR = str(Paths.audio_dir())
_RAW_AUDIO_FILE = str(Paths.raw_audio())
_VOCAL_AUDIO_FILE = str(Paths.vocal_audio())
_BACKGROUND_AUDIO_FILE = str(Paths.background_audio())
_AUDIO_REFERS_DIR = str(Paths.audio_refers_dir())
_AUDIO_SEGS_DIR = str(Paths.audio_segs_dir())
_AUDIO_TMP_DIR = str(Paths.audio_tmp_dir())

# Dubbing output
DUB_VOCAL_FILE = str(Paths.dub_vocal())
DUB_SUB_FILE = str(Paths.dub_subtitle())

# Log directories
GPT_LOG_FOLDER = str(Paths.gpt_log_dir())

# Export all backward compatibility variables
__all__ = [
    "_2_CLEANED_CHUNKS",
    "_3_1_SPLIT_BY_NLP",
    "_3_2_SPLIT_BY_MEANING",
    "_4_1_TERMINOLOGY",
    "_4_2_TRANSLATION",
    "_5_SPLIT_SUB",
    "_5_REMERGED",
    "_8_1_AUDIO_TASK",
    "_OUTPUT_DIR",
    "_AUDIO_DIR",
    "_RAW_AUDIO_FILE",
    "_VOCAL_AUDIO_FILE",
    "_BACKGROUND_AUDIO_FILE",
    "_AUDIO_REFERS_DIR",
    "_AUDIO_SEGS_DIR",
    "_AUDIO_TMP_DIR",
    "DUB_VOCAL_FILE",
    "DUB_SUB_FILE",
    "GPT_LOG_FOLDER",
]
