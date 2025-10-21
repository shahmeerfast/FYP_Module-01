#!/usr/bin/env python3
"""
Whisper Demo Script
===================

This script demonstrates how to use OpenAI's Whisper model to transcribe audio files.
It loads the "small" model and transcribes a sample audio file.

Requirements:
- Audio file named 'sample.wav' in the same directory
- Whisper library installed
- FFmpeg installed on system (for audio processing)
"""

import whisper
import os
import sys
from pathlib import Path

def transcribe_audio(audio_file_path, model_size="small"):
    """
    Transcribe an audio file using Whisper model.
    
    Args:
        audio_file_path (str): Path to the audio file
        model_size (str): Size of Whisper model to use (tiny, base, small, medium, large)
    
    Returns:
        str: Transcribed text
    """
    print(f"Loading Whisper model: {model_size}")
    print("Note: First run will download the model (~244MB for 'small' model)")
    
    # Load the Whisper model
    model = whisper.load_model(model_size)
    
    print(f"Model loaded successfully!")
    print(f"Transcribing audio file: {audio_file_path}")
    
    # Transcribe the audio file
    result = model.transcribe(audio_file_path)
    
    # Extract the transcribed text
    transcribed_text = result["text"]
    
    print(f"\nTranscription completed!")
    print(f"Transcribed text:\n{'-' * 50}")
    print(transcribed_text)
    print(f"{'-' * 50}")
    
    return transcribed_text

def main():
    """
    Main function to run the Whisper demo.
    """
    # Check if sample audio file exists
    audio_file = "sample.wav"
    
    if not os.path.exists(audio_file):
        print(f"Error: Audio file '{audio_file}' not found!")
        print("Please place a sample audio file named 'sample.wav' in this directory.")
        print("\nYou can:")
        print("1. Record a short audio clip and save it as 'sample.wav'")
        print("2. Download a sample audio file from the internet")
        print("3. Convert an existing audio file to WAV format")
        sys.exit(1)
    
    try:
        # Transcribe the audio file
        transcribed_text = transcribe_audio(audio_file)
        
        # Save transcription to file
        output_file = "transcription_output.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcribed_text)
        
        print(f"\nTranscription saved to: {output_file}")
        
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        print("\nCommon issues:")
        print("1. Make sure FFmpeg is installed on your system")
        print("2. Check that the audio file is in a supported format")
        print("3. Ensure you have enough disk space for the model download")
        sys.exit(1)

if __name__ == "__main__":
    main()
