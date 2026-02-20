"""
Base ASR Backend Interface

Defines the abstract base class for ASR (Automatic Speech Recognition) backends.
All ASR implementations should inherit from this class and implement the required methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ASRBackend(ABC):
    """Abstract base class for ASR backends."""

    @abstractmethod
    def transcribe(
        self,
        raw_audio_path: str,
        vocal_audio_path: str,
        start: Optional[float] = None,
        end: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text with word-level timestamps.

        Args:
            raw_audio_path: Path to the original raw audio file
            vocal_audio_path: Path to the processed vocal audio file
            start: Optional start time in seconds (for partial transcription)
            end: Optional end time in seconds (for partial transcription)

        Returns:
            Dictionary containing transcription results in Whisper-compatible format:
            {
                "segments": [
                    {
                        "text": "segment text",
                        "start": 0.0,
                        "end": 2.5,
                        "speaker_id": 0,
                        "words": [
                            {"text": "word", "start": 0.0, "end": 0.5}
                        ]
                    }
                ]
            }
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this ASR backend."""
        pass

    @property
    @abstractmethod
    def supports_word_level_timestamps(self) -> bool:
        """Check if this backend supports word-level timestamps."""
        pass

    @property
    @abstractmethod
    def supports_diarization(self) -> bool:
        """Check if this backend supports speaker diarization."""
        pass
