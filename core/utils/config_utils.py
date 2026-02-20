import streamlit as st
import json
import os
import threading

lock = threading.Lock()

# -----------------------
# Import pure config
# -----------------------
from core.utils.config import (
    DEFAULT_CONFIG,
    RUNTIME_CONFIG,
    load_key as load_key_pure,
    set_runtime_key,
    clear_runtime_config,
    get_joiner,
    _load_config_from_file_pure,
)

# -----------------------
# Streamlit-specific config functions
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
    """Load config value from RUNTIME_CONFIG, session_state, or DEFAULT_CONFIG"""
    # First try RUNTIME_CONFIG (for worker threads)
    if key in RUNTIME_CONFIG and RUNTIME_CONFIG[key] is not None:
        return RUNTIME_CONFIG[key]

    # Then try session_state (Streamlit context)
    if hasattr(st, 'session_state') and st.session_state:
        config = st.session_state.get("config", {})
        if config is not None and key in config:
            value = config[key]
            # Check if value is not None (allow False, 0, empty string)
            if value is not None:
                return value

    # Fallback to pure config (file or default)
    return load_key_pure(key)


def update_key(key, value):
    """Update config value in session_state"""
    if hasattr(st, 'session_state') and st.session_state:
        if "config" not in st.session_state:
            st.session_state.config = DEFAULT_CONFIG.copy()

        # Use key directly (flat key structure, not nested)
        st.session_state.config[key] = value
        return True
    return False


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
    """Load config from file into session_state"""
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


def init_session_config():
    """Initialize session_state config from DEFAULT_CONFIG or file"""
    if not hasattr(st, 'session_state'):
        return
    if "config" not in st.session_state or st.session_state.config is None:
        # Try to load from file first
        file_config = _load_config_from_file_pure()
        if file_config:
            merged_config = DEFAULT_CONFIG.copy()
            merged_config.update(file_config)
            st.session_state.config = merged_config
        else:
            st.session_state.config = DEFAULT_CONFIG.copy()


if __name__ == "__main__":
    print(load_key('language_split_with_space'))

