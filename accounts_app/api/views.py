from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from accounts_app.models import User
from accounts_app.api.serializers import RegisterSerializer, LoginSerializer
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.response import Response
from accounts_app.tasks.email_tasks import send_verification_email_task
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = default_token_generator.make_token(user)
        send_verification_email_task.delay(user.id, token)

        return Response({
            "user": {
                "id": user.id,
                "email": user.email,
            },
            "token": token,
        }, status=status.HTTP_201_CREATED)


class ActivateView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
        except (TypeError, ValueError, UnicodeDecodeError):
            return Response(status=status.HTTP_404_NOT_FOUND)
             
        user = get_object_or_404(User, pk=uid)

        if not default_token_generator.check_token(user, token):
            return Response(
                {"message": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response(
            {"message": "Account successfully activated."},
            status=status.HTTP_200_OK,
        )

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        refresh = serializer.validated_data["refresh"]
        access = serializer.validated_data["access"]

        response = Response({
            "detail": "Login successful",
            "user": {
                "id": serializer.validated_data["id"],
                "username": serializer.validated_data["username"],
            }
        }, status=status.HTTP_200_OK)
        
        response.set_cookie("refresh", refresh, httponly=True)
        response.set_cookie("access", access, httponly=True)

        return response


class CookieRefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs) -> Response:
        refresh = request.COOKIES.get("refresh")
        serializer = self.get_serializer(data={"refresh": refresh})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        access = serializer.validated_data["access"]
        response = Response({"detail": "Token refreshed"}, status=status.HTTP_200_OK)
        response.set_cookie("access", access, httponly=True)
        return response