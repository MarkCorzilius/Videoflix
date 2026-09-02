from videos_app.models import Video
from pathlib import Path
from django.conf import settings
from django.core.files import File
import subprocess


def generate_hls_files(video_id):
    video = Video.objects.get(id=video_id)
    video_uuid = video.uuid
    path = video.video.path
    output_dir = (Path(settings.MEDIA_ROOT) / "video" / str(video_uuid) / "hls")
    convert_resolution(path, output_dir, 480)
    convert_resolution(path, output_dir, 720)
    convert_resolution(path, output_dir, 1080)

    thumbnail_extension = getattr(settings, "THUMBNAIL_EXTENSION", "jpg")
    thumbnail_filename = f"thumbnail.{thumbnail_extension}"
    thumbnail_path = Path(settings.MEDIA_ROOT) / "video" / str(video_uuid) / thumbnail_filename
    generate_thumbnail(path, thumbnail_path)

    with open(thumbnail_path, "rb") as f:
        video.thumbnail_url.save(thumbnail_filename, File(f), save=True)

    video.is_processed = True
    video.save(update_fields=["thumbnail_url"])

def convert_resolution(source, output_dir, resolution):
    resolution_dir = output_dir / f"{resolution}p"
    resolution_dir.mkdir(parents=True, exist_ok=True)

    width = int(resolution * 16 / 9)
    width -= width % 2

    cmd = [
        "ffmpeg", "-i", source,
        "-vf",
        f"scale=w={width}:h={resolution}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{resolution}:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-crf", "23", "-c:a", "aac",
        "-f", "hls", "-hls_time", "6", "-hls_playlist_type", "vod",
        "-hls_segment_filename", str(resolution_dir / "segment_%03d.ts"),
        str(resolution_dir / "index.m3u8"),
    ]
    subprocess.run(cmd)


def generate_thumbnail(source, output_path):
    cmd = [
        "ffmpeg", "-y", "-i", source, "-ss", "00:00:01",
        "-vframes", "1", str(output_path),
    ]
    subprocess.run(cmd, check=True)