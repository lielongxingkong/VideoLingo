import streamlit as st
import json
import os
from translations.translations import translate as t
from translations.translations import DISPLAY_LANGUAGES
from core.utils.config_utils import DEFAULT_CONFIG, load_key, update_key, save_config_to_file, load_config_from_file
from core.constants import (
    TTS_METHOD_OPTIONS,
    OPENAI_TTS_VOICE_OPTIONS,
    OPENAI_TTS_MODEL_OPTIONS,
    ASR_RUNTIME_OPTIONS,
    API_FORMAT_OPTIONS,
    ASR_LANGUAGE_OPTIONS,
    DEFAULT_OPENAI_TTS_VOICE,
    DEFAULT_OPENAI_TTS_MODEL,
    DEFAULT_EDGE_TTS_VOICE,
)
from core.utils import *

# Common edge-tts voices by language (voice: (locale, gender))
EDGE_TTS_VOICE_OPTIONS = {
    # Chinese
    "zh-CN-XiaoxiaoNeural": ("中文", "女"),
    "zh-CN-XiaoyiNeural": ("中文", "女"),
    "zh-CN-YunjianNeural": ("中文", "男"),
    "zh-HK-HiuGaaiNeural": ("粤语", "女"),
    "zh-HK-HiuMaanNeural": ("粤语", "女"),
    # English
    "en-US-JennyNeural": ("英语", "女"),
    "en-US-GuyNeural": ("英语", "男"),
    "en-US-EmmaNeural": ("英语", "女"),
    "en-GB-SoniaNeural": ("英语", "女"),
    "en-AU-NatashaNeural": ("英语", "女"),
    # Japanese
    "ja-JP-NanamiNeural": ("日语", "女"),
    "ja-JP-KeitaNeural": ("日语", "男"),
    # Korean
    "ko-KR-SunHiNeural": ("韩语", "女"),
    "ko-KR-HyunsuMultilingualNeural": ("韩语", "男"),
    # European
    "es-ES-XimenaNeural": ("西班牙语", "女"),
    "fr-FR-DeniseNeural": ("法语", "女"),
    "de-DE-AmalaNeural": ("德语", "女"),
    "ru-RU-SvetlanaNeural": ("俄语", "女"),
}


def get_edge_voice_display(voice):
    """Get display text for voice"""
    if voice in EDGE_TTS_VOICE_OPTIONS:
        lang, gender = EDGE_TTS_VOICE_OPTIONS[voice]
        return f"{voice} ({lang}-{gender})"
    return voice


def config_input(label, key, help=None, key_suffix=None, placeholder=None):
    """Generic config input handler"""
    unique_key = f"{key}_{key_suffix}" if key_suffix else key
    # Get initial value from our config
    initial_value = load_key(key)
    # Text input - Streamlit auto-manages state via key
    result = st.text_input(label, value=initial_value, placeholder=placeholder, help=help, key=unique_key)
    # Always update config with current value from widget
    if result != initial_value:
        update_key(key, result)
    return result

