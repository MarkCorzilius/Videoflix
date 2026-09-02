from videos_app.models import Video
from pathlib import Path
from django.conf import settings
import subprocess

def generate_hls_files(video_id):
    video = Video.objects.get(id=video_id)
    video_uuid = video.uuid
    path = video.video.path
    output_dir = (Path(settings.MEDIA_ROOT) / "video" / str(video_uuid) / "hls")
    convert_resolution(path, output_dir, 480)
    convert_resolution(path, output_dir, 720)
    convert_resolution(path, output_dir, 1080)

def convert_resolution(source, output_dir, resolution):
    resolution_dir = output_dir / f"{resolution}p"
    resolution_dir.mkdir(parents=True, exist_ok=True)

    width = int(resolution * 16 / 9)

    cmd = [
    "ffmpeg",
    "-i", source,
    "-vf",
    (
        f"scale=w={width}:h={resolution}:"
        "force_original_aspect_ratio=decrease,"
        f"pad={width}:{resolution}:(ow-iw)/2:(oh-ih)/2"
    ),
    "-c:v", "libx264",
    "-crf", "23",
    "-c:a", "aac",
    "-f", "hls",
    "-hls_time", "6",
    "-hls_playlist_type", "vod",
    "-hls_segment_filename", str(resolution_dir / "segment_%03d.ts"),
    str(resolution_dir / "index.m3u8"),
    ]
    subprocess.run(cmd)