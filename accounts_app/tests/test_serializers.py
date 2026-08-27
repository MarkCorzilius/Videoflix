from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts_app.models import User
from accounts_app.api.serializers import RegisterSerializer, LoginSerializer


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


class LoginSerializerTests(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "Password123!"
        self.user = User.objects.create_user(email=self.email, password=self.password, is_active=True)
        self.correct_data = {
            "email": self.email,
            "password": self.password,
        }

    def test_success_login(self):
        serializer = LoginSerializer(data=self.correct_data)

        self.assertTrue(serializer.is_valid())

    def test_not_registered_user_login(self):
        serializer = LoginSerializer(data={
            "email": "notRegisteredUser@gmail.com",
            "password": self.password,
        })

        self.assertFalse(serializer.is_valid())

    def test_wrong_password_login(self):
        data = self.correct_data.copy()
        data["password"] = "wrongPassword123!"
        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_login_without_password(self):
        data = self.correct_data.copy()
        data.pop("password")
        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_login_without_email(self):
        data = self.correct_data.copy()
        data.pop("email")
        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_inactive_user_login(self):
        email = "seconduser@gmail.com"
        password="strongpassword123!"
        User.objects.create_user(email=email, password=password, is_active=False)
        data = {
            "email": email,
            "password": password,
        }
        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_login_without_email_and_password(self):
        serializer = LoginSerializer(data={})

        self.assertFalse(serializer.is_valid())

# add serializer
# add jwt