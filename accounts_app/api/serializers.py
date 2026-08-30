from rest_framework import serializers
from accounts_app.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "confirmed_password"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirmed_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirmed_password")
        return User.objects.create_user(**validated_data)


class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        data["id"] = self.user.id
        data["username"] = self.user.username
        
        return data



class PasswordResetRequestSerializer(serializers.Serializer):
    pass


class PasswordResetConfirmSerializer(serializers.Serializer):
    pass