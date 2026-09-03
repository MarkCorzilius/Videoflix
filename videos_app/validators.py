import os
from django.core.exceptions import ValidationError


def validate_thumbnail_file_extension(value):
  ext = os.path.splitext(value.name)[1]
  valid_extensions = [".jpg", ".jpeg", ".png", ".webp"]
  if not ext in valid_extensions:
    raise ValidationError(u'File not supported!')


def validate_video_file_extension(value):
  ext = os.path.splitext(value.name)[1]
  valid_extensions = [".mp4", ".mov", ".mkv", ".webm"]
  if not ext in valid_extensions:
    raise ValidationError(u'File not supported!')
