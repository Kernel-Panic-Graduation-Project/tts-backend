import os
import librosa
import numpy as np
from pydub import AudioSegment
import tempfile
from gtts import gTTS  # Google Text-to-Speech library (for testing purposes)
import soundfile as sf

def generate_audio_from_text(input_text):
    """
    Generate audio from text based on a style parameter
    Returns generated audio file path and additional text info
    """
    # Create a temporary file to store the generated audio
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    temp_file.close()
    
    # Generate speech with gTTS
    tts = gTTS(input_text, lang='en')
    temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    temp_mp3.close()
    tts.save(temp_mp3.name)
    
    # Convert to WAV format
    y, sr = librosa.load(temp_mp3.name)
    sf.write(temp_file.name, y, sr)
    
    # Clean up temporary MP3
    os.unlink(temp_mp3.name)

    print(f"Generated audio saved to {temp_file.name}")
        
    return temp_file.name
