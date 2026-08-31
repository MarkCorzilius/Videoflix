from django.test import TestCase
from videos_app.models import Video
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

class VideoModelTests(TestCase):
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

    def test_created_video_successfully(self):
        self.assertEqual(self.video.title, "Test Movie")
        self.assertEqual(self.video.description, "Test Description")
        self.assertEqual(self.video.category, "Drama")
        self.assertIsNotNone(self.video.id)
        self.assertEqual(Video.objects.count(), 1)

    def test_created_at_is_set_automatically(self):
        self.assertIsNotNone(self.video.created_at)

    def test_title_is_required(self):
        video = Video(
            description="Test Description",
            thumbnail_url=self.thumbnail,
            video=self.video_file,
            category="Drama",
        )

        with self.assertRaises(ValidationError):
            video.full_clean()

    def test_description_is_required(self):
        video = Video(
            title="Test Movie",
            thumbnail_url=self.thumbnail,
            video=self.video_file,
            category="Drama",
        )

        with self.assertRaises(ValidationError):
            video.full_clean()

    def test_thumbnail_is_required(self):
        video = Video(
            title="Test Movie",
            description="Test Description",
            video=self.video_file,
            category="Drama",
        )

        with self.assertRaises(ValidationError):
            video.full_clean()

    def test_video_is_required(self):
        video = Video(
            title="Test Movie",
            description="Test Description",
            thumbnail_url=self.thumbnail,
            category="Drama",
        )

        with self.assertRaises(ValidationError):
            video.full_clean()

    def test_category_is_required(self):
        video = Video(
            title="Test Movie",
            description="Test Description",
            thumbnail_url=self.thumbnail,
            video=self.video_file,
        )

        with self.assertRaises(ValidationError):
            video.full_clean()