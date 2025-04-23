from rest_framework import serializers
from .models import AudioFile, TextToAudioResult

class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = ['id', 'file', 'uploaded_at']

class TextToAudioInputSerializer(serializers.Serializer):
    input_text = serializers.CharField(required=True)
    audio_file_id = serializers.IntegerField(required=True)

class TextToAudioResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextToAudioResult
        fields = ['id', 'input_text', 'audio_file_id', 'generated_audio', 'created_at']
        read_only_fields = ['id', 'created_at']