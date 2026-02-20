import functools
import time
import os
from core.logger import get_logger

# ------------------------------
# retry decorator
# ------------------------------

def except_handler(error_msg, retry=0, delay=1, default_return=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__name__)
            last_exception = None
            for i in range(retry + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.error(f"{error_msg}: {e}, retry: {i+1}/{retry}")
                    if i == retry:
                        if default_return is not None:
                            return default_return
                        raise last_exception
                    time.sleep(delay * (2**i))
        return wrapper
    return decorator


# ------------------------------
# check file exists decorator
# ------------------------------

def validate_excel_file(file_path):
    """Validate that an Excel file exists and can be read."""
    try:
        import pandas as pd
        # Check file size > 0
        if os.path.getsize(file_path) == 0:
            return False
        # Try to read the Excel file
        pd.read_excel(file_path)
        return True
    except Exception:
        return False


def check_file_exists(file_path, validate_func=None, force_rerun=False):
    """
    Decorator that checks if a file exists before executing the function.

    Args:
        file_path: Path to the file to check
        validate_func: Optional validation function that takes file_path and returns bool
        force_rerun: If True, always execute the function regardless of file existence
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__name__)

            # If force_rerun is True, always execute
            if force_rerun:
                logger.info(f"Force rerun enabled, executing <{func.__name__}> step.")
                return func(*args, **kwargs)

            # Check if file exists
            if os.path.exists(file_path):
                # Basic size check first
                if os.path.getsize(file_path) == 0:
                    logger.warning(f"File <{file_path}> exists but is empty, re-executing <{func.__name__}> step.")
                    return func(*args, **kwargs)

                # If validation function is provided, use it
                if validate_func is not None:
                    try:
                        if validate_func(file_path):
                            logger.warning(f"File <{file_path}> already exists and passed validation, skip <{func.__name__}> step.")
                            return
                        else:
                            logger.warning(f"File <{file_path}> exists but failed validation, re-executing <{func.__name__}> step.")
                    except Exception as e:
                        logger.warning(f"Validation failed for file <{file_path}>: {e}, re-executing <{func.__name__}> step.")
                else:
                    # Default: just check existence and non-empty
                    logger.warning(f"File <{file_path}> already exists, skip <{func.__name__}> step.")
                    return

            # File doesn't exist or validation failed, execute the function
            return func(*args, **kwargs)
        return wrapper
    return decorator

if __name__ == "__main__":
    @except_handler("function execution failed", retry=3, delay=1)
    def test_function():
        raise Exception("test exception")
    test_function()
