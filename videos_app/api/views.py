from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from videos_app.api.serializers import VideoListSerializer
from pathlib import Path
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404

from videos_app.models import Video


class VideoListView(ListAPIView):
    queryset = Video.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = VideoListSerializer


class m3u8View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        video = get_object_or_404(Video, id=movie_id)
        file_path = (
            Path(video.video.path).parent
            / "hls"
            / resolution
            / "index.m3u8"
        )

        if not file_path.is_file():
            raise Http404("Playlist not found.")

        return FileResponse(
            open(file_path, "rb"),
            content_type="application/vnd.apple.mpegurl"
        )

class VideoSegmentView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, movie_id, resolution, segment):
        video = get_object_or_404(Video, id=movie_id)
        file_path = (
            Path(video.video.path).parent
            / "hls"
            / resolution
            / segment
        )

        if not file_path.is_file():
            raise Http404("Video segments not found.")


        return FileResponse(
            open(file_path, "rb"),
            content_type="application/vnd.apple.mpegurl"
        )


# prevent videos being distorted.
# remove video content on video deletion
# docs, imports, logs