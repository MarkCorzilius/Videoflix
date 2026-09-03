from django.apps import AppConfig


class VideosAppConfig(AppConfig):
    name = 'videos_app'

    def ready(self):
        """Connect the signal handlers when the app is ready."""

        import videos_app.signals
