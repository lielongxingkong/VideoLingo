from core.utils import *
from core.asr_backend.audio_preprocess import process_transcription, convert_video_to_audio, split_audio, save_results
from core._1_ytdlp import find_video_files
from core.utils.models import *
from core.utils.config_utils import load_key

@check_file_exists(_2_CLEANED_CHUNKS)
def transcribe():
    # 1. video to audio
    video_file = find_video_files()
    convert_video_to_audio(video_file)

    # 2. Demucs vocal separation (optional)
    if load_key("demucs.enabled"):
        from core.asr_backend.demucs_vl import separate_vocal_audio
        model = load_key("demucs.model") or "htdemucs"
        rprint("[cyan]🎵 Using Demucs for vocal separation...[/cyan]")
        separate_vocal_audio(_RAW_AUDIO_FILE, model)
        vocal_audio = _VOCAL_AUDIO_FILE
    else:
        vocal_audio = _RAW_AUDIO_FILE

    # 3. Extract audio
    segments = split_audio(_RAW_AUDIO_FILE)

    # 4. Transcribe audio by clips
    all_results = []
    runtime = load_key("asr.runtime")
    if runtime == "elevenlabs":
        from core.asr_backend.elevenlabs_asr import transcribe_audio_elevenlabs as ts
        rprint("[cyan]🎤 Transcribing audio with ElevenLabs API...[/cyan]")
    elif runtime == "openai":
        from core.asr_backend.openai_asr import transcribe_audio_openai as ts
        rprint("[cyan]🎤 Transcribing audio with OpenAI Whisper API...[/cyan]")
    else:
        # Default to elevenlabs if runtime is invalid
        from core.asr_backend.elevenlabs_asr import transcribe_audio_elevenlabs as ts
        rprint("[cyan]🎤 Transcribing audio with ElevenLabs API...[/cyan]")

    for start, end in segments:
        result = ts(_RAW_AUDIO_FILE, vocal_audio, start, end)
        all_results.append(result)

    # 5. Combine results
    combined_result = {'segments': []}
    for result in all_results:
        combined_result['segments'].extend(result['segments'])

    # 6. Process df
    df = process_transcription(combined_result)
    save_results(df)

if __name__ == "__main__":
    transcribe()