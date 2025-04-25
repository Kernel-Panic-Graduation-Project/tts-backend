from django.db import models

class AudioFile(models.Model):
    user_id = models.IntegerField(blank=False, null=False, default=0)
    file = models.FileField(upload_to='uploads/')
    name = models.TextField(blank=False, null=False, default="")
    transcript = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return f"Audio {self.id} - {self.user_id} - {self.name} - {self.file} - {self.transcript} - {self.uploaded_at} - {self.duration}"
    
class TextToAudioResult(models.Model):
    input_text = models.TextField()
    audio_file_id = models.ForeignKey(AudioFile, on_delete=models.CASCADE, related_name='text_to_audio_results')
    generated_audio = models.FileField(upload_to='generated/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Text-to-Audio {self.id} - {self.created_at}"
    