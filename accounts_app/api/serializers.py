from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts_app.models import User


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "confirmed_password"]

    def validate_password(self, value):
        """Validate the password against Django's password strength rules."""

        validate_password(value)
        return value

    def validate(self, attrs):
        """Ensure the password and confirmation match."""

        if attrs["password"] != attrs["confirmed_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        """Create a new user, discarding the confirmation field."""

        validated_data.pop("confirmed_password")
        return User.objects.create_user(**validated_data)


class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        """Add the user id and username to the token response payload."""

        data = super().validate(attrs)

        data["id"] = self.user.id
        data["username"] = self.user.username

        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        """Validate the password against Django's password strength rules."""

        validate_password(value)
        return value

    def validate(self, attrs):
        """Ensure the password and confirmation match."""

        if attrs["password"] != attrs["confirmed_password"]:
            raise serializers.ValidationError({"confirmed_password": "Passwords do not match."})
        return attrs