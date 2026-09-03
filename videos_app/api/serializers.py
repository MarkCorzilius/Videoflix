from rest_framework import serializers
from videos_app.models import Video

class VideoListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Video
        fields = [
            "id",
            "created_at",
            "title",
            "description",
            "thumbnail_url",
            "category",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "title",
            "description",
            "thumbnail_url",
            "category",
        ]