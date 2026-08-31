from django.db import models

class Video(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    thumbnail_url = models.ImageField(upload_to="thumbnails/")
    video = models.FileField(upload_to="videos/originals/")
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.title