import os
import json
import time
import tempfile
import librosa
import soundfile as sf
from openai import OpenAI
from rich import print as rprint
from core.utils.config_utils import load_key, update_key


# ----------------------------
# OpenAI format to whisper format
# ----------------------------

def openai2whisper(openai_words, start_offset=0, word_level_timestamp=True):
    """
    Convert OpenAI word-level timestamps to Whisper format
    """
    if not openai_words:
        return {"segments": []}

    segments = []
    current_segment = None
    SPLIT_GAP = 1.0  # Gap threshold to split segments

    for i, word_info in enumerate(openai_words):
        # Adjust timestamps with offset
        word_start = word_info.get("start", 0) + start_offset
        word_end = word_info.get("end", 0) + start_offset
        word_text = word_info.get("word", "")

        if current_segment is None:
            # Start new segment
            current_segment = {
                "text": word_text,
                "start": word_start,
                "end": word_end,
                "speaker_id": 0,  # OpenAI doesn't do diarization by default
                "words": []
            }
            if word_level_timestamp:
                current_segment["words"].append({
                    "text": word_text,
                    "start": word_start,
                    "end": word_end
                })
        else:
            # Check if we need to split
            prev_end = current_segment["end"]
            gap = word_start - prev_end

            if gap > SPLIT_GAP:
                # Finalize current segment
                current_segment["text"] = current_segment["text"].strip()
                if not word_level_timestamp:
                    current_segment.pop("words")
                segments.append(current_segment)

                # Start new segment
                current_segment = {
                    "text": word_text,
                    "start": word_start,
                    "end": word_end,
                    "speaker_id": 0,
                    "words": []
                }
                if word_level_timestamp:
                    current_segment["words"].append({
                        "text": word_text,
                        "start": word_start,
                        "end": word_end
                    })
            else:
                # Continue current segment
                current_segment["text"] += " " + word_text
                current_segment["end"] = word_end
                if word_level_timestamp:
                    current_segment["words"].append({
                        "text": word_text,
                        "start": word_start,
                        "end": word_end
                    })

    # Add the last segment
    if current_segment is not None:
        current_segment["text"] = current_segment["text"].strip()
        if not word_level_timestamp:
            current_segment.pop("words")
        segments.append(current_segment)

    return {"segments": segments}


def transcribe_audio_openai(raw_audio_path, vocal_audio_path, start=None, end=None):
    """
    Transcribe audio using OpenAI Whisper API
    """
    rprint(f"[cyan]🎤 Processing audio transcription with OpenAI, file path: {vocal_audio_path}[/cyan]")
    LOG_FILE = f"output/log/openai_transcribe_{start}_{end}.json"
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    # Load audio and process start/end parameters
    y, sr = librosa.load(vocal_audio_path, sr=16000)
    audio_duration = len(y) / sr

    if start is None or end is None:
        start = 0
        end = audio_duration

    # Slice audio based on start/end
    start_sample = int(start * sr)
    end_sample = int(end * sr)
    y_slice = y[start_sample:end_sample]

    # Create temporary file for the sliced audio
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
        temp_filepath = temp_file.name
        sf.write(temp_filepath, y_slice, sr, format='MP3')

    try:
        # Get API configuration
        api_key = load_key("whisper.openai_api_key") or load_key("api.key")
        base_url = load_key("whisper.openai_base_url") or load_key("api.base_url")

        if not api_key:
            raise ValueError("OpenAI API key is not set. Please set either whisper.openai_api_key or api.key in config.yaml")

        # Handle base URL
        if not base_url or base_url == "":
            base_url = "https://api.openai.com/v1"
        elif 'v1' not in base_url:
            base_url = base_url.strip('/') + '/v1'

        client = OpenAI(api_key=api_key, base_url=base_url)
        language = load_key("whisper.language")

        with open(temp_filepath, 'rb') as audio_file:
            start_time = time.time()

            # Call OpenAI Whisper API with word-level timestamps
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )

            rprint(f"[yellow]API request sent, processing completed[/yellow]")

            # Convert to dict
            transcript_dict = transcript.model_dump()

            # Save detected language
            if 'language' in transcript_dict:
                detected_lang = transcript_dict['language']
                update_key("whisper.detected_language", detected_lang)

            # Extract words
            words = transcript_dict.get('words', [])

            # Adjust timestamps for all words by adding the start time
            if start is not None and words:
                for word in words:
                    if 'start' in word:
                        word['start'] += start
                    if 'end' in word:
                        word['end'] += start

            rprint(f"[green]✓ Transcription completed in {time.time() - start_time:.2f} seconds[/green]")

            # Convert OpenAI format to Whisper format
            parsed_result = openai2whisper(words, start_offset=0, word_level_timestamp=True)

            os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(parsed_result, f, indent=4, ensure_ascii=False)

            return parsed_result

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)


if __name__ == "__main__":
    file_path = input("Enter local audio file path: ")
    language = input("Enter language code for transcription (en or zh or other...): ")
    result = transcribe_audio_openai(file_path, file_path)
    print(result)

    # Save result to file
    with open("output/transcript_openai.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
