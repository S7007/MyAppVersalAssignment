# myapp/tasks.py

from celery import shared_task
from .models import UserImage

@shared_task
def process_image(image_id):
    image = UserImage.objects.get(id=image_id)
    # Perform your sample operation on the image here
    print(f"Processing image: {image.image.name}")
