from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from accounts_app.api.serializers import RegisterSerializer


class RegisterSerializerTests(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "Password123!"
        self.user = User.objects.create_user(email=self.email, password=self.password)

    def test_required_fields(self):
        data = {
            "email": self.email,
            "password": self.password,
            "confirmed_password": self.password,
        }
        required_fields = [
            "email",
            "password",
            "confirmed_password",
        ]

        for field in required_fields:
            test_data = data.copy()
            test_data.pop(field)
            serializer = RegisterSerializer(data=test_data)

            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
                

    def test_invalid_password(self):
        serializer = RegisterSerializer(data={
            "email": self.email,
            "password": "bad-pass",
            "confirmed_password": "bad-pass",
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_invalid_email(self):
        serializer = RegisterSerializer(data={
            "email": "invalid_mail",
            "password": self.password,
            "confirmed_password": self.password,
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


    def test_passwords_do_not_match(self):
        serializer = RegisterSerializer(data={
            "email": self.email,
            "password": self.password,
            "confirmed_password": "WrongPassword123!",
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("confirmed_password", serializer.errors)

    def test_duplicate_email(self):
        serializer = RegisterSerializer(data={
            "email": self.email,
            "password": self.password,
            "confirmed_password": self.password,
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_serialized_output(self):
        serializer = RegisterSerializer(self.user)

        self.assertEqual(serializer.data["email"], self.email)
        self.assertNotIn("password", serializer.data)
