from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
import django_rq
from videos_app.tasks import generate_hls
from pathlib import Path
from django.db import transaction
from django.conf import settings
import shutil

from videos_app.models import Video

@receiver(post_save, sender=Video)
def video_saved(sender, instance, created, **kwargs):
    if created or getattr(instance, "video_changed", False):
        django_rq.enqueue(generate_hls, instance.id)

@receiver(pre_save, sender=Video)
def video_updated(sender, instance, **kwargs):
    if not instance.pk:
        return

    old_instance = Video.objects.get(pk=instance.pk)

    if old_instance.video != instance.video:
        hls_dir = Path(old_instance.video.path).parent / "hls"

        Path(old_instance.video.path).unlink()

        if hls_dir.exists():
            shutil.rmtree(hls_dir)

        instance.video_changed = True

    if old_instance.thumbnail_url != instance.thumbnail_url:
        Path(old_instance.thumbnail_url.path).unlink()

@receiver(post_delete, sender=Video)
def video_deleted(sender, instance, using, origin, **kwargs):
    media_video_dir = Path(settings.MEDIA_ROOT) / "video"
    video_dir = media_video_dir / str(instance.id)

    if media_video_dir.is_dir() and video_dir.parent == media_video_dir:
        shutil.rmtree(video_dir)
    