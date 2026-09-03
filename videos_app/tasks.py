from videos_app.services.hls import generate_hls_files, generate_thumbnail
from django.conf import settings
from pathlib import Path
from videos_app.models import Video

def generate_hls(video_id):
    generate_hls_files(video_id)

def generate_thumbnail_for_video(video_id):
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