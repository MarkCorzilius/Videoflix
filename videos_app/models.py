from django.db import models
import uuid
from videos_app.utils import video_upload_path, thumbnail_upload_path
from videos_app.validators import validate_thumbnail_file_extension, validate_video_file_extension


class Video(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    thumbnail_url = models.ImageField(upload_to=thumbnail_upload_path, blank=True, validators=[validate_thumbnail_file_extension])
    video = models.FileField(upload_to=video_upload_path, validators=[validate_video_file_extension])
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.title