# Lazy import core modules only when needed
# This avoids startup delays and import errors

__all__ = [
    'ask_gpt',
    'load_key',
    'update_key',
    'cleanup',
    'delete_dubbing_files',
    'get_logger',
    '_1_ytdlp',
    '_2_asr',
    '_3_1_split_nlp',
    '_3_2_split_meaning',
    '_4_1_summarize',
    '_4_2_translate',
    '_5_split_sub',
    '_6_gen_sub',
    '_7_sub_into_vid',
    '_8_1_audio_task',
    '_8_2_dub_chunks',
    '_9_refer_audio',
    '_10_gen_audio',
    '_11_merge_audio',
    '_12_dub_to_vid'
]

# Lazy import on first access
def __getattr__(name):
    if name == 'get_logger':
        from .logger import get_logger
        return get_logger
    elif name in ['ask_gpt', 'load_key', 'update_key']:
        from .utils import ask_gpt, load_key, update_key
        if name == 'ask_gpt':
            return ask_gpt
        elif name == 'load_key':
            return load_key
        elif name == 'update_key':
            return update_key
    elif name == 'cleanup':
        from .utils.onekeycleanup import cleanup
        return cleanup
    elif name == 'delete_dubbing_files':
        from .utils.delete_retry_dubbing import delete_dubbing_files
        return delete_dubbing_files
    elif name.startswith('_'):
        import importlib
        return importlib.import_module(f'.{name}', __name__)
    raise AttributeError(f"module {__name__} has no attribute {name}")
