from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from django.contrib.auth import get_user_model
from videos_app.models import Video
from django.core.cache import cache

User = get_user_model()

class VideoListViewTests(APITestCase):
    def setUp(self):
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
            name="test_video.mp4",
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

        self.url = "/api/video/"

    def test_get_videos_authenticated(self):
        Video.objects.create(**self.request_data)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_videos_required_fields(self):
        Video.objects.create(**self.request_data)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0].keys(), self.required_video_keys)

    def test_get_videos_returns_correct_data(self):
        Video.objects.create(**self.request_data)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["title"], self.request_data["title"])
        self.assertEqual(response.data[0]["description"], self.request_data["description"])
        self.assertEqual(response.data[0]["category"], self.request_data["category"])
        self.assertIn("test_thumbnail.jpg", response.data[0]["thumbnail_url"])
        self.assertIn("test_video.mp4", response.data[0]["video"])

    def test_empty_list(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_videos_unauthenticated(self):
        self.client.force_authenticate(user=None)
        Video.objects.create(**self.request_data)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
