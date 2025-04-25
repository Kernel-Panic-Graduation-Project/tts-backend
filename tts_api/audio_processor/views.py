from django.shortcuts import render
import os
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from .models import AudioFile, TextToAudioResult
from .serializers import (AudioFileSerializer,
    TextToAudioInputSerializer, TextToAudioResultSerializer)
from .audio_utils import *
import tempfile

class AudioFileViewSet(viewsets.ViewSet):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer

    @action(detail=False, methods=['post'])
    def upload(self, request):
        print("Received request to upload audio file")
        # Validate file upload
        if 'file' not in request.FILES:
            print("No file provided in request")
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'name' not in request.data:
            return Response({"error": "No name provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'user_id' not in request.data:
            return Response({"error": "No user ID provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        print("Validating file upload")
        
        audio_file = request.FILES['file']
        name = request.data['name'].strip()

        print(f"Audio file name: {name}")

        # Save audio as temporary file to process
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1])
        temp_file.close()

        with open(temp_file.name, 'wb') as dest:
            for chunk in audio_file.chunks():
                dest.write(chunk)

        # Trim the audio file to 10 seconds
        trimmed_audio_file = None
        duration_after_trim = 0
        try:
            (trimmed_audio_file, duration_after_trim) = trim_audio_file(temp_file.name, 10)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        # Check if transcript is provided
        transcript = ""
        if 'transcript' in request.data and request.data['transcript']:
            transcript = request.data['transcript']
        else:
            # Generate transcript using Whisper
            try:
                transcript = transcribe_with_whisper(trimmed_audio_file)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Save the trimmed audio file to the model
        audio_file_instance = AudioFile()
        audio_file_instance.name = name
        audio_file_instance.file.save(os.path.basename(trimmed_audio_file), open(trimmed_audio_file, 'rb'))
        audio_file_instance.transcript = transcript
        audio_file_instance.user_id = request.data['user_id']
        audio_file_instance.duration = duration_after_trim
        audio_file_instance.save()

        # Delete the temporary files
        os.unlink(temp_file.name)
        os.unlink(trimmed_audio_file)
        
        # Return the serialized data of the saved instance
        serializer = AudioFileSerializer(audio_file_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def getlist(self, request):
        user_id = request.META['HTTP_USER_ID']
        print(f"User ID: {user_id}")
        # Get the list of audio files for the user
        audio_files = AudioFile.objects.filter(user_id=user_id)
        serializer = AudioFileSerializer(audio_files, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TextToAudioViewSet(viewsets.ViewSet):
    queryset = TextToAudioResult.objects.all()

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
            generated_file_path = generate_speech_using_gtts(
                input_text,
                #audio_file,
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

            os.unlink(generated_file_path)

            # Serve the generated audio file
            file_path = result.generated_audio.path
            if os.path.exists(file_path):
                response = FileResponse(open(file_path, 'rb'))
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
            else:
                return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
