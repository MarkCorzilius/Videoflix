from django.urls import path
from accounts_app.api.views import RegisterView, ActivateView, LogoutView, LoginView, CookieRefreshTokenView, PasswordResetRequestView, PasswordResetConfirmView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<str:uidb64>/<str:token>/', ActivateView.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CookieRefreshTokenView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password_confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_confirm'),
]