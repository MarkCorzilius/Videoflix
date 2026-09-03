from pathlib import Path

def video_upload_path(instance, filename):
    extension = Path(filename).suffix
    return f"video/{instance.uuid}/original{extension}"

def thumbnail_upload_path(instance, filename):
    extension = Path(filename).suffix
    return f"video/{instance.uuid}/thumbnail{extension}"