from django.urls import path
from videos_app.api.views import VideoListView, m3u8View

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video-list'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', m3u8View.as_view(), name='m3u8')
]