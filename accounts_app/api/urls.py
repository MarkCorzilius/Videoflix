from django.urls import path
from accounts_app.api.views import RegisterView, ActivateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<str:uidb64>/<str:token>/', ActivateView.as_view(), name='activate'),
]