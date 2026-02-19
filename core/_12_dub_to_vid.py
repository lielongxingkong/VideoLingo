import platform
import subprocess

import cv2
import numpy as np
from rich.console import Console

from core._1_ytdlp import find_video_files
from core.asr_backend.audio_preprocess import normalize_audio_volume
from core.utils import *
from core.utils.models import *

console = Console()

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

    # Merge video and audio with translated subtitles
    video = cv2.VideoCapture(VIDEO_FILE)
    TARGET_WIDTH = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    TARGET_HEIGHT = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video.release()
    rprint(f"[bold green]Video resolution: {TARGET_WIDTH}x{TARGET_HEIGHT}[/bold green]")

    # Check if burn_subtitles is enabled
    burn_subtitles = load_key("burn_subtitles")

    if burn_subtitles:
        # Try to use subtitles filter (requires libass support in FFmpeg)
        cmd = [
            'ffmpeg', '-y', '-i', VIDEO_FILE, '-i', normalized_dub_audio,
            '-filter_complex',
            f'[0:v]scale={TARGET_WIDTH}:{TARGET_HEIGHT}:force_original_aspect_ratio=decrease,'
            f'pad={TARGET_WIDTH}:{TARGET_HEIGHT}:(ow-iw)/2:(oh-ih)/2,'
            f"subtitles=filename={DUB_SUB_FILE}[v]"
        ]

        if load_key("ffmpeg_gpu"):
            rprint("[bold green]Using GPU acceleration...[/bold green]")
            cmd.extend(['-map', '[v]', '-map', '1:a', '-c:v', 'h264_nvenc'])
        else:
            cmd.extend(['-map', '[v]', '-map', '1:a'])

        cmd.extend(['-c:a', 'aac', '-b:a', '96k', DUB_VIDEO])

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Check if subtitles filter is available
        if 'No such filter' in result.stderr or 'Filter not found' in result.stderr:
            rprint("[yellow]⚠️ FFmpeg does not support 'subtitles' filter (missing libass). Skipping subtitle burning...[/yellow]")
            burn_subtitles = False
        else:
            if result.returncode != 0:
                rprint(f"[yellow]⚠️ Subtitle burning failed, falling back to no subtitles...[/yellow]")
                rprint(f"[yellow]Error: {result.stderr[:200]}[/yellow]")
                burn_subtitles = False
            else:
                rprint(f"[bold green]Video and audio successfully merged into {DUB_VIDEO}[/bold green]")
                return

    # Fallback: merge without subtitles
    if not burn_subtitles:
        cmd = [
            'ffmpeg', '-y', '-i', VIDEO_FILE, '-i', normalized_dub_audio,
        ]

        if load_key("ffmpeg_gpu"):
            rprint("[bold green]Using GPU acceleration...[/bold green]")
            cmd.extend(['-map', '0:v', '-map', '1:a', '-c:v', 'h264_nvenc'])
        else:
            cmd.extend(['-map', '0:v', '-map', '1:a'])

        cmd.extend(['-c:a', 'aac', '-b:a', '96k', DUB_VIDEO])

        subprocess.run(cmd)
        rprint(f"[bold green]Video and audio successfully merged into {DUB_VIDEO}[/bold green]")

if __name__ == '__main__':
    merge_video_audio()
