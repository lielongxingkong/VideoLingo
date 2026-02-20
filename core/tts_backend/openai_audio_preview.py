from openai import OpenAI
from pathlib import Path
import base64
from core.utils.config_utils import load_key
from core.utils.decorator import except_handler
from core.constants import DEFAULT_OPENAI_TTS_VOICE, DEFAULT_OPENAI_TTS_BASE_URL
from rich import print as rprint


@except_handler("Failed to generate audio using OpenAI Audio Preview")
def openai_audio_preview_for_videolingo(text, save_as):
    """
    Generate speech using OpenAI gpt-4o-mini-audio-preview via Chat Completions API
    """
    # Get API configuration from config, fall back to main API config if not set
    api_key = load_key("openai_tts.api_key") or load_key("api.key")
    base_url = load_key("openai_tts.base_url") or load_key("api.base_url")
    voice = load_key("openai_tts.voice") or DEFAULT_OPENAI_TTS_VOICE

    if not api_key:
        raise ValueError("OpenAI API key is not set. Please set either openai_tts.api_key or api.key in the Streamlit settings page")

    # Handle base URL
    if not base_url or base_url == "":
        base_url = DEFAULT_OPENAI_TTS_BASE_URL
    elif 'v1' not in base_url:
        base_url = base_url.strip('/') + '/v1'

    client = OpenAI(api_key=api_key, base_url=base_url)

    save_path = Path(save_as)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Get target language from config
    target_language = load_key("target_language") or "Chinese"

    # Use gpt-4o-mini-audio-preview with chat completions API
    response = client.chat.completions.create(
        model="gpt-4o-mini-audio-preview",
        modalities=["text", "audio"],
        audio={"voice": voice, "format": "wav"},
        messages=[
            {
                "role": "user",
                "content": f"请用{target_language}语言朗读以下文本，要求清晰自然：{text}"
            }
        ]
    )

    # Save the audio
    if response.choices[0].message.audio:
        audio_data = base64.b64decode(response.choices[0].message.audio.data)
        with open(save_path, 'wb') as f:
            f.write(audio_data)
        rprint(f"音频已成功保存至: {save_path}")
        return True
    else:
        raise Exception("No audio output received from the model")
