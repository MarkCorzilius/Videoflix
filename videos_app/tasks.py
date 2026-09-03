from pathlib import Path

from django.conf import settings

from videos_app.models import Video
from videos_app.services.hls import generate_hls_files, generate_thumbnail


def generate_hls(video_id):
    """Trigger HLS generation for the given video."""

    generate_hls_files(video_id)


def generate_thumbnail_for_video(video_id):
    """Generate and save a thumbnail image for the given video."""

    video = Video.objects.get(id=video_id)

    extension = Path(video.thumbnail_url.name).suffix
    thumbnail_filename = f"thumbnail{extension}"

    thumbnail_path = (
        Path(settings.MEDIA_ROOT)
        / "video"
        / str(video.uuid)
        / thumbnail_filename
    )

    generate_thumbnail(video.video.path, thumbnail_path)

    video.thumbnail_url.name = (
        f"video/{video.uuid}/{thumbnail_filename}"
    )
    video.save(update_fields=["thumbnail_url"])
