"""
Unified logging system for VideoLingo.

This module provides a unified logging interface that replaces direct use of
print() and rprint() statements with a structured logging system that supports:

- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- Colored console output using rich
- File logging to output/log/app.log
- Helper methods for common patterns (success, error, warning, info, debug)
- Backward compatibility with existing code
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


# ------------------------------
# Configuration
# ------------------------------

# Get project root directory (parent of core/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, "output", "log")
LOG_FILE = os.path.join(LOG_DIR, "app.log")
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5  # Keep 5 backup log files


# ------------------------------
# Rich Console for Colored Output
# ------------------------------

console = Console()


# ------------------------------
# Custom Logger Class
# ------------------------------

class VideoLingoLogger(logging.Logger):
    """Custom logger with rich output and helper methods."""

    def __init__(self, name: str, level: int = logging.DEBUG):
        super().__init__(name, level)
        self._console = console

    def success(self, message: str, *args, **kwargs):
        """Log a success message (green text)."""
        self.info(f"[green]{message}[/green]", *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log a warning message (yellow text)."""
        self._log(logging.WARNING, f"[yellow]⚠️ {message}[/yellow]", args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log an error message (red text)."""
        self._log(logging.ERROR, f"[red]❌ {message}[/red]", args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log an info message (cyan text for processes, white for general)."""
        if any(keyword in message.lower() for keyword in ["processing", "transcribing", "downloading", "generating"]):
            self._log(logging.INFO, f"[cyan]{message}[/cyan]", args, **kwargs)
        else:
            self._log(logging.INFO, message, args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        """Log a debug message (gray text)."""
        self._log(logging.DEBUG, f"[gray]{message}[/gray]", args, **kwargs)


# ------------------------------
# Logger Initialization
# ------------------------------

def get_logger(name: str) -> VideoLingoLogger:
    """
    Get a logger instance for the given module name.

    Args:
        name: The name of the module (usually __name__)

    Returns:
        VideoLingoLogger instance with configured handlers
    """
    # Set custom logger class
    logging.setLoggerClass(VideoLingoLogger)

    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Capture all levels at logger level

    # Check if logger already has handlers (avoid duplication)
    if logger.handlers:
        return logger

    # ------------------------------
    # Console Handler (Rich)
    # ------------------------------
    console_handler = RichHandler(
        console=console,
        show_path=False,
        show_time=True,
        rich_tracebacks=True
    )
    console_handler.setLevel(logging.INFO)  # Show INFO and above in console

    # ------------------------------
    # File Handler (Rotating)
    # ------------------------------
    # Ensure log directory exists before creating file handler
    os.makedirs(LOG_DIR, exist_ok=True)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)  # Log all levels to file

    # ------------------------------
    # Formatter
    # ------------------------------
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)

    # ------------------------------
    # Add Handlers
    # ------------------------------
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# ------------------------------
# Backward Compatibility
# ------------------------------

def rprint(*args, **kwargs):
    """
    Backward compatibility function for rich.print.

    Uses logger.info() to maintain compatibility with existing code that
    uses from rich import print as rprint.
    """
    logger = get_logger("rprint")
    message = " ".join(str(arg) for arg in args)
    logger.info(message)


# ------------------------------
# Progress Tracking Helper
# ------------------------------

def log_progress(current: int, total: int, task: str):
    """
    Log progress for iterative tasks.

    Args:
        current: Current item number
        total: Total number of items
        task: Description of the task
    """
    logger = get_logger("progress")
    percentage = (current / total) * 100
    logger.info(f"[blue]Progress: {current}/{total} ({percentage:.1f}%) - {task}[/blue]")


# ------------------------------
# Module Level Convenience
# ------------------------------

# Default logger for quick use
logger = get_logger(__name__)

if __name__ == "__main__":
    # Test the logger
    test_logger = get_logger("test")
    test_logger.debug("Debug message - only in log file")
    test_logger.info("Info message - console and log file")
    test_logger.success("Success message - green text")
    test_logger.warning("Warning message - yellow text with warning symbol")
    test_logger.error("Error message - red text with error symbol")

    # Test progress logging
    log_progress(3, 10, "Processing audio segments")

    # Test backward compatibility
    rprint("[cyan]Testing rprint compatibility[/cyan]")
