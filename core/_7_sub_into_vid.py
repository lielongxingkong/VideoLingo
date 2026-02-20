import os, time
import ffmpeg
from core._1_ytdlp import find_video_files
from core.utils import *

# Check if we're in Streamlit environment
try:
    import streamlit as st
    IN_STREAMLIT = True
except ImportError:
    IN_STREAMLIT = False


def show_warning(message):
    """Show warning message in both console and Streamlit UI if available"""
    rprint(f"[bold yellow]{message}[/bold yellow]")
    if IN_STREAMLIT:
        st.warning(message)


def check_gpu_available():
    """Check if h264_nvenc encoder is available via ffmpeg"""
    try:
        import subprocess
        result = subprocess.run(
            ['ffmpeg', '-hide_banner', '-encoders'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return 'h264_nvenc' in result.stdout
    except:
        return False

OUTPUT_DIR = "output"
OUTPUT_VIDEO = f"{OUTPUT_DIR}/output_sub.mp4"
SRC_SRT = f"{OUTPUT_DIR}/src.srt"
TRANS_SRT = f"{OUTPUT_DIR}/trans.srt"

SRC_FONT_SIZE = 15
TRANS_FONT_SIZE = 17
SRC_FONT_COLOR = "white"
TRANS_FONT_COLOR = "yellow"


def merge_subtitles_to_video():
    video_file = find_video_files()
    os.makedirs(os.path.dirname(OUTPUT_VIDEO), exist_ok=True)

    if not load_key("burn_subtitles"):
        import cv2
        import numpy as np
        rprint("[bold yellow]Warning: A 0-second black video will be generated as a placeholder as subtitles are not burned in.[/bold yellow]")
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, 1, (1920, 1080))
        out.write(frame)
        out.release()
        rprint("[bold green]Placeholder video has been generated.[/bold green]")
        return

    if not os.path.exists(SRC_SRT) or not os.path.exists(TRANS_SRT):
        rprint("Subtitle files not found in the 'output' directory.")
        exit(1)

    rprint("🎬 Start merging subtitles to video...")
    start_time = time.time()

    # Use ffmpeg-python to build the command
    stream = ffmpeg.input(video_file)

    # Get video info to check resolution
    probe = ffmpeg.probe(video_file)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_info['width'])
    height = int(video_info['height'])
    rprint(f"[bold green]Video resolution: {width}x{height}[/bold green]")

    # Build filter chain: scale + src_subtitle + trans_subtitle
    # FFmpeg subtitles filter with force_style
    src_style = f"FontSize={SRC_FONT_SIZE},PrimaryColour=&HFFFFFF,OutlineColour=&H000000"
    trans_style = f"FontSize={TRANS_FONT_SIZE},PrimaryColour=&H00FFFF,OutlineColour=&H000000"

    # Chain subtitles filters using filter_complex
    filter_str = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
        f"subtitles={SRC_SRT}:force_style='{src_style}',"
        f"subtitles={TRANS_SRT}:force_style='{trans_style}'"
    )

    ffmpeg_gpu = load_key("ffmpeg_gpu")
    gpu_success = False

    # Try GPU first if enabled and available
    if ffmpeg_gpu:
        # First check if GPU is actually available
        if check_gpu_available():
            try:
                rprint("[bold green]Using GPU acceleration...[/bold green]")
                gpu_stream = ffmpeg.input(video_file)
                gpu_stream = ffmpeg.output(
                    gpu_stream,
                    OUTPUT_VIDEO,
                    vf=filter_str,
                    vcodec='h264_nvenc',
                    acodec='aac',
                    y=None
                )
                ffmpeg.run(gpu_stream, overwrite_output=True, quiet=True)
                gpu_success = True
            except ffmpeg.Error:
                # Any GPU error falls back to CPU
                show_warning("⚠️ GPU acceleration failed, falling back to CPU...")
        else:
            show_warning("⚠️ GPU acceleration not available, falling back to CPU...")

    # Use CPU if GPU failed or not enabled
    if not gpu_success:
        cpu_stream = ffmpeg.input(video_file)
        cpu_stream = ffmpeg.output(
            cpu_stream,
            OUTPUT_VIDEO,
            vf=filter_str,
            vcodec='libx264',
            acodec='aac',
            y=None
        )
        ffmpeg.run(cpu_stream, overwrite_output=True, quiet=True)

    rprint(f"\n✅ Done! Time taken: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    merge_subtitles_to_video()
