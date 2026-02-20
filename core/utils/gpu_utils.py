import platform
import subprocess


def check_gpu_available():
    """
    Check if hardware acceleration encoder is available via ffmpeg

    Returns:
        str or None: GPU encoder name ('h264_nvenc', 'h264_videotoolbox') or None if not available
    """
    try:
        result = subprocess.run(
            ['ffmpeg', '-hide_banner', '-encoders'],
            capture_output=True,
            text=True,
            timeout=10
        )
        encoders = result.stdout
        print(f"[DEBUG] Platform: {platform.system()}")
        print(f"[DEBUG] Encoders contain h264_nvenc: {'h264_nvenc' in encoders}")
        print(f"[DEBUG] Encoders contain h264_videotoolbox: {'h264_videotoolbox' in encoders}")

        # Apple Silicon (M1+) - h264_videotoolbox
        if platform.system() == 'Darwin':
            if 'h264_videotoolbox' in encoders:
                return 'h264_videotoolbox'
            return None

        # NVIDIA GPU (Linux/Windows) - h264_nvenc
        if 'h264_nvenc' in encoders:
            return 'h264_nvenc'

        return None
    except Exception as e:
        print(f"[DEBUG] check_gpu_available exception: {e}")
        return None
