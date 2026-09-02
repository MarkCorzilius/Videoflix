from django.db import models
import uuid
from videos_app.utils import video_upload_path, thumbnail_upload_path

class Video(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    thumbnail_url = models.ImageField(upload_to=thumbnail_upload_path, blank=True)
    video = models.FileField(upload_to=video_upload_path)
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.title