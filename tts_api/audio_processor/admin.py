from django.contrib import admin
from .models import AudioFile, TextToAudioResult

@admin.register(AudioFile)
class AudioFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'uploaded_at']

@admin.register(TextToAudioResult)
class TextToAudioResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'input_text', 'audio_file_id', 'created_at']
    