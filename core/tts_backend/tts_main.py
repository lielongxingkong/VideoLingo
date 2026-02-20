import os
import re
import struct
import wave
from pydub import AudioSegment

from core.asr_backend.audio_preprocess import get_audio_duration
from core.tts_backend.edge_tts import edge_tts
from core.tts_backend.openai_tts import openai_tts_for_videolingo
from core.prompts import get_correct_text_prompt
from core.utils import *


def create_silent_wav(file_path, duration_ms=100, sample_rate=16000, num_channels=1, sample_width=2):
    """Create a valid silent WAV file"""
    num_samples = int(sample_rate * duration_ms / 1000)
    with wave.open(file_path, 'wb') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        # Write silent samples (all zeros)
        silence_data = b'\x00\x00' * num_samples
        wav_file.writeframes(silence_data)


def clean_text_for_tts(text):
    """Remove problematic characters for TTS"""
    chars_to_remove = ['&', '®', '™', '©']
    for char in chars_to_remove:
        text = text.replace(char, '')
    return text.strip()


def tts_main(text, save_as, number, task_df):
    text = clean_text_for_tts(text)
    # Check if text is empty or single character, single character voiceovers are prone to bugs
    cleaned_text = re.sub(r'[^\w\s]', '', text).strip()
    if not cleaned_text or len(cleaned_text) <= 1:
        # Create valid silent WAV file
        os.makedirs(os.path.dirname(save_as), exist_ok=True)
        create_silent_wav(save_as, duration_ms=100)
        rprint(f"Created silent audio for empty/single-char text: {save_as}")
        return
    
    # Skip if file exists
    if os.path.exists(save_as):
        return
    
    print(f"Generating <{text}...>")
    TTS_METHOD = load_key("tts_method")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if attempt >= max_retries - 1:
                print("Asking GPT to correct text...")
                correct_text = ask_gpt(get_correct_text_prompt(text),resp_type="json", log_title='tts_correct_text')
                text = correct_text['text']
            if TTS_METHOD == 'edge_tts':
                edge_tts(text, save_as)
            elif TTS_METHOD == 'openai_tts':
                openai_tts_for_videolingo(text, save_as)

            # Check generated audio duration
            duration = get_audio_duration(save_as)
            if duration > 0:
                break
            else:
                if os.path.exists(save_as):
                    os.remove(save_as)
                if attempt == max_retries - 1:
                    print(f"Warning: Generated audio duration is 0 for text: {text}")
                    # Create silent audio file
                    os.makedirs(os.path.dirname(save_as), exist_ok=True)
                    create_silent_wav(save_as, duration_ms=100)
                    return
                print(f"Attempt {attempt + 1} failed, retrying...")
        except Exception as e:
            if attempt == max_retries - 1:
                raise Exception(f"Failed to generate audio after {max_retries} attempts: {str(e)}")
            print(f"Attempt {attempt + 1} failed, retrying...")