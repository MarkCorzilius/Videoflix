from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from django.core import mail


class RegisterModelTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.email = "test@example.com"
        self.password = "Password123!"
        self.register_data = {
            "email": self.email,
            "password": self.password,
            "confirmed_password": self.password,
        }

    def test_register_success(self):
        response = self.client.post("/api/register/", self.register_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_email_returns_400(self):
        User.objects.create_user(email=self.email, password=self.password)
        response = self.client.post("/api/register/", self.register_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email_returns_400(self):
        data = self.register_data.copy()
        data["email"] = "invalid_mail"
        response = self.client.post("/api/register/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weak_password_returns_400(self):
        data = self.register_data.copy()
        data["confirmed_password"] = "weakpass"
        data["password"] = "weakpass"
        response = self.client.post("/api/register/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_passwords_do_not_match_returns_400(self):
        data = self.register_data.copy()
        data["confirmed_password"] = "AnotherPassword123!"
        response = self.client.post("/api/register/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_required_fields_missing(self):
        response = self.client.post("/api/register/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_is_unverified_after_registration(self):
        response = self.client.post("/api/register/", self.register_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=self.email)
        self.assertFalse(user.is_active)

    def test_verification_email_is_sent(self):
        response = self.client.post("/api/register/", self.register_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.email])