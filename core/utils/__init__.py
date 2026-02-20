# use try-except to avoid error when installing
import warnings

try:
    from .ask_gpt import ask_gpt
    from .decorator import except_handler, check_file_exists
    from .config_utils import load_key, update_key, get_joiner
    from rich import print as rprint
except ImportError as e:
    warnings.warn(f"Failed to import core.utils modules: {e}. Some functionality may not be available.", ImportWarning)
    ask_gpt = None
    except_handler = None
    check_file_exists = None
    load_key = None
    update_key = None
    get_joiner = None
    rprint = None

__all__ = ["ask_gpt", "except_handler", "check_file_exists", "load_key", "update_key", "rprint", "get_joiner"]