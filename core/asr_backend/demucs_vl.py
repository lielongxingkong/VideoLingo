# -*- coding: utf-8 -*-
"""
Demucs vocal separation module
Separates vocals from background music using htdemucs model
"""
import os
from pathlib import Path
import torch

from core.utils import rprint
from core.paths import Paths


def _patch_torchaudio_save():
    """Patch torchaudio.save to use soundfile backend instead of torchcodec."""
    import torchaudio as ta
    import torch

    original_save = ta.save

    def patched_save(filepath, src, sample_rate, **kwargs):
        """Patched save that uses soundfile backend."""
        # Convert tensor to numpy
        if isinstance(src, torch.Tensor):
            src = src.cpu().numpy()
        # Handle multi-channel: soundfile expects (samples, channels)
        if src.ndim == 1:
            src = src.reshape(-1, 1)
        elif src.shape[0] < src.shape[1]:
            src = src.T

        # Filter out kwargs that soundfile doesn't support
        unsupported = ['encoding', 'bits_per_sample', 'format', 'preset', 'bitrate']
        sf_kwargs = {k: v for k, v in kwargs.items() if k not in unsupported}

        # Use soundfile directly
        import soundfile as sf
        sf.write(filepath, src, sample_rate, **sf_kwargs)

    ta.save = patched_save


def separate_vocal_audio(audio_file: str, model_name: str = "htdemucs"):
    """
    Separate vocals from background audio using Demucs

    Args:
        audio_file: Path to the input audio file
        model_name: Demucs model to use (default: htdemucs)
    """
    rprint("[cyan]🎵 Separating vocals with Demucs...[/cyan]")

    # Patch torchaudio.save to avoid torchcodec dependency
    _patch_torchaudio_save()

    # Import demucs
    try:
        from demucs import separate
    except ImportError as e:
        rprint("[red]Error: demucs not installed. Run: pip install demucs[/red]")
        raise
    except Exception as e:
        rprint(f"[red]Error loading demucs: {e}[/red]")
        rprint("[yellow]Try: pip uninstall torchcodec && brew reinstall ffmpeg-full[/yellow]")
        raise

    # Get output directory
    audio_dir = Paths.audio_dir()

    # Determine device: cuda > mps > cpu
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    rprint(f"[cyan]Using device: {device}[/cyan]")

    # Run separation
    # Demucs creates output in: audio_dir/model_name/filename/
    separate.main([
        "--out",
        str(audio_dir),
        "--device",
        device,
        "--name",
        model_name,
        audio_file
    ])

    # Find the output files
    # Demucs creates: audio_dir/htdemucs/filename/vocals.wav, other.wav, etc.
    model_out_dir = audio_dir / model_name / Path(audio_file).stem

    vocal_path = Paths.vocal_audio()
    background_path = Paths.background_audio()

    # Demucs outputs: vocals.wav, no_vocals.wav (for htdemucs)
    demucs_vocal = model_out_dir / "vocals.wav"
    demucs_background = model_out_dir / "other.wav"

    # Copy to our expected locations
    import shutil as sh
    if demucs_vocal.exists():
        sh.copy(demucs_vocal, vocal_path)
        rprint(f"[green]✓ Saved vocal audio to {vocal_path}[/green]")
    else:
        rprint(f"[yellow]Warning: Demucs did not produce vocals.mp3 in expected location[/yellow]")

    if demucs_background.exists():
        sh.copy(demucs_background, background_path)
        rprint(f"[green]✓ Saved background audio to {background_path}[/green]")
    else:
        rprint(f"[yellow]Warning: Demucs did not produce no_vocals.mp3 in expected location[/yellow]")


if __name__ == "__main__":
    # Test
    test_file = str(Paths.raw_audio())
    if os.path.exists(test_file):
        separate_vocal_audio(test_file)
    else:
        print(f"Test file not found: {test_file}")
