import streamlit as st
import os, sys

# SET PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
os.environ['PATH'] += os.pathsep + current_dir
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="VideoLingo", page_icon="docs/logo.svg")

# Lazy import utilities
from core.st_utils.imports_and_utils import (
    download_subtitle_zip_button,
    button_style,
    give_star_button
)
from core.st_utils.sidebar_setting import page_setting
from core.st_utils.download_video_section import download_video_section
from translations.translations import translate as t
from core.utils.config_utils import load_key

# Lazy load core modules only when needed
def get_core_modules():
    from core import (
        _2_asr,
        _3_1_split_nlp,
        _3_2_split_meaning,
        _4_1_summarize,
        _4_2_translate,
        _5_split_sub,
        _6_gen_sub,
        _7_sub_into_vid,
        _8_1_audio_task,
        _8_2_dub_chunks,
        _9_refer_audio,
        _10_gen_audio,
        _11_merge_audio,
        _12_dub_to_vid
    )
    from core.utils.onekeycleanup import cleanup
    from core.utils.delete_retry_dubbing import delete_dubbing_files
    return locals()

SUB_VIDEO = "output/output_sub.mp4"
DUB_VIDEO = "output/output_dub.mp4"

def text_processing_section():
    st.header(t("b. Translate and Generate Subtitles"))
    with st.container(border=True):
        st.markdown(f"""
        <p style='font-size: 20px;'>
        {t("This stage includes the following steps:")}
        <p style='font-size: 20px;'>
            1. {t("WhisperX word-level transcription")}<br>
            2. {t("Sentence segmentation using NLP and LLM")}<br>
            3. {t("Summarization and multi-step translation")}<br>
            4. {t("Cutting and aligning long subtitles")}<br>
            5. {t("Generating timeline and subtitles")}<br>
            6. {t("Merging subtitles into the video")}
        """, unsafe_allow_html=True)

        if not os.path.exists(SUB_VIDEO):
            if st.button(t("Start Processing Subtitles"), key="text_processing_button"):
                process_text()
                st.rerun()
        else:
            if load_key("burn_subtitles"):
                st.video(SUB_VIDEO)
            download_subtitle_zip_button(text=t("Download All Srt Files"))

            if st.button(t("Archive to 'history'"), key="cleanup_in_text_processing"):
                mods = get_core_modules()
                mods['cleanup']()
                st.rerun()
            return True

def process_text():
    mods = get_core_modules()
    with st.spinner(t("Using Whisper for transcription...")):
        mods['_2_asr'].transcribe()
    with st.spinner(t("Splitting long sentences...")):
        mods['_3_1_split_nlp'].split_by_spacy()
        mods['_3_2_split_meaning'].split_sentences_by_meaning()
    with st.spinner(t("Summarizing and translating...")):
        mods['_4_1_summarize'].get_summary()
        if load_key("pause_before_translate"):
            input(t("⚠️ PAUSE_BEFORE_TRANSLATE. Go to `output/log/terminology.json` to edit terminology. Then press ENTER to continue..."))
        mods['_4_2_translate'].translate_all()
    with st.spinner(t("Processing and aligning subtitles...")):
        mods['_5_split_sub'].split_for_sub_main()
        mods['_6_gen_sub'].align_timestamp_main()
    with st.spinner(t("Merging subtitles to video...")):
        mods['_7_sub_into_vid'].merge_subtitles_to_video()

    st.success(t("Subtitle processing complete! 🎉"))
    st.balloons()

def audio_processing_section():
    st.header(t("c. Dubbing"))
    with st.container(border=True):
        st.markdown(f"""
        <p style='font-size: 20px;'>
        {t("This stage includes the following steps:")}
        <p style='font-size: 20px;'>
            1. {t("Generate audio tasks and chunks")}<br>
            2. {t("Extract reference audio")}<br>
            3. {t("Generate and merge audio files")}<br>
            4. {t("Merge final audio into video")}
        """, unsafe_allow_html=True)
        if not os.path.exists(DUB_VIDEO):
            if st.button(t("Start Audio Processing"), key="audio_processing_button"):
                process_audio()
                st.rerun()
        else:
            st.success(t("Audio processing is complete! You can check the audio files in the `output` folder."))
            if load_key("burn_subtitles"):
                st.video(DUB_VIDEO)
            mods = get_core_modules()
            if st.button(t("Delete dubbing files"), key="delete_dubbing_files"):
                mods['delete_dubbing_files']()
                st.rerun()
            if st.button(t("Archive to 'history'"), key="cleanup_in_audio_processing"):
                mods['cleanup']()
                st.rerun()

def process_audio():
    mods = get_core_modules()
    with st.spinner(t("Generate audio tasks")):
        mods['_8_1_audio_task'].gen_audio_task_main()
        mods['_8_2_dub_chunks'].gen_dub_chunks()
    with st.spinner(t("Extract refer audio")):
        mods['_9_refer_audio'].extract_refer_audio_main()
    with st.spinner(t("Generate all audio")):
        mods['_10_gen_audio'].gen_audio()
    with st.spinner(t("Merge full audio")):
        mods['_11_merge_audio'].merge_full_audio()
    with st.spinner(t("Merge dubbing to the video")):
        mods['_12_dub_to_vid'].merge_video_audio()

    st.success(t("Audio processing complete! 🎇"))
    st.balloons()

def main():
    logo_col, _ = st.columns([1,1])
    with logo_col:
        st.image("docs/logo.png", use_column_width=True)
    st.markdown(button_style, unsafe_allow_html=True)
    welcome_text = t("Hello, welcome to VideoLingo. If you encounter any issues, feel free to get instant answers with our Free QA Agent <a href=\"https://share.fastgpt.in/chat/share?shareId=066w11n3r9aq6879r4z0v9rh\" target=\"_blank\">here</a>! You can also try out our SaaS website at <a href=\"https://videolingo.io\" target=\"_blank\">videolingo.io</a> for free!")
    st.markdown(f"<p style='font-size: 20px; color: #808080;'>{welcome_text}</p>", unsafe_allow_html=True)
    # add settings
    with st.sidebar:
        page_setting()
        st.markdown(give_star_button, unsafe_allow_html=True)
    download_video_section()
    text_processing_section()
    audio_processing_section()

if __name__ == "__main__":
    main()
