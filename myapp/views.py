from django.shortcuts import render

# myapp/views.py

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from .models import CustomUser, UserImage
from .serializers import UserSerializer, UserImageSerializer
from .tasks import process_image

class UserImageUploadView(generics.CreateAPIView):
    serializer_class = UserImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        image = serializer.save(user=user)
        process_image.delay(image.id)

class UserImageListView(generics.ListAPIView):
    serializer_class = UserImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return UserImage.objects.filter(user=user)

# Create your views here.
