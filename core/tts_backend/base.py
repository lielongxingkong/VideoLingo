"""
Base TTS Backend Interface

Defines the abstract base class for TTS (Text-to-Speech) backends.
All TTS implementations should inherit from this class and implement the required methods.
"""

from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class TTSBackend(ABC):
    """Abstract base class for TTS backends."""

    @abstractmethod
    def synthesize(
        self,
        text: str,
        output_path: str,
        number: Optional[int] = None,
        task_df: Optional[pd.DataFrame] = None
    ) -> None:
        """
        Synthesize text to audio and save to file.

        Args:
            text: The text to synthesize
            output_path: Path where the audio file should be saved
            number: Optional segment number for reference
            task_df: Optional DataFrame with task context
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this TTS backend."""
        pass

    @property
    @abstractmethod
    def supports_ssml(self) -> bool:
        """Check if this backend supports SSML (Speech Synthesis Markup Language)."""
        pass

    @property
    @abstractmethod
    def available_voices(self) -> list:
        """Get list of available voice names for this backend."""
        pass
