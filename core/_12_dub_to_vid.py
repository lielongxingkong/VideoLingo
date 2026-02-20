import os
import platform
import ffmpeg

import cv2
import numpy as np
from rich.console import Console

from core._1_ytdlp import find_video_files
from core.asr_backend.audio_preprocess import normalize_audio_volume
from core.utils import *
from core.utils.models import *
from core.utils.gpu_utils import check_gpu_available

console = Console()

# Check if we're in Streamlit environment
try:
    import streamlit as st
    IN_STREAMLIT = True
except ImportError:
    IN_STREAMLIT = False


def show_warning(message):
    """Show warning message in both console and Streamlit UI if available"""
    console.print(f"[bold yellow]{message}[/bold yellow]")
    if IN_STREAMLIT:
        st.warning(message)

DUB_VIDEO = "output/output_dub.mp4"
DUB_SUB_FILE = 'output/dub.srt'
DUB_AUDIO = 'output/dub.mp3'

TRANS_FONT_SIZE = 17
TRANS_FONT_NAME = 'Arial'
if platform.system() == 'Linux':
    TRANS_FONT_NAME = 'NotoSansCJK-Regular'
if platform.system() == 'Darwin':
    TRANS_FONT_NAME = 'Arial Unicode MS'

TRANS_FONT_COLOR = '&H00FFFF'
TRANS_OUTLINE_COLOR = '&H000000'
TRANS_OUTLINE_WIDTH = 1
TRANS_BACK_COLOR = '&H33000000'


def merge_with_gpu(input_video, background_file, normalized_dub_audio,
                   filter_str, filter_complex, DUB_VIDEO, TARGET_WIDTH, TARGET_HEIGHT, burn_subtitles, gpu_encoder):
    """Try to merge with GPU acceleration"""
    try:
        if burn_subtitles:
            if background_file:
                stream = ffmpeg.input(input_video)
                bg = ffmpeg.input(background_file)
                dub = ffmpeg.input(normalized_dub_audio)
                output_kwargs = {
                    'y': None,
                    'c:v': gpu_encoder,
                    'c:a': 'aac',
                    'b:a': '96k',
                }
                stream = ffmpeg.output(
                    stream, bg, dub,
                    DUB_VIDEO,
                    filter_complex=filter_complex,
                    **output_kwargs
                )
            else:
                stream = ffmpeg.input(input_video)
                dub = ffmpeg.input(normalized_dub_audio)
                output_kwargs = {
                    'y': None,
                    'vf': filter_str,
                    'c:v': gpu_encoder,
                    'c:a': 'aac',
                    'b:a': '96k',
                }
                stream = ffmpeg.output(
                    stream, dub,
                    DUB_VIDEO,
                    **output_kwargs
                )
        else:
            if background_file:
                stream = ffmpeg.input(input_video)
                bg = ffmpeg.input(background_file)
                dub = ffmpeg.input(normalized_dub_audio)
                output_kwargs = {
                    'y': None,
                    'c:v': gpu_encoder,
                    'c:a': 'aac',
                    'b:a': '96k',
                }
                stream = ffmpeg.output(
                    stream, bg, dub,
                    DUB_VIDEO,
                    filter_complex=filter_complex,
                    **output_kwargs
                )
            else:
                stream = ffmpeg.input(input_video)
                dub = ffmpeg.input(normalized_dub_audio)
                output_kwargs = {
                    'y': None,
                    'c:v': gpu_encoder,
                    'c:a': 'aac',
                    'b:a': '96k',
                }
                stream = ffmpeg.output(
                    stream, dub,
                    DUB_VIDEO,
                    **output_kwargs
                )

        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        return True
    except ffmpeg.Error:
        # Any GPU error falls back to CPU
        return False


def merge_with_cpu(input_video, background_file, normalized_dub_audio,
                   filter_str, filter_complex, DUB_VIDEO, TARGET_WIDTH, TARGET_HEIGHT, burn_subtitles):
    """Merge with CPU"""
    if burn_subtitles:
        if background_file:
            stream = ffmpeg.input(input_video)
            bg = ffmpeg.input(background_file)
            dub = ffmpeg.input(normalized_dub_audio)
            output_kwargs = {
                'y': None,
                'c:v': 'libx264',
                'c:a': 'aac',
                'b:a': '96k',
            }
            stream = ffmpeg.output(
                stream, bg, dub,
                DUB_VIDEO,
                filter_complex=filter_complex,
                **output_kwargs
            )
        else:
            stream = ffmpeg.input(input_video)
            dub = ffmpeg.input(normalized_dub_audio)
            output_kwargs = {
                'y': None,
                'vf': filter_str,
                'c:v': 'libx264',
                'c:a': 'aac',
                'b:a': '96k',
            }
            stream = ffmpeg.output(
                stream, dub,
                DUB_VIDEO,
                **output_kwargs
            )
    else:
        if background_file:
            stream = ffmpeg.input(input_video)
            bg = ffmpeg.input(background_file)
            dub = ffmpeg.input(normalized_dub_audio)
            output_kwargs = {
                'y': None,
                'c:v': 'libx264',
                'c:a': 'aac',
                'b:a': '96k',
            }
            stream = ffmpeg.output(
                stream, bg, dub,
                DUB_VIDEO,
                filter_complex=filter_complex,
                **output_kwargs
            )
        else:
            stream = ffmpeg.input(input_video)
            dub = ffmpeg.input(normalized_dub_audio)
            output_kwargs = {
                'y': None,
                'c:v': 'libx264',
                'c:a': 'aac',
                'b:a': '96k',
            }
            stream = ffmpeg.output(
                stream, dub,
                DUB_VIDEO,
                **output_kwargs
            )

    ffmpeg.run(stream, overwrite_output=True, quiet=True)


