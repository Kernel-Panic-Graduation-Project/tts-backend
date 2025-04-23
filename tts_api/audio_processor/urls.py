from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AudioFileViewSet, TextToAudioViewSet

router = DefaultRouter()
router.register(r'audio-files', AudioFileViewSet)
router.register(r'text-to-audio', TextToAudioViewSet, basename='text-to-audio')

urlpatterns = [
    path('', include(router.urls)),
]
