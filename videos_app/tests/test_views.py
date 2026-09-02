from videos_app.tests.test_services import TemporaryMediaTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from pathlib import Path

from django.contrib.auth import get_user_model
from videos_app.models import Video
from django.core.cache import cache

User = get_user_model()


class VideoListViewTests(TemporaryMediaTestCase):
    def setUp(self):
        super().setUp()
        cache.clear()
        self.user = User.objects.create_user(email="test@gmail.com", password="secureTest123!", is_active=True)
        self.client.force_authenticate(user=self.user)

        self.required_video_keys = {
            "id",
            "created_at",
            "title",
            "description",
            "thumbnail_url",
            "category",
        }

        self.video_url = SimpleUploadedFile(
            name="video.mp4",
            content=b"fake-video-content",
            content_type="video/mp4",
        )

        self.thumbnail_url = SimpleUploadedFile(
            name="thumbnail.jpg",
            content=b"fake-image-content",
            content_type="image/jpeg",
        )

        self.request_data = {
            "title": "New Movie",
            "description": "New Desription",
            "thumbnail_url": self.thumbnail_url,
            "video": self.video_url,
            "category": "Drama",
        }

        self.url = "/api/video/"

    def test_get_videos_authenticated(self):
        Video.objects.create(**self.request_data)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_videos_required_fields(self):
        Video.objects.create(**self.request_data)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data[0].keys()), self.required_video_keys)

    def test_get_videos_returns_correct_data(self):
        Video.objects.create(**self.request_data)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["title"], self.request_data["title"])
        self.assertEqual(response.data[0]["description"], self.request_data["description"])
        self.assertEqual(response.data[0]["category"], self.request_data["category"])
        self.assertIn("thumbnail", response.data[0]["thumbnail_url"])

    def test_empty_list(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_videos_unauthenticated(self):
        self.client.force_authenticate(user=None)
        Video.objects.create(**self.request_data)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class VideoResolutionViewTests(TemporaryMediaTestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(email="test@gmail.com", password="securePassword123!", is_active=True)
        self.video_url = SimpleUploadedFile(
            name="video.mp4",
            content=b"fake-video-content",
            content_type="video/mp4",
        )
        self.thumbnail_url = SimpleUploadedFile(
            name="test_thumbnail.jpg",
            content=b"fake-image-content",
            content_type="image/jpeg",
        )
        self.request_data = {
            "title": "New Movie",
            "description": "New Desription",
            "thumbnail_url": self.thumbnail_url,
            "video": self.video_url,
            "category": "Drama",
        }

        self.client.force_authenticate(user=self.user)

    def create_hls_playlist(self, resolution="720p"):
        video = Video.objects.create(**self.request_data)
    
        hls_path = (
            Path(video.video.path).parent
            / "hls"
            / resolution
        )
        hls_path.mkdir(parents=True)
    
        playlist = hls_path / "index.m3u8"
        playlist.write_text("#EXTM3U\n#EXT-X-VERSION:3")
    
        return video

    def test_index_m3u8_success(self):
        video = self.create_hls_playlist()
        response = self.client.get(
            f"/api/video/{video.id}/720p/index.m3u8"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.streaming)

    def test_index_m3u8_content_type(self):
        video = self.create_hls_playlist()
        response = self.client.get(
            f"/api/video/{video.id}/720p/index.m3u8"
        )

        self.assertEqual(response["Content-Type"], "application/vnd.apple.mpegurl")

    def test_index_m3u8_video_not_found(self):
        response = self.client.get(
            f"/api/video/9999/720p/index.m3u8"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_index_m3u8_resolution_not_found(self):
        video = Video.objects.create(**self.request_data)
        response = self.client.get(
            f"/api/video/{video.id}/1440p/index.m3u8"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_index_m3u8_file_not_found(self):
        video = Video.objects.create(**self.request_data)
        hls_path = Path(video.video.path).parent / "hls" / "720p"
        hls_path.mkdir(parents=True)

        response = self.client.get(
            f"/api/video/{video.id}/720p/index.m3u8"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_index_m3u8_requires_authentication(self):
        video = Video.objects.create(**self.request_data)
        self.client.force_authenticate(user=None)

        response = self.client.get(
            f"/api/video/{video.id}/720p/index.m3u8"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
