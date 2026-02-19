from openai import OpenAI
from pathlib import Path
from core.utils.config_utils import load_key
from core.utils.decorator import except_handler
from rich import print as rprint


@except_handler("Failed to generate audio using OpenAI TTS")
def openai_tts_for_videolingo(text, save_as):
    """
    Generate speech using OpenAI Text-to-Speech API
    """
    # Get API configuration from config, fall back to main API config if not set
    api_key = load_key("openai_tts.api_key") or load_key("api.key")
    base_url = load_key("openai_tts.base_url") or load_key("api.base_url")
    voice = load_key("openai_tts.voice") or "alloy"
    model = load_key("openai_tts.model") or "tts-1"

    if not api_key:
        raise ValueError("OpenAI API key is not set. Please set either openai_tts.api_key or api.key in the Streamlit settings page")

    # Handle base URL
    if not base_url or base_url == "":
        base_url = "https://api.openai.com/v1"
    elif 'v1' not in base_url:
        base_url = base_url.strip('/') + '/v1'

    client = OpenAI(api_key=api_key, base_url=base_url)

    save_path = Path(save_as)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    with client.audio.speech.with_streaming_response.create(
        model=model,
        voice=voice,
        input=text,
        response_format="wav"
    ) as response:
        response.stream_to_file(save_path)

    rprint(f"音频已成功保存至: {save_path}")
    return True