def page_setting():
    # Initialize session state with defaults
    if "config" not in st.session_state:
        st.session_state.config = DEFAULT_CONFIG.copy()
        # Try to load from config file if exists
        config_path = DEFAULT_CONFIG.get("config_file_path", "./videolingo_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    imported_config = json.load(f)
                # Merge with DEFAULT_CONFIG to ensure all keys exist
                st.session_state.config = DEFAULT_CONFIG.copy()
                st.session_state.config.update(imported_config)
            except Exception:
                pass

    # Configuration management
    with st.expander(t("Configuration Management") + " 💾", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t("Save Configuration"), key="save_config"):
                success, result = save_config_to_file()
                if success:
                    st.success(f"Saved to: {result}")
                else:
                    st.error(f"Error: {result}")
        with col2:
            if st.button(t("Load Configuration"), key="load_config"):
                success, result = load_config_from_file()
                if success:
                    st.success(f"Loaded from: {result}")
                    st.rerun()
                else:
                    st.error(f"Error: {result}")

    current_display_lang = load_key("display_language")
    if "prev_display_language" not in st.session_state:
        st.session_state.prev_display_language = current_display_lang

    display_language = st.selectbox("Display Language 🌐",
                                  options=list(DISPLAY_LANGUAGES.keys()),
                                  index=list(DISPLAY_LANGUAGES.values()).index(current_display_lang),
                                  key="display_lang_selectbox")
    if DISPLAY_LANGUAGES[display_language] != st.session_state.prev_display_language:
        update_key("display_language", DISPLAY_LANGUAGES[display_language])
        st.session_state.prev_display_language = DISPLAY_LANGUAGES[display_language]
        st.rerun()

    # with st.expander(t("Youtube Settings"), expanded=True):
    #     config_input(t("Cookies Path"), "youtube.cookies_path")

    with st.expander(t("LLM Configuration"), expanded=True):
        config_input(t("API_KEY"), "api.key", placeholder="sk-...")
        config_input(t("BASE_URL"), "api.base_url", help=t("Openai format, will add /v1/chat/completions automatically"), placeholder="https://api.openai.com/v1")

        # API format selection
        current_api_format = load_key("api.format")
        # Track previous value to avoid rerun loop
        if "prev_api_format" not in st.session_state:
            st.session_state.prev_api_format = current_api_format

        api_format = st.selectbox(
            t("API Format"),
            options=API_FORMAT_OPTIONS,
            index=0 if current_api_format == "openai" else 1,
            help=t("OpenAI format or Anthropic format"),
            key="api_format_selectbox"
        )
        if api_format != st.session_state.prev_api_format:
            update_key("api.format", api_format)
            st.session_state.prev_api_format = api_format
            st.rerun()

        c1, c2 = st.columns([4, 1])
        with c1:
            config_input(t("MODEL"), "api.model", help=t("click to check API validity")+ " 👉")
        with c2:
            if st.button("📡", key="api"):
                is_valid, msg = check_api()
                st.toast(msg, icon="✅" if is_valid else "❌")
        llm_support_json = st.toggle(t("LLM JSON Format Support"), value=load_key("api.llm_support_json"), help=t("Enable if your LLM supports JSON mode output"))
        if llm_support_json != load_key("api.llm_support_json"):
            update_key("api.llm_support_json", llm_support_json)
            st.rerun()
    with st.expander(t("Subtitles Settings"), expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            current_asr_lang = load_key("asr.language")
            if "prev_asr_language" not in st.session_state:
                st.session_state.prev_asr_language = current_asr_lang

            lang = st.selectbox(
                t("Recog Lang"),
                options=list(ASR_LANGUAGE_OPTIONS.keys()),
                index=list(ASR_LANGUAGE_OPTIONS.values()).index(current_asr_lang),
                key="asr_lang_selectbox"
            )
            if ASR_LANGUAGE_OPTIONS[lang] != st.session_state.prev_asr_language:
                update_key("asr.language", ASR_LANGUAGE_OPTIONS[lang])
                st.session_state.prev_asr_language = ASR_LANGUAGE_OPTIONS[lang]
                st.rerun()

        current_asr_runtime = load_key("asr.runtime")
        if "prev_asr_runtime" not in st.session_state:
            st.session_state.prev_asr_runtime = current_asr_runtime

        runtime = st.selectbox(t("ASR Service"), options=ASR_RUNTIME_OPTIONS, index=0 if current_asr_runtime == "elevenlabs" else 1, help=t("ElevenLabs ASR or OpenAI Whisper API"), key="asr_runtime_selectbox")
        if runtime != st.session_state.prev_asr_runtime:
            update_key("asr.runtime", runtime)
            st.session_state.prev_asr_runtime = runtime
            st.rerun()
        if runtime == "elevenlabs":
            config_input(("ElevenLabs API"), "asr.elevenlabs_api_key", placeholder="sk_...")
        elif runtime == "openai":
            config_input(t("OpenAI API Key (ASR)"), "asr.openai_api_key", key_suffix="asr_api", placeholder="sk-...")
            config_input(t("OpenAI Base URL"), "asr.openai_base_url", key_suffix="asr_url", placeholder="https://api.openai.com/v1")

        with c2:
            target_language = st.text_input(t("Target Lang"), value=load_key("target_language"), help=t("Input any language in natural language, as long as llm can understand"))
            if target_language != load_key("target_language"):
                update_key("target_language", target_language)
                st.rerun()

        burn_subtitles = st.toggle(t("Burn-in Subtitles"), value=load_key("burn_subtitles"), help=t("Whether to burn subtitles into the video, will increase processing time"))
        if burn_subtitles != load_key("burn_subtitles"):
            update_key("burn_subtitles", burn_subtitles)
            st.rerun()

        # Demucs vocal separation
        demucs_enabled = st.toggle(
            t("Enable Demucs Vocal Separation"),
            value=load_key("demucs.enabled"),
            help=t("Separate vocals from background audio before ASR")
        )
        if demucs_enabled != load_key("demucs.enabled"):
            update_key("demucs.enabled", demucs_enabled)
            st.rerun()
    with st.expander(t("Dubbing Settings"), expanded=True):
        current_tts = load_key("tts_method")
        if "prev_tts_method" not in st.session_state:
            st.session_state.prev_tts_method = current_tts

        select_tts = st.selectbox(t("TTS Method"), options=TTS_METHOD_OPTIONS, index=TTS_METHOD_OPTIONS.index(current_tts) if current_tts in TTS_METHOD_OPTIONS else 0, key="tts_method_selectbox")
        if select_tts != st.session_state.prev_tts_method:
            update_key("tts_method", select_tts)
            st.session_state.prev_tts_method = select_tts
            st.rerun()

        # sub settings for each tts method
        if select_tts == "edge_tts":
            voice_options = list(EDGE_TTS_VOICE_OPTIONS.keys())
            voice_display = [get_edge_voice_display(v) for v in voice_options]

            current_voice = load_key("edge_tts.voice") or DEFAULT_EDGE_TTS_VOICE
            if current_voice not in voice_options:
                current_voice = voice_options[0]

            selected_voice = st.selectbox(
                t("Edge TTS Voice"),
                options=voice_display,
                index=voice_options.index(current_voice),
                key="edge_voice_selectbox"
            )
            # Map back to actual voice name
            selected_voice = voice_options[voice_display.index(selected_voice)]
            if selected_voice != current_voice:
                update_key("edge_tts.voice", selected_voice)

        elif select_tts == "openai_tts":
            config_input(t("OpenAI API Key"), "openai_tts.api_key", key_suffix="tts_api", placeholder="sk-...")
            config_input(t("OpenAI Base URL"), "openai_tts.base_url", key_suffix="tts_url", placeholder="https://api.openai.com/v1")

            # Voice selection
            current_voice = load_key("openai_tts.voice") or DEFAULT_OPENAI_TTS_VOICE
            if "prev_openai_voice" not in st.session_state:
                st.session_state.prev_openai_voice = current_voice

            selected_voice = st.selectbox(
                t("OpenAI Voice"),
                options=OPENAI_TTS_VOICE_OPTIONS,
                index=OPENAI_TTS_VOICE_OPTIONS.index(current_voice) if current_voice in OPENAI_TTS_VOICE_OPTIONS else 0,
                key="openai_voice_selectbox"
            )
            # Model selection
            current_model = load_key("openai_tts.model") or DEFAULT_OPENAI_TTS_MODEL
            if "prev_openai_model" not in st.session_state:
                st.session_state.prev_openai_model = current_model

            selected_model = st.selectbox(
                t("OpenAI Model"),
                options=OPENAI_TTS_MODEL_OPTIONS,
                index=OPENAI_TTS_MODEL_OPTIONS.index(current_model) if current_model in OPENAI_TTS_MODEL_OPTIONS else 0,
                key="openai_model_selectbox"
            )
            if selected_model != st.session_state.prev_openai_model:
                update_key("openai_tts.model", selected_model)
                st.session_state.prev_openai_model = selected_model
                st.rerun()

    # Advanced Settings
    with st.expander(t("Advanced Settings ⚙️"), expanded=False):
        # Use tabs instead of nested expanders
        tab_names = [t("General"), t("LLM"), t("Subtitle"), t("Video"), t("Audio")]
        tabs = st.tabs(tab_names)

        with tabs[0]:
            # General settings
            config_file_path = st.text_input(
                t("Config File Path"),
                value=load_key("config_file_path"),
                help=t("Path to save/load configuration file"),
                key="adv_config_file_path"
            )
            if config_file_path != load_key("config_file_path"):
                update_key("config_file_path", config_file_path)

        with tabs[1]:
            # LLM settings
            max_workers = st.number_input(
                t("Max Workers"),
                min_value=1,
                max_value=32,
                value=load_key("max_workers"),
                help=t("Number of parallel LLM requests"),
                key="adv_max_workers"
            )
            if max_workers != load_key("max_workers"):
                update_key("max_workers", max_workers)

            summary_length = st.number_input(
                t("Summary Length"),
                min_value=1000,
                max_value=20000,
                value=load_key("summary_length"),
                step=1000,
                help=t("Summary length in characters"),
                key="adv_summary_length"
            )
            if summary_length != load_key("summary_length"):
                update_key("summary_length", summary_length)

            reflect_translate = st.toggle(t("Reflect Translation"), value=load_key("reflect_translate"), help=t("Show translation in original text context"), key="adv_reflect")
            if reflect_translate != load_key("reflect_translate"):
                update_key("reflect_translate", reflect_translate)
                st.rerun()

            pause_before_translate = st.toggle(t("Pause Before Translate"), value=load_key("pause_before_translate"), help=t("Pause to allow terminology adjustment"), key="adv_pause")
            if pause_before_translate != load_key("pause_before_translate"):
                update_key("pause_before_translate", pause_before_translate)
                st.rerun()

        with tabs[2]:
            # Subtitle settings
            max_length = st.number_input(
                t("Subtitle Max Length"),
                min_value=20,
                max_value=150,
                value=load_key("subtitle.max_length"),
                help=t("Maximum characters per subtitle line"),
                key="adv_max_length"
            )
            if max_length != load_key("subtitle.max_length"):
                update_key("subtitle.max_length", max_length)

            target_multiplier = st.number_input(
                t("Target Multiplier"),
                min_value=1.0,
                max_value=2.0,
                value=load_key("subtitle.target_multiplier"),
                step=0.1,
                help=t("Translated subtitle length multiplier"),
                key="adv_multiplier"
            )
            if target_multiplier != load_key("subtitle.target_multiplier"):
                update_key("subtitle.target_multiplier", target_multiplier)

            max_split_length = st.number_input(
                t("Max Split Length"),
                min_value=10,
                max_value=30,
                value=load_key("max_split_length"),
                help=t("Maximum words for initial split"),
                key="adv_split_length"
            )
            if max_split_length != load_key("max_split_length"):
                update_key("max_split_length", max_split_length)

        with tabs[3]:
            # Video settings
            ffmpeg_gpu = st.toggle(t("FFmpeg GPU Acceleration"), value=load_key("ffmpeg_gpu"), help=t("Use h264_nvenc for faster encoding"), key="adv_ffmpeg")
            if ffmpeg_gpu != load_key("ffmpeg_gpu"):
                update_key("ffmpeg_gpu", ffmpeg_gpu)
                st.rerun()

            burn_subtitles_adv = st.toggle(t("Burn Subtitles"), value=load_key("burn_subtitles"), help=t("Burn subtitles into video"), key="adv_burn")
            if burn_subtitles_adv != load_key("burn_subtitles"):
                update_key("burn_subtitles", burn_subtitles_adv)
                st.rerun()

        with tabs[4]:
            # Audio/Dubbing settings
            c1, c2 = st.columns(2)
            with c1:
                min_speed = st.number_input(
                    t("Min Speed Factor"),
                    min_value=1.0,
                    max_value=2.0,
                    value=float(load_key("speed_factor.min")),
                    step=0.1,
                    help=t("Minimum audio speed"),
                    key="adv_min_speed"
                )
                if min_speed != load_key("speed_factor.min"):
                    update_key("speed_factor.min", min_speed)
            with c2:
                max_speed = st.number_input(
                    t("Max Speed Factor"),
                    min_value=1.0,
                    max_value=2.0,
                    value=float(load_key("speed_factor.max")),
                    step=0.1,
                    help=t("Maximum audio speed"),
                    key="adv_max_speed"
                )
                if max_speed != load_key("speed_factor.max"):
                    update_key("speed_factor.max", max_speed)

            accept_speed = st.number_input(
                t("Acceptable Speed Factor"),
                min_value=1.0,
                max_value=2.0,
                value=float(load_key("speed_factor.accept")),
                step=0.1,
                help=t("Maximum acceptable speed without warning"),
                key="adv_accept_speed"
            )
            if accept_speed != load_key("speed_factor.accept"):
                update_key("speed_factor.accept", accept_speed)

            c1, c2 = st.columns(2)
            with c1:
                min_sub_dur = st.number_input(
                    t("Min Subtitle Duration"),
                    min_value=0.5,
                    max_value=10.0,
                    value=float(load_key("min_subtitle_duration")),
                    step=0.5,
                    help=t("Minimum subtitle duration in seconds"),
                    key="adv_min_sub_dur"
                )
                if min_sub_dur != load_key("min_subtitle_duration"):
                    update_key("min_subtitle_duration", min_sub_dur)
            with c2:
                min_trim_dur = st.number_input(
                    t("Min Trim Duration"),
                    min_value=0.5,
                    max_value=10.0,
                    value=float(load_key("min_trim_duration")),
                    step=0.5,
                    help=t("Subtitles shorter than this won't be split"),
                    key="adv_min_trim"
                )
                if min_trim_dur != load_key("min_trim_duration"):
                    update_key("min_trim_duration", min_trim_dur)

            tolerance = st.number_input(
                t("Tolerance"),
                min_value=0.1,
                max_value=5.0,
                value=float(load_key("tolerance")),
                step=0.1,
                help=t("Allowed extension time to next subtitle"),
                key="adv_tolerance"
            )
            if tolerance != load_key("tolerance"):
                update_key("tolerance", tolerance)

def check_api():
    """Test API with a simple JSON request (no retry)"""
    from openai import OpenAI
    import json
    api_key = load_key("api.key")
    base_url = load_key("api.base_url")

    if not api_key:
        return False, "❌ API key is not set"

    # Normalize base_url
    if 'v1' not in base_url:
        base_url = base_url.strip('/') + '/v1'

    print(f"[API Test] Testing {base_url} with model {load_key('api.model')}")

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)

        # Try with response_format and reasoning_split first
        try:
            resp = client.chat.completions.create(
                model=load_key("api.model"),
                messages=[{"role": "user", "content": "Reply with JSON: {\"message\": \"success\"}"}],
                response_format={"type": "json_object"},
                extra_body={"reasoning_split": True}
            )
            print(f"[API Test] Used response_format + reasoning_split")
        except Exception as format_err:
            print(f"[API Test] response_format/reasoning_split not supported, trying without: {format_err}")
            try:
                resp = client.chat.completions.create(
                    model=load_key("api.model"),
                    messages=[{"role": "user", "content": "Reply with JSON: {\"message\": \"success\"}"}],
                    response_format={"type": "json_object"}
                )
            except Exception as format_err2:
                print(f"[API Test] response_format not supported either, trying basic: {format_err2}")
                resp = client.chat.completions.create(
                    model=load_key("api.model"),
                    messages=[{"role": "user", "content": "Reply with JSON: {\"message\": \"success\"}"}]
                )

        print(f"[API Test] Full response: {resp}")
        msg = resp.choices[0].message
        # When reasoning_split=True, JSON is in content, thinking is in reasoning_details
        # So we use content directly
        content = msg.content
        print(f"[API Test] Using content (JSON): {repr(content)}")
        json_content = content.strip()

        resp_data = json.loads(json_content)
        if isinstance(resp_data, dict) and 'message' in resp_data:
            return True, f"✅ API works! Response: {resp_data}"
        else:
            return False, f"❌ Invalid response: {resp_data}"
    except Exception as e:
        import traceback
        print(f"[API Test] Error: {e}")
        traceback.print_exc()
        return False, f"❌ API error: {str(e)[:150]}"

if __name__ == "__main__":
    check_api()
