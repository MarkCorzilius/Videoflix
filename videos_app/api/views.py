from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from videos_app.api.serializers import VideoListSerializer

from videos_app.models import Video


class VideoListView(ListAPIView):
    queryset = Video.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = VideoListSerializer