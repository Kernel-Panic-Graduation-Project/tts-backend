import os
import librosa
import numpy as np
from pydub import AudioSegment
import tempfile
from gtts import gTTS  # Google Text-to-Speech library (for testing purposes)
import soundfile as sf
from gradio_client import Client, handle_file
from django.conf import settings
import whisper

def generate_speech_using_gtts(input_text):
    """
    Generate audio from text based on a style parameter
    Returns generated audio file path
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

def generate_speech_using_f5_tts(input_text, ref_audio_file):
    """
    Generate speech using F5-TTS model
    Returns generated temp audio file path
    """

    # add MEDIA path to the file path
    ref_audio_path = os.path.join(settings.MEDIA_ROOT, ref_audio_file.file.name)

    client = Client("http://localhost:7860/")
    result = client.predict(
        ref_audio_input=handle_file(ref_audio_path),
        ref_text_input=ref_audio_file.transcript,
        gen_text_input=input_text,
        remove_silence=False,
        cross_fade_duration_slider=0.15,
        nfe_slider=32,
        speed_slider=1,
        api_name="/basic_tts"
    )

    # the generated speech file is the first element of the result
    generated_audio_path = result[0]

    return generated_audio_path

def transcribe_with_whisper(audio_file_path):
    """
    Transcribe audio using Whisper ASR model
    Returns the transcription text
    """

    # Load model (choose size: tiny, base, small, medium, large)
    model = whisper.load_model("medium")
    
    # Transcribe
    result = model.transcribe(audio_file_path)

    # strip the result to get only the text
    transcript = result["text"].strip()
    
    return transcript

def trim_audio_file(input_audio_file, length):
    """
    Trim the audio file to the specified length in seconds.
    Returns the trimmed audio file path.
    """

    # Load the audio file
    audio = AudioSegment.from_file(input_audio_file)

    # Trim the audio file
    trimmed_audio = audio[:length * 1000]  # Convert seconds to milliseconds

    final_duration = len(trimmed_audio) / 1000  # Convert milliseconds to seconds

    # Create a temporary file to save the trimmed audio
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    temp_file.close()

    # Export the trimmed audio to the temporary file
    trimmed_audio.export(temp_file.name, format="wav")

    return temp_file.name, final_duration
