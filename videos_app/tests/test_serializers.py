from videos_app.models import Video
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from videos_app.api.serializers import VideoListSerializer


class VideoSerializerTests(TestCase):
    def setUp(self):
        self.thumbnail = SimpleUploadedFile(
            name="thumbnail.jpg",
            content=b"fake-image-content",
            content_type="image/jpeg",
        )
        self.video_file = SimpleUploadedFile(
            name="movie.mp4",
            content=b"fake-video-content",
            content_type="video/mp4",
        )

        self.video = Video.objects.create(
            title="Test Movie",
            description="Test Description",
            thumbnail_url=self.thumbnail,
            video=self.video_file,
            category="Drama"
        )

    def test_serializer_returns_correct_data(self):
        serializer = VideoListSerializer(self.video)

        self.assertEqual(serializer.data["id"], self.video.id)
        self.assertEqual(serializer.data["title"], "Test Movie")
        self.assertEqual(
            serializer.data["description"],
            "Test Description",
        )
        self.assertEqual(serializer.data["category"], "Drama")

    def test_serializer_returns_created_at(self):
        serializer = VideoListSerializer(self.video)

        self.assertEqual(
            serializer.data["created_at"],
            self.video.created_at.isoformat().replace("+00:00", "Z"),
        )

    def test_serializer_returns_thumbnail_url(self):
        serializer = VideoListSerializer(self.video)

        self.assertIn("thumbnail", serializer.data["thumbnail_url"])

    def test_serializer_does_not_return_video(self):
        serializer = VideoListSerializer(self.video)

        self.assertNotIn("video", serializer.data)

