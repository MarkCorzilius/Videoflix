import shutil
from pathlib import Path

import django_rq
from django.conf import settings
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from videos_app.models import Video
from videos_app.tasks import generate_hls, generate_thumbnail_for_video


@receiver(post_save, sender=Video)
def video_saved(sender, instance, created, **kwargs):
    """Enqueue HLS and thumbnail generation jobs when a video is created or its file changes."""

    if created:
        django_rq.enqueue(generate_hls, instance.id)
        django_rq.enqueue(generate_thumbnail_for_video, instance.id)

    elif getattr(instance, "video_changed", False):
        django_rq.enqueue(generate_hls, instance.id)


@receiver(pre_save, sender=Video)
def video_updated(sender, instance, **kwargs):
    """Clean up old video/thumbnail files and flag reprocessing when they are replaced."""

    if not instance.pk:
        return

    old_instance = Video.objects.get(pk=instance.pk)

    if old_instance.video != instance.video:
        hls_dir = Path(old_instance.video.path).parent / "hls"

        Path(old_instance.video.path).unlink()

        if hls_dir.exists():
            shutil.rmtree(hls_dir)

        instance.video_changed = True
        instance.is_processed = False

    if old_instance.thumbnail_url != instance.thumbnail_url:
        Path(old_instance.thumbnail_url.path).unlink()


@receiver(post_delete, sender=Video)
def video_deleted(sender, instance, using, origin, **kwargs):
    """Remove a video's media directory from disk after its record is deleted."""

    media_video_dir = Path(settings.MEDIA_ROOT) / "video"
    video_dir = media_video_dir / str(instance.uuid)

    if media_video_dir.is_dir() and video_dir.parent == media_video_dir:
        shutil.rmtree(video_dir)