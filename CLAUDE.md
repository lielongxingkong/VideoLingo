# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

VideoLingo is an all-in-one video translation, localization, and dubbing tool that generates Netflix-quality single-line subtitles. Key features:

- YouTube video download via yt-dlp
- Word-level subtitle recognition with WhisperX
- NLP and AI-powered subtitle segmentation
- Custom + AI-generated terminology for coherent translation
- 3-step Translate-Reflect-Adaptation for cinematic quality
- Netflix-standard, single-line subtitles only
- Dubbing with GPT-SoVITS, Azure, OpenAI, and more
- One-click startup and processing in Streamlit

---

## Tech Stack

- **Python 3.12** - Main programming language
- **Streamlit** - Interactive web UI
- **WhisperX** - Word-level ASR with diarization
- **LLMs** - OpenAI, Claude, GPT-4.1, DeepSeek, Gemini, etc.
- **spaCy** - NLP for sentence segmentation
- **FFmpeg** - Video/audio processing
- **PyTorch** - ML model inference
- **Demucs** - Vocal separation

---

## Common Commands

### Installation & Setup

```bash
# Create conda environment
conda create -n videolingo python=3.12 -y
conda activate videolingo

# Install dependencies
python install.py

# Launch the application
streamlit run st.py
```

### Development

- No standard pytest/unittest files found
- Testing is done manually via the Streamlit UI
- Entry point: [st.py](st.py)

---

## Code Architecture

### Processing Pipeline (Sequential)

The core processing follows a numbered sequence in [core/](core/):

1. [core/_1_ytdlp.py](core/_1_ytdlp.py) - YouTube video download
2. [core/_2_asr.py](core/_2_asr.py) - WhisperX transcription
3. [core/_3_1_split_nlp.py](core/_3_1_split_nlp.py) - NLP-based sentence segmentation
4. [core/_3_2_split_meaning.py](core/_3_2_split_meaning.py) - Meaning-based sentence splitting
5. [core/_4_1_summarize.py](core/_4_1_summarize.py) - Content summarization
6. [core/_4_2_translate.py](core/_4_2_translate.py) - Multi-step translation with context
7. [core/_5_split_sub.py](core/_5_split_sub.py) - Subtitle splitting
8. [core/_6_gen_sub.py](core/_6_gen_sub.py) - Subtitle generation and alignment
9. [core/_7_sub_into_vid.py](core/_7_sub_into_vid.py) - Merge subtitles into video
10. [core/_8_1_audio_task.py](core/_8_1_audio_task.py) - Audio task generation
11. [core/_8_2_dub_chunks.py](core/_8_2_dub_chunks.py) - Audio chunking for dubbing
12. [core/_9_refer_audio.py](core/_9_refer_audio.py) - Reference audio extraction
13. [core/_10_gen_audio.py](core/_10_gen_audio.py) - Audio generation (TTS)
14. [core/_11_merge_audio.py](core/_11_merge_audio.py) - Audio merging
15. [core/_12_dub_to_vid.py](core/_12_dub_to_vid.py) - Final dubbing merge

### Key Directories

- [core/utils/](core/utils/) - Utility functions (LLM API, config management, decorators
- [core/st_utils/](core/st_utils/) - Streamlit UI components
- [core/asr_backend/](core/asr_backend/) - ASR engine backends
- [core/tts_backend/](core/tts_backend/) - TTS engine backends
- [translations/](translations/) - Multi-language UI translations
- [batch/](batch/) - Batch processing mode

### Configuration

Main configuration file: [config.yaml](config.yaml)

Key settings:
- API keys and base URL
- Target language
- Whisper model and language
- TTS method (azure_tts, openai_tts, gpt_sovits, fish_tts, edge_tts, etc.)
- Demucs vocal separation
- Subtitle length limits
- Max workers for LLM parallelism

---

## Code Style Guidelines

From [.cursorrules](.cursorrules):

- Use `# ------------` for block comments
- Avoid complex inline comments
- No type definitions in function variables
- Use English comments and print statements

---

## Entry Points

- **Main UI**: [st.py](st.py) - Streamlit interface
- **Core Pipeline**: Sequential `core/_*.py` modules
- **LLM API**: [core/utils/ask_gpt.py](core/utils/ask_gpt.py)
- **Prompts**: [core/prompts.py](core/prompts.py)
