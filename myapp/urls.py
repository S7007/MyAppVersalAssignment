# myapp/urls.py

from django.urls import path
from .views import UserImageUploadView, UserImageListView

urlpatterns = [
    path('upload/', UserImageUploadView.as_view(), name='image-upload'),
    path('images/', UserImageListView.as_view(), name='image-list'),
]
