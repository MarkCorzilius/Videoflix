from videos_app.models import Video
from pathlib import Path
import subprocess

def generate_hls_files(video_id):
    video = Video.objects.get(id=video_id)
    path = video.video.path
    output_dir = (Path(path).parent / "hls")
    convert_resolution(path, output_dir, 480)
    convert_resolution(path, output_dir, 720)
    convert_resolution(path, output_dir, 1080)

def convert_resolution(source, output_dir, resolution):
    resolution_dir = output_dir / f"{resolution}p"
    resolution_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
    "ffmpeg",
    "-i", source,
    "-s", f"hd{resolution}",
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