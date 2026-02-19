import streamlit as st
from translations.translations import translate as t
from translations.translations import DISPLAY_LANGUAGES
from core.utils import *

def config_input(label, key, help=None, key_suffix=None):
    """Generic config input handler"""
    unique_key = f"{key}_{key_suffix}" if key_suffix else key
    val = st.text_input(label, value=load_key(key), help=help, key=unique_key)
    if val != load_key(key):
        update_key(key, val)
    return val

def page_setting():

    display_language = st.selectbox("Display Language 🌐", 
                                  options=list(DISPLAY_LANGUAGES.keys()),
                                  index=list(DISPLAY_LANGUAGES.values()).index(load_key("display_language")))
    if DISPLAY_LANGUAGES[display_language] != load_key("display_language"):
        update_key("display_language", DISPLAY_LANGUAGES[display_language])
        st.rerun()

    # with st.expander(t("Youtube Settings"), expanded=True):
    #     config_input(t("Cookies Path"), "youtube.cookies_path")

    with st.expander(t("LLM Configuration"), expanded=True):
        config_input(t("API_KEY"), "api.key")
        config_input(t("BASE_URL"), "api.base_url", help=t("Openai format, will add /v1/chat/completions automatically"))

        # API format selection
        api_format = st.selectbox(
            t("API Format"),
            options=["openai", "anthropic"],
            index=0 if load_key("api.format") == "openai" else 1,
            help=t("OpenAI format or Anthropic format")
        )
        if api_format != load_key("api.format"):
            update_key("api.format", api_format)
            st.rerun()

        c1, c2 = st.columns([4, 1])
        with c1:
            config_input(t("MODEL"), "api.model", help=t("click to check API validity")+ " 👉")
        with c2:
            if st.button("📡", key="api"):
                st.toast(t("API Key is valid") if check_api() else t("API Key is invalid"),
                        icon="✅" if check_api() else "❌")
        llm_support_json = st.toggle(t("LLM JSON Format Support"), value=load_key("api.llm_support_json"), help=t("Enable if your LLM supports JSON mode output"))
        if llm_support_json != load_key("api.llm_support_json"):
            update_key("api.llm_support_json", llm_support_json)
            st.rerun()
    with st.expander(t("Subtitles Settings"), expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            langs = {
                "🇺🇸 English": "en",
                "🇨🇳 简体中文": "zh",
                "🇪🇸 Español": "es",
                "🇷🇺 Русский": "ru",
                "🇫🇷 Français": "fr",
                "🇩🇪 Deutsch": "de",
                "🇮🇹 Italiano": "it",
                "🇯🇵 日本語": "ja"
            }
            lang = st.selectbox(
                t("Recog Lang"),
                options=list(langs.keys()),
                index=list(langs.values()).index(load_key("whisper.language"))
            )
            if langs[lang] != load_key("whisper.language"):
                update_key("whisper.language", langs[lang])
                st.rerun()

        runtime = st.selectbox(t("WhisperX Runtime"), options=["elevenlabs", "openai"], index=0 if load_key("whisper.runtime") == "elevenlabs" else 1, help=t("ElevenLabs runtime requires ElevenLabs API key, OpenAI runtime uses OpenAI Whisper API"))
        if runtime != load_key("whisper.runtime"):
            update_key("whisper.runtime", runtime)
            st.rerun()
        if runtime == "elevenlabs":
            config_input(("ElevenLabs API"), "whisper.elevenlabs_api_key")
        elif runtime == "openai":
            config_input(t("OpenAI API Key (Whisper)"), "whisper.openai_api_key", key_suffix="whisper_api")
            config_input(t("OpenAI Base URL"), "whisper.openai_base_url", key_suffix="whisper_url")

        with c2:
            target_language = st.text_input(t("Target Lang"), value=load_key("target_language"), help=t("Input any language in natural language, as long as llm can understand"))
            if target_language != load_key("target_language"):
                update_key("target_language", target_language)
                st.rerun()

        burn_subtitles = st.toggle(t("Burn-in Subtitles"), value=load_key("burn_subtitles"), help=t("Whether to burn subtitles into the video, will increase processing time"))
        if burn_subtitles != load_key("burn_subtitles"):
            update_key("burn_subtitles", burn_subtitles)
            st.rerun()
    with st.expander(t("Dubbing Settings"), expanded=True):
        tts_methods = ["edge_tts", "custom_tts", "openai_tts"]
        current_tts = load_key("tts_method")
        select_tts = st.selectbox(t("TTS Method"), options=tts_methods, index=tts_methods.index(current_tts) if current_tts in tts_methods else 0)
        if select_tts != load_key("tts_method"):
            update_key("tts_method", select_tts)
            st.rerun()

        # sub settings for each tts method
        if select_tts == "edge_tts":
            config_input(t("Edge TTS Voice"), "edge_tts.voice")

        elif select_tts == "openai_tts":
            config_input(t("OpenAI API Key"), "openai_tts.api_key", key_suffix="tts_api")
            config_input(t("OpenAI Base URL"), "openai_tts.base_url", key_suffix="tts_url")

            # Voice selection
            voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            current_voice = load_key("openai_tts.voice") or "alloy"
            selected_voice = st.selectbox(
                t("OpenAI Voice"),
                options=voice_options,
                index=voice_options.index(current_voice) if current_voice in voice_options else 0
            )
            if selected_voice != current_voice:
                update_key("openai_tts.voice", selected_voice)
                st.rerun()

            # Model selection
            model_options = ["tts-1", "tts-1-hd"]
            current_model = load_key("openai_tts.model") or "tts-1"
            selected_model = st.selectbox(
                t("OpenAI Model"),
                options=model_options,
                index=model_options.index(current_model) if current_model in model_options else 0
            )
            if selected_model != current_model:
                update_key("openai_tts.model", selected_model)
                st.rerun()

    # Advanced Settings
    with st.expander(t("Advanced Settings ⚙️"), expanded=False):
        # Use tabs instead of nested expanders
        tab_names = [t("Whisper/ASR"), t("LLM"), t("Subtitle"), t("Video"), t("Audio")]
        tabs = st.tabs(tab_names)

        with tabs[0]:
            # Whisper & ASR settings
            whisper_models = ["large-v3", "large-v3-turbo"]
            current_model = load_key("whisper.model") or "large-v3"
            selected_model = st.selectbox(
                t("Whisper Model"),
                options=whisper_models,
                index=whisper_models.index(current_model) if current_model in whisper_models else 0,
                help=t("Whisper model selection"),
                key="adv_whisper_model"
            )
            if selected_model != current_model:
                update_key("whisper.model", selected_model)
                st.rerun()

            demucs = st.toggle(t("Demucs Vocal Separation"), value=load_key("demucs"), help=t("Use Demucs for vocal separation before transcription"), key="adv_demucs")
            if demucs != load_key("demucs"):
                update_key("demucs", demucs)
                st.rerun()

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
    try:
        resp = ask_gpt("This is a test, response 'message':'success' in json format.", 
                      resp_type="json", log_title='None')
        return resp.get('message') == 'success'
    except Exception:
        return False
    
if __name__ == "__main__":
    check_api()
