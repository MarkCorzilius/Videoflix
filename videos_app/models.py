from django.db import models

class Video(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    thumbnail_url = models.ImageField(upload_to="thumbnails/")
    video = models.FileField(upload_to="videos/originals/")
    category = models.CharField(max_length=100)


# 1: tests for VideoListViewTests
# 2: VideoListSerializer
# 3: VideoListView
# 4: task and service for deletions (deleting files –> signal)
