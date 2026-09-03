from pathlib import Path


def video_upload_path(instance, filename):
    """Build the upload path for a video's original file."""

    extension = Path(filename).suffix
    return f"video/{instance.uuid}/original{extension}"


def thumbnail_upload_path(instance, filename):
    """Build the upload path for a video's thumbnail file."""

    extension = Path(filename).suffix
    return f"video/{instance.uuid}/thumbnail{extension}"
