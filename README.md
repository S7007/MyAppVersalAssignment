

### Step 1: Set Up Your Django Project

First, set up a Django project and create a new app within that project.

```bash
django-admin startproject myproject
cd myproject
python manage.py startapp myapp
```

### Step 2: Install Required Packages

Install the required packages including `django-celery` for background tasks and `Pillow` for image handling.

```bash
pip install django celery Pillow
```

### Step 3: Update `settings.py`

Update your `settings.py` to include the new app and configure Celery.

```python
# myproject/settings.py

INSTALLED_APPS = [
    # other apps
    'myapp',
    'django_celery_results',
]

# Celery configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-db'
```

### Step 4: Define Models

Create your models in `models.py`.

```python
# myapp/models.py

# myapp/models.py

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=30, blank=True, null=True)
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Add this line
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Add this line
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='customuser',
    )

class UserImage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name

```

### Step 5: Create Serializers

Create serializers for the models in `serializers.py`.

```python
# myapp/serializers.py

from rest_framework import serializers
from .models import CustomUser, UserImage

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'bio', 'location']

class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = ['id', 'image', 'uploaded_at']
```

### Step 6: Create Views

Create views for uploading images and getting the list of uploaded images.

```python
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
```

### Step 7: Create Background Task

Create a Celery task for processing the image.

```python
# myapp/tasks.py

from celery import shared_task
from .models import UserImage

@shared_task
def process_image(image_id):
    image = UserImage.objects.get(id=image_id)
    # Perform your sample operation on the image here
    print(f"Processing image: {image.image.name}")
```

### Step 8: Update `urls.py`

Add URLs to route the views.

```python
# myapp/urls.py

from django.urls import path
from .views import UserImageUploadView, UserImageListView

urlpatterns = [
    path('upload/', UserImageUploadView.as_view(), name='image-upload'),
    path('images/', UserImageListView.as_view(), name='image-list'),
]
```

### Step 9: Migrate Database

Apply the migrations to create database tables.

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 10: Configure Celery

Create a `celery.py` file in your project directory.

```python
# myproject/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

Update `__init__.py` to make sure Celery is loaded with Django.

```python
# myproject/__init__.py

from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### Step 11: Run Celery

Start the Celery worker.

```bash
celery -A myproject worker --loglevel=info
```

### Step 12: Run the Server

Finally, run the Django development server.

```bash
python manage.py runserver
```

With these steps, you should have a working application that allows users to upload images and view the list of their uploaded images.
