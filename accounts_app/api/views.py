from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from accounts_app.models import User
from accounts_app.api.serializers import RegisterSerializer
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.response import Response
from accounts_app.services.email_service import send_verification_email
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404

class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = default_token_generator.make_token(user)
        send_verification_email(user, token)

        return Response({
            "user": {
                "id": user.id,
                "email": user.email,
            },
            "token": token,
        }, status=status.HTTP_201_CREATED)


class ActivateView(APIView):
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
