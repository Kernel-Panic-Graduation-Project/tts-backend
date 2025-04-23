from django.shortcuts import render
import os
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AudioFile, TextToAudioResult
from .serializers import (AudioFileSerializer,
    TextToAudioInputSerializer, TextToAudioResultSerializer)
from .audio_utils import generate_audio_from_text

class AudioFileViewSet(viewsets.ViewSet):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer

    @action(detail=False, methods=['post'])
    def upload(self, request):
        # Validate file upload
        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        audio_file = request.FILES['file']
        
        # Save the file to the model
        audio_file_instance = AudioFile(file=audio_file)
        audio_file_instance.save()
        
        # Return the serialized data of the saved instance
        serializer = AudioFileSerializer(audio_file_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TextToAudioViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def generate(self, request):
        # Validate input
        serializer = TextToAudioInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract validated data
        input_text = serializer.validated_data['input_text']
        audio_file_id = serializer.validated_data['audio_file_id']
        audio_file = None

        print(f"Input text: {input_text}")
        print(f"Audio file ID: {audio_file_id}")

        # Try to get the audio file
        try:
            audio_file = AudioFile.objects.get(id=audio_file_id)
        except AudioFile.DoesNotExist:
            return Response({"error": "Audio file not found"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Generate audio from text
            #TODO: Add support for F5-TTS
            generated_file_path = generate_audio_from_text(
                input_text,
            )
            
            # Create result object
            result = TextToAudioResult(
                input_text=input_text,
                audio_file_id=audio_file,
                generated_audio=generated_file_path,
            )
            
            # Save generated file to result
            filename = os.path.basename(generated_file_path)
            with open(generated_file_path, 'rb') as f:
                result.generated_audio.save(filename, f)
            
            # Save result
            result.save()
            
            # Delete temporary file
            os.unlink(generated_file_path)
            
            # Return result
            result_serializer = TextToAudioResultSerializer(result)
            return Response(result_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
