from django.db.models.signals import post_save
from django.dispatch import receiver
import django_rq
from videos_app.tasks import generate_hls

from videos_app.models import Video

@receiver(post_save, sender=Video)
def video_created(sender, instance, created, **kwargs):
    if created:
        django_rq.enqueue(generate_hls, instance.id)