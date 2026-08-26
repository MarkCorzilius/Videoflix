from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts_app.models import User
from accounts_app.api.serializers import RegisterSerializer


class RegisterSerializerTests(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "Password123!"

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
        self.assertIn(field, serializer.errors)
                

    def test_invalid_password(self):
        serializer = RegisterSerializer(data={
            "email": self.email,
            "password": "123",
            "confirmed_password": "123",
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
        self.assertEqual(
            str(serializer.errors["non_field_errors"][0]),
            "Passwords do not match."
        )
        
    def test_duplicate_email(self):
        User.objects.create_user(email=self.email, password=self.password)
        serializer = RegisterSerializer(data={
            "email": self.email,
            "password": self.password,
            "confirmed_password": self.password,
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_serialized_output(self):
        user = User.objects.create_user(email=self.email, password=self.password)
        serializer = RegisterSerializer(user)

        self.assertEqual(serializer.data["email"], self.email)
        self.assertNotIn("password", serializer.data)
