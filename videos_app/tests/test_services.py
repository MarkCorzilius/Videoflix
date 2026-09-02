from rest_framework.test import APIClient, APITestCase
from django.test import override_settings
from accounts_app.models import User
from videos_app.models import Video
from django.core.files.uploadedfile import SimpleUploadedFile
from videos_app.services.hls import generate_hls_files, convert_resolution
from pathlib import Path
from django.core.files import File
from django.conf import settings
from unittest.mock import patch
import subprocess
import tempfile
import shutil



class TemporaryMediaTestCase(APITestCase):

    def setUp(self):
        super().setUp()
        self.temp_media = tempfile.TemporaryDirectory()
        self.media_override = override_settings(
            MEDIA_ROOT=self.temp_media.name
        )
        self.media_override.enable()
        self.rq_patch = patch(
            "videos_app.signals.django_rq.enqueue"
        )

        self.rq_patch.start()

    def tearDown(self):
        self.rq_patch.stop()
        self.media_override.disable()
        self.temp_media.cleanup()
        super().tearDown()

@override_settings(MEDIA_ROOT=Path(tempfile.TemporaryDirectory().name))
class VideoHLSServiceTests(TemporaryMediaTestCase):
    def setUp(self):
        super().setUp()
        self.thumbnail_url = SimpleUploadedFile(
            name="test_thumbnail.jpg",
            content=b"fake-image-content",
            content_type="image/jpeg",
        )
        video_path = Path(__file__).parent / "files" / "test.mp4"
        with open(video_path, "rb") as file:
            self.video = Video.objects.create(
                title="New Movie",
                description="New Description",
                video=File(file, name="original.mp4"),
                category="Drama",
            )

        print("MEDIA_ROOT:", settings.MEDIA_ROOT)
        print("VIDEO PATH:", self.video.video.path)

    def test_generate_hls_files_creates_hls_directory(self):
        generate_hls_files(self.video.id)
        hls_path = Path(self.video.video.path).parent / "hls"

        self.assertTrue(hls_path.is_dir())

    @patch("videos_app.services.hls.convert_resolution")
    def test_generate_hls_files_uses_correct_resolutions(self, mock_convert):
        generate_hls_files(self.video.id)

        resolutions = [
            call.args[2]
            for call in mock_convert.call_args_list
        ]

        self.assertEqual(resolutions, [480, 720, 1080])

    @patch("videos_app.services.hls.convert_resolution")
    def test_generate_hls_files_converts_all_resolutions(self, mock_convert):
        generate_hls_files(self.video.id)

        self.assertEqual(mock_convert.call_count, 3)

    def test_generate_hls_files_creates_segments(self):
        generate_hls_files(self.video.id)
        hls_path = Path(self.video.video.path).parent / "hls"

        for resolution in ["480p", "720p", "1080p"]:
            resolution_path = hls_path / resolution
            segments = list(resolution_path.glob("*.ts"))

            self.assertTrue(segments)

    @patch("videos_app.services.hls.subprocess.run")
    def test_convert_resolution_calls_ffmpeg_correctly(self, mock_run):
        source = self.video.video.path
        output_dir = Path(settings.MEDIA_ROOT) / "video" / str(self.video.uuid) / "hls"

        convert_resolution(source, output_dir, 720)

        mock_run.assert_called_once()

        cmd = mock_run.call_args[0][0]

        self.assertEqual(cmd[0], "ffmpeg")
        self.assertEqual(cmd[1], "-i")
        self.assertEqual(cmd[2], source)
        self.assertEqual(cmd[3], "-s")
        self.assertEqual(cmd[4], "hd720")

    @patch("videos_app.services.hls.subprocess.run")
    def test_convert_resolution_handles_ffmpeg_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(
            1,
            "ffmpeg"
        )

        source = self.video.video.path
        output_dir = (
            Path(settings.MEDIA_ROOT)
            / "video"
            / str(self.video.uuid)
            / "hls"
        )

        with self.assertRaises(subprocess.CalledProcessError):
            convert_resolution(source, output_dir, 720)
