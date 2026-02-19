#!/usr/bin/env python
"""
Simple installation script for VideoLingo.
For full installation instructions, see README.md.
"""
import sys
import subprocess

def main():
    print("Installing VideoLingo...")
    print()
    print("Please make sure you have the following system dependencies installed:")
    print("  - FFmpeg")
    print("  - For macOS: brew install ffmpeg")
    print("  - For Ubuntu/Debian: sudo apt install ffmpeg")
    print()

    # Install in editable mode
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])

    print()
    print("✓ Installation completed!")
    print()
    print("To start the application:")
    print("  streamlit run st.py")

if __name__ == "__main__":
    main()