def merge_video_audio():
    """Merge video and audio"""
    VIDEO_FILE = find_video_files()

    if not load_key("burn_subtitles"):
        rprint("[bold yellow]Warning: A 0-second black video will be generated as a placeholder as subtitles are not burned in.[/bold yellow]")

        # Create a black frame
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(DUB_VIDEO, fourcc, 1, (1920, 1080))
        out.write(frame)
        out.release()

        rprint("[bold green]Placeholder video has been generated.[/bold green]")
        return

    # Normalize dub audio
    normalized_dub_audio = 'output/normalized_dub.wav'
    normalize_audio_volume(DUB_AUDIO, normalized_dub_audio)

    # Check if background audio exists (from Demucs vocal separation)
    background_file = _BACKGROUND_AUDIO_FILE if os.path.exists(_BACKGROUND_AUDIO_FILE) else None
    if background_file:
        rprint("[cyan]🎵 Background audio detected, will mix with dub audio[/cyan]")

    # Merge video and audio with translated subtitles
    video = cv2.VideoCapture(VIDEO_FILE)
    TARGET_WIDTH = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    TARGET_HEIGHT = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video.release()
    rprint(f"[bold green]Video resolution: {TARGET_WIDTH}x{TARGET_HEIGHT}[/bold green]")

    # Check if burn_subtitles is enabled
    burn_subtitles = load_key("burn_subtitles")
    ffmpeg_gpu = load_key("ffmpeg_gpu")

    # Build filter strings first
    if burn_subtitles:
        if background_file:
            filter_str = None
            filter_complex = (
                f'[0:v]scale={TARGET_WIDTH}:{TARGET_HEIGHT}:force_original_aspect_ratio=decrease,'
                f'pad={TARGET_WIDTH}:{TARGET_HEIGHT}:(ow-iw)/2:(oh-ih)/2,'
                f"subtitles=filename={DUB_SUB_FILE}[v];"
                f'[1:a][2:a]amix=inputs=2:duration=first:dropout_transition=3[a]'
            )
        else:
            filter_str = (
                f'[0:v]scale={TARGET_WIDTH}:{TARGET_HEIGHT}:force_original_aspect_ratio=decrease,'
                f'pad={TARGET_WIDTH}:{TARGET_HEIGHT}:(ow-iw)/2:(oh-ih)/2,'
                f"subtitles=filename={DUB_SUB_FILE}[v]"
            )
            filter_complex = None
    else:
        if background_file:
            filter_str = None
            filter_complex = (
                f'[0:v]scale={TARGET_WIDTH}:{TARGET_HEIGHT}:force_original_aspect_ratio=decrease,'
                f'pad={TARGET_WIDTH}:{TARGET_HEIGHT}:(ow-iw)/2:(oh-ih)/2,'
                f'setsar=1[v];'
                f'[1:a][2:a]amix=inputs=2:duration=first:dropout_transition=3[a]'
            )
        else:
            filter_str = None
            filter_complex = None

    # Try GPU first if enabled and available
    gpu_success = False
    if ffmpeg_gpu:
        gpu_encoder = check_gpu_available()
        if gpu_encoder:
            console.print(f"[bold green]Using GPU acceleration ({gpu_encoder})...[/bold green]")
            gpu_success = merge_with_gpu(
                VIDEO_FILE, background_file, normalized_dub_audio,
                filter_str, filter_complex, DUB_VIDEO,
                TARGET_WIDTH, TARGET_HEIGHT, burn_subtitles, gpu_encoder
            )
            if not gpu_success:
                show_warning("⚠️ GPU acceleration failed, falling back to CPU...")
        else:
            show_warning("⚠️ GPU acceleration not available, falling back to CPU...")

    # Use CPU if GPU failed or not enabled
    if not gpu_success:
        merge_with_cpu(
            VIDEO_FILE, background_file, normalized_dub_audio,
            filter_str, filter_complex, DUB_VIDEO,
            TARGET_WIDTH, TARGET_HEIGHT, burn_subtitles
        )

    rprint(f"[bold green]Video and audio successfully merged into {DUB_VIDEO}[/bold green]")


if __name__ == '__main__':
    merge_video_audio()
